"""API 请求/响应 Pydantic Schema。

纯数据结构定义，不含 MongoDB 持久化逻辑。
用于 FastAPI 路由层的请求校验和响应序列化。
"""

from typing import Generic, TypeVar

from pydantic import BaseModel

# ═══════════════════════════════════════════════════════════════════════
# 泛型包装
# ═══════════════════════════════════════════════════════════════════════

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应包装。

    成功响应:
        {"code": 0, "message": "success", "data": {...}}
    错误响应:
        {"code": 40001, "message": "...", "data": null}
    """

    code: int
    """业务状态码。0 = 成功，非 0 = 错误码。"""

    message: str
    """提示信息。"""

    data: T | None = None
    """响应数据，错误时为 None。"""


# ═══════════════════════════════════════════════════════════════════════
# 基金查询
# ═══════════════════════════════════════════════════════════════════════


class FundInfoResponse(BaseModel):
    """GET /api/v1/funds/{code} 响应体。"""

    fund_code: str
    """6 位基金代码。"""

    name: str
    """基金名称。"""

    fund_type: str
    """基金类型。"""

    nav: float | None = None
    """最新单位净值。"""

    seven_day_annual_yield: float | None = None
    """七日年化收益率（%），非货币基金可能为 None。"""

    updated_at: str
    """数据更新时间（ISO 格式字符串）。"""

    disclaimer: str
    """免责声明固定文本。"""


# ═══════════════════════════════════════════════════════════════════════
# 收益计算
# ═══════════════════════════════════════════════════════════════════════


class CalculationRequest(BaseModel):
    """POST /api/v1/calculations 请求体。"""

    fund_code: str
    """6 位基金代码（格式校验由 service 层负责）。"""


class CalculationResponse(BaseModel):
    """GET /api/v1/calculations/{id} 响应体。

    字段命名与 ADR 5.3 节响应 JSON 完全一致。
    """

    fund_code: str
    fund_name: str

    # ── 8 项收益指标 ──────────────────────────────────────────

    nav: float | None = None
    daily_change_pct: float | None = None
    seven_day_annual_yield: float | None = None
    wanfen_income: float | None = None
    one_month_return: float | None = None
    three_month_max_drawdown: float | None = None
    ten_year_treasury: float | None = None
    credit_spread_aa_plus: float | None = None

    # ── 元数据 ────────────────────────────────────────────────

    data_date: str
    """数据日期 "YYYY-MM-DD"。"""

    is_trading_day: bool
    """是否为交易日。"""

    disclaimer: str
    """免责声明固定文本。"""
