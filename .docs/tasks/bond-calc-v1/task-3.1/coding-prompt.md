# Coding Prompt — Task 3.1: 前端 API 层与状态管理

## 1. 任务目标

实现前端的 API 请求封装层、TypeScript 类型定义、Pinia 状态管理 store、数值格式化工具函数和中文文案常量文件，为后续所有页面和组件提供数据和类型基础。

## 2. 技术上下文

- **语言/框架**: Vue 3.5 + TypeScript 6.0 + Pinia 3.0 + Vue Router 5.1 + Vite 8.1
- **样式方案**: Tailwind CSS 4.3（本 Task 不涉及样式）
- **包管理器**: npm
- **路径别名**: `@/` → `src/`
- **TypeScript 约束**: `erasableSyntaxOnly: true`（禁止 `enum` 关键字，错误码用 `const` 对象 + `as const`）
- **后端 API 基路径**: `/api/v1`
- **开发环境后端地址**: `http://localhost:8000`

### 涉及文件（全部新建）

| 文件 | 说明 |
|------|------|
| `client/src/types/api.ts` | TypeScript 类型定义 |
| `client/src/api/index.ts` | fetch 封装层 |
| `client/src/api/funds.ts` | 基金查询 API |
| `client/src/api/calculations.ts` | 计算 API |
| `client/src/stores/fund.ts` | Pinia store |
| `client/src/utils/format.ts` | 数值格式化工具 |
| `client/src/locales/zh-CN.ts` | 中文文案常量 |

## 3. 实现要求

### 3.1 文件 `client/src/types/api.ts`

**职责**: 定义所有 API 相关的 TypeScript 类型。

#### 3.1.1 `ApiResponse<T>` 泛型接口

```typescript
interface ApiResponse<T> {
  code: number;       // 业务状态码，0 = 成功
  message: string;    // 提示信息
  data: T | null;     // 响应数据
}
```

#### 3.1.2 `ErrorCode` 常量对象

使用 `const` 对象 + `as const`（**不能使用 `enum`**，因为 `erasableSyntaxOnly: true`）：

```typescript
export const ErrorCode = {
  TIMEOUT: 0,              // 前端自定义：请求超时
  NETWORK_ERROR: -1,       // 前端自定义：网络异常
  FUND_NOT_FOUND: 40001,       // 后端：基金不存在
  TYPE_MISMATCH: 40002,        // 后端：基金类型不匹配
  INVALID_CODE_FORMAT: 40003,  // 后端：基金代码格式错误
  DATA_SOURCE_FAILED: 40004,   // 后端：数据源获取失败
  ALL_SOURCES_FAILED: 50001,   // 后端：所有数据源不可用
  CALCULATION_FAILED: 50002,   // 后端：计算失败
} as const;

export type ErrorCodeValue = (typeof ErrorCode)[keyof typeof ErrorCode];
```

#### 3.1.3 `FundInfo` 接口

对应后端 `GET /api/v1/funds/{code}` 响应 data 字段：

```typescript
export interface FundInfo {
  fund_code: string;
  name: string;
  fund_type: string;
  nav: number | null;
  seven_day_annual_yield: number | null;
  updated_at: string;
  disclaimer: string;
}
```

字段说明：
- `nav`: 最新单位净值，可能为 null
- `seven_day_annual_yield`: 七日年化收益率（小数形式，如 0.0382 表示 3.82%），非货币基金可能为 null
- `updated_at`: ISO 格式日期字符串
- `disclaimer`: 免责声明固定文本

#### 3.1.4 `Calculation` 接口

对应后端 `GET /api/v1/calculations/{id}` 响应 data 字段。需要支持三种状态：

```typescript
export interface Calculation {
  // 状态标识
  status: 'processing' | 'completed' | 'failed';

  // 基础信息（completed 时有值）
  fund_code?: string;
  fund_name?: string;

  // 8 项收益指标（completed 时有值，允许 null）
  nav?: number | null;
  daily_change_pct?: number | null;
  seven_day_annual_yield?: number | null;
  wanfen_income?: number | null;
  one_month_return?: number | null;
  three_month_max_drawdown?: number | null;
  ten_year_treasury?: number | null;
  credit_spread_aa_plus?: number | null;

  // 元数据
  data_date?: string;
  is_trading_day?: boolean;
  disclaimer?: string;

  // failed 状态
  error_message?: string;
}
```

注意：所有指标字段使用 `?`（可选），因为 processing/failed 状态下这些字段不存在。Boolean 类型不使用 `null`（`is_trading_day` 只可能是 `true/false/undefined`）。

#### 3.1.5 导出所有类型

确保所有 interface、type 使用 `export` 导出。

---

### 3.2 文件 `client/src/api/index.ts`

**职责**: fetch 请求封装、ApiError 类、BASE_URL 常量。

#### 3.2.1 `ApiError` 类

```typescript
export class ApiError extends Error {
  code: number;
  constructor(code: number, message: string) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
  }
}
```

- 继承 `Error`，设置 `name = 'ApiError'`
- `code` 属性存储业务错误码

#### 3.2.2 `BASE_URL` 常量

```typescript
export const BASE_URL: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```

#### 3.2.3 `baseFetch<T>` 函数

```typescript
export async function baseFetch<T>(path: string, options?: RequestInit): Promise<T>
```

**关键逻辑**：

1. 创建 `AbortController`，`setTimeout(() => controller.abort(), 15000)` 实现 15 秒超时
2. 调用 `fetch(BASE_URL + path, { ...options, signal: controller.signal, headers: { 'Content-Type': 'application/json', ...options?.headers } })`
3. **HTTP 状态码检查**：`!res.ok` → `throw new ApiError(res.status, `请求失败: ${res.statusText}`)`
4. **JSON 解析**：`const json: ApiResponse<T> = await res.json()`
5. **业务错误码检查**：`json.code !== 0` → `throw new ApiError(json.code, json.message)`
6. **成功**：`return json.data`
7. **错误处理（catch）**：
   - 已是 `ApiError` 实例 → 直接 `throw`
   - `error.name === 'AbortError'` → `throw new ApiError(ErrorCode.TIMEOUT, '请求超时，请稍后重试')`
   - 其他 → `throw new ApiError(ErrorCode.NETWORK_ERROR, '网络异常，请检查网络连接')`
8. **finally**：`clearTimeout(timeout)` 确保定时器被清除

**函数签名细节**：
- `<T>` 泛型，返回 `Promise<T>`（直接返回 `data` 字段，调用方不需要再 `.data`）
- `path` 必须以 `/` 开头（如 `/api/v1/funds/020741`）
- `options` 为可选参数，用于传递 method、body 等

---

### 3.3 文件 `client/src/api/funds.ts`

**职责**: 基金查询 API 函数。

#### 3.3.1 `fetchFund` 函数

```typescript
import { baseFetch } from './index';
import type { FundInfo } from '@/types/api';

export async function fetchFund(code: string): Promise<FundInfo> {
  return baseFetch<FundInfo>(`/api/v1/funds/${encodeURIComponent(code)}`);
}
```

- 调用 `baseFetch<FundInfo>` 发起 GET 请求
- 使用 `encodeURIComponent` 对基金代码编码（安全做法）

---

### 3.4 文件 `client/src/api/calculations.ts`

**职责**: 计算触发与结果查询 API 函数。

#### 3.4.1 `triggerCalculation` 函数

```typescript
import { baseFetch } from './index';
import type { Calculation } from '@/types/api';

interface TriggerResult {
  calculation_id: string;
  status: string;
}

export async function triggerCalculation(code: string): Promise<TriggerResult> {
  return baseFetch<TriggerResult>('/api/v1/calculations', {
    method: 'POST',
    body: JSON.stringify({ fund_code: code }),
  });
}
```

- POST 请求，body 为 JSON 字符串
- 返回 `{ calculation_id, status }`

#### 3.4.2 `getCalculation` 函数

```typescript
export async function getCalculation(id: string): Promise<Calculation> {
  return baseFetch<Calculation>(`/api/v1/calculations/${encodeURIComponent(id)}`);
}
```

---

### 3.5 文件 `client/src/stores/fund.ts`

**职责**: Pinia store，管理基金信息和计算结果的全局状态。

**使用 Composition API 风格**（`defineStore` + `setup` 函数），与项目已有的 `<script setup>` 风格保持一致。

#### 3.5.1 Store 结构

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { FundInfo, Calculation } from '@/types/api';
import { fetchFund } from '@/api/funds';
import { triggerCalculation, getCalculation } from '@/api/calculations';
import { ERROR_MESSAGES } from '@/locales/zh-CN';

export const useFundStore = defineStore('fund', () => {
  // ==== 状态 ====
  const fundInfo = ref<FundInfo | null>(null);
  const calculation = ref<Calculation | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // ==== 计算属性 ====
  const isBondFund = computed(() => {
    return fundInfo.value?.fund_type?.includes('债') ?? false;
  });

  const hasCalculation = computed(() => calculation.value !== null);

  // ==== 操作 ====
  // ...（见下方）
});
```

#### 3.5.2 `fetchFundInfo(code: string)` 操作

1. 设置 `loading.value = true`，清空 `error.value = null`
2. 调用 `fetchFund(code)`
3. 成功：`fundInfo.value = result`
4. 失败（catch）：
   - 如果 `err instanceof ApiError`：`error.value = err.message`
   - 否则：`error.value = ERROR_MESSAGES.UNKNOWN_ERROR`
5. finally：`loading.value = false`

**重要**：异常必须在 store 内部捕获，不能让异常传播到组件层（组件通过 `store.error` 获取错误信息）。

#### 3.5.3 `refreshCalculation(code: string)` 操作

**核心逻辑 — 触发计算 + 轮询结果**：

1. 设置 `loading.value = true`，清空 `error.value = null`
2. 调用 `triggerCalculation(code)`
   - 失败：设置 `error.value`，`return`
3. 获取 `calculation_id`，进入轮询循环：
   - **轮询间隔**：2 秒（每 2 秒调用一次 getCalculation）
   - **最大时长**：120 秒（60 次轮询）
   - 每次轮询：
     - 调用 `getCalculation(calculation_id)`
     - 如果 `status === 'completed'`：`calculation.value = result`，退出循环
     - 如果 `status === 'failed'`：`error.value = result.error_message || '计算失败'`，退出循环
     - 如果 `status === 'processing'`：继续等待
   - 超时（超过 120 秒）：`error.value = '计算超时，请稍后重试'`
4. finally：`loading.value = false`

**轮询实现建议**：使用 `while` 循环 + `await new Promise(r => setTimeout(r, 2000))` 实现等待。循环内检查 `Date.now()` 判断是否超时。

#### 3.5.4 `clearError()` 操作

```typescript
function clearError() {
  error.value = null;
}
```

#### 3.5.5 返回值

```typescript
return {
  fundInfo, calculation, loading, error,
  isBondFund, hasCalculation,
  fetchFundInfo, refreshCalculation, clearError,
};
```

---

### 3.6 文件 `client/src/utils/format.ts`

**职责**: 数值格式化工具函数。

#### 3.6.1 `formatPercent(value: number | null | undefined): string`

- `null` 或 `undefined` → 返回 `"N/A"`
- 否则 → 将小数值转为百分比字符串，如 `0.31` → `"0.31%"`，`-0.45` → `"-0.45%"`
- 实现：`` `${value}%` ``（后端返回的值已经是百分比数值，如 0.31 表示 0.31%，**不需要乘以 100**）

> **重要说明**：后端 ADR 和 Schema 定义的收益率字段（如 `seven_day_annual_yield`、`daily_change_pct`）存储的是百分比数值。例如七日年化 3.82% 存储为 `3.82` 或 `0.0382`。
> 根据后端 `CalculationResponse` 的字段注释和 PRD 展示模板，**假设后端返回的已是可直接展示的百分比数值**（即 `3.82` 表示 3.82%）。
> 如果实际数据为小数形式（`0.0382`），需乘以 100。**当前按直接拼接 `%` 实现**，联调时如不一致再调整。

#### 3.6.2 `formatNA(value: unknown): string`

- `null` 或 `undefined` → 返回 `"N/A"`
- 否则 → `String(value)`

```typescript
export function formatNA(value: unknown): string {
  if (value === null || value === undefined) return 'N/A';
  return String(value);
}
```

#### 3.6.3 `formatDate(date: string | null | undefined): string`

- `null` 或 `undefined` → 返回 `"N/A"`
- 否则 → 将 `"YYYY-MM-DD"` 格式转为 `"YYYY年M月D日"` 中文展示
- 实现建议：用 `Date` 解析 → `getFullYear()` / `getMonth() + 1` / `getDate()` 拼接

---

### 3.7 文件 `client/src/locales/zh-CN.ts`

**职责**: 所有中文界面文案的集中定义。每个常量对象单独导出。

#### 3.7.1 `ERROR_MESSAGES`

```typescript
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络异常，请检查网络连接',
  TIMEOUT: '请求超时，请稍后重试',
  FUND_NOT_FOUND: '基金代码不存在，请检查后重试',
  TYPE_MISMATCH: '该基金不是债券型基金，请输入债券基金代码',
  INVALID_CODE_FORMAT: '基金代码格式错误，请输入6位数字',
  CALCULATION_FAILED: '计算失败，请稍后重试',
  UNKNOWN_ERROR: '未知错误，请稍后重试',
  POLLING_TIMEOUT: '计算超时，请稍后重试',
} as const;
```

#### 3.7.2 `LABELS`

```typescript
export const LABELS = {
  PAGE_TITLE: '债券收益计算',
  FUND_CODE_PLACEHOLDER: '请输入6位基金代码',
  QUERY_BUTTON: '查询',
  REFRESH_BUTTON: '刷新计算',
  LOADING: '加载中...',
  CALCULATING: '计算中，请稍候...',
  NAV: '最新净值',
  DAILY_CHANGE: '日涨跌',
  SEVEN_DAY_YIELD: '七日年化',
  WANFEN_INCOME: '万份收益',
  ONE_MONTH_RETURN: '近1月收益',
  MAX_DRAWDOWN: '近3月最大回撤',
  TEN_YEAR_TREASURY: '10年期国债',
  CREDIT_SPREAD: '信用利差',
  DATA_DATE: '数据日期',
  NOT_TRADING_DAY: '非交易日',
  BOND_FUND: '债券型',
  NON_BOND_FUND: '非债券型',
  YUAN: '元',
  FUND_INFO: '基金信息',
  CALCULATION_RESULT: '计算结果',
} as const;
```

#### 3.7.3 `DISCLAIMER`

```typescript
export const DISCLAIMER = {
  TITLE: '免责声明',
  TEXT: '本工具计算结果仅供参考，不构成任何投资建议。基金过往业绩不代表未来表现，投资有风险，选择需谨慎。数据来源：天天基金、东方财富、中债信息网。',
} as const;
```

---

## 4. 代码规范要求

1. **TypeScript 严格模式**：所有函数必须有明确的参数类型和返回值类型，不使用 `any`
2. **不允许 `enum`**：使用 `const` 对象 + `as const` 代替（`tsconfig` 中 `erasableSyntaxOnly: true` 禁止运行时枚举）
3. **Vue 3 Composition API**：Store 使用 `defineStore` + `setup` 函数风格，不使用 Options API
4. **async/await**：异步操作使用 `async/await`，不使用 `.then()` 链式调用
5. **错误不传播**：Store 中的 API 调用必须 try/catch，不向组件抛出异常
6. **导入路径**：跨目录导入使用 `@/` 别名（如 `@/api/index`、`@/types/api`），同级文件使用相对路径
7. **命名规范**：
   - 接口/类型：PascalCase（`FundInfo`、`ApiResponse`）
   - 函数/变量：camelCase（`fetchFund`、`baseFetch`）
   - 常量：UPPER_SNAKE_CASE（`ERROR_MESSAGES`）
   - 文件名：kebab-case 或与导出主符号一致
8. **未使用变量**：`noUnusedLocals: true` 和 `noUnusedParameters: true`，代码中不能有任何未使用的导入或变量

## 5. 测试要求

代码必须能通过以下测试用例（详见 `test-cases.md`）：

| 用例 | 内容 | 对应模块 |
|------|------|---------|
| TC-001 ~ TC-005 | baseFetch 正常/异常/超时/网络错误 | api/index.ts |
| TC-006 ~ TC-008 | API 端点调用正确性 | api/funds.ts, api/calculations.ts |
| TC-009 ~ TC-010 | BASE_URL 默认值/环境变量 | api/index.ts |
| TC-011 ~ TC-014 | TypeScript 类型编译检查 | types/api.ts |
| TC-015 ~ TC-025 | Store 状态/操作/计算属性 | stores/fund.ts |
| TC-026 ~ TC-036 | 格式化函数正常值/边界/异常 | utils/format.ts |
| TC-037 | 文案常量完整性 | locales/zh-CN.ts |
| TC-038 ~ TC-040 | 端到端集成调用链 | 跨模块 |

## 6. 注意事项

1. **`erasableSyntaxOnly` 是关键约束**：在 TypeScript 6.0 + `erasableSyntaxOnly: true` 下，`enum` 关键字会编译报错。必须使用 `const ErrorCode = { ... } as const` 代替。也不能使用 `import type` 与值的混合导入（已有单独 `import type` 语句没问题）。

2. **轮询终止条件**：`refreshCalculation` 的轮询循环必须同时检查三个退出条件：
   - 状态变为 `completed`（成功退出）
   - 状态变为 `failed`（失败退出）
   - 超过 120 秒（超时退出）
   缺少任何一个都会导致无限循环。

3. **AbortController 清理**：`baseFetch` 中的 `setTimeout` 必须在 finally 中 `clearTimeout`，否则超时定时器会泄漏。

4. **Pinia store 的 `loading` 状态**：在 `finally` 块中设置 `loading = false`，确保无论成功还是失败 loading 都会被重置。但如果 loading 的语义是"有请求在进行中"，注意 `refreshCalculation` 中 `fetchFundInfo` 内部也设置了 loading，两者不会同时调用，互不影响。

5. **formatPercent 的数值精度**：后端返回的收益率值可能有精度差异（如 `0.31` 或 `3.82`）。当前实现直接拼接 `%`，不做乘除。联调时如发现后端返回的是小数（`0.0382` 表示 3.82%），需在 formatPercent 中乘以 100。

6. **类型文件不可有副作用**：`types/api.ts` 仅包含 `interface` 和 `const` 类型声明，不包含任何运行时可执行代码（除了 `ErrorCode` 常量对象）。

7. **删除 .gitkeep 占位文件**：当在 `api/`、`stores/`、`types/`、`utils/`、`locales/` 目录中创建实际文件后，删除对应的 `.gitkeep` 占位文件。
