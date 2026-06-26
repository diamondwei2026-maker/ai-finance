# Coding Prompt — Task 4.3: 前后端联调与异常处理

> 生成日期：2025-06-26 | 基于 25 个测试用例

---

## 1. 任务目标

前端接入真实后端 API，补齐缺失的错误处理和交互细节，完成移动端基础适配验证，确保完整用户流程（输入 → 查询 → 计算 → 展示）可正常运行。

**关键前提**：前端组件、Store、API 层已在 Task 3.1-3.3 中基本完成，后端已在 Task 4.1-4.2 部署到 Render。本轮主要是 **查漏补缺**，而非从零搭建。

---

## 2. 技术上下文

- **语言/框架**: Vue 3 + TypeScript + Vite + Tailwind CSS + Pinia + Vue Router 4 (hash 模式)
- **后端 API**: FastAPI，已部署至 Render (`https://bond-calc-api.onrender.com`)
- **前端部署**: Vercel
- **涉及文件**:
  - (新建) `client/src/components/ErrorAlert.vue` — 可复用的错误提示 + 重试组件
  - (修改) `client/src/pages/FundInput.vue` — 错误状态增加重试按钮
  - (修改) `client/src/pages/FundResult.vue` — 替换为 ErrorAlert 组件
  - (修改) `client/src/components/FundPreview.vue` — 非债券型基金禁止确认
  - (修改) `client/index.html` — 修复 lang 和 title
  - (修改) `client/src/components/NavGrid.vue` — 移动端字体微调
  - (修改) `client/src/components/YieldMetrics.vue` — 移动端字体微调
- **外部依赖**: 后端 API `https://bond-calc-api.onrender.com`

---

## 3. 现状分析

| 模块 | 已是 ✅ / 待补 🔧 | 说明 |
|------|-------------------|------|
| API 封装层 | ✅ | baseFetch 超时 + ApiError 已实现 |
| Pinia Store | ✅ | fetchFundInfo / refreshCalculation + 轮询已实现 |
| SearchBar | ✅ | 输入校验、loading spinner、disabled 已实现 |
| RefreshButton | ✅ | loading spinner + disabled 已实现 |
| FundPreview | 🔧 | 非债券型基金弹警告但仍可点「确认」— 应禁止 |
| FundInput 错误态 | 🔧 | 展示错误信息但无重试按钮 — 需补充 |
| FundResult 错误态 | ✅ | 已有重试按钮，但代码与 FundInput 重复 |
| 骨架屏 | ✅ | FundResult 已实现 |
| N/A 展示 | ✅ | 所有组件 formatPercent/formatNA 已处理 null |
| 免责声明 | ✅ | DisclaimerBar 固定底部，两页均有 |
| 移动端适配 | 🔧 | 需微调 font-size 确保 375px 可读 |
| index.html | 🔧 | `lang="en"` → `"zh-CN"`，title 需改 |
| Router hash 模式 | ✅ | 已配置，Vercel rewrites 已就绪 |
| 后端 CORS | ✅ | allow_origins 已配置 |
| 生产环境变量 | ✅ | .env.production 指向 Render |

---

## 4. 实现要求

### 4.1 新建 `client/src/components/ErrorAlert.vue`

**职责**：可复用的错误提示组件，展示错误信息和重试按钮。

**接口定义**：
```typescript
// Props
interface ErrorAlertProps {
  /** 错误消息文本。 */
  message: string;
  /** 重试按钮文字，默认 "重试"。 */
  retryLabel?: string;
}

// Emits
interface ErrorAlertEmits {
  /** 用户点击重试时触发。 */
  (e: 'retry'): void;
}
```

**设计要求**：
- 红色/浅红配色（`bg-red-50 border-red-300 text-red-700`）
- `role="alert"` 无障碍标注
- 错误消息在上，重试按钮在下（`bg-red-600 text-white` 按钮）
- 按钮 hover/active 有颜色过渡
- 在 375px 宽度下不会横向溢出

**关键代码骨架**：
```vue
<script setup lang="ts">
interface Props {
  message: string;
  retryLabel?: string;
}
const props = withDefaults(defineProps<Props>(), {
  retryLabel: '重试',
});

const emit = defineEmits<{ retry: [] }>();
</script>

<template>
  <div role="alert" class="bg-red-50 border border-red-300 text-red-700 rounded-lg p-4 text-sm">
    <p class="mb-3">{{ message }}</p>
    <button
      class="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium
             hover:bg-red-700 active:bg-red-800 transition-colors"
      @click="emit('retry')"
    >
      {{ retryLabel }}
    </button>
  </div>
</template>
```

---

### 4.2 修改 `client/src/pages/FundInput.vue`

**修改内容**：

1. **引入 ErrorAlert 组件**：替换当前的内联错误 `<div>` 块
2. **新增 `onRetry` 方法**：清空错误后重新查询（使用上次输入的基金代码）
3. **保存上次输入的代码**：用 `ref` 记录最后一次搜索的基金代码，供重试使用

**具体改动**：

```typescript
// 在 <script setup> 中新增：
import ErrorAlert from '@/components/ErrorAlert.vue';

/** 记录最后一次搜索的基金代码，供重试使用。 */
const lastCode = ref<string | null>(null);

/** 处理基金代码搜索。 */
async function onSearch(code: string): Promise<void> {
  lastCode.value = code;
  await store.fetchFundInfo(code);
}

/** 重试：使用上次输入的代码重新查询。 */
function onRetry(): void {
  store.clearError();
  if (lastCode.value) {
    store.fetchFundInfo(lastCode.value);
  }
}
```

```html
<!-- 替换旧的内联错误 div 为： -->
<ErrorAlert
  v-if="store.error"
  :message="store.error"
  @retry="onRetry"
/>
```

---

### 4.3 修改 `client/src/pages/FundResult.vue`

**修改内容**：

1. **引入 ErrorAlert 组件**：替换当前内联的错误 + 重试 `<div>` 块
2. **代码清理**：删除重复的 `onRetry` 逻辑中的冗余

**具体改动**：

```typescript
// 在 <script setup> 中新增：
import ErrorAlert from '@/components/ErrorAlert.vue';
```

```html
<!-- 替换旧的内联错误 div（含重试按钮的那段）为： -->
<ErrorAlert
  v-if="store.error"
  :message="store.error"
  @retry="onRetry"
/>
```

**保留 `onRetry` 函数**（当前已存在，不需修改）：
```typescript
function onRetry(): void {
  store.clearError();
  store.refreshCalculation(code);
}
```

---

### 4.4 修改 `client/src/components/FundPreview.vue`

**问题**：当前非债券型基金仅展示警告框，但「确认并查看详情」按钮仍然可点击。

**修改**：非债券型基金确认按钮变灰（disabled），文案改为"当前仅支持债券型基金"。

**具体改动**：

```html
<!-- 确认按钮 — 替换现有按钮部分 -->
<button
  v-if="store.isBondFund"
  type="button"
  class="mt-5 w-full bg-blue-600 hover:bg-blue-700 active:bg-blue-800
         text-white text-sm font-medium rounded-lg py-2.5
         transition-colors duration-150"
  @click="onConfirm(fundInfo.fund_code)"
>
  {{ LABELS.CONFIRM_BUTTON }} →
</button>

<!-- 非债券型不可确认 — 替换为非可操作提示 -->
<div
  v-else
  class="mt-5 w-full text-center text-sm text-gray-400 py-2.5
         bg-gray-100 rounded-lg cursor-not-allowed"
>
  当前仅支持债券型基金
</div>
```

---

### 4.5 修改 `client/index.html`

**两处修改**：

```html
<!-- 修改前 -->
<html lang="en">
<!-- ... -->
<title>client</title>

<!-- 修改后 -->
<html lang="zh-CN">
<!-- ... -->
<title>债券收益计算</title>
```

---

### 4.6 修改 `client/src/components/NavGrid.vue` — 移动端字体

**问题**：净值 `text-2xl` (24px) 在 375px 下良好，但净值小数部分可用 `text-lg` (18px) 确保小屏不折行。

**具体改动**：无结构性变化，仅给净值容器加 `sm:` 断点响应式（当前已足够）。如果发现 375px 下数值溢出，则改为：

```html
<p class="text-xl sm:text-2xl font-semibold text-gray-900">{{ navDisplay }}</p>
```

> 此项为可选——先用 Chrome DevTools 在 375px 下实测，无问题则不修改。

---

### 4.7 修改 `client/src/components/YieldMetrics.vue` — 移动端字体

**问题**：指标值 `text-xl` (20px) + emoji `text-2xl` (24px)，在 375px 每列宽度 ~155px 下应能正常显示。

**具体改动**：如实测发现折行问题，调整：

```html
<span class="text-lg sm:text-xl font-semibold text-gray-900 mt-1">{{ item.display }}</span>
```

> 此项为可选——先用 Chrome DevTools 在 375px 下实测，无问题则不修改。

---

## 5. 需要验证但不需要改代码的项

以下项目代码层面已正确，只需运行时验证：

| 验证项 | 对应 TC | 验证方式 |
|--------|---------|---------|
| baseFetch 超时 15s | TC-4.3-009 | Store 中的 ApiError 已覆盖 |
| 轮询超时 120s | TC-4.3-004 | POLL_TIMEOUT 常量已设置 |
| 基金不存在 40001 | TC-4.3-006 | ApiError.code 匹配 ERROR_MESSAGES |
| 计算失败 status='failed' | TC-4.3-010 | refreshCalculation 中 handled |
| 骨架屏展示 | TC-4.3-012 | FundResult 已实现 |
| 免责声明可见 | TC-4.3-022/023 | 两页面均引用 DisclaimerBar |
| 浏览器前进后退 | TC-4.3-024 | hash router 天然支持 |
| 并发点击防抖 | TC-4.3-025 | loading 期间按钮 disabled |
| CORS 配置 | - | main.py + config.py 已配置 |
| Vercel SPA 重定向 | - | vercel.json rewrites 已配置 |

---

## 6. 代码规范要求

- 使用 `<script setup lang="ts">` 语法
- Props 用 `defineProps<InterfaceType>()` 类型推导
- Emits 用 `defineEmits<{ ... }>()` 类型推导
- 组件文件名 PascalCase（`ErrorAlert.vue`）
- Tailwind class 顺序：布局 → 颜色 → 圆角 → 间距 → 字体 → 过渡
- 错误提示使用 `role="alert"` 无障碍标注
- 中文文案引用自 `@/locales/zh-CN.ts`

---

## 7. 执行顺序

```
1. 新建 ErrorAlert.vue          → 可复用错误组件
2. 修改 FundInput.vue           → 接入 ErrorAlert + 重试逻辑
3. 修改 FundResult.vue          → 接入 ErrorAlert（替换内联代码）
4. 修改 FundPreview.vue         → 非债券型禁止确认
5. 修改 index.html              → lang + title
6. 可选：NavGrid / YieldMetrics → 移动端字体微调（实测后决定）
7. 验证                         → 运行 `npm run dev` + DevTools 375px 测试
```

---

## 8. 测试要求

代码完成后必须在本地验证以下场景：

- [ ] **TC-4.3-001**: 输入 `020741` → 查询 → 确认 → 计算 → 展示结果
- [ ] **TC-4.3-005**: 后端不可达时→ FundInput 展示"网络异常，请检查网络连接" + 重试按钮
- [ ] **TC-4.3-006**: 输入 `999999` → 展示基金不存在错误 + 可重试
- [ ] **TC-4.3-007**: 非债券型基金 → FundPreview 展示警告，确认按钮不可用
- [ ] **TC-4.3-014**: 首次失败后点击重试 → 成功展示 FundPreview
- [ ] **TC-4.3-019**: 375px 下 FundInput / FundResult 无横向溢出
- [ ] **TC-4.3-022**: FundInput 底部可见免责声明
- [ ] **TC-4.3-023**: FundResult 底部可见免责声明

---

## 9. 注意事项

1. **非债券型基金确认按钮** — 之前只是 `v-if="!store.isBondFund"` 展示 warning 但按钮依然可点。现在改为 `v-if/v-else`：债券型显示确认按钮，非债券型显示不可点击的提示区域。

2. **FundInput 重试需要记住上次代码** — 错误状态清除后，用户点击「重试」要用之前输入的基金代码自动重新查询。用 `ref<string | null>` 保存 `lastCode`。

3. **不要改动 Store** — `fetchFundInfo` 和 `refreshCalculation` 的错误处理已完善，本轮只修改 UI 层。

4. **DisclaimerBar 是 fixed 定位** — 页面主体已预留 `pb-20` 避免被遮挡，组件本身不需要改。

5. **后端 CORS 已在 Task 4.1 配置** — 本地开发 `localhost:5173` + 生产 Render URL 均在白名单。如果本地联调遇 CORS 错误，检查后端是否启动并确认 `.env` 中的 `CORS_ORIGINS`。

6. **本地开发使用 `VITE_API_BASE_URL`** — 未设置时默认 `http://localhost:8000`。生产构建时 `VITE_API_BASE_URL` 由 `.env.production` 提供 `https://bond-calc-api.onrender.com`。
