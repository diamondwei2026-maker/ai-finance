"""基金数据访问层 — MongoDB CRUD 操作。

所有函数异步，异常不在此层捕获——原样抛给 service 层处理。
"""

from datetime import datetime

from models.fund import Fund


async def find_by_code(code: str) -> Fund | None:
    """按基金代码查询缓存文档。

    Args:
        code: 6 位基金代码。

    Returns:
        Fund 文档或 None（未找到）。
    """
    return await Fund.find_one(Fund.fund_code == code)


async def upsert_fund(
    code: str,
    name: str,
    fund_type: str,
) -> Fund:
    """插入或更新基金缓存文档。

    若 fund_code 已存在则原地更新 name / fund_type / updated_at；
    否则插入新文档。

    Args:
        code: 6 位基金代码。
        name: 基金名称。
        fund_type: 基金类型（如"中长期纯债"）。

    Returns:
        保存后的 Fund 文档。
    """
    now = datetime.now()
    existing = await Fund.find_one(Fund.fund_code == code)

    if existing is not None:
        existing.name = name
        existing.fund_type = fund_type
        existing.updated_at = now
        await existing.save()
        return existing

    fund = Fund(
        fund_code=code,
        name=name,
        fund_type=fund_type,
        updated_at=now,
    )
    return await fund.insert()
