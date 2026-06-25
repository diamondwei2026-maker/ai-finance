"""市场利率数据服务 — 获取、缓存和持久化市场利率指标。

职责：
- 从 data_fetcher 获取 10 年期国债收益率和信用利差
- 优先从内存缓存读取（TTL 2min）
- 缓存未命中调 data_fetcher 并写入缓存
- 异步持久化到 MongoDB（fire-and-forget，不阻塞返回）
"""

import asyncio
import datetime as dt
from typing import Any

from loguru import logger

from external.data_fetcher import fetch_treasury_yield, fetch_credit_spread
from core.cache import get_cache

CACHE_PREFIX = "market:"
CACHE_KEY = "market:latest"
"""市场利率缓存键 — 所有市场利率数据共用同一个 key。"""


async def _persist_async(
    rates: dict[str, float | None],
    fetched_at: dt.datetime,
) -> None:
    """fire-and-forget 持久化：将市场利率数据异步写入 MongoDB。

    持久化失败仅记录警告日志，不影响主流程返回。
    """
    try:
        from repositories import market_repo

        tasks = []
        if rates.get("ten_year_treasury") is not None:
            tasks.append(
                market_repo.save_market_data(
                    indicator_name="treasury_yield_10y",
                    value=rates["ten_year_treasury"],
                    unit="%",
                    fetched_at=fetched_at,
                )
            )
        if rates.get("credit_spread_aa_plus") is not None:
            tasks.append(
                market_repo.save_market_data(
                    indicator_name="credit_spread_aa_plus",
                    value=rates["credit_spread_aa_plus"],
                    unit="bp",
                    fetched_at=fetched_at,
                )
            )
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.debug("市场数据已持久化到 MongoDB")
    except Exception:
        logger.warning("市场数据持久化失败（market_repo 不可用），仅影响历史记录")
        return


async def get_market_rates() -> dict[str, float | None]:
    """获取当前市场利率数据（含内存缓存）。

    返回：
        {"ten_year_treasury": float | None, "credit_spread_aa_plus": float | None}

    流程：
    1. 查内存缓存（key = "market:latest"，TTL 2min）
       → 命中直接返回
    2. 缓存未命中 → asyncio.gather 并行调用 fetch_treasury_yield() 和
       fetch_credit_spread()
       → 使用 return_exceptions=True，单源失败对应 value 为 None
    3. 组装结果 dict → 写入内存缓存
    4. fire-and-forget 异步持久化到 MongoDB：
       使用 asyncio.create_task 调用 market_repo.save_market_data()
       → 持久化失败不阻塞、不影响返回结果，仅 log 警告

    Returns:
        {"ten_year_treasury": float | None, "credit_spread_aa_plus": float | None}
    """
    # 步骤 1: 查内存缓存
    cache = get_cache(CACHE_PREFIX)
    if CACHE_KEY in cache:
        logger.debug("市场利率缓存命中")
        return cache[CACHE_KEY]

    # 步骤 2: 并行获取
    logger.info("市场利率缓存未命中，并行获取外部数据")
    results = await asyncio.gather(
        fetch_treasury_yield(),
        fetch_credit_spread(),
        return_exceptions=True,
    )

    treasury_raw = results[0] if not isinstance(results[0], BaseException) else None
    credit_raw = results[1] if not isinstance(results[1], BaseException) else None

    # 步骤 3: 组装结果
    rates: dict[str, float | None] = {
        "ten_year_treasury": treasury_raw.get("value") if treasury_raw else None,
        "credit_spread_aa_plus": credit_raw.get("value") if credit_raw else None,
    }

    # 写入内存缓存
    cache[CACHE_KEY] = rates
    logger.info(
        "市场利率已缓存 treasury={} spread={}",
        rates["ten_year_treasury"],
        rates["credit_spread_aa_plus"],
    )

    # 步骤 4: fire-and-forget 持久化
    try:
        _ = asyncio.create_task(_persist_async(rates, dt.datetime.now()))
    except Exception:
        logger.warning("market_repo 不可用，跳过持久化")

    return rates
