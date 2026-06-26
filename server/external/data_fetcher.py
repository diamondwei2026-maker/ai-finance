"""外部数据源适配模块 — 封装 akshare 调用。

所有函数通过 asyncio.to_thread 将同步 akshare 调用转为异步，
并对单个数据源异常抛出 RecoverableError（上层可据此将对应指标标 N/A）。

数据源：天天基金（东方财富）、雪球、中债信息网（中国债券信息网）。
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

import akshare as ak
import pandas as pd

from core.exceptions import RecoverableError, ErrorCode


async def _safe_fetch(
    indicator_name: str,
    fetch_fn: Any,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """通用的 try/except 包装器 — 在线程池中执行同步 akshare 调用。

    将 akshare 同步调用转为异步执行，并统一处理异常：
    - 网络错误、akshare 内部异常 → RecoverableError（含指标名称标识）
    - 返回空 DataFrame → RecoverableError

    注意：第一个参数命名为 indicator_name（而非 indicator），
    以避免与 akshare 函数的 indicator 关键字参数冲突。

    Args:
        indicator_name: 指标名称标识（如 "fund_info"），用于异常消息和日志定位
        fetch_fn: 同步的 akshare 函数引用（不在此处调用，只传入引用供 to_thread 调用）
        *args: 传递给 fetch_fn 的位置参数
        **kwargs: 传递给 fetch_fn 的关键字参数

    Returns:
        akshare 原始返回值（通常为 pd.DataFrame）

    Raises:
        RecoverableError: 数据获取失败或返回空数据
    """
    result: Any
    try:
        result = await asyncio.to_thread(fetch_fn, *args, **kwargs)
    except Exception as e:
        raise RecoverableError(
            message=f"{indicator_name} 数据获取失败: {e}",
            code=ErrorCode.DATA_SOURCE_FAILED,
        ) from e

    # 检查空 DataFrame
    if isinstance(result, pd.DataFrame) and result.empty:
        raise RecoverableError(
            message=f"{indicator_name} 数据为空",
            code=ErrorCode.DATA_SOURCE_FAILED,
        )

    return result


def _safe_float(value: Any) -> float | None:
    """安全地将值转换为 float，转换失败返回 None。"""
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _to_date_str(value: Any) -> str:
    """将日期值转换为 'YYYY-MM-DD' 字符串。

    支持 datetime.date、pd.Timestamp、datetime.datetime 和 str 类型。
    """
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d")
    return str(value)[:10]  # 兜底：取前 10 个字符


# ═══════════════════════════════════════════════════════════════════════
# 公开 API
# ═══════════════════════════════════════════════════════════════════════


async def fetch_fund_info(code: str) -> dict[str, Any]:
    """获取基金基本信息（名称、类型、最新净值）。

    使用两个数据源组装：
    - fund_individual_basic_info_xq（雪球）：获取名称、类型、代码等基本属性
    - fund_open_fund_info_em（天天基金）：获取最新单位净值

    注意：七日年化收益率通常仅货币基金提供，债券基金可能没有此数据；
    若无法获取，seven_day_yield 字段为 None。

    Args:
        code: 6 位基金代码（如 "020741"）

    Returns:
        {
            "indicator": "fund_info",
            "value": None,
            "name": str,
            "code": str,
            "type": str,
            "nav": float,
            "seven_day_yield": float | None,
            "unit": "",
            "source": "akshare",
            "fetched_at": datetime,
        }

    Raises:
        RecoverableError: 基金不存在或数据源获取失败
    """
    # 1. 获取基金基本信息（名称、类型）
    try:
        basic_df: pd.DataFrame = await _safe_fetch(
            "fund_info",
            ak.fund_individual_basic_info_xq,
            symbol=code,
            timeout=10,
        )
    except RecoverableError as e:
        # akshare 对无效基金代码返回的响应中缺少 'data' 键（KeyError），
        # _safe_fetch 将其包装为 RecoverableError。对于任何基金基本信息
        # 获取失败的情况，统一按"基金不存在"处理
        raise RecoverableError(
            message=f"基金不存在（代码：{code}），请检查后重新输入",
            code=ErrorCode.FUND_NOT_FOUND,
        ) from e

    # fund_individual_basic_info_xq 返回 item/value 两列
    basic_dict: dict[str, str] = {}
    for _, row in basic_df.iterrows():
        basic_dict[str(row["item"])] = str(row["value"])

    fund_name: str = basic_dict.get("基金名称", "")
    fund_type: str = basic_dict.get("基金类型", "")

    # 若找不到基金名称，说明代码无效
    if not fund_name:
        raise RecoverableError(
            message=f"基金不存在（代码：{code}），请检查后重新输入",
            code=ErrorCode.FUND_NOT_FOUND,
        )

    # 2. 获取最新净值
    nav: float | None = None
    try:
        nav_df: pd.DataFrame = await _safe_fetch(
            "fund_nav_latest",
            ak.fund_open_fund_info_em,
            symbol=code,
            indicator="单位净值走势",
            period="成立以来",
        )
        if not nav_df.empty:
            # 最后一行是最新净值（按日期升序），取「单位净值」列
            latest = nav_df.iloc[-1]
            nav_col = (
                "单位净值"
                if "单位净值" in nav_df.columns
                else nav_df.columns[1]
            )
            nav = _safe_float(latest[nav_col])
    except RecoverableError:
        # 净值获取失败不阻断整体流程，nav 保持 None
        pass

    # 3. 七日年化 — 债券基金通常不提供，设为 None
    # 该字段需通过 fund_money_fund_info_em 等货币基金专用接口获取，
    # 对于债券基金暂不可用，保留 None 供上层处理
    seven_day_yield: float | None = None

    return {
        "indicator": "fund_info",
        "value": None,  # 复合数据，value 为 None
        "name": fund_name,
        "code": code,
        "type": fund_type,
        "nav": nav,
        "seven_day_yield": seven_day_yield,
        "unit": "",
        "source": "akshare",
        "fetched_at": datetime.now(),
    }


async def fetch_fund_nav_history(
    code: str,
    days: int = 90,
) -> dict[str, Any]:
    """获取基金历史净值序列（近 N 日）。

    使用 fund_open_fund_info_em 获取单位净值走势，按日期降序排列后
    截取前 days 条。若历史数据不足 days 条，返回全部已有数据（不抛异常）。

    Args:
        code: 6 位基金代码
        days: 获取天数，默认 90

    Returns:
        {
            "indicator": "fund_nav_history",
            "value": None,
            "data": [{"date": "YYYY-MM-DD", "nav": float}, ...],
            "unit": "",
            "source": "akshare",
            "fetched_at": datetime,
        }
    """
    df: pd.DataFrame = await _safe_fetch(
        "fund_nav_history",
        ak.fund_open_fund_info_em,
        symbol=code,
        indicator="单位净值走势",
        period="成立以来",
    )

    # 确定日期列和净值列
    date_col: str = df.columns[0]  # 第一列为净值日期
    nav_col: str = (
        "单位净值" if "单位净值" in df.columns else df.columns[1]
    )

    # 构建数据列表并转为标准格式
    records: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        records.append({
            "date": _to_date_str(row[date_col]),
            "nav": _safe_float(row[nav_col]),
        })

    # 按日期降序排列（最新在前），过滤掉 nav 为 None 的行
    records = [r for r in records if r["nav"] is not None]
    records.sort(key=lambda x: x["date"], reverse=True)

    # 截取前 days 条（days <= 0 时返回空列表）
    if days > 0:
        records = records[:days]
    else:
        records = []

    return {
        "indicator": "fund_nav_history",
        "value": None,
        "data": records,
        "unit": "",
        "source": "akshare",
        "fetched_at": datetime.now(),
    }


async def fetch_treasury_yield() -> dict[str, Any]:
    """获取当前中国 10 年期国债收益率。

    使用 bond_china_yield 获取中债国债收益率曲线。
    DataFrame 结构：列为 ['曲线名称', '日期', '3月', '6月', '1年', '3年', '5年', '7年', '10年', '30年']
    行为不同债券类型（国债、企业债 AAA 等）。

    当日数据可能尚未发布 → 逐日回退到最近 5 个自然日。

    Returns:
        {
            "indicator": "treasury_yield_10y",
            "value": float | None,    # 收益率（%）
            "unit": "%",
            "source": "akshare",
            "fetched_at": datetime,
        }
    """
    yield_value: float | None = None
    today = datetime.now()

    for offset in range(5):
        target_date = today - pd.Timedelta(days=offset)
        date_str: str = target_date.strftime("%Y%m%d")
        try:
            df: pd.DataFrame = await _safe_fetch(
                "treasury_yield_10y",
                ak.bond_china_yield,
                start_date=date_str,
                end_date=date_str,
            )
            # 查找「曲线名称」列和「10年」列
            name_col = _find_column(df, ["曲线名称"])
            if name_col and "10年" in df.columns:
                for _, row in df.iterrows():
                    if "国债" in str(row[name_col]):
                        yield_value = _safe_float(row["10年"])
                        break
            if yield_value is not None:
                break
        except RecoverableError:
            # 当日无数据，回退到前一天
            continue

    return {
        "indicator": "treasury_yield_10y",
        "value": yield_value,
        "unit": "%",
        "source": "akshare",
        "fetched_at": datetime.now(),
    }


async def fetch_credit_spread() -> dict[str, Any]:
    """获取 AA+ 级信用债与国债的利差（bp）。

    信用利差为辅助指标。bond_china_yield 直接提供的是 AAA 级和国债数据，
    AA+ 利差不可直接获取，采用优雅降级策略：
    - 优先尝试从 bond_china_yield 中获取 AAA 企业债与国债 10 年期利差作为近似
    - 若 bond_china_yield 不可用，value 设为 None，不抛异常

    Returns:
        {
            "indicator": "credit_spread_aa_plus",
            "value": float | None,  # 利差（bp），不可获取时为 None
            "unit": "bp",
            "source": "akshare",
            "fetched_at": datetime,
        }
    """
    spread_value: float | None = None
    today = datetime.now()

    for offset in range(5):
        target_date = today - pd.Timedelta(days=offset)
        date_str: str = target_date.strftime("%Y%m%d")
        try:
            df: pd.DataFrame = await _safe_fetch(
                "credit_spread_aa_plus",
                ak.bond_china_yield,
                start_date=date_str,
                end_date=date_str,
            )
            name_col = _find_column(df, ["曲线名称"])
            if name_col and "10年" in df.columns:
                treasury_10y: float | None = None
                enterprise_10y: float | None = None
                for _, row in df.iterrows():
                    name_str = str(row[name_col])
                    if "国债" in name_str:
                        treasury_10y = _safe_float(row["10年"])
                    elif "AAA" in name_str:
                        # bond_china_yield 提供的 AAA 级曲线包括
                        # "商业银行普通债(AAA)"、"中短期票据(AAA)" 等，
                        # 使用 AAA 作为 AA+ 的近似值
                        enterprise_10y = _safe_float(row["10年"])
                if treasury_10y is not None and enterprise_10y is not None:
                    # 收益率差 × 100 = bp
                    spread_value = round((enterprise_10y - treasury_10y) * 100, 2)
                    break
        except RecoverableError:
            continue

    return {
        "indicator": "credit_spread_aa_plus",
        "value": spread_value,
        "unit": "bp",
        "source": (
            "akshare (AAA proxy for AA+)"
            if spread_value is not None
            else "akshare: credit_spread_not_available"
        ),
        "fetched_at": datetime.now(),
    }


def _find_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """在 DataFrame 列名中查找第一个匹配的列名。

    支持部分匹配：若列名包含候选字符串即视为匹配。

    Args:
        df: 待搜索的 DataFrame
        candidates: 候选列名子串列表

    Returns:
        匹配到的第一个列名，未找到返回 None
    """
    for col in df.columns:
        for candidate in candidates:
            if candidate in str(col):
                return col
    return None
