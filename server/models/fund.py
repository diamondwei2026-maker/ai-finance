"""基金基本信息 MongoDB 文档模型。

缓存从 akshare 获取的基金数据，以 fund_code 为唯一标识。
"""

from datetime import datetime

from beanie import Document, Indexed


class Fund(Document):
    """基金文档模型 — 映射到 MongoDB `funds` 集合。"""

    fund_code: Indexed(str, unique=True)
    """6 位基金代码，唯一索引。"""

    name: str
    """基金名称。"""

    fund_type: str
    """基金类型（如"中长期纯债"、"混合型"）。"""

    updated_at: datetime
    """数据更新时间（由调用方在写入前赋值）。"""

    class Settings:
        name = "funds"
        """MongoDB collection name。"""
