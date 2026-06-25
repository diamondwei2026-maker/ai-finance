# Coding Prompt — Task 3.2: 基金输入页与组件

### 1. 任务目标

实现基金输入页（`FundInput.vue`）及其子组件：搜索栏（`SearchBar.vue`）、基金预览卡片（`FundPreview.vue`）和全局免责声明横幅（`DisclaimerBar.vue`）。页面负责接收用户输入、调用 API 查询基金信息、展示确认预览。

### 2. 技术上下文

- **语言/框架**: Vue 3 Composition API `<script setup lang="ts">` + TypeScript
- **涉及文件**:
  - (新建) `src/components/SearchBar.vue` — 基金代码输入搜索栏
  - (新建) `src/components/FundPreview.vue` — 基金预览卡片
  - (新建) `src/components/DisclaimerBar.vue` — 免责声明横幅
  - (修改) `src/pages/FundInput.vue` — 页面主组件（替换当前 stub）
- **已有依赖（Task 3.1 产出）**:
  - `src/api/index.ts` — `baseFetch()`, `ApiError` 类
  - `src/api/funds.ts` — `fetchFund()`
  - `src/stores/fund.ts` — `useFundStore()` 含 `fetchFundInfo`, `loading`, `error`, `fundInfo`, `isBondFund`, `clearError`
  - `src/types/api.ts` — `FundInfo` 接口, `ErrorCode` 常量
  - `src/locales/zh-CN.ts` — `ERROR_MESSAGES`, `LABELS`, `DISCLAIMER`
  - `src/router/index.ts` — 路由: `/` → FundInput, `/fund/:code` → FundResult
  - `src/utils/format.ts` — `formatPercent()`, `formatNA()`, `formatDate()`
  - `src/App.vue` — `<RouterView>` 已配置 `min-h-screen bg-gray-50`

### 3. 实现要求

#### 3.1 文件 `src/components/SearchBar.vue`（新建）

- **Props**:
  - `loading: boolean` — 加载状态（默认 false）

- **Emits**:
  - `search(code: string): void` — 用户输入 6 位有效代码后触发

- **模板结构**（Tailwind CSS）:
  ```
  <div> 容器
    <label for="fund-code-input"> 基金代码（屏幕阅读器可用）
    <input id="fund-code-input" type="text" inputmode="numeric" maxlength="6"
           placeholder="请输入6位基金代码" />
    <span role="alert" v-if="本地校验错误"> 请输入 6 位基金代码
    <button :disabled="loading">
      <span v-if="loading"> spinner（SVG 动画或 CSS animate-spin）
      <span v-else> 查询
  ```

- **关键逻辑**:
  1. **数字过滤**: 监听 `@input`，用正则 `/\D/g` 过滤非数字字符后重新赋值 `inputValue`
  2. **300ms 防抖**: 维护一个 `debounceTimer: ReturnType<typeof setTimeout> | null`，`@input` 时清除旧 timer、新建 300ms timer。timer 回调内执行本地校验 + emit
  3. **按钮立即触发**: 点击查询按钮 → 先清除防抖 timer → 立即执行校验 → emit
  4. **Enter 键**: `@keyup.enter` → 同按钮逻辑
  5. **本地校验**: 调用 `isValidCode(code)` 函数，检查 `code.length === 6 && /^\d{6}$/.test(code)`；不通过则设置 `localError` 为 `"请输入 6 位基金代码"`，**不 emit**
  6. **Loading 态**: `loading=true` 时按钮 `disabled`，Enter 键不触发；`loading=false` 时恢复正常
  7. **错误清除**: 输入框内容变化时清除 `localError`

- **代码风格**:
  - 使用 `ref<string>` 管理 `inputValue`
  - 使用 `ref<string | null>` 管理 `localError`
  - `watch` inputValue 变化时清除 localError（可选，简单方案：在 onInput 中同时清除）

#### 3.2 文件 `src/components/FundPreview.vue`（新建）

- **Props**:
  - `fundInfo: FundInfo | null` — 基金信息（null 时不渲染）

- **Emits**:
  - `confirm(code: string): void` — 用户确认基金

- **模板结构**（Tailwind CSS）:
  ```
  <div v-if="fundInfo" class="卡片容器（bg-white rounded-xl shadow-sm p-6）">
    <!-- 正常样式：灰色边框；警告样式：橙色边框 + 橙色背景 -->
    <section>
      基金名称 fundInfo.name（text-lg font-semibold）
      基金代码 fundInfo.fund_code（text-sm text-gray-500）
      基金类型 fundInfo.fund_type（带标签样式 pill badge）
      最新净值 fundInfo.nav | formatNA（带"元"单位）
      七日年化 fundInfo.seven_day_annual_yield | 格式化为百分比
    </section>

    <!-- 非债券型警告 -->
    <div v-if="非债券型" class="bg-amber-50 border border-amber-400 text-amber-800 rounded-lg p-3">
      ⚠️ 该基金不是债券型基金，请输入债券基金代码
    </div>

    <button @click="onConfirm" class="w-full bg-blue-600 text-white rounded-lg py-2">
      确认并查看详情 →
    </button>
  </div>
  ```

- **关键逻辑**:
  1. `v-if="fundInfo"` — prop 为 null 时不渲染任何 DOM
  2. 非债券型判断：`fundInfo.fund_type` 不含"债"字，即 `!fundInfo.fund_type.includes('债')`
  3. 此时卡片整体使用橙色警告样式：`border-amber-400 bg-amber-50`
  4. nav / seven_day_annual_yield 为 null 时显示 `"--"` 或 `"暂无数据"`（使用 `formatNA` 函数）
  5. `onConfirm()` 函数中 emit `('confirm', fundInfo.fund_code)`

#### 3.3 文件 `src/components/DisclaimerBar.vue`（新建）

- **Props**: 无
- **Emits**: 无

- **模板结构**（Tailwind CSS）:
  ```
  <footer class="fixed bottom-0 left-0 right-0 z-10
                  bg-gray-100/90 backdrop-blur-sm
                  border-t border-gray-200
                  px-4 py-3 text-center">
    <p class="text-xs text-gray-500 leading-relaxed max-w-2xl mx-auto">
      本工具提供的收益数据基于公开数据计算，仅供参考，不构成投资建议。投资有风险，操作需谨慎。
    </p>
  </footer>
  ```

- **关键逻辑**:
  1. `position: fixed; bottom: 0` 固定在视口底部
  2. 半透明背景 `bg-gray-100/90` + `backdrop-blur-sm`（毛玻璃效果）
  3. 文字小号、灰色、居中、最大宽度约束
  4. **重要**: 此组件是全局复用组件，在 `App.vue` 或页面中引入时，需确保页面主体有 `pb-16`（约 64px）的 padding-bottom，避免底部内容被 DisclaimerBar 遮挡

#### 3.4 文件 `src/pages/FundInput.vue`（修改，替换当前 stub）

- **职责**: 组装 SearchBar + FundPreview + DisclaimerBar，管理查询流程和路由跳转

- **模板结构**（Tailwind CSS）:
  ```
  <div class="max-w-2xl mx-auto px-4 py-8 pb-20">
    <!-- 页面标题 -->
    <h1 class="text-2xl font-bold text-center mb-2">债券收益计算</h1>
    <p class="text-gray-500 text-center mb-6">输入基金代码，一键获取收益数据</p>

    <!-- 搜索栏 -->
    <SearchBar :loading="store.loading" @search="onSearch" />

    <!-- 全局错误提示（API 返回的业务错误，如 40001/40002/40003） -->
    <div v-if="store.error"
         role="alert"
         class="bg-red-50 border border-red-300 text-red-700 rounded-lg p-4 mt-4">
      {{ store.error }}
    </div>

    <!-- 基金预览卡片（查询成功后展示） -->
    <FundPreview :fund-info="store.fundInfo" @confirm="onConfirm" />

    <!-- 免责声明 -->
    <DisclaimerBar />
  </div>
  ```

- **关键逻辑**:
  1. `onSearch(code: string)`: 调用 `store.fetchFundInfo(code)`，触发 API 查询
     - 调用前可先 `store.clearError()` 清空旧错误
  2. `onConfirm(code: string)`: `router.push({ name: 'FundResult', params: { code } })`
  3. **Store 已处理三种错误码的文案映射**（见 `src/stores/fund.ts` 中的 ApiError → message 和 `src/locales/zh-CN.ts` 中的 `ERROR_MESSAGES`），页面只需展示 `store.error`：
     - `40001` → `"基金代码不存在，请检查后重试"`
     - `40002` → `"该基金不是债券型基金，请输入债券基金代码"`
     - `40003` → `"基金代码格式错误，请输入6位数字"`
  4. 页面底部 `pb-20` 确保 DisclaimerBar 不遮挡内容

### 4. 代码规范要求

- 使用 `<script setup lang="ts">` 语法，**不使用** Options API
- 使用 `defineProps<T>()` 类型化 Props 声明（Vue 3.3+）
- 使用 `defineEmits<T>()` 类型化 Emits 声明
- 所有样式使用 Tailwind CSS utility class，**不写** `<style scoped>` 块
- 遵循已有的命名约定：文件名 PascalCase，ref 变量 camelCase
- TypeScript 严格模式 (`strict: true`)，禁止 `any`
- 不引入额外依赖（Vue 3 + Tailwind 已有工具足够）
- 使用现有文案常量（`src/locales/zh-CN.ts` 中的 `ERROR_MESSAGES`、`LABELS`、`DISCLAIMER`），不在组件中硬编码文案

### 5. 测试要求

代码需能通过以下关键测试用例（完整清单见 `test-cases.md`）：

**SearchBar（TC-001 ~ TC-010）**:
- TC-001: 输入 6 位数字 → 300ms 后 emit search 事件
- TC-002: 点击查询按钮 → 立即触发（跳过防抖）
- TC-003: Enter 键 → 立即触发
- TC-004: 输入非数字字符 → 被过滤
- TC-005: 输入超过 6 位 → maxlength 截断
- TC-006/007: 不足 6 位 → 显示"请输入 6 位基金代码"，不 emit
- TC-008/009: loading 状态 → 按钮禁用 + spinner / 恢复正常
- TC-010: `<label for>` 与 `<input id>` 正确关联

**FundPreview（TC-011 ~ TC-016）**:
- TC-011: 正常基金信息完整展示
- TC-012: nav / yield 为 null → 显示占位符，不崩溃
- TC-013: 债券型基金 → 默认样式，无警告
- TC-014: 非债券型基金 → 橙色警告样式
- TC-015: 点击确认 → emit confirm 事件
- TC-016: fundInfo=null → 不渲染 DOM

**FundInput + DisclaimerBar（TC-017 ~ TC-030）**:
- TC-017: 页面完整布局（标题 + SearchBar + 居中 + DisclaimerBar）
- TC-018: 查询成功 → 展示 FundPreview
- TC-019~021: 三种错误码正确展示 error 文本，`role="alert"`
- TC-022: 确认 → 跳转到 `/fund/:code`
- TC-023: 300ms 防抖验证（快速输入只触发 1 次查询）
- TC-024: 本地校验 → 不调用 API
- TC-025: 新输入 → 清除旧 error
- TC-026: DisclaimerBar 固定底部
- TC-027: 免责文案完整
- TC-028: 底部有足够 padding 不被遮挡
- TC-029~030: 网络异常 / 超时错误处理

### 6. 注意事项

1. **防抖实现**: 使用 `setTimeout` / `clearTimeout` 实现，**不引入** lodash debounce。timer ref 在 `onUnmounted` 中清除
2. **Loading 按钮禁用时机**: SearchBar 的 `loading` prop 绑定 `store.loading`，但需注意：在 `@search` emit 后、`store.loading` 变为 true 之前有一个微任务间隙，按钮不会立即禁用。为提升体验，可在 `onSearch` 中先设置一个本地 loading 标记，或接受这个微小延迟
3. **FundPreview 警告样式**: 使用 `bg-amber-50 border border-amber-400 text-amber-800` 作为非债券型警告样式。正常状态使用 `bg-white border border-gray-200`
4. **错误消息 vs 本地校验**: 本地校验（位数不足）由 SearchBar 内部处理，不经过 store；业务错误（40001/40002/40003）由 store.error 处理，FundInput 展示。两者互不干扰
5. **DisclaimerBar 复用**: 后续 FundResult 页面也需要此组件，确保它是独立的、可复用的。不从页面传 props，所有文案自包含
6. **Tailwind 响应式**: 输入页使用 `max-w-2xl mx-auto` 居中约束宽度，小屏时使用 `px-4` 水平 padding
7. **不要引入新依赖**: 使用已有的 Vue 3、Pinia、Vue Router、Tailwind CSS 能力，不安装任何新 npm 包
8. **现有代码风格**: 观察已有的 `src/api/index.ts`、`src/stores/fund.ts` 等文件——使用 JSDoc 注释函数、const 优先、箭头函数。保持一致
