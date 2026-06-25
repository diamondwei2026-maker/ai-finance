# Task 0.2: 前端项目脚手架与基础配置

| 属性 | 值 |
|------|-----|
| ID | 0.2 |
| 状态 | pending |
| 优先级 | P0 |
| 依赖 | 无 |
| 阶段 | 阶段0: 项目初始化 |
| 预估工时 | 2-3 小时 |

## 描述

使用 Vite 创建 Vue 3 + TypeScript 前端项目，安装配置 Tailwind CSS、Pinia、Vue Router 4（hash 模式），初始化目录结构，编写根目录 README.md。

## 验收标准

- [ ] `npm create vite@latest client -- --template vue-ts` 创建项目，`npm run dev` 可启动
- [ ] Tailwind CSS 4 安装配置完成（`@tailwindcss/vite` 插件），任意组件中使用 Tailwind class 生效
- [ ] Pinia 安装并注册到 Vue 应用
- [ ] Vue Router 4 安装并配置 hash 模式，含两个路由：`/`（FundInput）和 `/fund/:code`（FundResult）
- [ ] 前端目录结构符合 ADR 定义（`src/api/`、`src/pages/`、`src/components/`、`src/stores/`、`src/router/`、`src/types/`、`src/utils/`、`src/locales/`）
- [ ] 根目录 `README.md` 包含：项目简介、技术栈、本地运行步骤（前后端）、目录结构说明
- [ ] `vercel.json` 配置 SPA 路由重定向：`{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }`

## 子任务

### SUB-0.2.1: Vite 项目创建与依赖安装
- **描述**: 创建 Vue 3 + TypeScript 项目，安装所有依赖
- **验收标准**:
  - [ ] `npm create vite@latest client -- --template vue-ts` 执行成功
  - [ ] `npm install vue-router pinia tailwindcss @tailwindcss/vite` 安装成功
  - [ ] `npm run dev` 启动无报错

### SUB-0.2.2: Tailwind CSS 配置
- **描述**: 配置 Tailwind CSS 4 与 Vite 集成
- **验收标准**:
  - [ ] `vite.config.ts` 中注册 `@tailwindcss/vite` 插件
  - [ ] `src/style.css` 中 `@import "tailwindcss"` 生效
  - [ ] 验证：在 App.vue 中使用 Tailwind class 能正常渲染样式

### SUB-0.2.3: 路由与状态管理配置
- **描述**: 配置 Vue Router（hash 模式）和 Pinia
- **验收标准**:
  - [ ] `src/router/index.ts` 定义两条路由（`/` → FundInput, `/fund/:code` → FundResult），使用懒加载
  - [ ] `src/main.ts` 中注册 router 和 pinia
  - [ ] 路由跳转正常，hash 模式 URL 正确（`/#/` 和 `/#/fund/020741`）

### SUB-0.2.4: 目录结构与 README
- **描述**: 创建完整目录结构，编写 README.md
- **验收标准**:
  - [ ] `src/api/`、`src/pages/`、`src/components/`、`src/stores/`、`src/types/`、`src/utils/`、`src/locales/` 目录已创建
  - [ ] 根目录 `README.md` 内容完整（项目简介 + 技术栈 + 本地运行指南）
  - [ ] `vercel.json` 创建并配置 SPA 重写规则
