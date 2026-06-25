"""收益计算完整指标快照 MongoDB 文档模型。

每次计算产生的完整结果快照，关联基金代码，支持历史查询。
"""

from datetime import datetime

from beanie import Document


class Calculation(Document):
    """计算结果文档模型 — 映射到 MongoDB `calculations` 集合。"""

    fund_code: str
    """关联的基金代码。"""

    fund_name: str = ""
    """基金名称。"""

    # ── 8 项收益指标 ──────────────────────────────────────────

    nav: float | None = None
    """最新单位净值。"""

    daily_change_pct: float | None = None
    """日涨跌幅（%）。"""

    seven_day_annual_yield: float | None = None
    """七日年化收益率（%）。"""

    wanfen_income: float | None = None
    """万份收益（元）。"""

    one_month_return: float | None = None
    """近 1 月收益率（%）。"""

    three_month_max_drawdown: float | None = None
    """近 3 月最大回撤（%）。"""

    ten_year_treasury: float | None = None
    """10 年期国债收益率（%）。"""

    credit_spread_aa_plus: float | None = None
    """信用利差（bp）。"""

    # ── 元数据 ────────────────────────────────────────────────

    data_date: str
    """数据日期，格式 "YYYY-MM-DD"。"""

    is_trading_day: bool
    """是否为交易日。"""

    status: str = "processing"
    """计算状态：processing | completed | failed。"""

    error_message: str | None = None
    """失败时的错误描述。"""

    disclaimer: str = ""
    """免责声明文本。"""

    created_at: datetime
    """计算结果创建时间（由调用方在写入前赋值）。"""

    class Settings:
        name = "calculations"
        indexes = [
            [("fund_code", 1), ("created_at", -1)],
        ]
