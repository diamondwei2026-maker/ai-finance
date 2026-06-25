"""计算 API 路由 — POST /api/v1/calculations + GET /api/v1/calculations/{id}。"""

import re
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from loguru import logger
from bson import ObjectId
from bson.errors import InvalidId

from models.schemas import ApiResponse, CalculationRequest
from models.calculation import Calculation
from services.calculation_service import calculate as do_calculate
from core.exceptions import AppException, ErrorCode
from core.config import settings

router = APIRouter(prefix="/calculations", tags=["收益计算"])


# ── 辅助函数 ──────────────────────────────────────────────────────────


def _validate_fund_code(fund_code: str) -> None:
    """校验基金代码格式：必须为 6 位数字。

    Args:
        fund_code: 待校验的基金代码。

    Raises:
        AppException: 格式不合法时抛出（status_code=200，由 ApiResponse 表达错误）。
    """
    if not re.match(r"^\d{6}$", fund_code):
        raise AppException(
            message="基金代码格式错误，请输入 6 位数字",
            code=ErrorCode.INVALID_CODE_FORMAT,
            status_code=200,
        )


def _build_completed_data(calc_doc: Calculation) -> dict:
    """从 Calculation 文档组装 GET completed 响应 data。

    所有字段显式列出，None 值字段也保留键名（前端展示为 N/A）。
    """
    return {
        "fund_code": calc_doc.fund_code,
        "fund_name": calc_doc.fund_name,
        "nav": calc_doc.nav,
        "daily_change_pct": calc_doc.daily_change_pct,
        "seven_day_annual_yield": calc_doc.seven_day_annual_yield,
        "wanfen_income": calc_doc.wanfen_income,
        "one_month_return": calc_doc.one_month_return,
        "three_month_max_drawdown": calc_doc.three_month_max_drawdown,
        "ten_year_treasury": calc_doc.ten_year_treasury,
        "credit_spread_aa_plus": calc_doc.credit_spread_aa_plus,
        "data_date": calc_doc.data_date,
        "is_trading_day": calc_doc.is_trading_day,
        "disclaimer": calc_doc.disclaimer,
        "status": "completed",
    }


# ── 路由 ──────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=ApiResponse[dict],
    summary="触发基金收益计算",
    description=(
        "输入 6 位基金代码，触发 8 项收益指标异步计算。"
        "同一基金代码 + 5 分钟内有缓存结果时直接返回已有 calculation_id。"
    ),
    responses={
        200: {"description": "计算完成"},
        503: {"description": "所有数据源不可用"},
    },
)
async def trigger_calculation(request: CalculationRequest):
    """POST /api/v1/calculations

    触发收益计算，返回 calculation_id 供后续查询。
    同一基金代码在 5 分钟内重复请求直接返回已有结果。

    Args:
        request: CalculationRequest（fund_code 必填）。

    Returns:
        ApiResponse[dict]: {"calculation_id": str, "status": str}
    """
    fund_code = request.fund_code

    calc_doc = None  # 在 try 块内赋值，用于区分"校验失败"和"计算失败"

    try:
        # 1. 格式校验
        _validate_fund_code(fund_code)

        # 2. MongoDB 缓存检查 — 同一 fund_code + 5 分钟内已完成计算
        five_min_ago = datetime.utcnow() - timedelta(seconds=settings.CACHE_TTL_CALC)
        existing = await Calculation.find_one(
            Calculation.fund_code == fund_code,
            Calculation.created_at >= five_min_ago,
            Calculation.status == "completed",
        )
        if existing:
            logger.debug("命中 MongoDB 缓存 code={}", fund_code)
            return ApiResponse(
                code=0,
                message="success",
                data={"calculation_id": str(existing.id), "status": "completed"},
            )

        # 3. 检查是否已有进行中的计算（防止并发重复创建）
        in_progress = await Calculation.find_one(
            Calculation.fund_code == fund_code,
            Calculation.status == "processing",
        )
        if in_progress:
            logger.debug("已有进行中的计算 code={} id={}", fund_code, in_progress.id)
            return ApiResponse(
                code=0,
                message="success",
                data={
                    "calculation_id": str(in_progress.id),
                    "status": "processing",
                },
            )

        # 4. 创建 processing 文档
        logger.info("开始计算 code={}", fund_code)
        calc_doc = Calculation(
            fund_code=fund_code,
            fund_name="",
            status="processing",
            data_date="",
            is_trading_day=False,
            disclaimer="",
            created_at=datetime.utcnow(),
        )
        await calc_doc.insert()

        # 5. 执行计算
        result = await do_calculate(fund_code)

        # 6. 字段映射 — CalculationResponse → Calculation 文档
        calc_doc.fund_name = result.fund_name
        calc_doc.nav = result.nav
        calc_doc.daily_change_pct = result.daily_change_pct
        calc_doc.seven_day_annual_yield = result.seven_day_annual_yield
        calc_doc.wanfen_income = result.wanfen_income
        calc_doc.one_month_return = result.one_month_return
        calc_doc.three_month_max_drawdown = result.three_month_max_drawdown
        calc_doc.ten_year_treasury = result.ten_year_treasury
        calc_doc.credit_spread_aa_plus = result.credit_spread_aa_plus
        calc_doc.data_date = result.data_date
        calc_doc.is_trading_day = result.is_trading_day
        calc_doc.disclaimer = result.disclaimer
        calc_doc.status = "completed"
        await calc_doc.save()

        logger.info("计算完成 code={} id={}", fund_code, calc_doc.id)
        return ApiResponse(
            code=0,
            message="success",
            data={"calculation_id": str(calc_doc.id), "status": "completed"},
        )

    except AppException as e:
        # FatalError 是 AppException 子类，统一在此捕获
        if calc_doc is not None:
            # 计算过程中失败 — 标记 failed 并返回 calculation_id
            calc_doc.status = "failed"
            calc_doc.error_message = e.message
            await calc_doc.save()
            logger.error("计算失败 code={}: {}", fund_code, e.message)
            return ApiResponse(
                code=e.code,
                message=e.message,
                data={
                    "calculation_id": str(calc_doc.id),
                    "status": "failed",
                },
            )
        # 格式校验失败（calc_doc 未创建）— 返回纯错误，无 calculation_id
        logger.warning("请求参数校验失败 code={}: {}", fund_code, e.message)
        return ApiResponse(code=e.code, message=e.message, data=None)

    except Exception as e:
        calc_doc.status = "failed"
        calc_doc.error_message = str(e)
        await calc_doc.save()
        logger.error("计算失败（未知异常） code={}: {}", fund_code, str(e))
        return ApiResponse(
            code=ErrorCode.CALCULATION_FAILED,
            message=f"计算失败：{str(e)}",
            data={
                "calculation_id": str(calc_doc.id),
                "status": "failed",
            },
        )


@router.get(
    "/{calculation_id}",
    response_model=ApiResponse[dict],
    summary="获取计算结果",
    description="根据 calculation_id 查询收益计算详情。",
    responses={
        200: {"description": "计算结果"},
        404: {"description": "计算结果不存在"},
    },
)
async def get_calculation(calculation_id: str):
    """GET /api/v1/calculations/{id}

    根据 calculation_id 查询计算结果。支持三种状态返回：
    - processing: 计算中，提示刷新
    - completed: 返回完整的 8 项指标 + 元数据
    - failed: 返回错误信息

    Args:
        calculation_id: MongoDB ObjectId 字符串（24 字符十六进制）。

    Returns:
        ApiResponse[dict]: 根据状态返回不同结构的 data。

    Raises:
        HTTPException: ID 格式无效或计算结果不存在时返回 404。
    """
    # 1. ID 格式校验
    try:
        obj_id = ObjectId(calculation_id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="计算结果不存在")

    # 2. MongoDB 查询
    calc_doc = await Calculation.get(obj_id)
    if calc_doc is None:
        raise HTTPException(status_code=404, detail="计算结果不存在")

    # 3. 状态分支
    if calc_doc.status == "processing":
        return ApiResponse(
            code=0,
            message="success",
            data={"status": "processing", "message": "计算中，请稍后刷新"},
        )

    if calc_doc.status == "failed":
        return ApiResponse(
            code=0,
            message="success",
            data={
                "status": "failed",
                "error_message": calc_doc.error_message or "未知错误",
            },
        )

    # status == "completed"
    return ApiResponse(
        code=0,
        message="success",
        data=_build_completed_data(calc_doc),
    )
