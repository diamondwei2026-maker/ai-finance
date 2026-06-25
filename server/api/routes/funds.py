"""基金查询 API 路由 — GET /api/v1/funds/{code}。"""

from fastapi import APIRouter

from models.schemas import ApiResponse, FundInfoResponse
from services.fund_service import query_fund
from core.exceptions import AppException

router = APIRouter(prefix="/funds", tags=["基金查询"])


@router.get(
    "/{code}",
    response_model=ApiResponse[FundInfoResponse],
    summary="查询基金基本信息",
    description=(
        "输入 6 位基金代码，返回基金名称、类型、最新净值、"
        "七日年化等信息。仅支持债券型基金。"
    ),
)
async def get_fund(code: str) -> ApiResponse[FundInfoResponse]:
    """GET /api/v1/funds/{code}

    Args:
        code: 6 位基金代码（如 020741）。

    Returns:
        统一 ApiResponse 包装的 FundInfoResponse。
    """
    # 格式校验放在 Service 层（返回 40003 中文错误），
    # 不使用 Path(pattern=...) 避免 FastAPI 默认 422 响应
    try:
        fund_info = await query_fund(code)
        return ApiResponse(code=0, message="success", data=fund_info)
    except AppException as e:
        return ApiResponse(code=e.code, message=e.message, data=None)
