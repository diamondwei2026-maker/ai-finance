"""市场数据访问层 — MongoDB CRUD 操作。

操作 market_data 集合，记录每次获取的市场利率指标值。
"""

from datetime import datetime

from models.market_data import MarketData


async def save_market_data(
    indicator_name: str,
    value: float,
    unit: str,
    fetched_at: datetime | None = None,
) -> MarketData:
    """保存一条市场数据记录到 MongoDB。

    Args:
        indicator_name: 指标名称（如 "treasury_yield_10y"、"credit_spread_aa_plus"）。
        value: 指标数值。
        unit: 单位（"%" 或 "bp"）。
        fetched_at: 数据获取时间，None 时自动设为当前时间。

    Returns:
        保存后的 MarketData 文档。
    """
    md = MarketData(
        indicator_name=indicator_name,
        value=value,
        unit=unit,
        fetched_at=fetched_at or datetime.now(),
    )
    return await md.insert()


async def get_latest(indicator_name: str) -> MarketData | None:
    """查询指定指标的最新一条记录。

    按 fetched_at 降序排列，取第一条。

    Args:
        indicator_name: 指标名称。

    Returns:
        最新的 MarketData 文档或 None（无记录）。
    """
    return await MarketData.find_one(
        MarketData.indicator_name == indicator_name
    ).sort(-MarketData.fetched_at)
