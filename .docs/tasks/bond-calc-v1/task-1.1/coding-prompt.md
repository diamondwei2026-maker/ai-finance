# Coding Prompt — Task 1.1: 外部数据源适配（akshare）

> 生成日期：2025-06-25 | 关联：[Task 详情](./task.md) | [测试用例](./test-cases.md)

---

## 1. 任务目标

在 `server/external/data_fetcher.py` 中实现统一的 akshare 外部数据源适配层，提供基金信息、历史净值、国债收益率、信用利差四类数据的异步获取能力，内置异常分级处理（单源失败抛 `RecoverableError`），返回格式统一。

---

## 2. 技术上下文

- **语言/框架**: Python 3.11+ / akshare ≥ 1.14.0
- **涉及文件**:
  - (新建) `server/external/data_fetcher.py` — 核心实现，四个异步数据获取函数
  - (已存在) `server/external/__init__.py` — 当前仅一行注释，无需修改（函数直接从 `data_fetcher` 导入）
  - (已存在) `server/core/exceptions.py` — `RecoverableError` / `ErrorCode` 已定义，直接 `from core.exceptions import RecoverableError, ErrorCode` 使用
  - (已存在) `server/requirements.txt` — akshare 版本已锁定 `>=1.14.0`，无需修改
- **外部依赖**: akshare（使用 `ak.fund_open_fund_info_em()`、`ak.fund_open_fund_info_em()` 的净值部分、`ak.bond_china_yield()` 等接口）
- **异步策略**: 使用 `asyncio.to_thread()` 包装 akshare 同步调用 → 暴露为 `async def` 函数，不阻塞事件循环

---

## 3. 实现要求

### 3.1 文件 `server/external/data_fetcher.py`（新建）

#### 整体结构

```python
"""外部数据源适配模块 — 封装 akshare 调用。

所有函数通过 asyncio.to_thread 将同步 akshare 调用转为异步，
并对单个数据源异常抛出 RecoverableError（上层可据此将对应指标标 N/A）。
"""

import asyncio
from datetime import datetime, date
from typing import Any

import akshare as ak

from core.exceptions import RecoverableError, ErrorCode
```

#### 3.1.1 通用工具函数

**`_safe_fetch(indicator: str, fetch_fn, *args, **kwargs) -> dict`**（私有函数）

- **职责**: 通用的 try/except 包装器，供四个公开函数内部复用
- **签名**:
  ```python
  async def _safe_fetch(
      indicator: str,
      fetch_fn: callable,
      *args: Any,
      **kwargs: Any,
  ) -> dict:
  ```
- **关键逻辑**:
  1. 使用 `asyncio.to_thread(fetch_fn, *args, **kwargs)` 在线程池中执行同步的 akshare 调用
  2. 返回原始数据（DataFrame / dict / Series），由调用方进一步解析
  3. 若 `to_thread` 抛出任何异常 → 捕获后抛出 `RecoverableError`，message 格式为 `"{indicator} 数据获取失败: {原始异常信息}"`，code 使用 `ErrorCode.DATA_SOURCE_FAILED`
  4. 若 akshare 返回空 DataFrame（`.empty` 为 True）→ 抛出 `RecoverableError`，message 为 `"{indicator} 数据为空"`
- **注意**: `fetch_fn` 是同步函数引用（如 `ak.fund_open_fund_info_em`），不在此处调用，只传入引用供 `to_thread` 调用

#### 3.1.2 基金信息获取

**`fetch_fund_info(code: str) -> dict`**

- **签名**: `async def fetch_fund_info(code: str) -> dict`
- **职责**: 使用 akshare 获取基金基本信息（名称、类型、最新净值、七日年化）
- **关键逻辑**:
  1. 调用 `_safe_fetch("fund_info", ak.fund_open_fund_info_em, symbol=code, indicator="单位净值走势")`
     - 备选：如上述调用方式不工作，尝试 `ak.fund_open_fund_info_em(fund=code, indicator="单位净值走势")`
  2. 检查返回的 DataFrame 是否包含目标基金代码的数据行：
     - 遍历 DataFrame 查找 code 匹配的行
     - 若找不到匹配行 → 抛出 `RecoverableError("基金不存在", code=ErrorCode.FUND_NOT_FOUND)`
  3. 从匹配行提取字段并组装返回 dict：
     ```python
     return {
         "indicator": "fund_info",
         "value": None,           # 复合数据，value 为 None
         "name": str,             # 基金简称
         "code": str,             # 基金代码（如 "020741"）
         "type": str,             # 基金类型（如 "债券型-长债"）
         "nav": float,            # 单位净值
         "seven_day_yield": float | None,  # 七日年化（若无则为 None）
         "unit": "",              # 复合数据无统一单位
         "source": "akshare",
         "fetched_at": datetime.now(),
     }
     ```
  4. 所有数值字段做 `float()` 转换，转换失败则设为 `None`

**akshare 接口参考**:
- 函数: `ak.fund_open_fund_info_em(symbol="020741", indicator="单位净值走势")`
- 返回: DataFrame，列含 `基金代码`、`基金简称`、`单位净值`、`累计净值`、`日增长率` 等
- 七日年化可能需要额外调用或从其他 indicator 获取（如 `"累计净值走势"` 或 `"分红送配详情"`）。**实际实现时先获取可得的字段，七日年化若无法直接从该接口获取则设为 `None`，并在代码注释中说明原因。**

#### 3.1.3 历史净值获取

**`fetch_fund_nav_history(code: str, days: int = 90) -> list[dict]`**

- **签名**: `async def fetch_fund_nav_history(code: str, days: int = 90) -> list[dict]`
- **职责**: 获取指定基金的近 N 日历史净值序列
- **关键逻辑**:
  1. 调用 `_safe_fetch("fund_nav_history", ak.fund_open_fund_info_em, symbol=code, indicator="单位净值走势")`
  2. 从 DataFrame 中提取日期和净值两列
  3. 按日期降序排列（最新日期在前）
  4. 截取前 `days` 条记录
  5. 若历史数据不足 `days` 条 → 返回全部已有数据，**不抛异常**
  6. 组装返回 dict：
     ```python
     return {
         "indicator": "fund_nav_history",
         "value": None,
         "data": [{"date": str, "nav": float}, ...],
         "unit": "",
         "source": "akshare",
         "fetched_at": datetime.now(),
     }
     ```
  7. `date` 字段：若 akshare 返回的是 `datetime.date` 或 `pd.Timestamp` → 转为 `"YYYY-MM-DD"` 字符串
  8. `nav` 字段做 `float()` 转换

#### 3.1.4 国债收益率获取

**`fetch_treasury_yield() -> dict`**

- **签名**: `async def fetch_treasury_yield() -> dict`
- **职责**: 获取当前中国 10 年期国债收益率
- **关键逻辑**:
  1. 调用 `_safe_fetch("treasury_yield_10y", ak.bond_china_yield, start_date="<当日日期>")`
     - `start_date` 取最近一个交易日（可用 `datetime.now().date()`，akshare 会自动取最近有效数据）
  2. 从返回 DataFrame 中找到 `10年期` 对应行，提取收益率值
  3. 组装返回：
     ```python
     return {
         "indicator": "treasury_yield_10y",
         "value": float,          # 收益率值（%）
         "unit": "%",
         "source": "akshare",
         "fetched_at": datetime.now(),
     }
     ```

**akshare 接口参考**:
- 函数: `ak.bond_china_yield(start_date="2025-06-23")`
- 返回: DataFrame，列包含 `曲线名称`、`收益率(%)` 等，行含 "10年期"、"5年期"、"2年期" 等

#### 3.1.5 信用利差获取

**`fetch_credit_spread() -> dict`**

- **签名**: `async def fetch_credit_spread() -> dict`
- **职责**: 获取 AA+ 级信用债与国债的利差（bp）
- **关键逻辑**:
  1. 由于 akshare 信用利差数据可能需要从多个接口组合，实现时采用以下策略（按优先级尝试）：
     - **方案 A（优先）**: 使用 `ak.bond_china_yield()` 分别获取 AA+ 企业债收益率和同期限国债收益率，计算差值转为 bp
     - **方案 B**: 若有专用信用利差接口，直接使用
     - **方案 C**: 若上述均不可行，`value` 设为 `None`，在 `source` 中标注 `"akshare: credit_spread_not_available"`，**不抛异常**（优雅降级，因为信用利差是辅助指标）
  2. 组装返回：
     ```python
     return {
         "indicator": "credit_spread_aa_plus",
         "value": float | None,   # 利差值（bp），不可获取时 None
         "unit": "bp",
         "source": "akshare",
         "fetched_at": datetime.now(),
     }
     ```

**akshare 接口参考**:
- `ak.bond_china_yield(start_date="2025-06-23")` 返回的 DataFrame 包含多种期限和评级收益率
- 若返回中包含 AA+ 评级行，则 `credit_spread = AA+收益率 - 同期限国债收益率`，乘以 100 转为 bp

---

## 4. 代码规范要求

### 4.1 异步约束
- ✅ 所有公开函数必须是 `async def`
- ✅ 所有 akshare 同步调用必须通过 `asyncio.to_thread()` 包装
- ✅ 不要在 `data_fetcher.py` 中直接调用 `loop.run_in_executor()` — 统一使用 `to_thread`

### 4.2 异常处理
- ✅ 每个函数或通过 `_safe_fetch` 间接包含 try/except
- ✅ 单源失败抛出 `RecoverableError`（不可抛出裸 `Exception`）
- ✅ `RecoverableError` 的 `message` 中必须包含指标名称标识（如 `"fund_info"`），方便上层日志定位
- ✅ `ErrorCode` 使用已定义的常量：`DATA_SOURCE_FAILED`（40003）、`FUND_NOT_FOUND`（40001）
- ❌ 不要在 `data_fetcher.py` 中抛出 `FatalError`（那是上层 service 的职责，当所有数据源全部不可用时才抛出）

### 4.3 代码风格
- ✅ 使用 Python type hints（所有函数签名标注参数和返回类型）
- ✅ 使用 `datetime.now()` 而非 `datetime.utcnow()`（后者已废弃）
- ✅ 使用 f-string 格式化日志和异常消息
- ✅ 使用 `import akshare as ak` 统一别名
- ✅ 文件头部包含模块级 docstring

### 4.4 数据健壮性
- ✅ 所有 `float()` 转换包裹在 try/except 中，失败时设为 `None`
- ✅ 不假设 DataFrame 一定有某列 — 使用 `.get()` 或 `try/except KeyError`
- ✅ 空 DataFrame 检查（`.empty`）

---

## 5. 测试要求

代码必须能通过以下测试用例（详见 [test-cases.md](./test-cases.md)）：

| 编号 | 测试要点 | 对应实现要求 |
|------|---------|-------------|
| TC-001 | `fetch_fund_info("020741")` 返回完整基金信息 | §3.1.2 |
| TC-002 | `fetch_fund_nav_history("020741")` 返回日期降序净值列表 | §3.1.3 |
| TC-003 | `fetch_treasury_yield()` 返回 10 年期国债收益率 | §3.1.4 |
| TC-004 | `fetch_credit_spread()` 返回 AA+ 信用利差 | §3.1.5 |
| TC-005 | 四个函数返回值均含 `indicator, value, unit, source, fetched_at` | §3.1.2-§3.1.5 |
| TC-006 | `fetch_fund_info("000000")` 抛出 `RecoverableError("基金不存在")` | §3.1.2 步骤 2 |
| TC-007 | 空字符串代码抛出 `RecoverableError` | §3.1.1 通用错误捕获 |
| TC-008 | 新基金历史不足时返回已有数据（不抛异常） | §3.1.3 步骤 5 |
| TC-009 | `days=0` 不导致未捕获异常 | §3.1.3（`days` 参数处理） |
| TC-010 | 网络不可达时抛出 `RecoverableError`（含指标标识） | §3.1.1 `_safe_fetch` |
| TC-011 | akshare 返回空 DataFrame 抛出 `RecoverableError` | §3.1.1 步骤 4 |
| TC-012 | 单个利率指标失败不影响其他指标 | §3.1.4 & §3.1.5 独立性 |
| TC-013 | 异步事件循环中调用不阻塞 | §4.1 |
| TC-014 | 异常为 `RecoverableError` 实例，`status_code=200` | §4.2 |
| TC-015 | akshare 已在 `requirements.txt` 中锁定版本 | 无需修改（已满足） |

---

## 6. 注意事项

1. **akshare API 签名确认**: akshare 的接口参数名在不同版本可能不同。实现前先用 `help(ak.fund_open_fund_info_em)` 或 akshare 官方文档确认参数名。常见变体：`symbol` vs `fund`、`code` vs `fund_code`。**如果发现 akshare 接口与本文档描述的签名不同，以 akshare 实际签名为准，但返回值格式保持不变。**

2. **七日年化数据来源**: `fund_open_fund_info_em` 可能不直接返回七日年化。货币基金才普遍有七日年化，债券基金可能没有。如果 akshare 无法提供七日年化，`seven_day_yield` 字段设为 `None`，并在代码注释中说明。

3. **`_safe_fetch` 设计**: 这是关键抽象。它不负责解析数据，只负责"安全地调用 akshare 并把异常转为 RecoverableError"。解析逻辑在四个公开函数中各自实现。

4. **信用利差降级**: 信用利差是辅助指标，若 akshare 无直接接口则优雅降级（`value=None`），不要因此阻塞整体流程。

5. **模块导入路径**: `data_fetcher.py` 在 `server/external/` 下，导入 `core.exceptions` 时注意 Python path — 需确保 `server/` 在 `PYTHONPATH` 中或使用相对导入。建议使用 `from core.exceptions import RecoverableError, ErrorCode`（前提是 server 目录被正确配置为 Python 包根目录）。

6. **单元测试编写**: 测试用例中有多个需要 mock akshare 的场景（TC-010, TC-011, TC-012, TC-014）。实现时确保 `_safe_fetch` 的可测试性 — 通过 `fetch_fn` 参数传入函数引用即可用 `unittest.mock.patch` 或 `pytest.monkeypatch` 替换。
