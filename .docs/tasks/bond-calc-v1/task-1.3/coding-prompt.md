# Coding Prompt — Task 1.3: 基金查询 API

> 生成日期：2025-06-25 | 基于 ADR v1.0 + 测试用例 v1.0

---

## 1. 任务目标

实现完整的基金查询链路：Repository 层（MongoDB CRUD）→ Service 层（基金校验 + 类型判断 + 数据编排）→ Route 层（`GET /api/v1/funds/{code}`），集成交易日历和错误码体系。

---

## 2. 技术上下文

- **语言/框架**: Python 3.11+ / FastAPI / Beanie ODM / Motor
- **数据库**: MongoDB Atlas → `funds` 集合
- **外部依赖**: `exchange_calendars`（交易日历）、`akshare`（已由 data_fetcher 封装）
- **已有可复用代码**:
  - `models/fund.py` — Fund Beanie 文档模型（`fund_code`, `name`, `fund_type`, `updated_at`）
  - `models/schemas.py` — `ApiResponse[T]`、`FundInfoResponse`（响应 Schema 已定义）
  - `external/data_fetcher.py` — `fetch_fund_info(code)` 异步函数，返回 fund_info dict
  - `core/exceptions.py` — `AppException`、`RecoverableError`、`FatalError`、`ErrorCode`
  - `core/cache.py` — `get_cache(prefix)`、`get_or_set(cache, key, factory)`

### 涉及文件

| 操作 | 文件 | 说明 |
|------|------|------|
| **新建** | `server/repositories/fund_repo.py` | 基金 MongoDB CRUD |
| **新建** | `server/services/fund_service.py` | 基金查询业务编排 |
| **新建** | `server/api/routes/funds.py` | `GET /api/v1/funds/{code}` 路由 |
| **新建** | `server/core/error_codes.py` | 错误码常量定义 |
| **新建** | `server/core/trading_calendar.py` | 交易日历封装 |
| **修改** | `server/core/exceptions.py` | 解决错误码 40003 冲突 |
| **修改** | `server/api/main.py` | 注册 Fund 模型 + fund 路由 |

---

## 3. 实现要求

### ⚠️ 重要：错误码冲突处理

当前 `exceptions.py` 中 `DATA_SOURCE_FAILED = 40003` 与任务要求的 `INVALID_CODE_FORMAT = 40003` 冲突。
解决方案：将 `DATA_SOURCE_FAILED` 移位至 `40004`，给 `INVALID_CODE_FORMAT` 腾出 `40003`。

### 3.1 新建 `server/core/error_codes.py` — 错误码常量

按任务验收标准定义以下常量（含中文错误消息）：

```python
class ErrorMessages:
    """错误码对应的中文提示信息。"""

    FUND_NOT_FOUND: str = "基金不存在（代码：{code}），请检查后重新输入"
    FUND_TYPE_MISMATCH: str = "仅支持债券型基金，当前类型：{fund_type}"
    INVALID_CODE_FORMAT: str = "基金代码格式错误，请输入6位数字代码"

    @classmethod
    def format(cls, template: str, **kwargs) -> str:
        """用关键字参数格式化消息模板。"""
        return template.format(**kwargs)
```

- `FUND_NOT_FOUND = 40001`
- `FUND_TYPE_MISMATCH = 40002`
- `INVALID_CODE_FORMAT = 40003`

> **注意**：这 3 个常量可以与 `core/exceptions.py` 中的 `ErrorCode` 类合并，也可以独立在 `error_codes.py` 中定义。推荐在 `error_codes.py` 中定义完整的错误码 + 消息映射，然后 `exceptions.py` 中的 `ErrorCode` 改为从 `error_codes` 导入。
>
> **具体做法**：将 `core/exceptions.py` 中的 `ErrorCode` 类修改为从 `core/error_codes` 导入常量（避免删除后影响已有引用代码）。同时将 `DATA_SOURCE_FAILED` 值改为 `40004`。

### 3.2 新建 `server/repositories/fund_repo.py` — 基金 Repository

```python
"""基金数据访问层 — MongoDB CRUD 操作。"""

from models.fund import Fund
from datetime import datetime


async def find_by_code(code: str) -> Fund | None:
    """按基金代码查询缓存文档。

    Args:
        code: 6 位基金代码

    Returns:
        Fund 文档或 None
    """
    # 使用 Beanie 的 find_one 异步查询
    pass


async def upsert_fund(
    code: str,
    name: str,
    fund_type: str,
) -> Fund:
    """插入或更新基金缓存文档。

    若 fund_code 已存在则更新 name / fund_type / updated_at；
    否则插入新文档。

    Args:
        code: 6 位基金代码
        name: 基金名称
        fund_type: 基金类型

    Returns:
        保存后的 Fund 文档
    """
    # 1. 先 find_one 检查是否存在
    # 2. 存在 → 更新字段 + save()
    # 3. 不存在 → 创建 Fund() + insert()
    # 注意：updated_at 每次写入时设为 datetime.now()
    pass
```

**关键点**：
- 依赖 `models/fund.py` 中的 `Fund(Document)` 模型
- `upsert_fund` 手动实现查+插逻辑（Beanie 的 `update_one(upsert=True)` 在异步下需要注意）
- 异常不做捕获——原样抛出给 service 层处理
- 返回的 `Fund` 实例含 MongoDB 自动生成的 `id` 字段

### 3.3 新建 `server/services/fund_service.py` — 基金 Service

```python
"""基金查询业务逻辑 — 格式校验、类型判断、缓存编排。"""

from models.fund import Fund
from models.schemas import FundInfoResponse
from external.data_fetcher import fetch_fund_info
from repositories import fund_repo
from core.exceptions import AppException, RecoverableError
from core.error_codes import ErrorMessages
from core.cache import get_cache, get_or_set

FUND_CODE_PATTERN = r"^\d{6}$"
"""基金代码格式：恰好 6 位数字。"""

DISCLAIMER_TEXT = (
    "本工具提供的收益数据基于公开数据计算，仅供参考，"
    "不构成投资建议。投资有风险，操作需谨慎。"
)
"""免责声明固定文本（与 ADR 5.3 节一致）。"""


def _validate_code(code: str) -> None:
    """校验基金代码格式：必须为恰好 6 位数字。

    Raises:
        AppException(code=40003, status_code=400): 格式不合法
    """
    import re
    if not re.match(FUND_CODE_PATTERN, code):
        raise AppException(
            message=ErrorMessages.INVALID_CODE_FORMAT,
            code=40003,
            status_code=400,
        )


def _validate_fund_type(fund_type: str) -> None:
    """校验基金类型是否含"债"字。

    Raises:
        AppException(code=40002): 非债券型，message 含实际类型
    """
    if "债" not in fund_type:
        raise AppException(
            message=ErrorMessages.format(
                ErrorMessages.FUND_TYPE_MISMATCH,
                fund_type=fund_type,
            ),
            code=40002,
        )


async def query_fund(code: str) -> FundInfoResponse:
    """查询基金信息的完整编排。

    流程：
    1. 格式校验（6位数字）
    2. 查缓存 → 命中则直接返回（跳过外部调用）
    3. 查 MongoDB → 命中则返回
    4. 调 data_fetcher.fetch_fund_info() → 持久化 → 返回
    5. 类型校验（必须含"债"字）

    Args:
        code: 6 位基金代码

    Returns:
        FundInfoResponse（符合 schemas.py 定义）

    Raises:
        AppException: 格式错误(40003) / 基金不存在(40001) / 类型不匹配(40002)
    """
    # 步骤 1：格式校验
    _validate_code(code)

    # 步骤 2：查内存缓存（key = f"fund:{code}"）
    # 使用 get_cache("fund:") + get_or_set

    # 步骤 3：缓存未命中 → 查 MongoDB
    # fund = await fund_repo.find_by_code(code)

    # 步骤 4：DB 未命中 → 调外部数据源
    # 若 fetch_fund_info 抛出 RecoverableError（基金不存在），
    # 将其转换为 AppException(code=40001)

    # 步骤 5：类型校验（fund_type 必须含"债"字）

    # 步骤 6：持久化到 MongoDB + 写入内存缓存

    # 步骤 7：组装 FundInfoResponse 返回
    pass
```

**关键逻辑说明**：

1. **格式校验优先**：在任何 I/O 操作前先校验代码格式，避免无效请求消耗外部 API
2. **缓存层级**：内存缓存（TTL 30min）→ MongoDB（持久化）→ 外部数据源
3. **基金不存在处理**：`data_fetcher.fetch_fund_info()` 对无效代码抛出 `RecoverableError(code=FUND_NOT_FOUND)`，service 层捕获后抛出 `AppException(code=40001, status_code=200)` 作为业务错误返回（非 HTTP 500）
4. **非债券型处理**：类型不含"债"字时在持久化前就抛出 `AppException(code=40002)`，不写入 DB
5. **`updated_at` 转换**：Fund 模型的 `updated_at` 是 `datetime` 类型，响应中转为 ISO 格式字符串

### 3.4 新建 `server/api/routes/funds.py` — 基金路由

```python
"""基金查询 API 路由 — GET /api/v1/funds/{code}。"""

from fastapi import APIRouter, Path
from models.schemas import ApiResponse, FundInfoResponse
from services.fund_service import query_fund
from core.exceptions import AppException

router = APIRouter(prefix="/funds", tags=["基金查询"])


@router.get(
    "/{code}",
    response_model=ApiResponse[FundInfoResponse],
    summary="查询基金基本信息",
    description="输入 6 位基金代码，返回名称、类型、最新净值、七日年化等信息。仅支持债券型基金。",
)
async def get_fund(
    code: str = Path(
        ...,
        pattern=r"^\d{6}$",
        description="6 位基金代码",
        example="020741",
    ),
) -> ApiResponse[FundInfoResponse]:
    """GET /api/v1/funds/{code}"""
    try:
        fund_info = await query_fund(code)
        return ApiResponse(
            code=0,
            message="success",
            data=fund_info,
        )
    except AppException as e:
        return ApiResponse(
            code=e.code,
            message=e.message,
            data=None,
        )
```

**关键点**：
- 路由前缀 `/funds`（注册到 main.py 时再加 `/api/v1`）
- `Path` 参数自带 `pattern=r"^\d{6}$"` 做第一道格式防线（FastAPI 层面校验，格式错误返回 422）
- `response_model` 用 `ApiResponse[FundInfoResponse]` 确保 Swagger 文档显示完整响应结构
- `tags=["基金查询"]` 确保 Swagger UI 中分组显示
- **注意**：Path 正则校验只能拦住一部分格式错误（FastAPI 返回 422），Service 层还有二次校验可返回更友好的中文错误（40003）。实际运行时如果 Path 正则已拦住，格式错误不会走到 Service 层——这是可接受的（FastAPI 默认返回的 422 含详细校验信息）。

### 3.5 新建 `server/core/trading_calendar.py` — 交易日历

```python
"""交易日历模块 — 封装 exchange_calendars，判断指定日期是否为交易日。"""

import datetime as dt
from loguru import logger


def is_trading_day(date: dt.date | None = None) -> bool:
    """判断指定日期是否为交易日（上交所/深交所）。

    默认按非交易日处理（保守策略）：若 exchange_calendars
    不可用、数据缺失、或发生任何异常，均返回 False。

    Args:
        date: 待判断的日期，None 表示当天

    Returns:
        True 表示交易日，False 表示非交易日或无法判断
    """
    if date is None:
        date = dt.date.today()

    try:
        import exchange_calendars as ec

        # XSHG = 上海证券交易所
        cal = ec.get_calendar("XSHG")
        # is_session() 判断是否为交易日
        return cal.is_session(str(date))
    except Exception:
        logger.warning(
            "交易日历判断失败，默认按非交易日处理 (date={})",
            date.isoformat(),
        )
        return False
```

**设计决策**：
- 使用 `XSHG`（上交所）日历——中国债券市场与股票市场交易日高度一致
- `is_session()` 参数类型需要实验确认：字符串 `"2025-06-25"` 或 `pd.Timestamp`。如果 `str(date)` 不行，尝试 `pd.Timestamp(date)`
- 保守策略：任何异常都返回 `False`，避免在非交易日给出"今天是交易日"的错误判断

### 3.6 修改 `server/core/exceptions.py` — 错误码冲突解决

**修改 `ErrorCode` 类**：

```python
# 修改前
DATA_SOURCE_FAILED: int = 40003   # 数据源获取失败（可恢复）

# 修改后
DATA_SOURCE_FAILED: int = 40004   # 数据源获取失败（可恢复）
```

同时检查 `data_fetcher.py` 中所有引用 `ErrorCode.DATA_SOURCE_FAILED` 的地方——仅引用常量名，不硬编码数字，因此修改常量值后无需改动调用方。

**新增导入**（可选——将错误码与消息合并管理）：

在 `ErrorCode` 类中添加：
```python
INVALID_CODE_FORMAT: int = 40003  # 基金代码格式错误
```

> 如果 `error_codes.py` 中已有 `INVALID_CODE_FORMAT = 40003`，则 `exceptions.py` 的 `ErrorCode` 中可以不加（但为避免多处定义不一致，推荐在 `ErrorCode` 中保留所有错误码，然后 `error_codes.py` 从 `exceptions.py` 导入）。

### 3.7 修改 `server/api/main.py` — 注册模型和路由

**修改位置 1**：Beanie 初始化 — `document_models` 列表

```python
# 修改前（第 24-27 行附近）
await init_beanie(
    database=client.get_default_database(),
    document_models=[],  # 后续 Task 逐步添加 Document 模型
)

# 修改后
from models.fund import Fund

await init_beanie(
    database=client.get_default_database(),
    document_models=[Fund],
)
```

**修改位置 2**：路由注册

```python
# 在 app = FastAPI(...) 之后，CORS 中间件之后添加
from api.routes import funds

app.include_router(funds.router, prefix="/api/v1")
```

---

## 4. 代码规范要求

1. **异步优先**：所有 I/O 操作（DB 查询、外部 API 调用）使用 `async/await`
2. **Pydantic 序列化**：响应对象使用 `schemas.py` 中已定义的 Schema，不用 dict 裸传
3. **异常传播**：Repository 层不捕获异常（原样抛出），Service 层捕获后转换为 `AppException`，Route 层捕获 `AppException` 生成错误响应
4. **日志**：使用 `loguru.logger`，关键步骤（外部数据源调用、DB 写入）记录 INFO 日志
5. **类型标注**：所有函数签名含完整 Python 类型标注
6. **中文错误消息**：所有面向用户的错误消息用中文
7. **免责声明**：`DISCLAIMER_TEXT` 常量定义在 `fund_service.py` 中，与 ADR 5.3 节一致

---

## 5. 测试要求

代码必须能通过以下 13 个测试用例（详见 `test-cases.md`）：

| 编号 | 用例 | 关键断言 |
|------|------|---------|
| TC-001 | 查询存在的债券型基金 | 200, `code: 0`, `data.fund_type` 含"债", DB 已缓存 |
| TC-002 | 查询已缓存基金 | 200, 不走外部数据源, `updated_at` 不变 |
| TC-003 | disclaimer 字段 | `data.disclaimer` 非空 |
| TC-004 | 6位数字边界 | `000001` 格式校验通过（不返回 40003） |
| TC-005 | 位数不足/超出 | 5位/7位/空 → 400, `code: 40003` |
| TC-006 | 含非数字字符 | 含字母/特殊字符/空格 → 400, `code: 40003` |
| TC-007 | INVALID_CODE_FORMAT | `abc` → 400, `code: 40003`, 中文提示 |
| TC-008 | FUND_NOT_FOUND | `999999` → 200, `code: 40001`, 中文提示 |
| TC-009 | FUND_TYPE_MISMATCH | 混合型 → 200, `code: 40002`, 含实际类型 |
| TC-010 | 数据源降级 | RecoverableError → 非 0 错误码, 降级不崩溃 |
| TC-011 | 端到端链路 | 首次写 DB + 二次从 DB 读 |
| TC-012 | is_trading_day | 周六→False, 周一→True, 异常→False |
| TC-013 | Swagger 文档 | `/api/v1/funds/{code}` 出现在 OpenAPI JSON |

---

## 6. 注意事项

1. **错误码 40003 冲突必须解决**：修改 `DATA_SOURCE_FAILED` 为 40004 后，确保 `data_fetcher.py` 中无硬编码数字引用
2. **Beanie `find_one` 语法**：`await Fund.find_one(Fund.fund_code == code)`（用类属性做过滤条件）
3. **Beanie upsert 语义**：`await Fund.find_one(...).upsert(...)` 可用但不直观；推荐手动查+选择 insert 或 save
4. **Path 正则 vs Service 校验**：FastAPI 的 `Path(pattern=...)` 返回 422 而非 40003。两种处理都可行：Path 正则做第一道防线（返回 422），格式错误被 FastAPI 提前拦截；若要返回 40003 中文错误，则路由层不用 Path pattern，改在 Service 层统一校验
5. **`FundInfoResponse` 字段**：`updated_at` 在 Schema 中是 `str` 类型，需在 Service 层做 `datetime.isoformat()` 转换
6. **exchange_calendars 的 `is_session()` 参数**：需实验确认接受 `str` 还是 `pd.Timestamp`。如果 `str(date)` 报类型错误，改用 `pd.Timestamp(date)`
7. **内存缓存 key 设计**：`f"fund:{code}"` 与 `core/cache.py` 的前缀匹配规则对齐（`startswith("fund:")` → TTL 30min）
