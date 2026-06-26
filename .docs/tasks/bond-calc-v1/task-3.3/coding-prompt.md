# Coding Prompt — Task 3.3: 计算结果页与组件

> 生成日期：2025-06-26 | 基于 ADR client.md v1.0

---

## 1. 任务目标

实现计算结果展示页 `FundResult.vue` 及其 5 个子组件：`ResultHeader.vue`、`NavGrid.vue`、`YieldMetrics.vue`、`MarketRates.vue`、`RefreshButton.vue`。页面展示完整的 8 项收益指标计算结果，布局与 PRD 结果模板一致。

---

## 2. 技术上下文

- **语言/框架**: Vue 3 (Composition API + `<script setup>` + TypeScript)、Tailwind CSS、Pinia、Vue Router 4 (hash 模式)
- **涉及文件**:

| 操作 | 路径 | 说明 |
|------|------|------|
| ✏️ 重写 | `client/src/pages/FundResult.vue` | 已有骨架占位，需重写完整页面逻辑 |
| ✨ 新建 | `client/src/components/ResultHeader.vue` | 结果头部：基金名称 + 代码 + 数据日期 |
| ✨ 新建 | `client/src/components/NavGrid.vue` | 净值网格：最新净值 + 日涨跌幅 |
| ✨ 新建 | `client/src/components/YieldMetrics.vue` | 收益指标卡片：4 项 2×2 网格 |
| ✨ 新建 | `client/src/components/MarketRates.vue` | 市场利率卡片：2 项横排 |
| ✨ 新建 | `client/src/components/RefreshButton.vue` | 刷新计算按钮（含 loading/spinner 状态） |

- **已有依赖（直接使用，不修改）**:
  - `client/src/stores/fund.ts` — `useFundStore`（提供 `fundInfo`、`calculation`、`loading`、`error`、`refreshCalculation(code)`、`clearError()`）
  - `client/src/types/api.ts` — `Calculation`、`FundInfo` 类型
  - `client/src/utils/format.ts` — `formatPercent()`、`formatNA()`、`formatDate()`
  - `client/src/locales/zh-CN.ts` — `LABELS`、`ERROR_MESSAGES`、`DISCLAIMER`
  - `client/src/components/DisclaimerBar.vue` — 复用（import 即用，无需修改）
  - `client/src/router/index.ts` — 路由 `/fund/:code` → `FundResult` 已配置

---

## 3. 实现要求

### 3.1 文件 `client/src/pages/FundResult.vue` — ✏️ 重写

**职责**：计算结果页主组件，负责编排子组件、管理数据获取生命周期、处理加载/错误/结果三种状态。

**关键逻辑**：

1. **路由参数读取**：
   - 从 `route.params.code` 获取基金代码（类型 `string`）
   - 从 `route.query.refresh` 判断是否需要重新计算

2. **生命周期**：
   - `onMounted` 中：
     - 如果 `route.query.refresh === '1'` → 无条件调用 `store.refreshCalculation(code)`
     - 否则 → 如果 `store.calculation === null` → 调用 `store.refreshCalculation(code)`
     - （即：无可计算结果时自动触发，有结果但 query 要求刷新时也触发）

3. **三态渲染**（使用 `v-if` / `v-else-if` / `v-else` 或计算属性驱动）：

   - **加载态** (`store.loading === true` 且 `store.calculation === null`)：
     - 显示骨架屏（Skeleton），而非空白
     - 骨架屏包含 3 个占位区域，使用 `animate-pulse` + `bg-gray-200` + `rounded` 模拟：
       - 顶部一行（模拟 ResultHeader，高 `h-6` 宽 `w-3/4`）
       - 中间区域（模拟 NavGrid + YieldMetrics，`h-32` 宽 `w-full`）
       - 底部区域（模拟 MarketRates，`h-20` 宽 `w-full`）

   - **错误态** (`store.error !== null`)：
     - 显示红色错误提示卡片（`bg-red-50 border border-red-300 text-red-700 rounded-lg p-4`）
     - `role="alert"` 属性用于屏幕阅读器
     - 显示 `store.error` 文案
     - 显示"重试"按钮：点击 → `store.clearError()` → `store.refreshCalculation(code)`

   - **结果态** (`store.calculation?.status === 'completed'`)：
     - 按以下顺序渲染子组件：
       1. `ResultHeader`（传入 `calculation`、`fundInfo`）
       2. `NavGrid`（传入 `calculation.nav`、`calculation.daily_change_pct`）
       3. `YieldMetrics`（传入 4 项收益指标）
       4. `MarketRates`（传入 `ten_year_treasury`、`credit_spread_aa_plus`）
       5. `RefreshButton`（传入 `code`、`loading`）
     - 底部渲染 `DisclaimerBar`

4. **容器样式**：
   - `class="max-w-lg mx-auto px-4 py-6 pb-20"`（`pb-20` 确保底部不被固定 DisclaimerBar 遮挡）

---

### 3.2 文件 `client/src/components/ResultHeader.vue` — ✨ 新建

**Props**：
```typescript
interface Props {
  fundName?: string | null;
  fundCode?: string;
  dataDate?: string | null;
  isTradingDay?: boolean;
}
```

**职责**：展示基金名称、代码、数据日期及非交易日提示。

**渲染规则**：

1. **基金名称**：`props.fundName ?? 'N/A'`
   - 使用 `text-xl font-bold text-gray-900` 展示

2. **基金代码**：`props.fundCode ?? 'N/A'`
   - 使用 `text-sm text-gray-500` 展示在名称旁边/下方

3. **数据日期**：
   - 使用 `<time>` 语义标签，`datetime` 属性为原始 ISO 日期字符串
   - 格式：`formatDate(props.dataDate)` → 如 `"2025年6月24日"`
   - 如果 `props.dataDate` 为 null/undefined → 显示 `"N/A"`
   - 前缀文案：`"昨日净值 "`（拼接在日期前）

4. **非交易日标注**：
   - 仅在 `props.isTradingDay === false` 时渲染
   - 显示：`"非交易日，数据可能有延迟"`
   - 样式：`text-amber-600 text-xs mt-1`（黄色警告色）

---

### 3.3 文件 `client/src/components/NavGrid.vue` — ✨ 新建

**Props**：
```typescript
interface Props {
  nav?: number | null;
  dailyChangePct?: number | null;
}
```

**职责**：净值网格展示，含净值（4 位小数）和日涨跌（带正负号颜色）。

**渲染规则**：

1. **布局**：两列网格 `grid grid-cols-2 gap-4`，每列一个指标卡片（`bg-gray-50 rounded-lg p-4`）

2. **左列 — 最新净值**：
   - 标签：`LABELS.NAV`（"最新净值"），`text-xs text-gray-500`
   - 数值：
     - 有值 → `props.nav!.toFixed(4)`（保留 4 位小数）
     - null → `"N/A"`
   - 数值样式：`text-2xl font-semibold text-gray-900`

3. **右列 — 日涨跌幅**：
   - 标签：`LABELS.DAILY_CHANGE`（"日涨跌"），`text-xs text-gray-500`
   - 数值（颜色规则）：
     - null → `"N/A"`，灰色
     - `> 0` → `"+0.15%"`（使用 `formatPercent` 并加 `+` 前缀），`text-green-600`
     - `< 0` → `"-0.08%"`（使用 `formatPercent`，自带 `-`），`text-red-600`
     - `=== 0` → `"0%"`，`text-gray-600`
   - 数值样式：`text-2xl font-semibold`

---

### 3.4 文件 `client/src/components/YieldMetrics.vue` — ✨ 新建

**Props**：
```typescript
interface Props {
  sevenDayYield?: number | null;
  wanfenIncome?: number | null;
  oneMonthReturn?: number | null;
  threeMonthMaxDrawdown?: number | null;
}
```

**职责**：展示 4 项收益指标，形成 2×2 网格卡片。

**4 项指标定义**（每项为 `{ emoji, label, value, unit, isPercent }` 结构）：

| 位置 | emoji | label 来源 | value 来源 | unit | isPercent |
|------|-------|-----------|-----------|------|-----------|
| 左上 | 📈 | `LABELS.SEVEN_DAY_YIELD` | `sevenDayYield` | 无（`formatPercent` 自带 %） | true |
| 右上 | 💵 | `LABELS.WANFEN_INCOME` | `wanfenIncome` | `LABELS.YUAN`（"元"） | false |
| 左下 | 📉 | `LABELS.ONE_MONTH_RETURN` | `oneMonthReturn` | 无（`formatPercent` 自带 %） | true |
| 右下 | ⚠️ | `LABELS.MAX_DRAWDOWN` | `threeMonthMaxDrawdown` | 无（`formatPercent` 自带 %） | true |

**渲染规则**：
1. **布局**：`grid grid-cols-2 gap-3`（2×2 网格）
2. **每个卡片**：`bg-gray-50 rounded-lg p-4 flex flex-col items-center text-center`
3. **emoji**：`text-2xl mb-1`
4. **标签**：`text-xs text-gray-500`
5. **数值**：
   - 非 null → `isPercent ? formatPercent(value) : value + unit`
   - null → `"N/A"`
   - 样式：`text-xl font-semibold text-gray-900 mt-1`

---

### 3.5 文件 `client/src/components/MarketRates.vue` — ✨ 新建

**Props**：
```typescript
interface Props {
  tenYearTreasury?: number | null;
  creditSpreadAaPlus?: number | null;
}
```

**职责**：展示当前市场利率数据。

**渲染规则**：

1. **标题行**：📡 emoji + `"当前市场"`，`text-sm font-medium text-gray-700 mb-3`

2. **指标横排**：`flex gap-4`（或 `flex justify-between`），两块并排

3. **左块 — 10年期国债**：
   - 标签：`LABELS.TEN_YEAR_TREASURY`（"10年期国债"）
   - 数值：`formatPercent(props.tenYearTreasury)`
   - null → `"N/A"`

4. **右块 — 信用利差**：
   - 标签：`LABELS.CREDIT_SPREAD`（"信用利差"）
   - 数值：非 null → `${props.creditSpreadAaPlus}bp`，null → `"N/A"`

5. **整块容器**：`bg-blue-50 rounded-lg p-4`

---

### 3.6 文件 `client/src/components/RefreshButton.vue` — ✨ 新建

**Emits**：`defineEmits<{ refresh: [] }>()`

**Props**：
```typescript
interface Props {
  loading?: boolean;
}
```

**职责**：刷新计算按钮，支持正常/loading 两种状态。

**渲染规则**：

1. **正常态** (`loading === false`)：
   - 按钮可点击
   - 文案：`LABELS.REFRESH_BUTTON`（"刷新计算"）
   - 样式：`bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors w-full`

2. **Loading 态** (`loading === true`)：
   - 按钮 `disabled`
   - 文案：`"计算中…"`
   - 左侧显示旋转 spinner：
     ```html
     <svg class="animate-spin h-5 w-5 mr-2 inline" viewBox="0 0 24 24" fill="none">
       <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
       <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
     </svg>
     ```
   - 样式叠加：`opacity-50 cursor-not-allowed`

3. **点击事件**：`@click="$emit('refresh')"`

---

## 4. 代码规范要求

1. **Composition API + `<script setup lang="ts">`**：所有组件使用 `<script setup lang="ts">` + TypeScript
2. **Props 类型**：使用 `defineProps<Props>()` 语法（非运行时声明）
3. **Tailwind CSS**：所有样式使用 Tailwind utility class，不写 `<style scoped>`（除非必要）
4. **文案常量**：所有面向用户的中文文案引用自 `@/locales/zh-CN`，不写硬编码字符串
5. **格式化工具**：数值展示统一使用 `@/utils/format` 中的 `formatPercent`、`formatNA`、`formatDate`
6. **空值安全**：所有 `Calculation` 字段均可为 `null`，渲染时必须有 `?? 'N/A'` 或 `formatNA()` 兜底
7. **语义 HTML**：日期使用 `<time>` 标签，错误提示使用 `role="alert"`
8. **代码风格**：与已有代码（`FundInput.vue`、`FundPreview.vue`）风格一致——JSDoc 注释 ＋ 清晰的分段

---

## 5. 测试要求

代码必须能通过以下测试用例（详见 `.docs/tasks/bond-calc-v1/task-3.3/test-cases.md`）：

| 编号 | 描述 | 涉及组件 |
|------|------|----------|
| TC-001 | 进入页面自动触发计算 | FundResult |
| TC-002 | `?refresh=1` 重新触发计算 | FundResult |
| TC-003 | 加载中显示骨架屏 | FundResult |
| TC-004 | 计算完成后展示完整结果 | FundResult（集成） |
| TC-005 | 错误状态展示错误提示 + 重试按钮 | FundResult |
| TC-006 | 直接 URL 访问（无 fundInfo） | FundResult |
| TC-007 | 展示基金名称、代码、数据日期 | ResultHeader |
| TC-008 | 非交易日标注 | ResultHeader |
| TC-009 | 交易日无警告 | ResultHeader |
| TC-010 | 日期为 null 时显示 N/A | ResultHeader |
| TC-011 | 正常展示净值 4 位小数 + 日涨跌颜色 | NavGrid |
| TC-012 | 正涨跌幅绿色 | NavGrid |
| TC-013 | 负涨跌幅红色 | NavGrid |
| TC-014 | 涨跌幅为 0 中性色 | NavGrid |
| TC-015 | 净值为 null → N/A | NavGrid |
| TC-016 | 涨跌幅为 null → N/A | NavGrid |
| TC-017 | 4 项指标 2×2 网格布局 | YieldMetrics |
| TC-018 | 全部值为 null → 均 N/A | YieldMetrics |
| TC-019 | 部分有值部分 null | YieldMetrics |
| TC-020 | formatPercent 正确应用于百分比字段 | YieldMetrics |
| TC-021 | 2 项指标横排布局 | MarketRates |
| TC-022 | 两项均为 null → 均 N/A | MarketRates |
| TC-023 | % 和 bp 单位正确 | MarketRates |
| TC-024 | 点击触发刷新计算 | RefreshButton |
| TC-025 | Loading 态 disabled + spinner + "计算中…" | RefreshButton |
| TC-026 | 空闲态可点击 + 无 spinner | RefreshButton |
| TC-027 | 所有组件包含 DisclaimerBar | FundResult（集成） |
| TC-028 | 结果展示布局与 PRD 模板一致 | FundResult（集成） |
| TC-029 | 轮询超时处理 | FundResult |
| TC-030 | 服务端返回 failed 状态 | FundResult |

---

## 6. 注意事项

1. **Store 已有 `refreshCalculation` 方法**：该方法内部已处理触发计算 → 轮询 → 状态更新的完整流程（含超时处理），组件层只需调用 `store.refreshCalculation(code)`，无需自己实现轮询逻辑。

2. **`formatPercent` 签名**：`formatPercent(value: number | null | undefined): string` — 直接返回 `"0.31%"` 这样的字符串（含 `%` 后缀），不需要再手动加 `%`。

3. **`formatDate` 返回中文格式**：如 `"2025年6月24日"`，需要 `datetime` 属性时请用原始 `data_date` 字符串。

4. **Skeleton 骨架屏**：只需在 FundResult 中写 3 个 `div` 占位块，不需要抽取为独立组件。使用 Tailwind 的 `animate-pulse` + `bg-gray-200` + `rounded`。

5. **DisclaimerBar 复用**：直接 `import DisclaimerBar from '@/components/DisclaimerBar.vue'` 并在模板中使用，无需传 props。

6. **NAV 网格**：PRD 模板中 NavGrid 介于 ResultHeader 和 YieldMetrics 之间展示。

7. **页面最大宽度**：与 FundInput.vue 保持一致使用 `max-w-lg`（`max-width: 32rem`），居中 `mx-auto`。

8. **`v-if` 三态切换**：使用 `store.loading`、`store.error`、`store.calculation` 三个状态驱动条件渲染，确保同时刻只渲染一种状态。
