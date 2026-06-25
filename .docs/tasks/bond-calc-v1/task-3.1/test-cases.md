# 测试用例 — Task 3.1: 前端 API 层与状态管理

## 测试范围概述

| 维度 | 覆盖内容 |
|------|---------|
| 功能测试 | fetch 封装正常请求/响应、API 接口函数、Pinia store 状态流转、格式化函数输出 |
| 边界测试 | 空值/null处理、超时边界、轮询终止条件、极限输入值 |
| 异常测试 | 网络错误、HTTP 错误码、业务错误码、超时、JSON 解析失败 |
| 集成测试 | fundStore 与 API 层协作、路由参数传递、环境变量切换 |

---

## SUB-3.1.1: API 封装层

### TC-001: baseFetch 正常 GET 请求返回数据
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.1 — baseFetch 含超时控制、HTTP 状态码检查、业务错误码检查
- **前置条件**: Mock fetch 返回 `{code: 0, message: "success", data: {fund_code: "020741", name: "测试基金"}}`
- **输入**:
  - 调用 `baseFetch<FundInfo>("/api/v1/funds/020741")`
- **执行步骤**:
  1. 设置 mock `fetch` 返回 HTTP 200 + 业务 code=0 的 JSON
  2. 调用 `baseFetch`
  3. 检查返回值
- **预期输出**:
  - 返回 `data` 字段内容：`{fund_code: "020741", name: "测试基金"}`
  - 不会抛出异常
- **清理**: 无

### TC-002: baseFetch 业务错误码抛出 ApiError
- **类型**: 异常测试
- **关联验收标准**: SUB-3.1.1 — 业务错误码检查，ApiError 类含 code 和 message
- **前置条件**: Mock fetch 返回 `{code: 40001, message: "基金不存在", data: null}`
- **输入**:
  - 调用 `baseFetch("/api/v1/funds/999999")`
- **执行步骤**:
  1. 设置 mock `fetch` 返回 HTTP 200 + 业务 code=40001 的 JSON
  2. 调用 `baseFetch`，捕获抛出的异常
- **预期输出**:
  - 抛出 `ApiError` 实例
  - `error.code === 40001`
  - `error.message === "基金不存在"`
- **清理**: 无

### TC-003: baseFetch HTTP 非 2xx 状态码抛出 ApiError
- **类型**: 异常测试
- **关联验收标准**: SUB-3.1.1 — HTTP 状态码检查
- **前置条件**: Mock fetch 返回 HTTP 503
- **输入**:
  - 调用 `baseFetch("/api/v1/calculations/xxx")`
- **执行步骤**:
  1. 设置 mock `fetch` 返回 HTTP 503，无 JSON body
  2. 调用 `baseFetch`，捕获抛出的异常
- **预期输出**:
  - 抛出 `ApiError` 实例
  - `error.code === 503`
  - `error.message` 包含 "请求失败" 字样
- **清理**: 无

### TC-004: baseFetch 15 秒超时抛出 ApiError
- **类型**: 异常测试
- **关联验收标准**: SUB-3.1.1 — 超时控制（15s AbortController）
- **前置条件**: Mock fetch 延迟超过 15 秒（或用 jest.useFakeTimers 模拟 AbortController）
- **输入**:
  - 调用 `baseFetch("/api/v1/funds/020741")`
- **执行步骤**:
  1. Mock fetch 返回一个永不 resolve 的 Promise
  2. 推进虚拟时间至 15001ms
  3. 捕获抛出的异常
- **预期输出**:
  - 抛出 `ApiError` 实例
  - `error.code === 0`（超时错误码）
  - `error.message` 包含 "超时" 字样
- **清理**: 恢复真实定时器

### TC-005: baseFetch 网络异常抛出 ApiError
- **类型**: 异常测试
- **关联验收标准**: SUB-3.1.1 — 统一错误处理
- **前置条件**: Mock fetch 抛出 `TypeError: Failed to fetch`
- **输入**:
  - 调用 `baseFetch("/api/v1/funds/020741")`
- **执行步骤**:
  1. Mock fetch 为 `jest.fn().mockRejectedValue(new TypeError("Failed to fetch"))`
  2. 捕获抛出的异常
- **预期输出**:
  - 抛出 `ApiError` 实例
  - `error.code === -1`
  - `error.message` 包含 "网络异常" 字样
- **清理**: 无

### TC-006: fetchFund 调用正确的 API 端点
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.1 — fetchFund 调用 GET /api/v1/funds/{code}
- **前置条件**: Mock fetch 返回正常响应
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. Mock `fetch` 并记录调用参数
  2. 调用 `fetchFund("020741")`
- **预期输出**:
  - `fetch` 被调用 1 次
  - 请求 URL 为 `${BASE_URL}/api/v1/funds/020741`
  - 请求 method 为 `GET`
- **清理**: 无

### TC-007: triggerCalculation 调用正确的 API 端点
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.1 — triggerCalculation 调用 POST /api/v1/calculations
- **前置条件**: Mock fetch 返回 `{code: 0, message: "success", data: {calculation_id: "abc123", status: "completed"}}`
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. Mock `fetch` 并记录调用参数
  2. 调用 `triggerCalculation("020741")`
- **预期输出**:
  - `fetch` 被调用 1 次
  - 请求 URL 为 `${BASE_URL}/api/v1/calculations`
  - 请求 method 为 `POST`
  - 请求 body 为 `JSON.stringify({fund_code: "020741"})`
  - 请求头 `Content-Type` 为 `application/json`
- **清理**: 无

### TC-008: getCalculation 调用正确的 API 端点
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.1 — getCalculation 调用 GET /api/v1/calculations/{id}
- **前置条件**: Mock fetch 返回完整的 Calculation 响应
- **输入**:
  - `id = "507f1f77bcf86cd799439011"`
- **执行步骤**:
  1. Mock `fetch` 并记录调用参数
  2. 调用 `getCalculation("507f1f77bcf86cd799439011")`
- **预期输出**:
  - `fetch` 被调用 1 次
  - 请求 URL 为 `${BASE_URL}/api/v1/calculations/507f1f77bcf86cd799439011`
  - 请求 method 为 `GET`
- **清理**: 无

### TC-009: BASE_URL 默认值
- **类型**: 边界测试
- **关联验收标准**: SUB-3.1.1 — BASE_URL 从 import.meta.env.VITE_API_BASE_URL 读取，默认 http://localhost:8000
- **前置条件**: `import.meta.env.VITE_API_BASE_URL` 未设置（undefined）
- **输入**:
  - 无
- **执行步骤**:
  1. 在测试环境中清除 `VITE_API_BASE_URL` 环境变量
  2. 导入或重新加载 API 模块
  3. 检查 BASE_URL 值
- **预期输出**:
  - `BASE_URL === "http://localhost:8000"`
- **清理**: 无

### TC-010: BASE_URL 从环境变量读取
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.1 — BASE_URL 从 import.meta.env.VITE_API_BASE_URL 读取
- **前置条件**: 设置 `VITE_API_BASE_URL=https://api.example.com`
- **输入**:
  - 无
- **执行步骤**:
  1. Mock `import.meta.env.VITE_API_BASE_URL` 为 `"https://api.example.com"`
  2. 导入或重新加载 API 模块
  3. 检查 fetchFund 发出的请求 URL
- **预期输出**:
  - 请求发送至 `https://api.example.com/api/v1/funds/020741`
- **清理**: 恢复环境变量

---

## SUB-3.1.2: TypeScript 类型定义

### TC-011: FundInfo 类型结构验证
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.2 — FundInfo 接口：name, code, type, nav, seven_day_yield, updated_at
- **前置条件**: 类型定义文件已创建
- **输入**:
  - 构造一个符合 FundInfo 接口的对象
- **执行步骤**:
  1. 创建一个 FundInfo 类型的对象变量
  2. 赋值所有必填字段和可选字段
  3. TypeScript 编译检查
- **预期输出**:
  - 编译通过，无类型错误
  - 对象可包含字段：`fund_code` (string), `name` (string), `fund_type` (string), `nav` (number | null), `seven_day_annual_yield` (number | null), `updated_at` (string), `disclaimer` (string)
- **清理**: 无

### TC-012: Calculation 类型包含全部 8 项指标
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.2 — Calculation 接口：8 项指标 + fund_code + data_date + is_trading_day + disclaimer
- **前置条件**: 类型定义文件已创建
- **输入**:
  - 构造一个完整的 Calculation 类型对象
- **执行步骤**:
  1. 创建一个 Calculation 类型的对象变量
  2. 赋值所有 8 项指标（部分为 null）
  3. TypeScript 编译检查
- **预期输出**:
  - 编译通过
  - 8 项指标字段全部存在且类型为 `number | null`：
    nav, daily_change_pct, seven_day_annual_yield, wanfen_income,
    one_month_return, three_month_max_drawdown, ten_year_treasury, credit_spread_aa_plus
  - 元数据字段：fund_code (string), fund_name (string), data_date (string), is_trading_day (boolean), disclaimer (string)
  - status 字段：'processing' | 'completed' | 'failed'
- **清理**: 无

### TC-013: ApiResponse<T> 泛型类型
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.2 — ApiResponse<T> 泛型：code, message, data
- **前置条件**: 类型定义文件已创建
- **输入**:
  - 声明 `ApiResponse<FundInfo>` 和 `ApiResponse<null>` 类型变量
- **执行步骤**:
  1. 创建 `const resp1: ApiResponse<FundInfo>`
  2. 创建 `const resp2: ApiResponse<null>`
  3. TypeScript 编译检查
- **预期输出**:
  - `resp1.data` 类型为 `FundInfo | null`
  - `resp2.data` 类型为 `null`
  - `code` 类型为 `number`
  - `message` 类型为 `string`
- **清理**: 无

### TC-014: ErrorCode 常量枚举完整性
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.2 — ErrorCode 常量枚举：FUND_NOT_FOUND, FUND_TYPE_MISMATCH 等
- **前置条件**: 类型定义文件已创建
- **输入**:
  - 导入 ErrorCode 枚举
- **执行步骤**:
  1. 导入 ErrorCode
  2. 检查包含的错误码
- **预期输出**:
  - `ErrorCode.FUND_NOT_FOUND === 40001`
  - `ErrorCode.TYPE_MISMATCH === 40002` (或 FUND_TYPE_MISMATCH)
  - `ErrorCode.INVALID_CODE_FORMAT === 40003`
  - `ErrorCode.DATA_SOURCE_FAILED === 40004`
  - `ErrorCode.ALL_SOURCES_FAILED === 50001`
  - `ErrorCode.CALCULATION_FAILED === 50002`
  - `ErrorCode.TIMEOUT === 0`（前端自定义超时错误码）
  - `ErrorCode.NETWORK_ERROR === -1`（前端自定义网络异常错误码）
- **清理**: 无

---

## SUB-3.1.3: Pinia Store

### TC-015: 初始状态
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.3 — store 初始状态
- **前置条件**: 创建 fundStore 实例
- **输入**:
  - 无（不调用任何 action）
- **执行步骤**:
  1. 在 `setup` 中调用 `useFundStore()`
  2. 检查初始状态
- **预期输出**:
  - `fundInfo === null`
  - `calculation === null`
  - `loading === false`
  - `error === null`
  - `isBondFund === false`
  - `hasCalculation === false`
- **清理**: 无

### TC-016: fetchFundInfo 成功更新 fundInfo
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.3 — fetchFundInfo 调用 API、更新 fundInfo
- **前置条件**: Mock `fetchFund` 返回有效的 FundInfo 对象
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. Mock `fetchFund` 返回 `{fund_code: "020741", name: "测试基金", fund_type: "债券型", ...}`
  2. 调用 `store.fetchFundInfo("020741")`
  3. 等待 Promise resolve
- **预期输出**:
  - `store.fundInfo.fund_code === "020741"`
  - `store.fundInfo.name === "测试基金"`
  - `store.loading === false`
  - `store.error === null`
- **清理**: 无

### TC-017: fetchFundInfo 过程中 loading 为 true
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.3 — loading 状态在请求开始时为 true，结束时为 false
- **前置条件**: Mock `fetchFund` 返回一个可手动 resolve 的 Promise
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. 创建手动控制的 Promise
  2. Mock `fetchFund` 返回该 Promise
  3. 调用 `store.fetchFundInfo("020741")`（不 await）
  4. 立即检查 `store.loading`
  5. resolve Promise
  6. await 后检查 `store.loading`
- **预期输出**:
  - 步骤 4: `store.loading === true`
  - 步骤 6: `store.loading === false`
- **清理**: 无

### TC-018: fetchFundInfo 异常时设置 error
- **类型**: 异常测试
- **关联验收标准**: SUB-3.1.3 — 异常时设置 error
- **前置条件**: Mock `fetchFund` 抛出 ApiError
- **输入**:
  - `code = "999999"`
- **执行步骤**:
  1. Mock `fetchFund` 抛出 `new ApiError(40001, "基金不存在")`
  2. 调用 `store.fetchFundInfo("999999")`
  3. 等待 Promise resolve（不会 reject，错误被捕获在 store 中）
- **预期输出**:
  - `store.error === "基金不存在"`
  - `store.fundInfo === null`（未更新）
  - `store.loading === false`
- **清理**: 无

### TC-019: refreshCalculation 触发计算并获取结果
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.3 — refreshCalculation 触发计算 → 轮询结果 → 更新 calculation
- **前置条件**: 
  - Mock `triggerCalculation` 返回 `{calculation_id: "abc123", status: "completed"}`
  - Mock `getCalculation` 返回完整 Calculation
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. Mock 上述 API 函数
  2. 调用 `store.refreshCalculation("020741")`
  3. 等待 Promise resolve
- **预期输出**:
  - `store.calculation !== null`
  - `store.calculation.fund_code === "020741"`
  - `store.hasCalculation === true`
  - `store.loading === false`
- **清理**: 无

### TC-020: refreshCalculation 轮询 processing 状态
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.3 — 轮询结果（最多 2 分钟）
- **前置条件**:
  - Mock `triggerCalculation` 返回 `{calculation_id: "abc123", status: "processing"}`
  - Mock `getCalculation` 第一次返回 status=processing，第二次返回 status=completed
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. Mock `getCalculation` 前 2 次返回 `{status: "processing"}`，第 3 次返回完整结果
  2. 调用 `store.refreshCalculation("020741")`
  3. 等待 Promise resolve
- **预期输出**:
  - `getCalculation` 被调用 3 次
  - 最终 `store.calculation !== null`（拿到 completed 结果）
  - `store.loading === false`
- **清理**: 无

### TC-021: refreshCalculation 轮询超时（超过 2 分钟）
- **类型**: 边界测试
- **关联验收标准**: SUB-3.1.3 — 轮询最多 2 分钟
- **前置条件**:
  - Mock `getCalculation` 始终返回 status=processing
  - 使用 fake timers 加速时间
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. Mock `getCalculation` 一直返回 `{status: "processing"}`
  2. 调用 `store.refreshCalculation("020741")`
  3. 推进时间超过 120 秒
  4. 等待 Promise resolve（reject 由 store 内部捕获）
- **预期输出**:
  - `store.error` 包含 "超时" 或 "计算超时" 字样
  - `store.loading === false`
  - `getCalculation` 调用次数不超过 `120秒 / 轮询间隔`
- **清理**: 恢复真实定时器

### TC-022: refreshCalculation 计算失败状态
- **类型**: 异常测试
- **关联验收标准**: SUB-3.1.3 — refreshCalculation 异常处理
- **前置条件**:
  - Mock `triggerCalculation` 返回 `{calculation_id: "abc123", status: "failed"}`
  - 或 Mock `getCalculation` 返回 `{status: "failed", error_message: "数据源不可用"}`
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. Mock 返回 failed 状态
  2. 调用 `store.refreshCalculation("020741")`
  3. 等待 Promise resolve
- **预期输出**:
  - `store.error` 包含 "数据源不可用" 或错误信息
  - `store.loading === false`
- **清理**: 无

### TC-023: isBondFund 计算属性 — 类型含"债"字
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.3 — isBondFund（类型含"债"字）
- **前置条件**: 无
- **输入**:
  - 分别设置 fundInfo.fund_type 为不同值
- **执行步骤**:
  1. 设置 `store.fundInfo = {..., fund_type: "债券型"}`
  2. 检查 `store.isBondFund`
  3. 设置 `store.fundInfo = {..., fund_type: "混合偏债"}`
  4. 检查 `store.isBondFund`
  5. 设置 `store.fundInfo = {..., fund_type: "股票型"}`
  6. 检查 `store.isBondFund`
  7. 设置 `store.fundInfo = null`
  8. 检查 `store.isBondFund`
- **预期输出**:
  - `fund_type = "债券型"` → `isBondFund === true`
  - `fund_type = "混合偏债"` → `isBondFund === true`
  - `fund_type = "股票型"` → `isBondFund === false`
  - `fundInfo = null` → `isBondFund === false`
- **清理**: 无

### TC-024: hasCalculation 计算属性
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.3 — hasCalculation
- **前置条件**: 无
- **输入**:
  - 分别设置 calculation 为 null 和有值
- **执行步骤**:
  1. 初始状态，检查 `store.hasCalculation`
  2. 设置 `store.calculation = {fund_code: "020741", ...}`
  3. 检查 `store.hasCalculation`
- **预期输出**:
  - 初始: `hasCalculation === false`
  - 设置后: `hasCalculation === true`
- **清理**: 无

### TC-025: clearError 清空 error
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.3 — clearError 清空 error
- **前置条件**: store.error 已设置
- **输入**:
  - 无
- **执行步骤**:
  1. 设置 `store.error = "测试错误"`
  2. 调用 `store.clearError()`
  3. 检查 `store.error`
- **预期输出**:
  - `store.error === null`
- **清理**: 无

---

## SUB-3.1.4: 工具函数与文案常量

### TC-026: formatPercent 正常值转换
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.4 — formatPercent(0.31) 返回 "0.31%"
- **前置条件**: 导入 formatPercent 函数
- **输入**:
  - `value = 0.31`
- **执行步骤**:
  1. 调用 `formatPercent(0.31)`
- **预期输出**:
  - 返回 `"0.31%"`
- **清理**: 无

### TC-027: formatPercent null 值返回 "N/A"
- **类型**: 边界测试
- **关联验收标准**: SUB-3.1.4 — formatPercent(null) 返回 "N/A"
- **前置条件**: 导入 formatPercent 函数
- **输入**:
  - `value = null`
- **执行步骤**:
  1. 调用 `formatPercent(null)`
- **预期输出**:
  - 返回 `"N/A"`
- **清理**: 无

### TC-028: formatPercent undefined 值返回 "N/A"
- **类型**: 边界测试
- **关联验收标准**: SUB-3.1.4 — 格式化函数边界处理
- **前置条件**: 导入 formatPercent 函数
- **输入**:
  - `value = undefined`
- **执行步骤**:
  1. 调用 `formatPercent(undefined)`
- **预期输出**:
  - 返回 `"N/A"`
- **清理**: 无

### TC-029: formatPercent 负数
- **类型**: 边界测试
- **关联验收标准**: SUB-3.1.4 — 格式化边界值
- **前置条件**: 导入 formatPercent 函数
- **输入**:
  - `value = -0.45`
- **执行步骤**:
  1. 调用 `formatPercent(-0.45)`
- **预期输出**:
  - 返回 `"-0.45%"`
- **清理**: 无

### TC-030: formatPercent 零值
- **类型**: 边界测试
- **关联验收标准**: SUB-3.1.4 — 格式化边界值
- **前置条件**: 导入 formatPercent 函数
- **输入**:
  - `value = 0`
- **执行步骤**:
  1. 调用 `formatPercent(0)`
- **预期输出**:
  - 返回 `"0.00%"` 或 `"0%"`（取决于精度约定）
- **清理**: 无

### TC-031: formatNA null 值返回 "N/A"
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.4 — formatNA(null) 返回 "N/A"
- **前置条件**: 导入 formatNA 函数
- **输入**:
  - `value = null`
- **执行步骤**:
  1. 调用 `formatNA(null)`
- **预期输出**:
  - 返回 `"N/A"`
- **清理**: 无

### TC-032: formatNA 有值原样返回
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.4 — formatNA("0.85") 返回 "0.85"
- **前置条件**: 导入 formatNA 函数
- **输入**:
  - `value = "0.85"`
- **执行步骤**:
  1. 调用 `formatNA("0.85")`
- **预期输出**:
  - 返回 `"0.85"`
- **清理**: 无

### TC-033: formatNA 数字转字符串
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.4 — formatNA 数字处理
- **前置条件**: 导入 formatNA 函数
- **输入**:
  - `value = 1.0234`（数字类型）
- **执行步骤**:
  1. 调用 `formatNA(1.0234)`
- **预期输出**:
  - 返回 `"1.0234"`（转为字符串）
- **清理**: 无

### TC-034: formatNA undefined 值返回 "N/A"
- **类型**: 边界测试
- **关联验收标准**: SUB-3.1.4 — formatNA 边界处理
- **前置条件**: 导入 formatNA 函数
- **输入**:
  - `value = undefined`
- **执行步骤**:
  1. 调用 `formatNA(undefined)`
- **预期输出**:
  - 返回 `"N/A"`
- **清理**: 无

### TC-035: formatDate 正常日期格式化
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.4 — formatDate 日期格式化
- **前置条件**: 导入 formatDate 函数
- **输入**:
  - `date = "2025-06-24"` （或 Date 对象）
- **执行步骤**:
  1. 调用 `formatDate("2025-06-24")`
- **预期输出**:
  - 返回格式化的中文日期字符串，如 `"2025年6月24日"` 或 `"2025-06-24"`
- **清理**: 无

### TC-036: formatDate null/undefined 返回 "N/A"
- **类型**: 边界测试
- **关联验收标准**: SUB-3.1.4 — formatDate 边界处理
- **前置条件**: 导入 formatDate 函数
- **输入**:
  - `date = null`
- **执行步骤**:
  1. 调用 `formatDate(null)` 然后 `formatDate(undefined)`
- **预期输出**:
  - 均返回 `"N/A"`
- **清理**: 无

### TC-037: zh-CN.ts 导出完整文案常量
- **类型**: 功能测试
- **关联验收标准**: SUB-3.1.4 — zh-CN.ts 导出 ERROR_MESSAGES、LABELS、DISCLAIMER 等常量对象
- **前置条件**: 导入 zh-CN 模块
- **输入**:
  - 无
- **执行步骤**:
  1. `import * as locales from '@/locales/zh-CN'`
  2. 检查导出的对象
- **预期输出**:
  - 至少包含 `ERROR_MESSAGES` 对象，含以下 key：
    - `NETWORK_ERROR`: "网络异常，请检查网络连接"
    - `TIMEOUT`: "请求超时，请稍后重试"
    - `FUND_NOT_FOUND`: "基金代码不存在，请检查后重试"
    - `TYPE_MISMATCH`: "该基金不是债券型基金，请输入债券基金代码"
    - `CALCULATION_FAILED`: "计算失败，请稍后重试"
    - `UNKNOWN_ERROR`: "未知错误，请稍后重试"
  - 包含 `LABELS` 对象，含以下 key：
    - `PAGE_TITLE`: 页面标题
    - `FUND_CODE_PLACEHOLDER`: 输入框占位提示
    - `QUERY_BUTTON`: 查询按钮文案
    - `REFRESH_BUTTON`: 刷新计算按钮文案
    - `NAV`: "最新净值"
    - `DAILY_CHANGE`: "日涨跌"
    - `SEVEN_DAY_YIELD`: "七日年化"
    - `WANFEN_INCOME`: "万份收益"
    - `ONE_MONTH_RETURN`: "近1月收益"
    - `MAX_DRAWDOWN`: "近3月最大回撤"
    - `TEN_YEAR_TREASURY`: "10年期国债"
    - `CREDIT_SPREAD`: "信用利差"
    - `DATA_DATE`: "数据日期"
  - 包含 `DISCLAIMER` 对象，含：
    - `TEXT`: 免责声明正文
- **清理**: 无

---

## 集成测试

### TC-038: fundStore.fetchFundInfo 完整调用链
- **类型**: 集成测试
- **关联验收标准**: SUB-3.1.3 + SUB-3.1.1 — Store 与 API 层协作
- **前置条件**: Mock `fetch` 全局函数
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. Mock fetch 返回正常的基金查询 JSON
  2. 调用 `store.fetchFundInfo("020741")`
  3. 验证整个数据流
- **预期输出**:
  - `fetch` 被正确调用（URL、method、headers）
  - `store.fundInfo` 正确填充
  - `store.loading` 生命周期正确（true → false）
  - 无异常抛出
- **清理**: 恢复 fetch mock

### TC-039: 网络错误时错误提示文案
- **类型**: 集成测试
- **关联验收标准**: SUB-3.1.1 + SUB-3.1.3 + SUB-3.1.4 — 错误处理全链路
- **前置条件**: Mock fetch 为网络断开状态
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. Mock fetch 抛出 `TypeError: Failed to fetch`
  2. 调用 `store.fetchFundInfo("020741")`
  3. 检查 store.error 内容
- **预期输出**:
  - `store.error` 包含 "网络异常" 及 "请检查网络连接" 字样（来自 zh-CN.ts）
- **清理**: 恢复 fetch mock

### TC-040: refreshCalculation 完整轮询链
- **类型**: 集成测试
- **关联验收标准**: SUB-3.1.1 + SUB-3.1.3 — 计算轮询全链路
- **前置条件**: 
  - Mock fetch 首次返回 processing，后续返回 completed
  - 使用 fake timers
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. Mock fetch：
     - POST `/calculations` → `{calculation_id: "abc", status: "processing"}`
     - GET `/calculations/abc` 第 1-2 次 → `{status: "processing"}`
     - GET `/calculations/abc` 第 3 次 → 完整 completed 结果
  2. 调用 `store.refreshCalculation("020741")`
  3. 推进 fake timers 模拟轮询间隔
  4. 等待 resolve
- **预期输出**:
  - `store.calculation` 包含完整的 8 项指标
  - `store.loading === false`
  - `store.hasCalculation === true`
  - `fetch` 共被调用 4 次（1 POST + 3 GET）
- **清理**: 恢复真实定时器和 fetch

---

## 统计

| 类型 | 数量 |
|------|------|
| 功能测试 | 21 |
| 边界测试 | 7 |
| 异常测试 | 6 |
| 集成测试 | 3 |
| **合计** | **37** |
