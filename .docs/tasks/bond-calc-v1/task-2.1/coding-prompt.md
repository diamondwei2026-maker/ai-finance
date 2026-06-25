# Coding Prompt — Task 2.1: 计算引擎与市场数据服务

> 生成日期：2025-06-25 | 基于 ADR v1.0 + 测试用例 v1.0

---

## 1. 任务目标

实现收益计算编排服务（并行拉取多数据源 → 独立计算 8 项指标 → 缓存结果）、市场数据服务（获取 + 缓存市场利率）和市场数据 Repository（MongoDB CRUD）。单源失败优雅降级，全源失败抛出 FatalError。

---

## 2. 技术上下文

- **语言/框架**: Python 3.11+ / FastAPI / Beanie ODM / cachetools
- **数据库**: MongoDB Atlas → `calculations` 集合、`market_data` 集合
- **外部依赖**: `akshare`（已封装）、`exchange_calendars`（交易日历）
- **已有可复用代码**:
  - `models/calculation.py` — `Calculation` Beanie 文档模型（8 项指标 + `data_date` + `is_trading_day` + `created_at`）
  - `models/market_data.py` — `MarketData` Beanie 文档模型（`indicator_name` + `value` + `unit` + `fetched_at`）
  - `models/schemas.py` — `CalculationResponse` Pydantic Schema（8 项指标 + 元数据，`disclaimer` 字段已定义）
  - `external/data_fetcher.py` — `fetch_fund_info(code)`、`fetch_fund_nav_history(code, days)`、`fetch_treasury_yield()`、`fetch_credit_spread()`
  - `core/cache.py` — `get_cache(prefix)` + `get_or_set(cache, key, factory)`，已注册 `"calc:"` (5min) 和 `"market:"` (2min) 前缀
  - `core/exceptions.py` — `AppException`、`RecoverableError`、`FatalError`、`ErrorCode`（含 `ALL_SOURCES_FAILED = 50001`、`CALCULATION_FAILED = 50002`）
  - `core/trading_calendar.py` — `is_trading_day(date)` 函数
  - `services/fund_service.py` — `DISCLAIMER_TEXT` 常量（计算服务需复用此文本）

### 涉及文件

| 操作 | 文件 | 说明 |
|------|------|------|
| **新建** | `server/services/calculation_service.py` | 收益计算编排 + 8 项指标计算 |
| **新建** | `server/services/market_service.py` | 市场利率数据获取与缓存 |
| **新建** | `server/repositories/market_repo.py` | 市场数据 MongoDB CRUD |
| **修改** | `server/api/main.py` | 注册 Calculation + MarketData 模型 |

---

## 3. 实现要求

### ⚠️ 重要：免责声明复用

`DISCLAIMER_TEXT` 常量已在 `services/fund_service.py` 中定义（与 ADR 5.3 节一致），计算服务中**不要重复定义**，直接从 `services.fund_service` 导入即可：
```python
from services.fund_service import DISCLAIMER_TEXT
```

### 3.1 新建 `server/services/calculation_service.py` — 计算编排服务

这是本 Task 的核心文件，包含两个部分：指标计算函数（内部）、编排函数 `calculate()`（公开）。

#### 3.1.1 8 项指标计算函数（模块级私有函数）

每个函数独立计算一个指标，单指标失败不抛异常——改为返回 `None`（让编排层统一处理）。

```python
"""收益计算编排服务 — 并行拉取数据源，计算 8 项收益指标。

每个指标独立计算：单指标失败返回 None，不中断其他指标计算。
编排层通过 asyncio.gather(return_exceptions=True) 实现数据源并行拉取与单源失败降级。
"""

import asyncio
import datetime as dt
from typing import Any

from loguru import logger

from external.data_fetcher import (
    fetch_fund_info,
    fetch_fund_nav_history,
    fetch_treasury_yield,
    fetch_credit_spread,
)
from models.schemas import CalculationResponse
from core.cache import get_cache
from core.exceptions import FatalError, ErrorCode
from core.trading_calendar import is_trading_day
from services.fund_service import DISCLAIMER_TEXT


# ═══════════════════════════════════════════════════════════════════════
# 8 项指标计算函数（每个独立，单指标失败返回 None）
# ═══════════════════════════════════════════════════════════════════════

def _calc_nav(nav_history: list[dict[str, Any]]) -> float | None:
    """最新单位净值：取历史净值列表第一条（最新日期）的 nav 值。

    Args:
        nav_history: fetch_fund_nav_history 返回的 data 列表，
                     按日期降序排列，每条为 {"date": str, "nav": float}。

    Returns:
        最新净值，列表为空时返回 None。
    """
    pass


def _calc_daily_change(nav_history: list[dict[str, Any]]) -> float | None:
    """日涨跌幅（%）：(当日净值 - 前一日净值) / 前一日净值 × 100。

    需要至少 2 条净值记录；不足 2 条返回 None，不抛异常。
    """
    pass


def _calc_one_month_return(nav_history: list[dict[str, Any]]) -> float | None:
    """近 1 月收益率（%）：(最新净值 - 30日前净值) / 30日前净值 × 100。

    历史净值不足 30 条时返回 None（优雅降级）。
    注意：30 条记录 != 30 个自然日，但采用保守处理——有 30 条就计算，
    不足则不计算，避免数据不足导致的计算偏差。
    """
    pass


def _calc_max_drawdown(nav_history: list[dict[str, Any]]) -> float | None:
    """近 3 月最大回撤（%）：max(1 - 当日净值 / 区间最高净值) × 100。

    遍历净值序列（从旧到新），维护区间最高净值，在每个点计算回撤率，
    取最大值。

    至少需要 1 条数据，否则返回 None。
    单调上涨时回撤为 0。
    """
    pass


def _calc_seven_day_yield(fund_info: dict[str, Any]) -> float | None:
    """七日年化收益率：直接获取或返回 None。

    债券基金通常不提供此数据。货币基金可能提供。
    从 fund_info["seven_day_yield"] 中提取。
    """
    pass


def _calc_wanfen_income(fund_info: dict[str, Any]) -> float | None:
    """万份收益：直接获取或返回 None。

    注意：当前 data_fetcher.fetch_fund_info 尚未返回万份收益字段，
    此函数预留接口，当前始终返回 None。后续 Task 如需支持货币基金可扩展。
    """
    pass
```

**关键设计决策 — 指标函数签名统一为接收原始数据、返回 float | None**：
- 所有指标函数不抛异常，无法计算时返回 `None`
- 编排层统一收集结果并组装 `CalculationResponse`

**关于 30 日前净值的处理**：
```python
# 取第 30 条（索引 29，最新在第 0 位）的净值
if len(nav_history) >= 30:
    old_nav = nav_history[29]["nav"]
    latest_nav = nav_history[0]["nav"]
    # 计算收益率
```

注意：历史净值序列是**按日期降序**（最新在前），所以索引 0 是最新净值。

**关于最大回撤的正向遍历**：
```python
# 从旧到新遍历（reversed）
max_nav = nav_history[-1]["nav"]  # 最旧净值作为初始最高
max_dd = 0.0
for record in reversed(nav_history):
    nav = record["nav"]
    max_nav = max(max_nav, nav)
    dd = (1 - nav / max_nav) * 100
    max_dd = max(max_dd, dd)
return max_dd
```

#### 3.1.2 编排函数 `calculate()`

```python
CACHE_PREFIX = "calc:"


async def calculate(fund_code: str) -> CalculationResponse:
    """计算基金收益指标的完整编排。

    流程：
    1. 检查内存缓存 — key = f"calc:{fund_code}"，命中直接返回
    2. asyncio.gather 并行拉取 4 个数据源：
       - fetch_fund_info(fund_code)
       - fetch_fund_nav_history(fund_code, days=90)
       - fetch_treasury_yield()
       - fetch_credit_spread()
       使用 return_exceptions=True，单源失败不中断
    3. 从 gather 结果中提取 fund_info、nav_history、treasury、credit_spread
       - 若某结果 is Exception → 对应变量为 None
    4. 调用 8 项指标计算函数（每个独立计算，失败返回 None）
    5. 组装 CalculationResponse：
       - fund_name 从 fund_info 中提取（若 fund_info 为 None 则空字符串）
       - 指标字段可能为 None（正常降级）
       - data_date = dt.date.today().isoformat()
       - is_trading_day = is_trading_day()
       - disclaimer = DISCLAIMER_TEXT
    6. 写入内存缓存（TTL 5min）
    7. 返回 CalculationResponse

    全部数据源失败判断：
    - 检查 fund_info、nav_history、treasury、credit_spread 是否全为 None
    - 若全为 None → raise FatalError(code=ALL_SOURCES_FAILED, status_code=503)

    Args:
        fund_code: 6 位基金代码。

    Returns:
        CalculationResponse（Pydantic Schema，含 8 项指标 + 元数据）。

    Raises:
        FatalError: 所有数据源均不可用（status_code=503）。
    """
    pass
```

**关键实现细节**：

1. **`asyncio.gather` 返回值处理**：
```python
results = await asyncio.gather(
    fetch_fund_info(fund_code),
    fetch_fund_nav_history(fund_code, days=90),
    fetch_treasury_yield(),
    fetch_credit_spread(),
    return_exceptions=True,
)

# 解包结果：Exception 实例 → None，正常值保留
fund_info = results[0] if not isinstance(results[0], BaseException) else None
nav_history_raw = results[1] if not isinstance(results[1], BaseException) else None
treasury_raw = results[2] if not isinstance(results[2], BaseException) else None
credit_raw = results[3] if not isinstance(results[3], BaseException) else None

# 提取净值列表
nav_history = nav_history_raw.get("data", []) if nav_history_raw else []
```

2. **全部失败判断逻辑**：
```python
# 4 个数据源全失败
if fund_info is None and nav_history_raw is None and treasury_raw is None and credit_raw is None:
    raise FatalError(
        message="服务暂时不可用，所有数据源获取失败，请稍后重试",
        code=ErrorCode.ALL_SOURCES_FAILED,
        status_code=503,
    )
```

注意判断条件：`nav_history_raw is None`（指数据源调用失败）与 `nav_history = []`（指数据为空）是不同的：
- 后者虽然历史净值为空，但如果 fund_info 成功获取（能拿到基金名），仍可返回部分结果
- 只有全部 4 个 `raw` 都是 `None`（都是 Exception），才算全源失败

3. **组装 `CalculationResponse`**：
```python
return CalculationResponse(
    fund_code=fund_code,
    fund_name=fund_info.get("name", "") if fund_info else "",
    nav=_calc_nav(nav_history),
    daily_change_pct=_calc_daily_change(nav_history),
    seven_day_annual_yield=_calc_seven_day_yield(fund_info or {}),
    wanfen_income=None,  # 当前始终为 None（见 3.1.1 _calc_wanfen_income 说明）
    one_month_return=_calc_one_month_return(nav_history),
    three_month_max_drawdown=_calc_max_drawdown(nav_history),
    ten_year_treasury=treasury_raw.get("value") if treasury_raw else None,
    credit_spread_aa_plus=credit_raw.get("value") if credit_raw else None,
    data_date=dt.date.today().isoformat(),
    is_trading_day=is_trading_day(),
    disclaimer=DISCLAIMER_TEXT,
)
```

4. **缓存写入**：
```python
# 在 return 前写入缓存
cache = get_cache(CACHE_PREFIX)
cache[f"{CACHE_PREFIX}{fund_code}"] = response
```
注意：存入缓存的是 `CalculationResponse` 对象本身，`cachetools.TTLCache` 存储 Python 对象没问题。读取时直接取出即可。

5. **缓存结构（读取侧）**：
```python
# 在 calculate() 开头检查缓存
cache = get_cache(CACHE_PREFIX)
cache_key = f"{CACHE_PREFIX}{fund_code}"
if cache_key in cache:
    logger.debug("计算结果缓存命中 code={}", fund_code)
    return cache[cache_key]
```

---

### 3.2 新建 `server/services/market_service.py` — 市场数据服务

```python
"""市场利率数据服务 — 获取、缓存和持久化市场利率指标。

职责：
- 从 data_fetcher 获取 10 年期国债收益率和信用利差
- 优先从内存缓存读取（TTL 2min）
- 缓存未命中调 data_fetcher 并写入缓存
- 异步持久化到 MongoDB（fire-and-forget，不阻塞返回）
"""

import asyncio
from typing import Any

from loguru import logger

from external.data_fetcher import fetch_treasury_yield, fetch_credit_spread
from core.cache import get_cache

CACHE_PREFIX = "market:"
CACHE_KEY = "market:latest"
"""市场利率缓存键 — 所有市场利率数据共用同一个 key。"""


async def get_market_rates() -> dict[str, float | None]:
    """获取当前市场利率数据（含内存缓存）。

    返回：
        {"ten_year_treasury": float | None, "credit_spread_aa_plus": float | None}

    流程：
    1. 查内存缓存（key = "market:latest"，TTL 2min）
       → 命中直接返回
    2. 缓存未命中 → asyncio.gather 并行调用 fetch_treasury_yield() 和
       fetch_credit_spread()
       → 使用 return_exceptions=True，单源失败对应 value 为 None
    3. 组装结果 dict → 写入内存缓存
    4. （可选）fire-and-forget 异步持久化到 MongoDB：
       使用 asyncio.create_task 调用 market_repo.save_market_data()
       → 持久化失败不阻塞、不影响返回结果，仅 log 警告

    Returns:
        {"ten_year_treasury": float | None, "credit_spread_aa_plus": float | None}
    """
    pass
```

**关键实现细节**：

1. **缓存优先**：与 `calculation_service` 的缓存逻辑一致，使用 `get_cache("market:")` + 直接 dict 存取。

2. **并行获取**：`fetch_treasury_yield()` 和 `fetch_credit_spread()` 本身各自有 5 日回退逻辑和独立异常处理，market_service 层仍需 `asyncio.gather(return_exceptions=True)` 兜底。

3. **fire-and-forget 持久化**（可选实现）：
```python
# 在 get_market_rates() 中，组装结果后：
try:
    from repositories import market_repo
    import datetime as dt

    now = dt.datetime.now()
    # 不 await — 让持久化在后台执行，不阻塞返回
    _ = asyncio.create_task(_persist_async(rates, now))
except Exception:
    logger.warning("market_repo 不可用，跳过持久化")
```
其中 `_persist_async` 是模块级 async 函数，将 `ten_year_treasury` 和 `credit_spread_aa_plus` 分别调用 `market_repo.save_market_data()` 持久化。

**如果跳过 fire-and-forget 持久化**，则仅实现缓存逻辑 + 返回 dict，持久化在后续 Task 2.2（计算 API 路由）中统一处理。两种方案均可，建议先做最简单的缓存版本。

---

### 3.3 新建 `server/repositories/market_repo.py` — 市场数据 Repository

```python
"""市场数据访问层 — MongoDB CRUD 操作。

操作 market_data 集合，记录每次获取的市场利率指标值。
"""

from datetime import datetime

from models.market_data import MarketData


async def save_market_data(
    indicator_name: str,
    value: float,
    unit: str,
    fetched_at: datetime | None = None,
) -> MarketData:
    """保存一条市场数据记录到 MongoDB。

    Args:
        indicator_name: 指标名称（如 "treasury_yield_10y"、"credit_spread_aa_plus"）。
        value: 指标数值。
        unit: 单位（"%" 或 "bp"）。
        fetched_at: 数据获取时间，None 时自动设为当前时间。

    Returns:
        保存后的 MarketData 文档。
    """
    pass


async def get_latest(indicator_name: str) -> MarketData | None:
    """查询指定指标的最新一条记录。

    按 fetched_at 降序排列，取第一条。

    Args:
        indicator_name: 指标名称。

    Returns:
        最新的 MarketData 文档或 None（无记录）。
    """
    pass
```

**关键实现细节**：

1. **Beanie 查询语法**：
```python
# 按 fetched_at 降序取最新
await MarketData.find_one(
    MarketData.indicator_name == indicator_name
).sort(-MarketData.fetched_at)
```

2. **`save_market_data` — 直接创建新文档**：
```python
md = MarketData(
    indicator_name=indicator_name,
    value=value,
    unit=unit,
    fetched_at=fetched_at or datetime.now(),
)
return await md.insert()
```
不需要 upsert——每条市场利率获取记录独立存储，用于后续历史查询。

3. **Beanie `find_one` + `sort`**：Beanie 的 `find_one` 返回链式查询对象，需先 `.sort()` 再 `await`。

---

### 3.4 修改 `server/api/main.py` — 注册新模型

**修改位置**：Beanie 初始化 — `document_models` 列表

```python
# 修改前
from models.fund import Fund

await init_beanie(
    database=client.get_default_database(),
    document_models=[Fund],
)

# 修改后
from models.fund import Fund
from models.calculation import Calculation
from models.market_data import MarketData

await init_beanie(
    database=client.get_default_database(),
    document_models=[Fund, Calculation, MarketData],
)
```

> **注意**：本 Task 不涉及路由注册（Task 2.2 负责 `api/routes/calculations.py`），仅注册 Document 模型以支持本 Task 的持久化需求。

---

## 4. 代码规范要求

1. **异步优先**：所有 I/O 操作（DB 查询、外部 API 调用）使用 `async/await`
2. **Pydantic 序列化**：`calculate()` 返回 `CalculationResponse` Pydantic Schema，不用 dict 裸传
3. **异常传播**：
   - 指标计算函数不抛异常（返回 None 表示无法计算）
   - 编排层仅在全部数据源失败时抛 `FatalError`
   - Repository 层不捕获异常（原样抛出）
4. **日志**：使用 `loguru.logger`，关键步骤（数据源调用、缓存命中/未命中、全源失败）记录 INFO/WARNING 日志
5. **类型标注**：所有函数签名含完整 Python 类型标注
6. **中文错误消息**：`FatalError` 的 message 用中文
7. **免责声明复用**：从 `services.fund_service` 导入 `DISCLAIMER_TEXT`，不重复定义
8. **缓存 key 规范**：
   - `"calc:{fund_code}"` → TTL 5min
   - `"market:latest"` → TTL 2min

---

## 5. 测试要求

代码必须能通过以下 24 个测试用例（详见 `test-cases.md`）：

| 编号 | 用例 | 关键断言 |
|------|------|---------|
| TC-001 | 8 项指标全部正常计算 | `nav`/`daily_change_pct`/`one_month_return`/`max_drawdown` 非 None，`fund_name` 非空 |
| TC-002 | 日涨跌幅精确值 | `daily_change_pct` = 5.0（1.05 vs 1.00） |
| TC-003 | 近1月收益率精确值 | `one_month_return` = 10.0 |
| TC-004 | 最大回撤正确性 | 区间最高 1.05 → 最低 0.98，max_dd ≈ 6.67% |
| TC-005 | 单调上涨无回撤 | `three_month_max_drawdown` ≈ 0 |
| TC-006 | 历史数据不足 30 条 | `one_month_return` = None，`daily_change_pct` 正常 |
| TC-007 | 历史数据仅 1 条 | `daily_change_pct` = None，`nav` 正常 |
| TC-008 | 历史净值完全为空 | 净值相关 4 指标全 None，市场利率正常 |
| TC-009 | 七日年化—货币基金获取 | `seven_day_annual_yield` 非 None |
| TC-010 | 七日年化—债券基金标 None | `seven_day_annual_yield` = None |
| TC-011 | 信用利差不可用 | `credit_spread_aa_plus` = None |
| TC-012 | asyncio.gather 并行成功 | 返回完整 8 项指标 |
| TC-013 | 单源失败—净值异常不中断 | nav 等 4 项为 None，市场利率正常 |
| TC-014 | 单源失败—利率异常不中断 | 利率 2 项为 None，净值相关正常 |
| TC-015 | 全部数据源失败 | `FatalError`，code=50001，status_code=503 |
| TC-016 | 缓存命中 5 分钟内 | 不走外部数据源，结果一致 |
| TC-017 | 缓存过期重新计算 | 清除缓存后重新走完整链路 |
| TC-018 | 返回完整 CalculationResponse | 所有字段存在（含 None），`data_date` + `is_trading_day` + `disclaimer` |
| TC-019 | get_market_rates 正常获取 | `ten_year_treasury` 和 `credit_spread_aa_plus` 存在 |
| TC-020 | 市场利率缓存命中 | TTL 2min 内不调 data_fetcher |
| TC-021 | 缓存未命中调 data_fetcher | 首次调用触发外部数据源 |
| TC-022 | save_market_data 持久化 | MongoDB 中写入新文档 |
| TC-023 | get_latest 查询最新 | 按 fetched_at 降序返回第一条 |
| TC-024 | 端到端链路 | `disclaimer` 非空，`data_date` 为当天，`is_trading_day` 正确 |

---

## 6. 注意事项

1. **历史净值序列顺序**：`fetch_fund_nav_history` 返回的 `data` 列表是**按日期降序**（`sort(key=lambda x: x["date"], reverse=True)`），最新净值在 `[0]`。计算最大回撤时需要 `reversed()` 从旧到新遍历，但取"30 日前净值"直接用索引 `[29]`（第 30 条，最新为 `[0]`）。

2. **全源失败 vs 部分失败**：`nav_history_raw is None`（数据源调用抛异常）≠ `nav_history = []`（调用成功但数据为空）。全源失败只检查 raw 是否全为 None；数据为空属于正常降级（部分指标标 None，不抛 FatalError）。

3. **除零保护**：日涨跌幅和近 1 月收益率公式中分母可能为 0（前一日净值/30 日前净值为 0），需加保护：
```python
if old_nav == 0 or latest_nav is None:
    return None
```

4. **最大回撤浮点精度**：使用 `float` 直接计算，最终结果在 `CalculationResponse` 中以 Pydantic 序列化。若需控制精度，可在组装时 `round(value, 4)`，但非必须。

5. **`market_service.get_market_rates()` 的持久化时机**：
   - 简单方案：仅缓存 + 返回，不持久化（后续 Task 2.2 路由层处理）
   - 完整方案：fire-and-forget 异步写 MongoDB
   - 两者均可通过测试用例，建议先实现简单方案确保核心功能正确，再补持久化

6. **`_calc_wanfen_income` 当前始终返回 None**：`data_fetcher.fetch_fund_info` 目前不返回万份收益字段。这是一个预留接口，后续如支持货币基金可扩展。在 `CalculationResponse` 组装时直接传 `None`。

7. **缓存 key 前缀匹配**：`core/cache.py` 的 `_get_ttl_for_prefix()` 用 `startswith()` 判断，因此 `"calc:020741"` 匹配 `"calc:"` → TTL 300s，`"market:latest"` 匹配 `"market:"` → TTL 120s。

8. **`trading_calendar.is_trading_day()` 返回值类型**：源码中已 `return bool(cal.is_session(str(date)))`，确保返回类型为 `bool`。在 `CalculationResponse` 中 `is_trading_day: bool` 类型一致。

9. **复用 `DISCLAIMER_TEXT`**：从 `services.fund_service` 导入，确保内容与 ADR 5.3 节完全一致：
```
"本工具提供的收益数据基于公开数据计算，仅供参考，不构成投资建议。投资有风险，操作需谨慎。"
```
