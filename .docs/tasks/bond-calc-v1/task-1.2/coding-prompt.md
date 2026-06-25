# Coding Prompt — Task 1.2: 数据模型定义

## 1. 任务目标

定义 3 个 Beanie MongoDB 文档模型（Fund、Calculation、MarketData）和 4+ 个 Pydantic API Schema（FundInfoResponse、CalculationRequest、CalculationResponse、ApiResponse[T]），为后续 repository 层和 API 层提供数据结构基础。

## 2. 技术上下文

- **语言/框架**: Python 3.11+ / Beanie ODM / Pydantic v2
- **数据库**: MongoDB Atlas（M0 免费层），集合名 `funds`、`calculations`、`market_data`
- **约束来源**: [ADR 第 6 章](../adr/server.md) 数据模型定义；[Task 1.1](task-1.1/task.md) data_fetcher 返回结构
- **已有代码**:
  - `server/models/__init__.py` — 当前仅一行注释，需扩展导出
  - `server/external/data_fetcher.py` — 4 个数据获取函数（返回 dict 结构见下文）
  - `server/core/exceptions.py` — RecoverableError、ErrorCode 已定义

### data_fetcher 返回结构速查（Task 1.1 产出）

| 函数 | 返回 dict key |
|------|--------------|
| `fetch_fund_info(code)` | `indicator`, `value`, `name`, `code`, `type`, `nav`, `seven_day_yield`, `unit`, `source`, `fetched_at` |
| `fetch_fund_nav_history(code, days)` | `indicator`, `value`, `data: [{date, nav}]`, `unit`, `source`, `fetched_at` |
| `fetch_treasury_yield()` | `indicator`, `value`, `unit`, `source`, `fetched_at` |
| `fetch_credit_spread()` | `indicator`, `value`, `unit`, `source`, `fetched_at` |

## 3. 涉及文件

| 操作 | 文件 | 说明 |
|------|------|------|
| 新建 | `server/models/fund.py` | Fund Beanie Document |
| 新建 | `server/models/calculation.py` | Calculation Beanie Document |
| 新建 | `server/models/market_data.py` | MarketData Beanie Document |
| 新建 | `server/models/schemas.py` | Pydantic API 请求/响应 Schema |
| 修改 | `server/models/__init__.py` | 导出所有模型和 Schema |

## 4. 实现要求

### 4.1 文件 `server/models/fund.py`

**职责**: 基金基本信息 MongoDB 文档模型，缓存从 akshare 获取的基金数据。

```python
from beanie import Document, Indexed
from datetime import datetime


class Fund(Document):
    fund_code: Indexed(str, unique=True)  # 6 位基金代码，唯一索引
    name: str                              # 基金名称
    fund_type: str                         # 基金类型（如"中长期纯债"）
    updated_at: datetime                   # 数据更新时间

    class Settings:
        name = "funds"                     # MongoDB collection name
```

**关键约束**:
- `fund_code` 使用 `Indexed(str, unique=True)` — Beanie 自动创建唯一索引
- `updated_at` 为 `datetime` 类型（非 `str`），由调用方在写入前赋值
- `Settings.name = "funds"` — 映射到 MongoDB `funds` 集合
- `Settings` 类不定义 `indexes`（唯一索引由 `Indexed(unique=True)` 自动处理）

### 4.2 文件 `server/models/calculation.py`

**职责**: 一次收益计算产生的完整指标快照，关联基金代码，支持历史查询。

```python
from beanie import Document
from datetime import datetime


class Calculation(Document):
    fund_code: str                         # 关联的基金代码
    nav: float | None = None               # 最新单位净值
    daily_change_pct: float | None = None  # 日涨跌幅（%）
    seven_day_annual_yield: float | None = None  # 七日年化收益率（%）
    wanfen_income: float | None = None     # 万份收益（元）
    one_month_return: float | None = None  # 近 1 月收益率（%）
    three_month_max_drawdown: float | None = None  # 近 3 月最大回撤（%）
    ten_year_treasury: float | None = None # 10 年期国债收益率（%）
    credit_spread_aa_plus: float | None = None  # 信用利差（bp）
    data_date: str                         # 数据日期 "YYYY-MM-DD"
    is_trading_day: bool                   # 是否为交易日
    created_at: datetime                   # 计算结果创建时间

    class Settings:
        name = "calculations"
        indexes = [
            [("fund_code", 1), ("created_at", -1)],  # 复合索引：按基金代码 + 时间降序
        ]
```

**关键约束**:
- 8 项指标字段类型统一为 `float | None`，默认值 `None` — 表示"数据不可获取"
- `data_date` 为 `str` 类型（格式 `"YYYY-MM-DD"`），与 `_to_date_str()` 输出一致
- `is_trading_day` 为 `bool` 类型
- `created_at` 为 `datetime` 类型
- `indexes` 定义复合索引 `(fund_code ASC, created_at DESC)` — 支持按基金代码查询并按时间降序排列
- 指标字段命名与 [ADR 5.3 节](../adr/server.md) 响应字段完全一致（如 `wanfen_income` 而非 `wanfen_yield`）

### 4.3 文件 `server/models/market_data.py`

**职责**: 市场利率数据时间序列，记录每次获取的指标值。

```python
from beanie import Document
from datetime import datetime


class MarketData(Document):
    indicator_name: str    # 指标名称（如 "treasury_yield_10y", "credit_spread_aa_plus"）
    value: float           # 指标数值
    unit: str              # 单位（"%" 或 "bp"）
    fetched_at: datetime   # 数据获取时间

    class Settings:
        name = "market_data"
        indexes = [
            [("indicator_name", 1), ("fetched_at", -1)],  # 复合索引
        ]
```

**关键约束**:
- `indicator_name` 存储 `data_fetcher` 返回的 `"indicator"` 字段值（如 `"treasury_yield_10y"`）
- `value` 为 `float`（非 `float | None`）— MarketData 仅在数据成功获取后才写入，不存在 None 场景
- `unit` 存储 `data_fetcher` 返回的 `"unit"` 字段值
- 复合索引 `(indicator_name ASC, fetched_at DESC)` 支持按指标名称查询最新数据

### 4.4 文件 `server/models/schemas.py`

**职责**: API 层使用的 Pydantic 请求/响应 Schema（不含 MongoDB 持久化逻辑）。

#### 4.4.1 ApiResponse[T] 泛型包装

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int           # 0 = 成功，非 0 = 错误码
    message: str        # 提示信息
    data: T | None = None  # 响应数据，错误时为 None
```

#### 4.4.2 FundInfoResponse — 基金查询响应

```python
class FundInfoResponse(BaseModel):
    fund_code: str
    name: str
    fund_type: str
    nav: float | None = None
    seven_day_annual_yield: float | None = None
    updated_at: str  # ISO 格式字符串
    disclaimer: str
```

**字段映射**（从 `data_fetcher.fetch_fund_info()` 的 dict）:

| Schema 字段 | data_fetcher 字段 | 说明 |
|------------|-------------------|------|
| `fund_code` | `code` | 基金代码 |
| `name` | `name` | 基金名称 |
| `fund_type` | `type` | 基金类型 |
| `nav` | `nav` | 最新净值 |
| `seven_day_annual_yield` | `seven_day_yield` | 七日年化 |
| `updated_at` | `fetched_at`（转 str） | 数据获取时间 |
| `disclaimer` | — | 固定免责声明文本 |

> **注意**: `disclaimer` 为固定值，在 service 层构造响应时赋值。文本内容：
> `"本工具提供的收益数据基于公开数据计算，仅供参考，不构成投资建议。投资有风险，操作需谨慎。"`

#### 4.4.3 CalculationRequest — 计算触发请求

```python
class CalculationRequest(BaseModel):
    fund_code: str  # 6 位基金代码
```

> 格式校验（6 位纯数字）在 service 层实现，不在 Schema 层做 regex 约束（保持 Schema 简洁）。

#### 4.4.4 CalculationResponse — 计算结果响应

```python
class CalculationResponse(BaseModel):
    fund_code: str
    fund_name: str
    nav: float | None = None
    daily_change_pct: float | None = None
    seven_day_annual_yield: float | None = None
    wanfen_income: float | None = None
    one_month_return: float | None = None
    three_month_max_drawdown: float | None = None
    ten_year_treasury: float | None = None
    credit_spread_aa_plus: float | None = None
    data_date: str
    is_trading_day: bool
    disclaimer: str
```

**关键约束**:
- 字段命名与 ADR 5.3 节响应 JSON 完全一致
- 所有数值指标默认 `None`（数据缺失场景）
- `disclaimer` 为必填字段，service 层构造时赋值

### 4.5 文件 `server/models/__init__.py`（修改）

当前内容仅一行注释，需扩展为导出所有公共符号：

```python
# Models module — Pydantic/Beanie 文档模型
from models.fund import Fund
from models.calculation import Calculation
from models.market_data import MarketData
from models.schemas import (
    ApiResponse,
    FundInfoResponse,
    CalculationRequest,
    CalculationResponse,
)

__all__ = [
    "Fund",
    "Calculation",
    "MarketData",
    "ApiResponse",
    "FundInfoResponse",
    "CalculationRequest",
    "CalculationResponse",
]
```

## 5. 代码规范要求

1. **Pydantic v2 风格**: 使用 `model_dump()` / `model_dump_json()` 序列化（非 v1 的 `dict()` / `json()`）
2. **类型注解**: 所有字段使用现代 Python 类型注解 `float | None`（非 `Optional[float]`）
3. **Beanie Document**: 继承 `Document`，`Settings` 内部类配置 collection name 和 indexes
4. **导入顺序**: 标准库 → 第三方库 → 本地模块
5. **文档字符串**: 每个类和模块含简短 `"""..."""` 说明
6. **泛型**: `ApiResponse` 使用 `Generic[T]` + `TypeVar`

## 6. 测试要求

代码必须能通过以下测试用例（详见 [test-cases.md](test-cases.md)）：

| 用例 | 验证点 |
|------|--------|
| TC-001 | Fund 创建、序列化、MongoDB 写入/查询 |
| TC-002 | Fund fund_code 唯一索引约束 |
| TC-003 | Fund 必填字段缺失 → ValidationError |
| TC-004 | Calculation 完整 8 项指标创建 |
| TC-005 | Calculation 部分指标为 None（数据缺失） |
| TC-006 | Calculation 复合索引 `(fund_code, created_at)` |
| TC-007 | Calculation created_at datetime 类型 |
| TC-008 | MarketData 创建与序列化 |
| TC-009 | MarketData 复合索引 `(indicator_name, fetched_at)` |
| TC-010 | FundInfoResponse 序列化含 disclaimer |
| TC-011 | CalculationRequest fund_code 字段存在且为 str |
| TC-012 | CalculationResponse 完整 + 部分 None 场景 |
| TC-013 | ApiResponse[T] 泛型成功 + 错误响应序列化 |
| TC-014 | Settings.name 和 indexes 配置正确 |
| TC-015 | 所有模型可从 `models` 包直接导入 |
| TC-016 | Schema 字段与 data_fetcher 返回结构兼容 |

## 7. 注意事项

1. **不要在此 Task 中初始化 Beanie 或连接 MongoDB** — Beanie 的 `init_beanie()` 调用在 `core/config.py`（Task 0.1 已完成）中，数据模型只定义结构，不需要也无法独立运行数据库操作
2. **`Indexed(str, unique=True)` 语法** — 这是 Beanie 的 `Indexed` 类型标注方式，不是 Pydantic 的 `Field()`，不要混淆
3. **`float | None` vs `Optional[float]`** — 使用前者（PEP 604 联合类型语法），与项目 Python 3.11+ 要求一致
4. **`Settings.indexes` 格式** — Beanie 要求 `list[list[tuple[str, int]]]`，每个元组为 `(字段名, 排序方向)`，1 = ASC，-1 = DESC
5. **不要创建 `models/base.py` 或自定义基类** — ADR 未定义此类抽象，直接继承 `Document` 即可
6. **Schema 中的 `disclaimer` 是 `str` 类型（非 optional）** — 每次响应都必须携带，service 层保证赋值
7. **`ApiResponse` 不要定义 `model_config` 或 `arbitrary_types_allowed`** — 普适泛型包装不应添加此类约束
