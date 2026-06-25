"""市场利率数据时间序列 MongoDB 文档模型。

记录每次获取的市场利率指标值，支持按指标名称和时间查询。
"""

from datetime import datetime

from beanie import Document


class MarketData(Document):
    """市场数据文档模型 — 映射到 MongoDB `market_data` 集合。"""

    indicator_name: str
    """指标名称（如 "treasury_yield_10y"、"credit_spread_aa_plus"）。"""

    value: float
    """指标数值。"""

    unit: str
    """单位（"%" 或 "bp"）。"""

    fetched_at: datetime
    """数据获取时间（由调用方在写入前赋值）。"""

    class Settings:
        name = "market_data"
        indexes = [
            [("indicator_name", 1), ("fetched_at", -1)],
        ]
