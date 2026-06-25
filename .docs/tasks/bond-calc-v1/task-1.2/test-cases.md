# 测试用例 — Task 1.2: 数据模型定义

> 共 **16** 个测试用例，覆盖 6 条验收标准。

---

## 测试用例列表

| 编号 | 名称 | 类型 | 关联验收 |
|------|------|------|----------|
| TC-001 | Fund 模型基本创建与序列化 | 功能测试 | models/fund.py |
| TC-002 | Fund 模型 fund_code 唯一索引约束 | 集成测试 | models/fund.py |
| TC-003 | Fund 模型必填字段缺失校验 | 异常测试 | models/fund.py |
| TC-004 | Calculation 模型基本创建（完整 8 项指标） | 功能测试 | models/calculation.py |
| TC-005 | Calculation 模型 — 部分指标为 None（数据缺失场景） | 边界测试 | models/calculation.py |
| TC-006 | Calculation 模型 — 复合索引验证 | 集成测试 | models/calculation.py |
| TC-007 | Calculation 模型 — created_at 自动赋值 | 功能测试 | models/calculation.py |
| TC-008 | MarketData 模型基本创建与序列化 | 功能测试 | models/market_data.py |
| TC-009 | MarketData 模型 — 复合索引验证 | 集成测试 | models/market_data.py |
| TC-010 | FundInfoResponse Schema — 正常序列化含 disclaimer | 功能测试 | models/schemas.py |
| TC-011 | CalculationRequest Schema — 基金代码格式校验 | 异常测试 | models/schemas.py |
| TC-012 | CalculationResponse Schema — 完整 + 部分缺失场景 | 边界测试 | models/schemas.py |
| TC-013 | ApiResponse[T] 泛型包装 — 成功与错误响应 | 功能测试 | models/schemas.py |
| TC-014 | Beanie Document Settings — collection name 配置正确 | 功能测试 | 所有 Document |
| TC-015 | 模型导入与模块结构完整性 | 功能测试 | 全部 |
| TC-016 | 与 Task 1.1 data_fetcher 返回结构兼容性 | 集成测试 | models/schemas.py |

---

## 详细测试用例

### TC-001: Fund 模型基本创建与序列化

- **类型**: 功能测试
- **关联验收标准**: `models/fund.py` — Beanie Document：fund_code（唯一索引）、name、fund_type、updated_at
- **前置条件**: MongoDB 连接已初始化（Beanie `init_beanie` 已完成）
- **输入**:
  ```python
  Fund(
      fund_code="020741",
      name="华泰保兴安悦债券C",
      fund_type="中长期纯债",
      updated_at=datetime(2025, 6, 25, 10, 0, 0)
  )
  ```
- **执行步骤**:
  1. 创建 `Fund` 实例
  2. 调用 `fund.model_dump()` 序列化为 dict
  3. 检查所有字段值正确
  4. 调用 `fund.insert()` 写入 MongoDB
  5. 调用 `Fund.find_one(Fund.fund_code == "020741")` 查询
- **预期输出**:
  - `model_dump()` 返回含 `_id` 的完整字段字典
  - `name` = `"华泰保兴安悦债券C"`
  - `fund_type` = `"中长期纯债"`
  - `updated_at` 为 `datetime` 类型
  - MongoDB 写入/查询成功，返回相同数据
- **清理**: `await Fund.find_one(Fund.fund_code == "020741").delete()`

---

### TC-002: Fund 模型 fund_code 唯一索引约束

- **类型**: 集成测试
- **关联验收标准**: `models/fund.py` — fund_code（Indexed, unique）
- **前置条件**: MongoDB 中已存在 `fund_code="020741"` 的记录
- **输入**:
  ```python
  Fund(fund_code="020741", name="重复基金", fund_type="混合型", updated_at=datetime.now())
  ```
- **执行步骤**:
  1. 插入第一条 `Fund(fund_code="020741", ...)` 到 MongoDB
  2. 尝试插入第二条相同 `fund_code` 的 `Fund` 记录
  3. 捕获异常
- **预期输出**:
  - 第二次 `insert()` 抛出 `DuplicateKeyError`（或 Beanie/Motor 对应异常）
  - 数据库中仅存在一条 `fund_code="020741"` 的记录
- **清理**: `await Fund.find_one(Fund.fund_code == "020741").delete()`

---

### TC-003: Fund 模型必填字段缺失校验

- **类型**: 异常测试
- **关联验收标准**: `models/fund.py` — 字段完整性
- **前置条件**: 无
- **输入**:
  ```python
  # 缺少 name 字段
  Fund(fund_code="020741", fund_type="中长期纯债", updated_at=datetime.now())
  ```
- **执行步骤**:
  1. 尝试创建缺少必填字段的 `Fund` 实例（Pydantic 校验在构造时触发）
  2. 捕获 `ValidationError`
- **预期输出**:
  - Pydantic 抛出 `ValidationError`
  - 错误信息指明 `name` 字段缺失
- **清理**: 无

---

### TC-004: Calculation 模型基本创建（完整 8 项指标）

- **类型**: 功能测试
- **关联验收标准**: `models/calculation.py` — 8 项指标字段（均为 `float | None`）+ fund_code、data_date、is_trading_day、created_at
- **前置条件**: MongoDB 连接已初始化
- **输入**:
  ```python
  Calculation(
      fund_code="020741",
      nav=1.0234,
      daily_change_pct=0.02,
      seven_day_annual_yield=3.82,
      wanfen_income=0.85,
      one_month_return=0.31,
      three_month_max_drawdown=0.45,
      ten_year_treasury=2.68,
      credit_spread_aa_plus=58,
      data_date="2025-06-25",
      is_trading_day=True,
      created_at=datetime.now()
  )
  ```
- **执行步骤**:
  1. 创建 `Calculation` 实例
  2. 序列化为 dict
  3. 写入 MongoDB 并查询
- **预期输出**:
  - 所有 11 个字段值与输入一致
  - `nav` 等指标为 `float` 类型
  - `data_date` 为 `str` 类型
  - `created_at` 为 `datetime` 类型
  - `is_trading_day` 为 `bool` 类型
- **清理**: 删除测试记录

---

### TC-005: Calculation 模型 — 部分指标为 None（数据缺失场景）

- **类型**: 边界测试
- **关联验收标准**: `models/calculation.py` — 指标字段为 `float | None`
- **前置条件**: MongoDB 连接已初始化
- **输入**:
  ```python
  Calculation(
      fund_code="020741",
      nav=1.0234,
      daily_change_pct=None,        # 当日无交易
      seven_day_annual_yield=3.82,
      wanfen_income=None,           # 货币基金才有
      one_month_return=None,        # 新基金不足1月
      three_month_max_drawdown=None,# 新基金不足3月
      ten_year_treasury=2.68,
      credit_spread_aa_plus=None,   # 信用利差获取失败
      data_date="2025-06-25",
      is_trading_day=False,
      created_at=datetime.now()
  )
  ```
- **执行步骤**:
  1. 创建 `Calculation` 实例（4 项为 None）
  2. 序列化 → 写入 MongoDB → 查询
  3. 验证 None 字段正确存储和读取
- **预期输出**:
  - Pydantic 不抛异常（`float | None` 允许 None）
  - MongoDB 中 None 字段保存为 `null`
  - 查询返回的 `daily_change_pct`、`wanfen_income`、`one_month_return`、`three_month_max_drawdown`、`credit_spread_aa_plus` 均为 `None`
- **清理**: 删除测试记录

---

### TC-006: Calculation 模型 — 复合索引验证

- **类型**: 集成测试
- **关联验收标准**: `models/calculation.py` — 复合索引 `(fund_code, created_at)`
- **前置条件**: MongoDB 连接已初始化，Beanie `init_beanie` 已调用
- **输入**: 无（检查索引元数据）
- **执行步骤**:
  1. 通过 Motor 直接列出 `calculations` 集合的索引：
     ```python
     indexes = await Calculation.get_motor_collection().index_information()
     ```
  2. 验证存在复合索引 `fund_code_1_created_at_-1`（或等价的 `(fund_code, created_at)` 复合索引）
- **预期输出**:
  - 索引列表中包含 `fund_code_1_created_at_-1`（升序 + 降序复合索引）
  - 除 `_id_` 默认索引外至少有一个自定义索引
- **清理**: 无

---

### TC-007: Calculation 模型 — created_at 自动赋值

- **类型**: 功能测试
- **关联验收标准**: `models/calculation.py` — `created_at` 为 `datetime` 类型
- **前置条件**: MongoDB 连接已初始化
- **输入**:
  ```python
  # 不显式传 created_at（如果可以默认），否则显式传入
  Calculation(
      fund_code="020741",
      data_date="2025-06-25",
      is_trading_day=True,
      created_at=datetime.now()
  )
  ```
- **执行步骤**:
  1. 在创建前记录当前时间 `before`
  2. 创建 `Calculation` 实例并插入
  3. 查询返回的 `created_at` 值
  4. 验证 `created_at` 在 `before` 和 `after` 之间
- **预期输出**:
  - `created_at` 为 `datetime` 类型
  - `created_at` 时间戳在合理时间窗口内
- **清理**: 删除测试记录

---

### TC-008: MarketData 模型基本创建与序列化

- **类型**: 功能测试
- **关联验收标准**: `models/market_data.py` — indicator_name、value、unit、fetched_at
- **前置条件**: MongoDB 连接已初始化
- **输入**:
  ```python
  MarketData(
      indicator_name="10年期国债收益率",
      value=2.68,
      unit="%",
      fetched_at=datetime.now()
  )
  ```
- **执行步骤**:
  1. 创建 `MarketData` 实例
  2. 序列化为 dict
  3. 写入 MongoDB 并查询
- **预期输出**:
  - `indicator_name` = `"10年期国债收益率"`
  - `value` = `2.68`（float 类型保留精度）
  - `unit` = `"%"`
  - `fetched_at` 为 `datetime` 类型
- **清理**: 删除测试记录

---

### TC-009: MarketData 模型 — 复合索引验证

- **类型**: 集成测试
- **关联验收标准**: `models/market_data.py` — 复合索引 `(indicator_name, fetched_at)`
- **前置条件**: MongoDB 连接已初始化
- **输入**: 无（检查索引元数据）
- **执行步骤**:
  1. 通过 Motor 列出 `market_data` 集合的索引
  2. 验证存在复合索引 `indicator_name_1_fetched_at_-1` 或等价索引
- **预期输出**:
  - 索引列表包含 `(indicator_name, fetched_at)` 复合索引
- **清理**: 无

---

### TC-010: FundInfoResponse Schema — 正常序列化含 disclaimer

- **类型**: 功能测试
- **关联验收标准**: `models/schemas.py` — FundInfoResponse、disclaimer 字段
- **前置条件**: 无（纯 Pydantic 测试，不依赖数据库）
- **输入**:
  ```python
  FundInfoResponse(
      fund_code="020741",
      name="华泰保兴安悦债券C",
      fund_type="中长期纯债",
      nav=1.0234,
      seven_day_annual_yield=3.82,
      updated_at=datetime.now(),
      disclaimer="本工具提供的收益数据基于公开数据计算，仅供参考，不构成投资建议。投资有风险，操作需谨慎。"
  )
  ```
- **执行步骤**:
  1. 创建 `FundInfoResponse` 实例
  2. 调用 `model_dump()` 或 `model_dump_json()`
  3. 验证所有字段存在且值正确
- **预期输出**:
  - JSON 包含 `disclaimer` 字段，值为免责声明文本
  - 所有基金信息字段与输入一致
  - `nav` 保留 float 精度
- **清理**: 无

---

### TC-011: CalculationRequest Schema — 基金代码格式校验

- **类型**: 异常测试
- **关联验收标准**: `models/schemas.py` — CalculationRequest 校验
- **前置条件**: 无（纯 Pydantic 测试）
- **输入**:
  ```python
  # 无效：长度不足
  CalculationRequest(fund_code="02074")
  # 无效：含非数字字符
  CalculationRequest(fund_code="02074A")
  # 无效：长度过长
  CalculationRequest(fund_code="0207411")
  # 无效：空字符串
  CalculationRequest(fund_code="")
  # 有效：标准 6 位
  CalculationRequest(fund_code="020741")
  ```
- **执行步骤**:
  1. 依次用上述输入创建 `CalculationRequest`
  2. 对无效输入捕获 `ValidationError`
  3. 对有效输入确认创建成功
- **预期输出**:
  - 无效 `fund_code` 均抛出 `ValidationError`
  - 有效 `fund_code="020741"` 创建成功，`model_dump()` 返回 `{"fund_code": "020741"}`
- **清理**: 无

> **注**: 如果 ADR 中 `CalculationRequest` 仅含 `fund_code` 字段（字符串），格式校验逻辑（6 位纯数字）可能在 service 层实现。此时改为验证 `fund_code` 字段存在且为 `str` 类型。

---

### TC-012: CalculationResponse Schema — 完整 + 部分缺失场景

- **类型**: 边界测试
- **关联验收标准**: `models/schemas.py` — CalculationResponse 含 `disclaimer` 字段
- **前置条件**: 无（纯 Pydantic 测试）
- **输入**:
  ```python
  # 场景 A：全部指标有效
  CalculationResponse(
      fund_code="020741",
      fund_name="华泰保兴安悦债券C",
      nav=1.0234,
      daily_change_pct=0.02,
      seven_day_annual_yield=3.82,
      wanfen_income=0.85,
      one_month_return=0.31,
      three_month_max_drawdown=0.45,
      ten_year_treasury=2.68,
      credit_spread_aa_plus=58,
      data_date="2025-06-25",
      is_trading_day=True,
      disclaimer="..."
  )

  # 场景 B：部分指标为 None
  CalculationResponse(
      fund_code="020741",
      fund_name="华泰保兴安悦债券C",
      nav=1.0234,
      daily_change_pct=None,
      seven_day_annual_yield=3.82,
      wanfen_income=None,
      one_month_return=None,
      three_month_max_drawdown=None,
      ten_year_treasury=2.68,
      credit_spread_aa_plus=None,
      data_date="2025-06-25",
      is_trading_day=False,
      disclaimer="..."
  )
  ```
- **执行步骤**:
  1. 分别创建两个场景的 `CalculationResponse` 实例
  2. 序列化为 JSON
  3. 比对 JSON 输出
- **预期输出**:
  - 场景 A：JSON 所有指标均为数值
  - 场景 B：JSON 中 `daily_change_pct`、`wanfen_income` 等为 `null`
  - 两个场景均含 `disclaimer` 字段
  - `is_trading_day` 值为 `bool` 类型
- **清理**: 无

---

### TC-013: ApiResponse[T] 泛型包装 — 成功与错误响应

- **类型**: 功能测试
- **关联验收标准**: `models/schemas.py` — `ApiResponse[T]` 泛型包装
- **前置条件**: 无（纯 Pydantic 测试）
- **输入**:
  ```python
  # 成功响应
  from typing import Generic, TypeVar
  T = TypeVar("T")

  class ApiResponse(BaseModel, Generic[T]):
      code: int
      message: str
      data: T | None

  fund_info = FundInfoResponse(...)  # 来自 TC-010 的实例
  success_resp = ApiResponse[FundInfoResponse](
      code=0,
      message="success",
      data=fund_info
  )

  # 错误响应
  error_resp = ApiResponse[FundInfoResponse](
      code=40001,
      message="未找到该基金（代码：999999），请检查后重新输入",
      data=None
  )
  ```
- **执行步骤**:
  1. 创建成功和错误两种 `ApiResponse` 实例
  2. 用 `model_dump_json()` 序列化
  3. 验证 JSON 结构与 ADR 5.1 节约定一致
- **预期输出**:
  - 成功响应 JSON: `{"code": 0, "message": "success", "data": {...}}`
  - 错误响应 JSON: `{"code": 40001, "message": "...", "data": null}`
  - `data` 字段类型随泛型参数正确嵌套
- **清理**: 无

---

### TC-014: Beanie Document Settings — collection name 配置正确

- **类型**: 功能测试
- **关联验收标准**: Beanie Document 的 `Settings` 类正确配置 collection name 和 indexes
- **前置条件**: 三个模型文件已创建
- **输入**: 无（代码静态检查）
- **执行步骤**:
  1. 导入三个模型类
  2. 检查 `Fund.Settings.name` 是否为 `"funds"`
  3. 检查 `Calculation.Settings.name` 是否为 `"calculations"`
  4. 检查 `MarketData.Settings.name` 是否为 `"market_data"`
  5. 检查 `Calculation.Settings.indexes` 是否定义了复合索引
  6. 检查 `MarketData.Settings.indexes` 是否定义了复合索引
- **预期输出**:
  - `Fund.Settings.name` = `"funds"`
  - `Calculation.Settings.name` = `"calculations"`
  - `MarketData.Settings.name` = `"market_data"`
  - `Calculation.Settings.indexes` 非空，含 `[("fund_code", 1), ("created_at", -1)]`
  - `MarketData.Settings.indexes` 非空，含 `[("indicator_name", 1), ("fetched_at", -1)]`
- **清理**: 无

---

### TC-015: 模型导入与模块结构完整性

- **类型**: 功能测试
- **关联验收标准**: 全部（模块结构正确，可正常导入）
- **前置条件**: 所有模型文件已创建
- **输入**: 无
- **执行步骤**:
  1. 执行 `from models.fund import Fund`
  2. 执行 `from models.calculation import Calculation`
  3. 执行 `from models.market_data import MarketData`
  4. 执行 `from models.schemas import FundInfoResponse, CalculationRequest, CalculationResponse, ApiResponse`
  5. 执行 `from models import Fund, Calculation, MarketData, FundInfoResponse, CalculationRequest, CalculationResponse, ApiResponse`
- **预期输出**:
  - 所有 import 语句无 `ImportError` 或 `ModuleNotFoundError`
  - `models/__init__.py` 正确导出所有公共符号
- **清理**: 无

---

### TC-016: 与 Task 1.1 data_fetcher 返回结构兼容性

- **类型**: 集成测试
- **关联验收标准**: `models/schemas.py` — API 响应 Schema 与 data_fetcher 返回结构匹配
- **前置条件**: Task 1.1 的 `external/data_fetcher.py` 已实现
- **输入**: 无（代码静态检查 + 结构比对）
- **执行步骤**:
  1. 检查 `data_fetcher.fetch_fund_info()` 返回的 dict 结构（`{"indicator": ..., "value": ..., "unit": ..., "source": ..., "fetched_at": ...}`）
  2. 确认 `FundInfoResponse` 能够从该 dict 构造（字段名映射或直接解包）
  3. 检查 `data_fetcher.fetch_fund_nav_history()` 返回的 `list[dict]` 是否能被计算引擎消费后填入 `Calculation` 模型
  4. 检查 `MarketData` 模型的 `indicator_name`、`value`、`unit`、`fetched_at` 与 `data_fetcher` 市场利率函数返回结构一致
- **预期输出**:
  - `FundInfoResponse` 的字段能覆盖/映射 `fetch_fund_info()` 的返回数据
  - `MarketData` 的字段与 `fetch_treasury_yield()`/`fetch_credit_spread()` 返回结构兼容
  - `Calculation` 模型的指标字段命名与 ADR 5.3 节响应字段说明一致
- **清理**: 无

---

## 按类型分布

| 类型 | 数量 | 用例编号 |
|------|------|----------|
| 功能测试 | 8 | TC-001, TC-004, TC-007, TC-008, TC-010, TC-013, TC-014, TC-015 |
| 边界测试 | 2 | TC-005, TC-012 |
| 异常测试 | 2 | TC-003, TC-011 |
| 集成测试 | 4 | TC-002, TC-006, TC-009, TC-016 |

---

## 测试环境要求

| 组件 | 要求 |
|------|------|
| Python | 3.11+ |
| MongoDB | Atlas M0 或本地 MongoDB 4.4+ |
| Beanie | 通过 `requirements.txt` 锁定版本 |
| 依赖模块 | `external/data_fetcher.py`（TC-016）|
| 测试框架 | 建议 pytest + pytest-asyncio |
