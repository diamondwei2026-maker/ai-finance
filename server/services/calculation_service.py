"""收益计算编排服务 — 并行拉取数据源，计算 8 项收益指标。

每个指标独立计算：单指标失败返回 None，不中断其他指标计算。
编排层通过 asyncio.gather(return_exceptions=True) 实现数据源并行拉取与单源失败降级。
"""

from __future__ import annotations

import asyncio
import datetime as dt
from typing import Any

from loguru import logger

from external.data_fetcher import (
    fetch_fund_info,
    fetch_fund_nav_history,
    fetch_treasury_yield,
    fetch_credit_spread,
)
from models.schemas import CalculationResponse
from core.cache import get_cache
from core.exceptions import FatalError, ErrorCode
from core.trading_calendar import is_trading_day
from services.fund_service import DISCLAIMER_TEXT

CACHE_PREFIX = "calc:"


# ═══════════════════════════════════════════════════════════════════════
# 8 项指标计算函数（每个独立，单指标失败返回 None）
# ═══════════════════════════════════════════════════════════════════════


def _calc_nav(nav_history: list[dict[str, Any]]) -> float | None:
    """最新单位净值：取历史净值列表第一条（最新日期）的 nav 值。

    Args:
        nav_history: fetch_fund_nav_history 返回的 data 列表，
                     按日期降序排列，每条为 {"date": str, "nav": float}。

    Returns:
        最新净值，列表为空时返回 None。
    """
    if not nav_history:
        return None
    return nav_history[0].get("nav")


def _calc_daily_change(nav_history: list[dict[str, Any]]) -> float | None:
    """日涨跌幅（%）：(当日净值 - 前一日净值) / 前一日净值 × 100。

    需要至少 2 条净值记录；不足 2 条返回 None，不抛异常。
    """
    if len(nav_history) < 2:
        return None

    latest_nav = nav_history[0].get("nav")
    prev_nav = nav_history[1].get("nav")

    if latest_nav is None or prev_nav is None or prev_nav == 0:
        return None

    return (latest_nav - prev_nav) / prev_nav * 100


def _calc_one_month_return(nav_history: list[dict[str, Any]]) -> float | None:
    """近 1 月收益率（%）：(最新净值 - 30日前净值) / 30日前净值 × 100。

    历史净值不足 30 条时返回 None（优雅降级）。
    注意：30 条记录 != 30 个自然日，但采用保守处理——有 30 条就计算，
    不足则不计算，避免数据不足导致的计算偏差。
    """
    if len(nav_history) < 30:
        return None

    latest_nav = nav_history[0].get("nav")
    old_nav = nav_history[29].get("nav")

    if latest_nav is None or old_nav is None or old_nav == 0:
        return None

    return (latest_nav - old_nav) / old_nav * 100


def _calc_max_drawdown(nav_history: list[dict[str, Any]]) -> float | None:
    """近 3 月最大回撤（%）：max(1 - 当日净值 / 区间最高净值) × 100。

    遍历净值序列（从旧到新），维护区间最高净值，在每个点计算回撤率，
    取最大值。

    至少需要 1 条数据，否则返回 None。
    单调上涨时回撤为 0。
    """
    if not nav_history:
        return None

    # 从旧到新遍历（reversed），因为 nav_history 是按日期降序（最新在前）
    max_nav = nav_history[-1].get("nav")
    if max_nav is None or max_nav == 0:
        return None

    max_dd = 0.0
    for record in reversed(nav_history):
        nav = record.get("nav")
        if nav is None:
            continue
        max_nav = max(max_nav, nav)
        dd = (1 - nav / max_nav) * 100
        max_dd = max(max_dd, dd)

    return max_dd


def _calc_seven_day_yield(fund_info: dict[str, Any]) -> float | None:
    """七日年化收益率：直接获取或返回 None。

    债券基金通常不提供此数据。货币基金可能提供。
    从 fund_info["seven_day_yield"] 中提取。
    """
    if not fund_info:
        return None
    return fund_info.get("seven_day_yield")


def _calc_wanfen_income(fund_info: dict[str, Any]) -> float | None:
    """万份收益：直接获取或返回 None。

    注意：当前 data_fetcher.fetch_fund_info 尚未返回万份收益字段，
    此函数预留接口，当前始终返回 None。后续 Task 如需支持货币基金可扩展。
    """
    if not fund_info:
        return None
    # 当前 data_fetcher 尚未返回万份收益字段，预留接口
    return fund_info.get("wanfen_income")


# ═══════════════════════════════════════════════════════════════════════
# 编排函数
# ═══════════════════════════════════════════════════════════════════════


async def calculate(fund_code: str) -> CalculationResponse:
    """计算基金收益指标的完整编排。

    流程：
    1. 检查内存缓存 — key = f"calc:{fund_code}"，命中直接返回
    2. asyncio.gather 并行拉取 4 个数据源：
       - fetch_fund_info(fund_code)
       - fetch_fund_nav_history(fund_code, days=90)
       - fetch_treasury_yield()
       - fetch_credit_spread()
       使用 return_exceptions=True，单源失败不中断
    3. 从 gather 结果中提取 fund_info、nav_history、treasury、credit_spread
       - 若某结果 is Exception → 对应变量为 None
    4. 调用 8 项指标计算函数（每个独立计算，失败返回 None）
    5. 组装 CalculationResponse：
       - fund_name 从 fund_info 中提取（若 fund_info 为 None 则空字符串）
       - 指标字段可能为 None（正常降级）
       - data_date = dt.date.today().isoformat()
       - is_trading_day = is_trading_day()
       - disclaimer = DISCLAIMER_TEXT
    6. 写入内存缓存（TTL 5min）
    7. 返回 CalculationResponse

    全部数据源失败判断：
    - 检查 fund_info、nav_history_raw、treasury_raw、credit_spread_raw 是否全为 None
    - 若全为 None → raise FatalError(code=ALL_SOURCES_FAILED, status_code=503)

    Args:
        fund_code: 6 位基金代码。

    Returns:
        CalculationResponse（Pydantic Schema，含 8 项指标 + 元数据）。

    Raises:
        FatalError: 所有数据源均不可用（status_code=503）。
    """
    # 步骤 1: 检查内存缓存
    cache = get_cache(CACHE_PREFIX)
    cache_key = f"{CACHE_PREFIX}{fund_code}"
    if cache_key in cache:
        logger.debug("计算结果缓存命中 code={}", fund_code)
        return cache[cache_key]

    # 步骤 2: asyncio.gather 并行拉取 4 个数据源
    logger.info("开始并行拉取数据源 code={}", fund_code)
    results = await asyncio.gather(
        fetch_fund_info(fund_code),
        fetch_fund_nav_history(fund_code, days=90),
        fetch_treasury_yield(),
        fetch_credit_spread(),
        return_exceptions=True,
    )

    # 步骤 3: 解包结果 — Exception 实例 → None，正常值保留
    fund_info = results[0] if not isinstance(results[0], BaseException) else None
    nav_history_raw = results[1] if not isinstance(results[1], BaseException) else None
    treasury_raw = results[2] if not isinstance(results[2], BaseException) else None
    credit_raw = results[3] if not isinstance(results[3], BaseException) else None

    # 记录各数据源状态
    sources = {
        "fund_info": "ok" if fund_info is not None else "failed",
        "nav_history": "ok" if nav_history_raw is not None else "failed",
        "treasury": "ok" if treasury_raw is not None else "failed",
        "credit": "ok" if credit_raw is not None else "failed",
    }
    logger.info("数据源拉取结果: {}", sources)

    # 步骤 4: 全部数据源失败检查
    if (
        fund_info is None
        and nav_history_raw is None
        and treasury_raw is None
        and credit_raw is None
    ):
        logger.error("所有数据源均不可用 code={}", fund_code)
        raise FatalError(
            message="服务暂时不可用，所有数据源获取失败，请稍后重试",
            code=ErrorCode.ALL_SOURCES_FAILED,
            status_code=503,
        )

    # 提取净值列表
    nav_history: list[dict[str, Any]] = (
        nav_history_raw.get("data", []) if nav_history_raw else []
    )

    # 步骤 4（续）: 调用各指标计算函数
    logger.debug("开始计算 8 项指标 code={}", fund_code)

    # 步骤 5: 组装 CalculationResponse
    response = CalculationResponse(
        fund_code=fund_code,
        fund_name=fund_info.get("name", "") if fund_info else "",
        nav=_calc_nav(nav_history),
        daily_change_pct=_calc_daily_change(nav_history),
        seven_day_annual_yield=_calc_seven_day_yield(fund_info or {}),
        wanfen_income=_calc_wanfen_income(fund_info or {}),
        one_month_return=_calc_one_month_return(nav_history),
        three_month_max_drawdown=_calc_max_drawdown(nav_history),
        ten_year_treasury=treasury_raw.get("value") if treasury_raw else None,
        credit_spread_aa_plus=credit_raw.get("value") if credit_raw else None,
        data_date=dt.date.today().isoformat(),
        is_trading_day=is_trading_day(),
        disclaimer=DISCLAIMER_TEXT,
    )

    logger.info(
        "计算完成 code={} nav={} daily_change={} 1m_return={} max_dd={} "
        "7d_yield={} wanfen={} treasury={} spread={}",
        fund_code,
        response.nav,
        response.daily_change_pct,
        response.one_month_return,
        response.three_month_max_drawdown,
        response.seven_day_annual_yield,
        response.wanfen_income,
        response.ten_year_treasury,
        response.credit_spread_aa_plus,
    )

    # 步骤 6: 写入内存缓存
    cache[cache_key] = response

    # 步骤 7: 返回
    return response
