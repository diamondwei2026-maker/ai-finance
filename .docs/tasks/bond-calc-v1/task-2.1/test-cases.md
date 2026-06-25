# 测试用例 — Task 2.1: 计算引擎与市场数据服务

> 生成日期：2025-06-25 | 基于 Task 2.1 验收标准

---

## 测试维度概览

| 维度 | 用例数 | 覆盖范围 |
|------|--------|---------|
| 功能测试 | 12 | 8 项指标计算、编排服务、市场数据服务 |
| 边界测试 | 4 | 历史数据不足、净值序列为空、单日数据 |
| 异常测试 | 5 | 单源失败降级、全源失败 FatalError、外部 API 异常 |
| 集成测试 | 3 | 端到端链路、MongoDB 持久化、缓存层级 |

**总计：24 个测试用例**

---

## 一、SUB-2.1.1 — 8 项指标计算逻辑

### TC-001: 8 项指标全部正常计算（完整数据）

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.1 全部验收标准
- **前置条件**:
  - 基金 `020741` 存在于数据源
  - 历史净值数据 ≥ 90 条
  - 10 年期国债收益率可获取
  - 信用利差数据可获取
- **输入**:
  - `fund_code = "020741"`
  - 历史净值列表（最新净值 1.05，前一日 1.048，30 日前 1.02，区间最高 1.06）
  - 市场利率 `{"ten_year_treasury": 2.85, "credit_spread_aa_plus": 150.3}`
- **执行步骤**:
  1. 调用 `calculation_service.calculate("020741")`
  2. 检查返回的 `CalculationResponse` 中 8 项指标字段
- **预期输出**:
  - `nav` = 1.05（浮点数，非 None）
  - `daily_change_pct` ≈ (1.05 - 1.048) / 1.048 × 100 ≈ 0.1908（保留合理精度）
  - `seven_day_annual_yield` 非 None（如有数据源）
  - `wanfen_income` 非 None（如有数据源）
  - `one_month_return` ≈ (1.05 - 1.02) / 1.02 × 100 ≈ 2.9412
  - `three_month_max_drawdown` ≈ (1 - 1.05/1.06) × 100 ≈ 0.9434
  - `ten_year_treasury` = 2.85
  - `credit_spread_aa_plus` = 150.3
  - `fund_name` 非空字符串
  - `data_date` 为当天日期 "YYYY-MM-DD" 格式
- **清理**: 无

---

### TC-002: 日涨跌幅计算正确性（精确值验证）

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.1 — 日涨跌幅
- **前置条件**:
  - 提供已知的历史净值数据
- **输入**:
  - 当日净值 = 1.05
  - 前一日净值 = 1.00
- **执行步骤**:
  1. 以模拟数据调用日涨跌幅计算函数
  2. 验证返回值
- **预期输出**:
  - `daily_change_pct` = 5.0（精确：`(1.05 - 1.00) / 1.00 × 100`）
- **清理**: 无

---

### TC-003: 近 1 月收益率计算正确性（精确值验证）

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.1 — 近1月收益率
- **前置条件**:
  - 提供已知的历史净值数据（30 条以上）
- **输入**:
  - 最新净值（第 0 日）= 1.10
  - 30 日前净值 = 1.00
- **执行步骤**:
  1. 以模拟数据调用近 1 月收益率计算函数
  2. 验证返回值
- **预期输出**:
  - `one_month_return` = 10.0（精确：`(1.10 - 1.00) / 1.00 × 100`）
- **清理**: 无

---

### TC-004: 近 3 月最大回撤计算正确性

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.1 — 近3月最大回撤
- **前置条件**:
  - 提供已知的历史净值序列（含波动）
- **输入**:
  - 净值序列（从旧到新）：[1.00, 1.05, 1.02, 0.98, 1.03, 1.01]
  - 最新净值为 1.01
- **执行步骤**:
  1. 以模拟数据调用最大回撤计算函数
  2. 验证返回值
- **预期输出**:
  - 区间最高净值 = 1.05（第 2 个点）
  - 最大回撤点净值 = 0.98（第 4 个点）
  - `three_month_max_drawdown` = (1 - 0.98/1.05) × 100 ≈ 6.6667
- **清理**: 无

---

### TC-005: 最大回撤 — 净值单调上涨（无回撤）

- **类型**: 边界测试
- **关联验收标准**: SUB-2.1.1 — 近3月最大回撤
- **前置条件**:
  - 净值序列单调递增
- **输入**:
  - 净值序列：[1.00, 1.01, 1.02, 1.03, 1.04, 1.05]
- **执行步骤**:
  1. 以模拟数据调用最大回撤计算函数
- **预期输出**:
  - `three_month_max_drawdown` ≈ 0.0（无回撤，应为 0 或非常接近 0）
- **清理**: 无

---

### TC-006: 历史数据不足 30 条 — 近 1 月收益率降级

- **类型**: 边界测试
- **关联验收标准**: SUB-2.1.1 — 单个失败不影响其他指标
- **前置条件**:
  - 历史净值数据仅 15 条（不足 30 日）
- **输入**:
  - 净值序列长度为 15（最新净值 1.05）
  - 前一日数据存在（可算日涨跌幅）
- **执行步骤**:
  1. 调用计算函数
  2. 检查各项指标
- **预期输出**:
  - `one_month_return` = `None`（数据不足，优雅降级）
  - `daily_change_pct` 正常计算（非 None，前一日数据足够）
  - `nav` 正常返回
  - 其他指标不受影响
  - 不抛出异常
- **清理**: 无

---

### TC-007: 历史数据仅 1 条 — 日涨跌幅降级

- **类型**: 边界测试
- **关联验收标准**: SUB-2.1.1 — 单个失败不影响其他指标
- **前置条件**:
  - 历史净值数据仅 1 条（无法计算前一日差值）
- **输入**:
  - 净值序列长度为 1，`nav = 1.05`
- **执行步骤**:
  1. 调用计算函数
- **预期输出**:
  - `daily_change_pct` = `None`（无前一日数据）
  - `one_month_return` = `None`（无 30 日前数据）
  - `three_month_max_drawdown` = `None`（数据不足）
  - `nav` = 1.05（直接获取，不受影响）
  - 不抛出异常
- **清理**: 无

---

### TC-008: 历史净值数据完全为空

- **类型**: 边界测试
- **关联验收标准**: SUB-2.1.1 — 单个失败不影响其他指标
- **前置条件**:
  - 基金存在但历史净值返回空列表
- **输入**:
  - `fund_code = "020741"`
  - 历史净值列表为空
  - 市场利率数据正常
- **执行步骤**:
  1. 调用计算编排服务
- **预期输出**:
  - `nav` = `None`（无净值数据）
  - `daily_change_pct` = `None`
  - `one_month_return` = `None`
  - `three_month_max_drawdown` = `None`
  - `ten_year_treasury` 正常（市场利率独立获取）
  - `credit_spread_aa_plus` 正常
  - 不抛出异常
- **清理**: 无

---

### TC-009: 七日年化收益率 — 货币基金直接获取

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.1 — 七日年化收益率
- **前置条件**:
  - 基金为货币基金类型（如 `000001`）
  - 数据源可提供七日年化数据
- **输入**:
  - `fund_code = "000001"`
  - `seven_day_yield` 字段存在于 data_fetcher 返回数据中
- **执行步骤**:
  1. 调用计算函数
  2. 检查七日年化字段
- **预期输出**:
  - `seven_day_annual_yield` 非 None（直接获取到值）
  - 值为正浮点数
- **清理**: 无

---

### TC-010: 七日年化收益率 — 债券基金不可获取时标 None

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.1 — 七日年化收益率
- **前置条件**:
  - 基金为纯债基金（如 `020741`）
  - 数据源不提供七日年化（债券基金通常无此指标）
- **输入**:
  - `fund_code = "020741"`
  - `seven_day_yield` 为 None
- **执行步骤**:
  1. 调用计算函数
- **预期输出**:
  - `seven_day_annual_yield` = `None`（债券基金不含此指标）
  - 其他指标正常
  - 不抛出异常
- **清理**: 无

---

### TC-011: 信用利差 — 数据不可用时返回 None

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.1 — 信用利差
- **前置条件**:
  - `fetch_credit_spread()` 返回 `value=None`（如 bond_china_yield 无数据）
- **输入**:
  - 市场利率数据中 `credit_spread_aa_plus` 为 None
- **执行步骤**:
  1. 调用计算编排服务
- **预期输出**:
  - `credit_spread_aa_plus` = `None`
  - 其他指标不受影响
  - 不抛出异常
- **清理**: 无

---

## 二、SUB-2.1.2 — 计算编排服务

### TC-012: asyncio.gather 并行拉取全部数据源成功

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.2 — asyncio.gather 并行调用
- **前置条件**:
  - 所有数据源正常可用
  - 基金 `020741` 存在
- **输入**:
  - `fund_code = "020741"`
- **执行步骤**:
  1. 调用 `calculation_service.calculate("020741")`
  2. 验证并行拉取了基金信息、历史净值、国债收益率、信用利差共 4 个数据源
  3. 验证耗时 ≤ 最长单源耗时（非串行累加）
- **预期输出**:
  - 返回 `CalculationResponse` 含完整 8 项指标
  - 计算耗时明显短于 4 个数据源串行总和（可通过日志验证 asyncio.gather 并行执行）
- **清理**: 无

---

### TC-013: 单源失败不中断 — 历史净值获取失败

- **类型**: 异常测试
- **关联验收标准**: SUB-2.1.2 — return_exceptions=True 处理单源失败
- **前置条件**:
  - 基金信息可正常获取
  - 历史净值数据源模拟故障（抛出 RecoverableError）
  - 市场利率数据正常
- **输入**:
  - `fund_code = "020741"`
  - `fetch_fund_nav_history` 抛出 `RecoverableError`
- **执行步骤**:
  1. 调用 `calculation_service.calculate("020741")`
  2. 检查返回值
- **预期输出**:
  - `fund_name` 正常返回
  - `nav` = `None`（净值数据依赖历史净值，标 None）
  - `daily_change_pct` = `None`
  - `one_month_return` = `None`
  - `three_month_max_drawdown` = `None`
  - `ten_year_treasury` 正常（独立数据源未受影响）
  - `credit_spread_aa_plus` 正常
  - HTTP 状态码 200（非 500/503）
- **清理**: 无

---

### TC-014: 单源失败不中断 — 市场利率获取失败

- **类型**: 异常测试
- **关联验收标准**: SUB-2.1.2 — return_exceptions=True 处理单源失败
- **前置条件**:
  - 基金信息和历史净值正常
  - `fetch_treasury_yield` 抛出 `RecoverableError`
- **输入**:
  - `fund_code = "020741"`
- **执行步骤**:
  1. 调用 `calculation_service.calculate("020741")`
- **预期输出**:
  - 与净值相关的 4 项指标（nav、daily_change_pct、one_month_return、three_month_max_drawdown）正常
  - `ten_year_treasury` = `None`
  - `credit_spread_aa_plus` = `None`
  - HTTP 状态码 200
- **清理**: 无

---

### TC-015: 全部数据源失败 — 抛出 FatalError

- **类型**: 异常测试
- **关联验收标准**: SUB-2.1.2 — 全部失败时抛出 FatalError
- **前置条件**:
  - 所有 3-4 个数据源均模拟故障
- **输入**:
  - `fund_code = "020741"`
  - `fetch_fund_info` → `RecoverableError`
  - `fetch_fund_nav_history` → `RecoverableError`
  - `fetch_treasury_yield` → `RecoverableError`
  - `fetch_credit_spread` → `RecoverableError`
- **执行步骤**:
  1. 调用 `calculation_service.calculate("020741")`
  2. 捕获异常
- **预期输出**:
  - 抛出 `FatalError`
  - `FatalError.code` = 50001（或 `ErrorCode.ALL_SOURCES_FAILED`）
  - `FatalError.status_code` = 503
  - `FatalError.message` 含"服务暂时不可用"类中文提示
- **清理**: 无

---

### TC-016: 缓存命中 — 5 分钟内重复请求返回缓存

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.2 — 5 分钟内重复请求返回缓存
- **前置条件**:
  - 前一次 `calculate("020741")` 已成功执行并写入缓存
  - 距上次请求不足 5 分钟
- **输入**:
  - `fund_code = "020741"`
- **执行步骤**:
  1. 首次调用 `calculate("020741")` — 确保走完整计算链路
  2. 立即第二次调用 `calculate("020741")`
  3. 验证第二次调用未触发外部数据源请求（通过日志或 mock 断言）
  4. 验证两次返回结果一致
- **预期输出**:
  - 第二次调用返回缓存结果，不重新请求外部数据源
  - 两次调用返回的 `nav`、`daily_change_pct` 等指标值相同
  - 缓存 key 前缀为 `"calc:"`，TTL = `settings.CACHE_TTL_CALC`（300s）
- **清理**: 清除缓存

---

### TC-017: 缓存过期后重新计算

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.2 — 缓存 TTL 5 分钟
- **前置条件**:
  - 缓存 TTL 已过期（超过 300s）或手动清除缓存
- **输入**:
  - `fund_code = "020741"`
- **执行步骤**:
  1. 首次调用 `calculate("020741")` 写入缓存
  2. 手动清除缓存或等待 TTL 过期
  3. 再次调用 `calculate("020741")`
- **预期输出**:
  - 第二次调用重新执行完整计算链路（非缓存命中）
  - 返回有效结果
- **清理**: 无

---

### TC-018: 计算服务 — calculate 返回完整 CalculationResponse

- **类型**: 功能测试
- **关联验收标准**: Task 2.1 验收标准 1 — calculate(fund_code) -> CalculationResult
- **前置条件**:
  - 所有数据源正常
- **输入**:
  - `fund_code = "020741"`
- **执行步骤**:
  1. 调用 `calculation_service.calculate("020741")`
  2. 验证返回类型
- **预期输出**:
  - 返回 `CalculationResponse` 实例（Pydantic BaseModel）
  - 包含 `fund_code`、`fund_name`
  - 包含全部 8 项指标字段（即便某些为 None）
  - 包含 `data_date`、`is_trading_day`、`disclaimer`
- **清理**: 无

---

## 三、SUB-2.1.3 — 市场数据服务

### TC-019: get_market_rates 正常获取市场利率

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.3 — market_service.get_market_rates()
- **前置条件**:
  - 国债收益率和信用利差数据源正常
  - 内存缓存无数据（冷启动）
- **输入**:
  - 无参数
- **执行步骤**:
  1. 调用 `market_service.get_market_rates()`
- **预期输出**:
  - 返回 dict，包含 `ten_year_treasury`（float 或 None）
  - 返回 dict，包含 `credit_spread_aa_plus`（float 或 None）
  - 至少一个指标非 None（数据源正常时）
- **清理**: 无

---

### TC-020: 市场利率内存缓存命中（TTL 2min 内）

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.3 — 优先从内存缓存读取（TTL 2min）
- **前置条件**:
  - 前一次 `get_market_rates()` 已执行并写入缓存
  - 距上次请求 < 120s
- **输入**:
  - 无参数
- **执行步骤**:
  1. 首次调用 `get_market_rates()` — 触发数据源获取
  2. 立即第二次调用 `get_market_rates()`
  3. 验证第二次未调用 `data_fetcher`
- **预期输出**:
  - 两次调用返回相同的市场利率数值
  - 缓存 key 前缀为 `"market:"`，TTL = `settings.CACHE_TTL_MARKET`（120s）
- **清理**: 清除缓存

---

### TC-021: 市场利率缓存未命中 — 调 data_fetcher 并写缓存

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.3 — 缓存未命中则调 data_fetcher 并写缓存
- **前置条件**:
  - 缓存为空或已过期
- **输入**:
  - 无参数
- **执行步骤**:
  1. 清除 market 缓存
  2. 调用 `get_market_rates()`
  3. 验证调用了 `fetch_treasury_yield()` 和 `fetch_credit_spread()`
  4. 再次调用 `get_market_rates()` 验证缓存命中
- **预期输出**:
  - 首次调用触发外部数据源
  - 结果写入内存缓存
  - 第二次调用直接返回缓存值
- **清理**: 无

---

### TC-022: market_repo — save_market_data 持久化到 MongoDB

- **类型**: 集成测试
- **关联验收标准**: SUB-2.1.3 — market_repo 持久化到 MongoDB
- **前置条件**:
  - MongoDB 连接正常
  - `MarketData` 模型已在 Beanie 注册
- **输入**:
  - `indicator_name = "treasury_yield_10y"`
  - `value = 2.85`
  - `unit = "%"`
  - `fetched_at = datetime.now()`
- **执行步骤**:
  1. 调用 `market_repo.save_market_data("treasury_yield_10y", 2.85, "%")`
  2. 查询 MongoDB `market_data` 集合
- **预期输出**:
  - 集合中存在一条新文档
  - `indicator_name` = `"treasury_yield_10y"`
  - `value` = 2.85
  - `unit` = `"%"`
  - `fetched_at` 为最近时间
- **清理**: 删除测试写入的文档

---

### TC-023: market_repo — get_latest 查询最新数据

- **类型**: 功能测试
- **关联验收标准**: SUB-2.1.3 — market_repo get_latest
- **前置条件**:
  - MongoDB 中已存在多条同名指标记录（不同时间）
- **输入**:
  - `indicator_name = "treasury_yield_10y"`
- **执行步骤**:
  1. 插入两条记录：旧时间 value=2.80，新时间 value=2.85
  2. 调用 `market_repo.get_latest("treasury_yield_10y")`
- **预期输出**:
  - 返回的 `MarketData` 文档 `value` = 2.85（最新一条）
  - 按 `fetched_at` 降序取第一条
- **清理**: 删除测试文档

---

## 四、集成测试

### TC-024: 计算编排完整端到端链路

- **类型**: 集成测试
- **关联验收标准**: Task 2.1 全部验收标准
- **前置条件**:
  - 基金 `020741` 已通过 Task 1.3 的基金查询 API 确认存在
  - MongoDB 连接正常
  - 所有数据源正常
- **输入**:
  - `fund_code = "020741"`
- **执行步骤**:
  1. 先调用 `fund_service.query_fund("020741")` 确认基金信息已缓存
  2. 调用 `calculation_service.calculate("020741")`
  3. 验证返回结果同时包含基金信息和 8 项指标
  4. 验证 `disclaimer` 字段非空且内容与 `fund_service.DISCLAIMER_TEXT` 一致
  5. 验证 `data_date` 为当天日期（YYYY-MM-DD）
  6. 验证 `is_trading_day` 正确（调用 `trading_calendar.is_trading_day()`）
- **预期输出**:
  - `fund_code` = `"020741"`
  - `fund_name` 非空
  - `disclaimer` 非空，与 ADR 5.3 一致
  - `data_date` 为 `"2025-06-25"` 格式
  - `is_trading_day` 为 `True` 或 `False`（取决于实际日期）
  - 所有字段符合 `CalculationResponse` Schema
- **清理**: 无

---

## 测试用例索引

| 编号 | 名称 | 类型 | 关联子任务 |
|------|------|------|-----------|
| TC-001 | 8 项指标全部正常计算 | 功能 | SUB-2.1.1 |
| TC-002 | 日涨跌幅精确值验证 | 功能 | SUB-2.1.1 |
| TC-003 | 近1月收益率精确值验证 | 功能 | SUB-2.1.1 |
| TC-004 | 近3月最大回撤正确性 | 功能 | SUB-2.1.1 |
| TC-005 | 最大回撤—单调上涨无回撤 | 边界 | SUB-2.1.1 |
| TC-006 | 历史数据不足30条—近1月收益降级 | 边界 | SUB-2.1.1 |
| TC-007 | 历史数据仅1条—日涨跌幅降级 | 边界 | SUB-2.1.1 |
| TC-008 | 历史净值完全为空 | 边界 | SUB-2.1.1 |
| TC-009 | 七日年化—货币基金直接获取 | 功能 | SUB-2.1.1 |
| TC-010 | 七日年化—债券基金标 None | 功能 | SUB-2.1.1 |
| TC-011 | 信用利差不可用时标 None | 功能 | SUB-2.1.1 |
| TC-012 | asyncio.gather 并行拉取成功 | 功能 | SUB-2.1.2 |
| TC-013 | 单源失败—历史净值异常不中断 | 异常 | SUB-2.1.2 |
| TC-014 | 单源失败—市场利率异常不中断 | 异常 | SUB-2.1.2 |
| TC-015 | 全部数据源失败—FatalError | 异常 | SUB-2.1.2 |
| TC-016 | 缓存命中—5分钟内返回缓存 | 功能 | SUB-2.1.2 |
| TC-017 | 缓存过期后重新计算 | 功能 | SUB-2.1.2 |
| TC-018 | calculate 返回完整 CalculationResponse | 功能 | Task 2.1 |
| TC-019 | get_market_rates 正常获取 | 功能 | SUB-2.1.3 |
| TC-020 | 市场利率缓存命中（TTL 2min） | 功能 | SUB-2.1.3 |
| TC-021 | 缓存未命中—调 data_fetcher 写缓存 | 功能 | SUB-2.1.3 |
| TC-022 | market_repo 持久化到 MongoDB | 集成 | SUB-2.1.3 |
| TC-023 | market_repo get_latest 查询最新 | 功能 | SUB-2.1.3 |
| TC-024 | 端到端链路—disclaimer + data_date + is_trading_day | 集成 | Task 2.1 |
