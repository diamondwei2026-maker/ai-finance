# 测试用例 — Task 0.2: 前端项目脚手架与基础配置

> 共 15 个测试用例：功能测试 12 个，边界测试 2 个，集成测试 1 个。

---

## SUB-0.2.1: Vite 项目创建与依赖安装

### TC-001: Vite 项目创建成功
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.1 — `npm create vite@latest client -- --template vue-ts` 执行成功
- **前置条件**: 无
- **输入**: 无
- **执行步骤**:
  1. 在项目根目录执行 `npm create vite@latest client -- --template vue-ts`（如 client 目录不存在）
  2. 进入 `client/` 目录
  3. 检查是否存在 `package.json`、`vite.config.ts`、`tsconfig.json`、`index.html`、`src/main.ts`
- **预期输出**:
  - `client/` 目录被创建
  - `package.json` 中包含 `vue`、`vite`、`typescript` 依赖声明
  - `vite.config.ts` 存在且使用 `vue` 插件
- **清理**: 无（项目脚手架即最终产物）

### TC-002: 依赖安装成功
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.1 — `npm install vue-router pinia tailwindcss @tailwindcss/vite` 安装成功
- **前置条件**: TC-001 通过，`client/` 目录已创建
- **输入**: 无
- **执行步骤**:
  1. 进入 `client/` 目录
  2. 执行 `npm install vue-router pinia tailwindcss @tailwindcss/vite`
  3. 检查 `package.json` 的 `dependencies` 字段
  4. 检查 `node_modules/` 目录是否存在
- **预期输出**:
  - `package.json` `dependencies` 中包含 `vue-router`、`pinia`、`tailwindcss`
  - `package.json` `devDependencies`（或 dependencies）中包含 `@tailwindcss/vite`
  - `npm install` 无报错退出
- **清理**: 无

### TC-003: 开发服务器可启动
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.1 — `npm run dev` 启动无报错
- **前置条件**: TC-001、TC-002 通过
- **输入**: 无
- **执行步骤**:
  1. 进入 `client/` 目录
  2. 执行 `npm run dev`（以 headless 方式或短时间运行后终止）
  3. 观察控制台输出
- **预期输出**:
  - Vite 开发服务器启动成功，显示本地访问地址（如 `http://localhost:5173`）
  - 无编译错误或警告
- **清理**: 终止开发服务器进程

---

## SUB-0.2.2: Tailwind CSS 配置

### TC-004: @tailwindcss/vite 插件已注册
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.2 — `vite.config.ts` 中注册 `@tailwindcss/vite` 插件
- **前置条件**: TC-002 通过
- **输入**: 无
- **执行步骤**:
  1. 读取 `client/vite.config.ts`
  2. 检查是否有 `import tailwindcss from '@tailwindcss/vite'`
  3. 检查 `plugins` 数组中是否包含 `tailwindcss()`
- **预期输出**:
  - 文件包含 `import tailwindcss from '@tailwindcss/vite'`
  - `plugins: [vue(), tailwindcss()]`（顺序不限）
- **清理**: 无

### TC-005: Tailwind CSS 入口样式文件正确
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.2 — `src/style.css` 中 `@import "tailwindcss"` 生效
- **前置条件**: TC-004 通过
- **输入**: 无
- **执行步骤**:
  1. 读取 `client/src/style.css`
  2. 检查文件内容
  3. 确认 `main.ts` 中 import 了 `style.css`
- **预期输出**:
  - `style.css` 第一行为 `@import "tailwindcss";`
  - `main.ts` 包含 `import './style.css'`
- **清理**: 无

### TC-006: Tailwind class 渲染验证
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.2 — 在 App.vue 中使用 Tailwind class 能正常渲染样式
- **前置条件**: TC-004、TC-005 通过，开发服务器可正常启动
- **输入**: 无
- **执行步骤**:
  1. 确认 `App.vue` 模板中至少一个元素使用了 Tailwind class（如 `class="text-red-500"` 或 `class="p-4"`）
  2. 启动开发服务器，用浏览器访问
  3. 检查 DevTools → Elements → Styles 面板是否出现了对应的 Tailwind CSS 规则
- **预期输出**:
  - 页面中 Tailwind class 对应的样式规则生效（如红色文字、内边距可见）
- **清理**: 终止开发服务器（如有）

### TC-007: Tailwind class 无未定义样式错误
- **类型**: 异常测试
- **关联验收标准**: SUB-0.2.2
- **前置条件**: TC-004、TC-005 通过
- **输入**: 无
- **执行步骤**:
  1. 启动开发服务器
  2. 检查控制台是否有 CSS 相关警告或错误（如 `@import` 解析失败）
- **预期输出**:
  - 无 CSS 相关控制台错误
  - Tailwind 的 `@import` 被正确解析为生成的 CSS
- **清理**: 终止开发服务器

---

## SUB-0.2.3: 路由与状态管理配置

### TC-008: 路由文件定义正确
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.3 — `src/router/index.ts` 定义两条路由，使用懒加载
- **前置条件**: TC-002 通过，`src/router/` 目录存在
- **输入**: 无
- **执行步骤**:
  1. 读取 `client/src/router/index.ts`
  2. 检查路由数组是否包含两条路由：`path: '/'` 和 `path: '/fund/:code'`
  3. 检查是否使用 `createWebHashHistory`（hash 模式）
  4. 检查组件引用是否使用 `() => import(...)` 懒加载语法
- **预期输出**:
  - 路由数组包含 `{ path: '/', name: 'FundInput', component: () => import('@/pages/FundInput.vue') }`
  - 路由数组包含 `{ path: '/fund/:code', name: 'FundResult', component: () => import('@/pages/FundResult.vue') }`
  - `createRouter` 使用 `createWebHashHistory()`
- **清理**: 无

### TC-009: main.ts 注册 router 和 pinia
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.3 — `src/main.ts` 中注册 router 和 pinia
- **前置条件**: TC-008 通过
- **输入**: 无
- **执行步骤**:
  1. 读取 `client/src/main.ts`
  2. 检查是否有 `import { createPinia } from 'pinia'`
  3. 检查是否有 `import router from './router'`
  4. 检查 `app.use(router)` 和 `app.use(createPinia())` 调用
- **预期输出**:
  - `const pinia = createPinia()` 或 `app.use(createPinia())`
  - `app.use(router)` 在 `app.mount('#app')` 之前
  - `app.use(pinia)` 在 `app.mount('#app')` 之前（如使用变量）
- **清理**: 无

### TC-010: Hash 模式 URL 路由正确
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.3 — 路由跳转正常，hash 模式 URL 正确
- **前置条件**: TC-008、TC-009 通过，FundInput 和 FundResult 页面占位组件存在
- **输入**: 导航路径 `/fund/020741`
- **执行步骤**:
  1. 启动开发服务器
  2. 使用浏览器访问 `http://localhost:5173` → 应显示 `/#/`（FundInput 页面）
  3. 修改 URL 为 `http://localhost:5173/#/fund/020741` → 应显示 FundResult 页面
  4. 检查 URL 是否始终包含 `/#/`（hash 模式特征）
- **预期输出**:
  - 访问根路径显示 FundInput 组件内容
  - 访问 `/#/fund/020741` 显示 FundResult 组件内容
  - URL 格式为 hash 模式（带 `#`）
- **清理**: 终止开发服务器

### TC-011: 不存在的路由处理
- **类型**: 边界测试
- **关联验收标准**: SUB-0.2.3
- **前置条件**: TC-008、TC-009 通过
- **输入**: 导航到不存在的路径 `/#/nonexistent`
- **执行步骤**:
  1. 启动开发服务器
  2. 访问 `http://localhost:5173/#/nonexistent`
  3. 观察页面行为（是否回退到首页、显示 404 或空白）
- **预期输出**:
  - 不崩溃、不白屏
  - 如配置了 catch-all 路由则显示 404 提示；否则回退到 `/` 首页
- **清理**: 终止开发服务器

---

## SUB-0.2.4: 目录结构与 README

### TC-012: 前端目录结构完整
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.4 — 所有指定目录已创建
- **前置条件**: TC-001 通过
- **输入**: 无
- **执行步骤**:
  1. 检查 `client/src/` 下是否存在以下目录（每个目录至少包含一个 `.gitkeep` 或占位文件）：
     - `src/api/`
     - `src/pages/`
     - `src/components/`
     - `src/stores/`
     - `src/router/`
     - `src/types/`
     - `src/utils/`
     - `src/locales/`
- **预期输出**:
  - 8 个目录全部存在
  - 每个目录内有文件（`.gitkeep`、`index.ts` 或占位组件）
- **清理**: 无

### TC-013: README.md 内容完整
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.4 — 根目录 `README.md` 内容完整
- **前置条件**: TC-001 通过
- **输入**: 无
- **执行步骤**:
  1. 读取项目根目录 `README.md`
  2. 检查是否包含以下内容块：
     - 项目简介（项目名称 + 一句话描述）
     - 技术栈（前端 Vue 3 + TS + Vite + Tailwind + Pinia + Vue Router，后端 FastAPI + Python）
     - 本地运行步骤（前端 `cd client && npm install && npm run dev`，后端 `cd server && pip install -r requirements.txt && uvicorn main:app --reload`）
     - 目录结构说明（至少列出 `client/` 和 `server/` 的顶层结构）
- **预期输出**:
  - 至少包含上述 4 个章节
  - 内容为中文，可读、无占位符
- **清理**: 无

### TC-014: vercel.json 配置正确
- **类型**: 功能测试
- **关联验收标准**: SUB-0.2.4 — `vercel.json` 创建并配置 SPA 重写规则
- **前置条件**: TC-001 通过
- **输入**: 无
- **执行步骤**:
  1. 读取 `client/vercel.json`
  2. 检查 JSON 结构
- **预期输出**:
  - `vercel.json` 内容为：
    ```json
    {
      "rewrites": [
        { "source": "/(.*)", "destination": "/index.html" }
      ]
    }
    ```
  - JSON 格式有效（无语法错误）
- **清理**: 无

### TC-015: 页面占位组件可渲染
- **类型**: 集成测试
- **关联验收标准**: SUB-0.2.3 + SUB-0.2.4
- **前置条件**: TC-008、TC-009、TC-012 通过
- **输入**: 无
- **执行步骤**:
  1. 确认 `src/pages/FundInput.vue` 存在且有有效 Vue SFC 模板
  2. 确认 `src/pages/FundResult.vue` 存在且有有效 Vue SFC 模板
  3. 启动开发服务器，访问 `/#/`
  4. 访问 `/#/fund/020741`
- **预期输出**:
  - 两个页面均可正常渲染，无空白页、无控制台 Vue 警告
  - 页面内容至少包含标识性文字（如 "FundInput"、"基金输入"）
- **清理**: 终止开发服务器

---

## 测试数据准备

| 数据项 | 值 | 用途 |
|--------|-----|------|
| 测试基金代码 | `020741` | 路由参数测试 |
| 开发服务器端口 | `5173` | Vite 默认端口 |

## 测试环境

| 项目 | 要求 |
|------|------|
| Node.js | >= 18 |
| 包管理器 | npm |
| 浏览器 | Chrome / Edge 最新版 |
| 操作系统 | 不限定 |
