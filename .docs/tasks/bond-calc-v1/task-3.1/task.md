# Task 3.1: 前端 API 层与状态管理

| 属性 | 值 |
|------|-----|
| ID | 3.1 |
| 状态 | done |
| 优先级 | P0 |
| 依赖 | 0.2 |
| 阶段 | 阶段3: 前端组件 |
| 预估工时 | 2-3 小时 |

## 描述

实现前端的 API 请求封装层、TypeScript 类型定义、Pinia 状态管理 store、数值格式化工具函数和中文文案常量文件。本 Task 为所有前端页面和组件提供数据和类型基础。

## 验收标准

- [ ] `src/api/index.ts` — fetch 封装（`baseFetch<T>`）：15 秒超时、统一错误处理、`ApiResponse<T>` 响应解析、`ApiError` 异常类
- [ ] `src/api/funds.ts` — `fetchFund(code: string): Promise<FundInfo>` 接口函数
- [ ] `src/api/calculations.ts` — `triggerCalculation(code: string): Promise<{calculation_id: string}>` + `getCalculation(id: string): Promise<Calculation>` 接口函数
- [ ] `src/types/api.ts` — TypeScript 类型定义：`FundInfo`、`Calculation`、`ApiResponse<T>`、`ApiError`、`ErrorCode` 常量枚举
- [ ] `src/stores/fund.ts` — Pinia store：
  - 状态：`fundInfo`、`calculation`、`loading`、`error`
  - 计算属性：`isBondFund`（类型含"债"字）、`hasCalculation`
  - 操作：`fetchFundInfo(code)`、`refreshCalculation(code)`、`clearError()`
- [ ] `src/utils/format.ts` — 格式化函数：`formatPercent(value)`（小数转百分比字符串）、`formatNA(value)`（null → "N/A"）、`formatDate(date)`（日期格式化）
- [ ] `src/locales/zh-CN.ts` — 中文文案常量：错误提示、免责声明、标签文案、加载文案

## 子任务

### SUB-3.1.1: API 封装层
- **描述**: 实现 fetch 封装和接口函数
- **验收标准**:
  - [ ] `baseFetch<T>` 含超时控制（15s AbortController）、HTTP 状态码检查、业务错误码检查
  - [ ] `ApiError` 类含 `code` 和 `message` 属性
  - [ ] `fetchFund` 调用 `GET /api/v1/funds/{code}`
  - [ ] `triggerCalculation` 调用 `POST /api/v1/calculations`，`getCalculation` 调用 `GET /api/v1/calculations/{id}`
  - [ ] `BASE_URL` 从 `import.meta.env.VITE_API_BASE_URL` 读取，默认 `http://localhost:8000`

### SUB-3.1.2: TypeScript 类型定义
- **描述**: 定义所有 API 相关 TypeScript 类型
- **验收标准**:
  - [ ] `FundInfo` 接口：name, code, type, nav, seven_day_yield, updated_at
  - [ ] `Calculation` 接口：8 项指标 + fund_code + data_date + is_trading_day + disclaimer
  - [ ] `ApiResponse<T>` 泛型：code, message, data
  - [ ] `ErrorCode` 常量枚举：FUND_NOT_FOUND, FUND_TYPE_MISMATCH 等

### SUB-3.1.3: Pinia Store
- **描述**: 实现 fundStore 状态管理
- **验收标准**:
  - [ ] `fetchFundInfo` 调用 API、更新 `fundInfo`、异常时设置 `error`
  - [ ] `refreshCalculation` 触发计算 → 轮询结果（最多 2 分钟）→ 更新 `calculation`
  - [ ] `loading` 状态在请求开始时为 `true`，结束时为 `false`
  - [ ] `clearError` 清空 `error`

### SUB-3.1.4: 工具函数与文案常量
- **描述**: 实现格式化工具和中文文案
- **验收标准**:
  - [ ] `formatPercent(0.31)` 返回 `"0.31%"`，`formatPercent(null)` 返回 `"N/A"`
  - [ ] `formatNA(null)` 返回 `"N/A"`，`formatNA("0.85")` 返回 `"0.85"`
  - [ ] `zh-CN.ts` 导出 `ERROR_MESSAGES`、`LABELS`、`DISCLAIMER` 等常量对象
