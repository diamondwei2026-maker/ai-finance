# Coding Prompt — Task 0.2: 前端项目脚手架与基础配置

## 1. 任务目标

使用 Vite 创建 Vue 3 + TypeScript 前端项目，安装并配置 Tailwind CSS 4、Pinia、Vue Router 4（hash 模式），初始化完整目录结构，编写根目录 README.md 和 vercel.json。

## 2. 技术上下文

- **语言/框架**: Vue 3（`<script setup>` + Composition API）+ TypeScript + Vite
- **样式方案**: Tailwind CSS 4（使用 `@tailwindcss/vite` 插件，**非** PostCSS 插件）
- **路由**: Vue Router 4 — hash 模式（`createWebHashHistory`），懒加载路由
- **状态管理**: Pinia — Composition API 风格（`defineStore` + setup 函数）
- **包管理器**: npm
- **Node.js**: >= 18
- **项目位置**: `client/`（项目根目录下的子目录）

### 涉及文件清单

| 操作 | 路径 | 说明 |
|------|------|------|
| **(新建)** | `client/` | 通过 Vite 脚手架创建 |
| **(新建)** | `client/vite.config.ts` | 注册 `@tailwindcss/vite` 插件 |
| **(新建)** | `client/src/style.css` | Tailwind CSS 入口 |
| **(新建)** | `client/src/main.ts` | 注册 router + pinia |
| **(新建)** | `client/src/App.vue` | 根组件，含 `<RouterView>` |
| **(新建)** | `client/src/router/index.ts` | 路由配置（hash 模式） |
| **(新建)** | `client/src/pages/FundInput.vue` | 首页占位组件 |
| **(新建)** | `client/src/pages/FundResult.vue` | 结果页占位组件 |
| **(新建)** | `client/src/stores/.gitkeep` | 目录占位（store 后续 Task 创建） |
| **(新建)** | `client/src/api/.gitkeep` | 目录占位 |
| **(新建)** | `client/src/types/.gitkeep` | 目录占位 |
| **(新建)** | `client/src/utils/.gitkeep` | 目录占位 |
| **(新建)** | `client/src/locales/.gitkeep` | 目录占位 |
| **(新建)** | `client/src/components/.gitkeep` | 目录占位 |
| **(新建)** | `client/vercel.json` | SPA 路由重定向配置 |
| **(新建)** | `README.md` | 项目根目录 README |

## 3. 实现要求

### 3.1 创建 Vite 项目（SUB-0.2.1）

**命令**：
```bash
npm create vite@latest client -- --template vue-ts
```

**注意**：
- 如果 `client/` 目录已存在且包含 `package.json`，跳过此步骤
- 创建完成后进入 `client/` 目录执行所有后续操作

**依赖安装**：
```bash
cd client
npm install vue-router pinia tailwindcss @tailwindcss/vite
```

- `tailwindcss` 和 `@tailwindcss/vite` 安装到 `devDependencies`
- `vue-router` 和 `pinia` 安装到 `dependencies`

### 3.2 配置 Tailwind CSS 4（SUB-0.2.2）

**文件**: `client/vite.config.ts`

修改 Vite 配置，添加 `@tailwindcss/vite` 插件：

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
})
```

**文件**: `client/src/style.css`

**清空**原有内容，写入 Tailwind CSS 入口：

```css
@import "tailwindcss";
```

**文件**: `client/src/main.ts`

确认已 `import './style.css'`（Vite 模板默认已包含，无需修改此行，但需确认存在）。

**验证**: 在 `App.vue` 的 `<template>` 中确认使用了 Tailwind class（Vite 默认模板可能不含，需要添加至少一个 Tailwind utility class，如 `class="p-4"`）。

### 3.3 配置 Vue Router 4（hash 模式）（SUB-0.2.3）

**文件**: `client/src/router/index.ts`（新建）

```typescript
import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'FundInput',
    component: () => import('@/pages/FundInput.vue'),
  },
  {
    path: '/fund/:code',
    name: 'FundResult',
    component: () => import('@/pages/FundResult.vue'),
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
```

**要点**：
- 使用 `createWebHashHistory()`，**不是** `createWebHistory()`
- 组件使用 `() => import(...)` 动态懒加载
- `:code` 为路由参数，对应基金代码

### 3.4 注册路由和状态管理到 Vue 应用（SUB-0.2.3）

**文件**: `client/src/main.ts`（修改）

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
```

**注意**：`app.use(router)` 和 `app.use(pinia)` 必须在 `app.mount('#app')` 之前调用。

### 3.5 更新 App.vue 根组件

**文件**: `client/src/App.vue`（替换模板内容）

```vue
<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <RouterView />
  </div>
</template>
```

**说明**：
- `min-h-screen bg-gray-50`：全屏浅灰背景
- `<RouterView />`：路由出口，渲染匹配的页面组件
- 保留原有的 `<script setup lang="ts">`，后续 Task 会添加逻辑

### 3.6 创建页面占位组件（SUB-0.2.3）

**文件**: `client/src/pages/FundInput.vue`（新建）

```vue
<script setup lang="ts">
</script>

<template>
  <div class="max-w-lg mx-auto p-6">
    <h1 class="text-2xl font-bold mb-4">债券基金收益计算</h1>
    <p class="text-gray-500">请输入基金代码查询</p>
  </div>
</template>
```

**文件**: `client/src/pages/FundResult.vue`（新建）

```vue
<script setup lang="ts">
</script>

<template>
  <div class="max-w-lg mx-auto p-6">
    <h1 class="text-2xl font-bold mb-4">计算结果</h1>
    <p class="text-gray-500">基金收益数据加载中...</p>
  </div>
</template>
```

### 3.7 创建目录结构（SUB-0.2.4）

在 `client/src/` 下创建以下目录，每个目录放入 `.gitkeep` 空文件：

```
src/api/
src/pages/         ← 已在上面步骤创建
src/components/
src/stores/
src/router/        ← 已在上面步骤创建
src/types/
src/utils/
src/locales/
```

**执行方式**：
```bash
cd client/src
mkdir -p api components stores types utils locales
touch api/.gitkeep components/.gitkeep stores/.gitkeep types/.gitkeep utils/.gitkeep locales/.gitkeep
```

> 注意：Windows 下 `mkdir -p` 等效于 `New-Item -ItemType Directory -Force`，`.gitkeep` 使用 `New-Item -ItemType File` 创建。

### 3.8 配置 TypeScript 路径别名

**文件**: `client/vite.config.ts`（在已有内容基础上追加）

```typescript
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
```

**文件**: `client/tsconfig.json`（在已有内容基础上追加）

在 `compilerOptions` 中添加：
```json
"baseUrl": ".",
"paths": {
  "@/*": ["./src/*"]
}
```

### 3.9 创建 vercel.json（SUB-0.2.4）

**文件**: `client/vercel.json`（新建）

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### 3.10 编写根目录 README.md（SUB-0.2.4）

**文件**: `README.md`（项目根目录，**不是** `client/` 下）

内容需包含以下章节：

1. **项目简介**：债券收益计算工具 — 面向个人债券基金投资者的 Web 应用，输入基金代码一键获取关键收益指标和当前市场利率
2. **技术栈**：
   - 前端：Vue 3 + TypeScript + Vite + Tailwind CSS 4 + Pinia + Vue Router 4
   - 后端：Python 3.11+ / FastAPI / Uvicorn
   - 数据库：MongoDB Atlas + Beanie ODM
   - 外部数据：akshare
3. **本地运行步骤**：
   - 后端：`cd server && pip install -r requirements.txt && uvicorn main:app --reload`
   - 前端：`cd client && npm install && npm run dev`
4. **目录结构说明**（列出顶层和关键子目录）
5. **部署**：前端 Vercel，后端 Render

## 4. 代码规范要求

- 使用 TypeScript，**不**使用 `any`（除非确实无法推断类型）
- Vue 组件使用 `<script setup lang="ts">` 语法
- 路由使用 `() => import(...)` 懒加载
- Hash 模式路由：`createWebHashHistory()`
- `import` 使用 `@/` 路径别名引用 `src/` 下的文件
- 所有组件命名使用 PascalCase

## 5. 测试要求

实现必须能通过以下测试用例（详见 [test-cases.md](./test-cases.md)）：

| 用例 | 验证要点 |
|------|---------|
| TC-001 | Vite 项目目录结构完整（package.json、vite.config.ts、tsconfig.json 等） |
| TC-002 | 依赖安装无报错（vue-router、pinia、tailwindcss、@tailwindcss/vite） |
| TC-003 | `npm run dev` 启动无编译错误 |
| TC-004 | `vite.config.ts` 注册了 `@tailwindcss/vite` 插件 |
| TC-005 | `src/style.css` 首行为 `@import "tailwindcss"` |
| TC-006 | App.vue 中使用 Tailwind class 能正常渲染样式 |
| TC-007 | CSS 无 `@import` 解析失败等控制台错误 |
| TC-008 | 路由文件包含 `/` 和 `/fund/:code` 两条路由，使用 hash 模式和懒加载 |
| TC-009 | `main.ts` 注册了 router 和 pinia |
| TC-010 | 访问 `/#/` 和 `/#/fund/020741` 能正确渲染对应页面组件 |
| TC-011 | 访问不存在的路由不崩溃 |
| TC-012 | `src/` 下 8 个目录全部存在 |
| TC-013 | 根目录 README.md 包含 4 个必要章节 |
| TC-014 | `vercel.json` 格式有效且配置正确 |
| TC-015 | 两个页面占位组件可正常渲染，无 Vue 警告 |

## 6. 注意事项

1. **Tailwind CSS 4 的配置方式与 v3 不同**：v4 使用 `@tailwindcss/vite` Vite 插件，CSS 入口是 `@import "tailwindcss"`（不是 v3 的 `@tailwind base/components/utilities`），不需要 `tailwind.config.js` 文件。
2. **client/ 目录可能已存在**：检查 `client/package.json` 是否已有，如有则跳过 `npm create vite`，直接安装依赖。
3. **创建目录时不要覆盖已有文件**：先检查目录是否存在，再创建。
4. **`.gitkeep` 文件确保目录被 git 追踪**：空目录不会被 git 记录，每个新建目录放一个空的 `.gitkeep`。
5. **TypeScript 路径别名**需要同时配置 `vite.config.ts`（运行时可解析）和 `tsconfig.json`（IDE 可解析）。
6. **README.md 放在项目根目录**，不是 `client/` 下——Task 所述"根目录"指 Git 仓库根目录。
7. **开发服务器验证**：完成所有配置后执行 `npm run dev` 确保无红屏报错，然后终止服务器即可。
