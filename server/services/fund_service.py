"""基金查询业务逻辑 — 格式校验、类型判断、缓存编排。

完整查询链路：
    格式校验 → 内存缓存 → MongoDB → 外部数据源 → 类型校验 → 持久化 → 返回
"""

import re
from typing import Any

from loguru import logger

from external.data_fetcher import fetch_fund_info
from models.fund import Fund
from models.schemas import FundInfoResponse
from repositories import fund_repo
from core.cache import get_cache
from core.error_codes import (
    FUND_NOT_FOUND,
    FUND_TYPE_MISMATCH,
    INVALID_CODE_FORMAT,
)
from core.error_codes import ErrorMessages
from core.exceptions import AppException, RecoverableError

# ═══════════════════════════════════════════════════════════════════════
# 常量
# ═══════════════════════════════════════════════════════════════════════

FUND_CODE_PATTERN = re.compile(r"^\d{6}$")
"""基金代码格式：恰好 6 位数字。"""

DISCLAIMER_TEXT = (
    "本工具提供的收益数据基于公开数据计算，仅供参考，"
    "不构成投资建议。投资有风险，操作需谨慎。"
)
"""免责声明固定文本（与 ADR 5.3 节保持一致）。"""

CACHE_PREFIX = "fund:"
"""内存缓存 key 前缀，与 core/cache.py 的 TTL 匹配规则对齐。"""


# ═══════════════════════════════════════════════════════════════════════
# 校验函数
# ═══════════════════════════════════════════════════════════════════════


def _validate_code(code: str) -> None:
    """校验基金代码格式：必须为恰好 6 位数字。

    Args:
        code: 待校验的基金代码。

    Raises:
        AppException(code=40003, status_code=400): 格式不合法。
    """
    if not FUND_CODE_PATTERN.match(code):
        raise AppException(
            message=ErrorMessages.INVALID_CODE_FORMAT,
            code=INVALID_CODE_FORMAT,
            status_code=400,
        )


def _validate_fund_type(fund_type: str) -> None:
    """校验基金类型是否含"债"字（债券型）。

    Args:
        fund_type: 基金类型字符串（如"中长期纯债"、"混合型"）。

    Raises:
        AppException(code=40002): 非债券型。
    """
    if "债" not in fund_type:
        raise AppException(
            message=ErrorMessages.format(
                ErrorMessages.FUND_TYPE_MISMATCH,
                fund_type=fund_type,
            ),
            code=FUND_TYPE_MISMATCH,
        )


# ═══════════════════════════════════════════════════════════════════════
# 核心业务函数
# ═══════════════════════════════════════════════════════════════════════


def _to_response(fund: Fund) -> FundInfoResponse:
    """将 Fund 文档模型转换为 API 响应 Schema。

    注意：Fund.updated_at 是 datetime 类型，需转为 ISO 格式字符串
    以匹配 FundInfoResponse 的 str 类型定义。
    """
    return FundInfoResponse(
        fund_code=fund.fund_code,
        name=fund.name,
        fund_type=fund.fund_type,
        nav=None,  # 净值在后续 Task 2.1 计算引擎中填充
        seven_day_annual_yield=None,
        updated_at=fund.updated_at.isoformat(),
        disclaimer=DISCLAIMER_TEXT,
    )


def _make_response_from_cache(data: dict[str, Any]) -> FundInfoResponse:
    """从缓存字典构建 FundInfoResponse。"""
    return FundInfoResponse(
        fund_code=str(data["fund_code"]),
        name=str(data["name"]),
        fund_type=str(data["fund_type"]),
        nav=data.get("nav"),
        seven_day_annual_yield=data.get("seven_day_annual_yield"),
        updated_at=str(data["updated_at"]),
        disclaimer=DISCLAIMER_TEXT,
    )


async def _fetch_and_persist(code: str) -> Fund:
    """调用外部数据源获取基金信息，校验类型后持久化到 MongoDB 和内存缓存。

    Args:
        code: 6 位基金代码（已通过格式校验）。

    Returns:
        持久化后的 Fund 文档。

    Raises:
        AppException(code=40001): 基金不存在。
        AppException(code=40002): 非债券型基金。
    """
    # 调用外部数据源
    logger.info("内存缓存未命中，调用外部数据源查询基金 code={}", code)
    try:
        raw = await fetch_fund_info(code)
    except RecoverableError as e:
        # data_fetcher 对无效代码已封装为 RecoverableError(code=FUND_NOT_FOUND)
        raise AppException(
            message=ErrorMessages.format(
                ErrorMessages.FUND_NOT_FOUND, code=code
            ),
            code=FUND_NOT_FOUND,
        )

    fund_name: str = str(raw.get("name", ""))
    fund_type: str = str(raw.get("type", ""))

    # 类型校验 —— 在持久化前执行，非债券型不写入 DB
    _validate_fund_type(fund_type)

    # 持久化到 MongoDB
    fund = await fund_repo.upsert_fund(
        code=code,
        name=fund_name,
        fund_type=fund_type,
    )
    logger.info("基金 {} ({}) 已缓存到 MongoDB", code, fund_name)

    # 写入内存缓存
    cache = get_cache(CACHE_PREFIX)
    cache[f"{CACHE_PREFIX}{code}"] = {
        "fund_code": fund.fund_code,
        "name": fund.name,
        "fund_type": fund.fund_type,
        "nav": None,
        "seven_day_annual_yield": None,
        "updated_at": fund.updated_at.isoformat(),
    }

    return fund


async def query_fund(code: str) -> FundInfoResponse:
    """查询基金信息的完整业务编排。

    流程：
    1. 格式校验 — 6 位数字，不合法抛出 AppException(40003)
    2. 查内存缓存 — 命中直接返回
    3. 查 MongoDB — 命中则写回内存缓存后返回
    4. 调外部数据源 → 类型校验 → 持久化 → 返回

    Args:
        code: 6 位基金代码。

    Returns:
        FundInfoResponse。

    Raises:
        AppException: 格式错误(40003) / 基金不存在(40001) / 类型不匹配(40002)。
    """
    # 步骤 1: 格式校验（在任何 I/O 前）
    _validate_code(code)

    cache_key = f"{CACHE_PREFIX}{code}"

    # 步骤 2: 查内存缓存
    cache = get_cache(CACHE_PREFIX)
    if cache_key in cache:
        logger.debug("内存缓存命中 code={}", code)
        return _make_response_from_cache(cache[cache_key])

    # 步骤 3: 查 MongoDB
    fund = await fund_repo.find_by_code(code)
    if fund is not None:
        logger.debug("MongoDB 缓存命中 code={}", code)
        # 写回内存缓存
        cache[cache_key] = {
            "fund_code": fund.fund_code,
            "name": fund.name,
            "fund_type": fund.fund_type,
            "nav": None,
            "seven_day_annual_yield": None,
            "updated_at": fund.updated_at.isoformat(),
        }
        return _to_response(fund)

    # 步骤 4: 调外部数据源 → 校验 → 持久化
    fund = await _fetch_and_persist(code)
    return _to_response(fund)
