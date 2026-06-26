# 债券收益计算工具 — 开发计划

| 属性 | 值 |
|------|-----|
| 版本 | v1.0 |
| 创建日期 | 2025-06-25 |
| 完成日期 | 2025-06-26 |
| 状态 | ✅ 已完成 |
| 关联 PRD | [PRD](../.docs/prd/prd.md) |
| 关联 ADR | [后端](../.docs/adr/server.md) / [前端](../.docs/adr/client.md) |

## 1. 项目概述

**债券收益计算工具**是一款面向个人债券基金投资者的 Web 应用。用户输入基金代码，一键即可获取基金关键收益指标（净值、七日年化、万份收益、近1月收益、最大回撤）和当前市场利率数据，帮助投资者快速了解持仓基金的收益表现。

**MVP 闭环**：输入基金代码 → 确认基金信息 → 点击刷新计算 → 屏幕展示完整结果。

## 2. 技术栈概要

| 层次 | 选型 |
|------|------|
| 前端 | Vue 3 + Vite + Tailwind CSS + Pinia + Vue Router 4 |
| 后端 | Python 3.11+ / FastAPI / Uvicorn |
| 数据库 | MongoDB Atlas（M0 免费层）+ Beanie ODM |
| 外部数据 | akshare（天天基金 / 东方财富 / 中债信息网） |
| 后端部署 | Render |
| 前端部署 | Vercel |

## 3. 开发阶段

### 阶段 0：项目初始化

**目标**：搭建前后端项目脚手架，配置开发环境和工具链

**预计产出**：
- [x] 后端：FastAPI 项目骨架初始化，分层目录结构就绪 ✅ 2025-06-25
- [x] 后端：核心模块搭好（`core/config.py`、`core/exceptions.py`、`core/logging.py`、`core/cache.py`）✅ 2025-06-25
- [x] 后端：MongoDB Atlas 连接 + Beanie 初始化 ✅ 2025-06-25
- [x] 后端：requirements.txt 锁定依赖版本 ✅ 2025-06-25
- [x] 前端：Vite + Vue 3 + TypeScript 项目脚手架 ✅ 2025-06-25
- [x] 前端：Tailwind CSS、Pinia、Vue Router 安装配置 ✅ 2025-06-25
- [x] 前端：目录结构初始化 + 路由配置（hash 模式）✅ 2025-06-25
- [x] 根目录 README.md（项目说明 + 本地运行指南）✅ 2025-06-25

### 阶段 1：后端数据层 + 基金查询 API

**目标**：打通外部数据源，实现基金信息查询接口

**预计产出**：
- [x] `external/data_fetcher.py` — akshare 数据源适配（基金信息、历史净值、市场利率）✅ 2025-06-25
- [x] `models/` — Pydantic/Beanie 文档模型（Fund、Calculation、MarketData）✅ 2025-06-25
- [x] `repositories/fund_repo.py` — 基金数据 MongoDB CRUD ✅ 2025-06-25
- [x] `services/fund_service.py` — 基金信息校验（代码格式、基金类型判断、异常处理）✅ 2025-06-25
- [x] `api/routes/funds.py` — `GET /api/v1/funds/{code}` 接口 ✅ 2025-06-25
- [x] 交易日历集成（`exchange_calendars`）✅ 2025-06-25
- [x] 错误码体系（40001 基金不存在、40002 类型不匹配 等）✅ 2025-06-25

### 阶段 2：后端收益计算引擎

**目标**：实现 8 项收益指标计算，完成计算相关 API

**预计产出**：
- [x] `services/calculation_service.py` — 收益计算编排（并行拉取 + 指标计算 + 交易日判断）✅ 2025-06-25
- [x] `services/market_service.py` — 市场利率数据获取与处理 ✅ 2025-06-25
- [x] `repositories/market_repo.py` — 市场数据 MongoDB CRUD ✅ 2025-06-25
- [x] `api/routes/calculations.py` — `POST /api/v1/calculations` + `GET /api/v1/calculations/{id}` 接口 ✅ 2025-06-25
- [x] 8 项指标计算逻辑：最新净值、日涨跌幅、七日年化、万份收益、近1月收益率、近3月最大回撤、10年期国债收益率、信用利差 ✅ 2025-06-25
- [x] 数据缺失优雅降级（部分指标标 N/A，关键字段缺失不中断）✅ 2025-06-25
- [x] 免责声明字段植入响应体 ✅ 2025-06-25
- [x] 后端 Swagger 文档可访问，接口自测通过 ✅ 2025-06-25

### 阶段 3：前端页面与组件

**目标**：完成前端所有页面和组件的静态搭建

**预计产出**：
- [x] `src/api/index.ts` — fetch 封装层（超时 + 错误处理 + 响应类型）✅ 2025-06-25
- [x] `src/api/funds.ts` + `src/api/calculations.ts` — API 接口函数 ✅ 2025-06-25
- [x] `src/types/api.ts` — TypeScript 类型定义 ✅ 2025-06-25
- [x] `src/stores/fund.ts` — Pinia store（fundInfo、calculation、loading、error）✅ 2025-06-25
- [x] `src/utils/format.ts` — 数值格式化工具 ✅ 2025-06-25
- [x] `src/locales/zh-CN.ts` — 中文文案常量 ✅ 2025-06-25
- [x] 页面 `FundInput.vue` + 组件 `SearchBar.vue`、`FundPreview.vue` ✅ 2025-06-25
- [x] 页面 `FundResult.vue` + 组件 `ResultHeader.vue`、`YieldMetrics.vue`、`MarketRates.vue`、`RefreshButton.vue` ✅ 2025-06-25
- [x] 组件 `DisclaimerBar.vue`（全局复用）✅ 2025-06-25
- [x] Tailwind 样式完成，结果展示模板与 PRD 一致 ✅ 2025-06-25

### 阶段 4：前后端联调与部署

**目标**：前后端对接跑通完整用户流程，部署到生产环境

**预计产出**：
- [x] 后端 CORS 配置（开发 + 生产环境）✅ 2025-06-26
- [x] 前端接入后端 API，完整流程跑通（输入代码 → 查询基金 → 触发计算 → 展示结果）✅ 2025-06-26
- [x] 异常状态前端展示（网络错误、基金不存在、类型不匹配、数据缺失 N/A）✅ 2025-06-26
- [x] 加载状态骨架屏 / loading 动画 ✅ 2025-06-26
- [x] 移动端基础适配验证 ✅ 2025-06-26
- [x] 后端 Render 部署（`render.yaml` + 环境变量）✅ 2025-06-26
- [x] 前端 Vercel 部署（`vercel.json` SPA 重定向）✅ 2025-06-26
- [x] 联调完整流程 + 验收标准自检 ✅ 2025-06-26

## 4. 里程碑

| 里程碑 | 阶段 | 验收标准 | 预计完成 |
|--------|------|---------|---------|
| M0 | 阶段 0 | 前后端项目可本地启动，目录结构完整 | 2025-06-25 |
| M1 | 阶段 1 | `GET /api/v1/funds/{code}` 返回正确基金信息，异常情况有相应错误码 | 2025-06-25 |
| M2 | 阶段 2 | `POST/GET /api/v1/calculations` 返回完整 8 项指标，Swagger 可测试 | 2025-06-25 |
| M3 | 阶段 3 | 前端所有页面组件静态渲染，样式与 PRD 模板一致，路由跳转正常 | 2025-06-25 |
| M4 | 阶段 4 | 完整用户流程走通（输入 → 查询 → 计算 → 展示），Vercel + Render 可访问 | 2025-06-26 |

## 5. 风险与假设

| 风险/假设 | 影响 | 应对 |
|-----------|------|------|
| akshare 上游数据源接口变动 | 高 | `external/data_fetcher.py` 封装隔离变化；异常分级（单源失败标 N/A） |
| MongoDB Atlas 免费层 512MB 限制 | 低 | 数据模型精简，仅 3 个集合；超限后可迁移 Supabase PG |
| Render 免费层冷启动延迟 5-10s | 低 | 首次访问提示等待；用户自行刷新 |
| 前端依赖后端阶段 2 完成才能联调 | 中 | 阶段 3 可先做静态组件，阶段 4 再对接真实 API |
| akshare 安装体积约 70MB | 中 | 开发环境预留足够空间；部署时用 slim Python 镜像 |
