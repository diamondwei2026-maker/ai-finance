# 债券收益计算工具 — 前端架构决策记录

| 属性 | 值 |
|------|-----|
| 版本 | v1.1 |
| 状态 | 已实现 |
| 作者 | Claude (ADR Architect) |
| 日期 | 2025-06-25 |
| 更新日期 | 2025-06-26 |
| 关联文档 | [后端 ADR](./server.md) |

## 1. 需求概述

### 1.1 项目名称
**债券收益计算工具**（Bond Yield Calculation Tool）

### 1.2 目标用户
个人债券基金投资者——持有债券基金，关注核心收益指标，需要快速获取数据辅助判断，要求操作简单。

### 1.3 MVP 核心功能

| 优先级 | 功能 | 描述 |
|--------|------|------|
| P0 | 基金信息查询 | 输入 6 位基金代码 → 展示名称、类型、最新净值、七日年化 |
| P0 | 一键收益计算 | 点击刷新按钮 → 触发后端计算 → 展示 8 项指标 |
| P0 | 屏幕展示结果 | 格式化展示（净值、七日年化、万份收益、近1月收益、最大回撤、市场利率） |

### 1.4 用户交互流程
```
输入基金代码 → 确认基金信息 → 点击「刷新计算」→ 等待加载 → 展示结果
```

### 1.5 预期结果展示模板

```
📊 华泰保兴安悦债券C（020741）
━━━━━━━━━━━━━━━━━━━━━━━
📅 数据日期：2025-06-23（昨日净值）

💰 最新净值：1.0234  ｜ 日涨跌：+0.02%
📈 七日年化：3.82%
💵 万份收益：0.85 元
📉 近1月收益：+0.31%
⚠️  近3月最大回撤：0.45%

📡 当前市场
10年期国债：2.68%
信用利差 AA+：58bp

━━━━━━━━━━━━━━━━━━━━━━━
```

### 1.6 MVP 明确不做
策略配置、操作建议、趋势图表、推送通知、历史记录、多基金、日内净值预估

---

## 2. 跨切面决策

> 以下引用后端 ADR 中的跨切面决策，仅记录前端相关的要点。

### 2.1 应用形态与部署架构
- **选定方案**：Web 应用（前后端分离）
- **部署目标**：前端 Vercel，后端 Render
- **前端影响**：前端为独立 SPA，通过 HTTP 与后端 API 通信；需配置 CORS（生产环境 Vercel 域名白名单，开发环境 `localhost:5173`）；Vercel 需配置 SPA 路由重定向

### 2.2 API 风格与规范
- **选定方案**：RESTful API（`/api/v1/...`）
- **前端影响**：请求封装层统一使用 REST 约定；URL 路径版本直观可读；与后端 Swagger 文档保持一致

### 2.3 缓存策略
- **选定方案**：后端内存缓存 + MongoDB 兜底
- **前端影响**：前端不做客户端缓存（每次刷新主动请求后端，由后端判断返回缓存还是新数据）；前端仅管理请求的 loading / error / data 状态

---

## 3. 技术选型

### 3.1 前端框架
- **选定方案**：Vue 3 + Vite
- **候选对比**：

| 维度 | Vue 3 + Vite | React + Vite | Next.js |
|------|-------------|-------------|---------|
| 学习曲线 | 低（模板语法直观，SFC 单文件组件） | 中（JSX、hooks 心智模型） | 高（SSR 概念、路由约定） |
| 移动端迁移 | Uni-app（H5 → 小程序/App，代码复用 80%+） | Taro（React 语法写小程序，复用率低于 Uni-app） | React Native（独立 App，非小程序） |
| 图表生态 | vue-echarts / echarts 成熟 | recharts / echarts-for-react 最丰富 | 同 React |
| 构建速度 | Vite（秒级 HMR） | Vite（秒级 HMR） | Turbopack / Webpack |
| Vercel 部署 | Vite preset，一键部署 | Vite preset，一键部署 | 原生支持 |
| 中文社区 | 极强（尤雨溪中文生态，Uni-app 中文文档） | 国际化为主 | 国际化为主 |

- **选择理由**：
  1. 目标用户为国内个人投资者，未来移动端最可能走微信小程序路径——Uni-app 基于 Vue，H5 代码复用率 80%+
  2. Vue 3 Composition API + `<script setup>` 开发体验与现代框架对齐
  3. Vite 构建极快，Vercel 一键部署
  4. 中文文档和社区资源丰富，降低后续维护门槛

### 3.2 样式方案
- **选定方案**：Tailwind CSS（MVP 手写组件，不引入 UI 组件库）
- **候选对比**：

| 维度 | Tailwind CSS | 纯手写 CSS | Element Plus（组件库） |
|------|-------------|-----------|---------------------|
| MVP 开发速度 | 快（utility class 拼接） | 中（全手动） | 最快（组件即用） |
| 未来组件库切换 | 互不冲突，共存 | 互不冲突 | 已锁定 Element Plus |
| 体积 | 构建时摇树，~3KB | 零 | 按需引入，~50KB+ |
| 设计自由度 | 高 | 最高 | 低（企业后台风格） |

- **选择理由**：
  1. MVP 页面极简（输入框 + 按钮 + 结果卡片），引入组件库"拿大炮打蚊子"
  2. Tailwind 提供一致的间距、颜色、响应式体系，比纯手写 CSS 效率高且不乱
  3. 不锁定任何组件库——未来根据移动端方向（Vant 小程序 / Element Plus Web）二选一时，Tailwind 与两者都和平共存

- **未来组件库方向**：
  - 做移动端/小程序 → **Vant 4**（有赞出品，Vue 3 移动端标准，自带微信小程序版本，Uni-app 官方推荐）
  - 留在桌面 Web → **Element Plus**（Vue 3 企业级最成熟，中文生态最好）

### 3.3 HTTP 请求方案
- **选定方案**：原生 fetch + 轻量封装
- **候选方案**：axios / VueUse `useFetch`
- **选择理由**：
  1. MVP 仅 2-3 个 API 调用，封装一个 30 行的 `api.ts`（超时 + 错误处理 + 响应类型）完全够用
  2. 零依赖，现代浏览器 fetch 已非常成熟
  3. 封装层隔离了实现——后续切 axios 或 VueUse 只需改一个文件

### 3.4 路由方案
- **选定方案**：Vue Router 4（hash 模式）
- **候选方案**：单页面条件渲染（`v-if` 切换视图）
- **选择理由**：
  1. hash 模式零服务端配置，Vercel 部署无需处理 SPA 重定向
  2. 结果页有独立 URL 可分享（`/#/fund/020741`）
  3. 浏览器前进后退按钮自然可用
  4. v1.4 多基金直接加动态路由，无需重构

### 3.5 状态管理
- **选定方案**：Pinia
- **候选方案**：`reactive` + `provide/inject` / 无状态管理（URL query 传参）
- **选择理由**：
  1. `defineStore` 定义跨路由数据共享——输入页写入基金代码，结果页直接读计算结果，零摩擦
  2. Vue 官方推荐（Vuex 继任者），DevTools 时间旅行调试
  3. 体积仅 ~8KB，API 与 `<script setup>` 风格统一
  4. 当前 MVP 用 5% 能力，后续版本零迁移成本

---

## 4. 架构设计

### 4.1 页面路由结构

```
/ (首页)
├── /#/              → 基金代码输入页（FundInput）
└── /#/fund/:code    → 计算结果展示页（FundResult）
                         └── /#/fund/:code?refresh=1 → 触发重新计算
```

### 4.2 组件树

```
App.vue
└── <RouterView>
    ├── FundInput.vue（首页 — 输入基金代码）
    │   ├── SearchBar.vue（代码输入框 + 查询按钮）
    │   ├── FundPreview.vue（基金基本信息确认卡片，查询后展示）
    │   ├── ErrorAlert.vue（错误提示横幅，全局复用）
    │   └── DisclaimerBar.vue（免责声明，全局展示）
    │
    └── FundResult.vue（结果页 — 计算并展示）
        ├── ResultHeader.vue（基金名称 + 数据日期标注）
        ├── NavGrid.vue（净值 + 日涨跌）
        ├── YieldMetrics.vue（七日年化 / 万份收益 / 近1月收益 / 近3月最大回撤）
        ├── MarketRates.vue（10年期国债 + 信用利差）
        ├── RefreshButton.vue（刷新计算按钮）
        ├── ErrorAlert.vue（错误提示，复用）
        └── DisclaimerBar.vue（免责声明，复用）
```

### 4.3 模块划分

| 模块 | 路径 | 职责 |
|------|------|------|
| 页面-输入 | `src/pages/FundInput.vue` | 基金代码输入、查询触发、基本信息预览 |
| 页面-结果 | `src/pages/FundResult.vue` | 计算结果展示、刷新触发、数据时效性标注 |
| 组件-搜索 | `src/components/SearchBar.vue` | 基金代码输入框 + 查询按钮 |
| 组件-预览 | `src/components/FundPreview.vue` | 基金基本信息确认卡片 |
| 组件-头部 | `src/components/ResultHeader.vue` | 基金名称 + 数据日期标注 |
| 组件-净值 | `src/components/NavGrid.vue` | 最新净值 + 日涨跌幅展示 |
| 组件-指标 | `src/components/YieldMetrics.vue` | 收益指标卡片组 |
| 组件-市场 | `src/components/MarketRates.vue` | 市场利率展示 |
| 组件-刷新 | `src/components/RefreshButton.vue` | 刷新计算按钮 |
| 组件-错误 | `src/components/ErrorAlert.vue` | 错误提示横幅（全局复用） |
| 组件-免责 | `src/components/DisclaimerBar.vue` | 免责声明横幅（全局复用） |
| API 层 | `src/api/index.ts` | fetch 封装（baseFetch、错误处理、响应类型） |
| API 接口 | `src/api/funds.ts` | 基金查询接口函数 |
| API 接口 | `src/api/calculations.ts` | 计算触发与结果获取接口函数 |
| Store | `src/stores/fund.ts` | 基金信息 + 计算结果 Pinia store |
| 路由 | `src/router/index.ts` | Vue Router 配置（hash 模式） |
| 类型 | `src/types/api.ts` | API 响应 TypeScript 类型定义 |
| 工具 | `src/utils/format.ts` | 数值格式化（百分比、货币等） |
| 文案 | `src/locales/zh-CN.ts` | 中文文案常量 |

### 4.4 目录结构

```
client/
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── src/
    ├── main.ts                  # 应用入口
    ├── App.vue                  # 根组件
    ├── router/
    │   └── index.ts             # 路由配置
    ├── stores/
    │   └── fund.ts              # Pinia store
    ├── api/
    │   ├── index.ts             # fetch 封装
    │   ├── funds.ts             # 基金 API
    │   └── calculations.ts      # 计算 API
    ├── pages/
    │   ├── FundInput.vue        # 输入页
    │   └── FundResult.vue       # 结果页
    ├── components/
    │   ├── SearchBar.vue
    │   ├── FundPreview.vue
    │   ├── ResultHeader.vue
    │   ├── NavGrid.vue
    │   ├── YieldMetrics.vue
    │   ├── MarketRates.vue
    │   ├── RefreshButton.vue
    │   ├── ErrorAlert.vue
    │   └── DisclaimerBar.vue
    ├── locales/
    │   └── zh-CN.ts             # 中文文案常量
    ├── types/
    │   └── api.ts               # TS 类型定义
    └── utils/
        └── format.ts            # 格式化工具
```

---

## 5. 接口设计

### 5.1 与后端的接口契约

| 方法 | 路径 | 说明 | 前端调用场景 |
|------|------|------|-------------|
| GET | `/api/v1/funds/{code}` | 查询基金信息 | FundInput → 用户输入代码后，验证基金是否存在及类型 |
| POST | `/api/v1/calculations` | 触发计算 | FundResult → 用户点击「刷新计算」按钮 |
| GET | `/api/v1/calculations/{id}` | 获取结果 | FundResult → 获取完整 8 项指标 |

### 5.2 前端请求封装

```typescript
// src/api/index.ts

interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

async function baseFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000); // 15s 超时

  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!res.ok) {
      throw new ApiError(res.status, `请求失败: ${res.statusText}`);
    }

    const json: ApiResponse<T> = await res.json();

    if (json.code !== 0) {
      throw new ApiError(json.code, json.message);
    }

    return json.data;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if ((err as Error).name === 'AbortError') {
      throw new ApiError(0, '请求超时，请稍后重试');
    }
    throw new ApiError(-1, '网络异常，请检查网络连接');
  } finally {
    clearTimeout(timeout);
  }
}
```

### 5.3 前端数据流

```
API 响应 (JSON)
    │
    ▼
Pinia Store (fundStore)
├── fundInfo: FundInfo        ← GET /funds/{code}
├── calculation: Calculation  ← POST + GET /calculations
├── loading: boolean          ← 请求进行中
├── error: string | null      ← 请求异常信息
│
    │ (组件通过 storeToRefs 读取)
    ▼
组件层
├── FundInput.vue  → fundStore.fetchFund(code)
├── FundResult.vue → fundStore.triggerCalculation(code)
│                     fundStore.calculation (自动响应式渲染)
```

---

## 6. 状态管理设计

### 6.1 Store 结构

```typescript
// src/stores/fund.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { FundInfo, Calculation } from '@/types/api';
import { fetchFund, triggerCalculation, getCalculation } from '@/api';

export const useFundStore = defineStore('fund', () => {
  // 状态
  const fundInfo = ref<FundInfo | null>(null);
  const calculation = ref<Calculation | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // 计算属性
  const isBondFund = computed(() => fundInfo.value?.fund_type?.includes('债'));
  const hasCalculation = computed(() => calculation.value !== null);

  // 操作
  async function fetchFundInfo(code: string) { /* ... */ }
  async function refreshCalculation(code: string) { /* ... */ }
  function clearError() { /* ... */ }

  return {
    fundInfo, calculation, loading, error,
    isBondFund, hasCalculation,
    fetchFundInfo, refreshCalculation, clearError,
  };
});
```

### 6.2 数据归一化
- 后端返回的百分比值（如 `0.31`）在前端格式化层统一转为 `"0.31%"` 展示
- 数值字段允许 `null`——表示数据缺失，展示时渲染 "N/A"
- 日期字段统一为 `YYYY-MM-DD` 字符串格式

### 6.3 持久化
- MVP 阶段不做状态持久化（页面刷新后数据丢失，用户重新查询）
- 后续版本可将基金代码存入 `localStorage`，实现"记住上次查询的基金"

---

## 7. 非功能性设计

### 性能
- **首屏加载**：Vite 构建产物 <100KB（gzip），Vercel 全球 CDN 分发
- **代码分割**：Vue Router 懒加载路由页面（`() => import('@/pages/FundResult.vue')`）
- **输入响应**：本地校验（代码格式 6 位数字），无需等待后端即可给出格式提示
- **加载状态**：使用骨架屏（Skeleton）而非空白等待，提升感知速度
- **防抖处理**：输入框 300ms 防抖，避免频繁触发查询

### 可访问性
- 输入框关联 `<label>`，支持屏幕阅读器
- 按钮使用 `<button>` 原生元素，支持键盘 `Enter` 触发
- 错误提示使用 `role="alert"` 确保屏幕阅读器即时播报
- 数据日期使用 `<time>` 语义标签

### 移动端适配
- Tailwind 响应式工具类（`sm:` / `md:` / `lg:` 断点）
- MVP 以桌面端为主，移动端基础可读（卡片最大宽度约束，小屏不溢出）
- 后续移动端（v1.4+）独立方案，不在此 MVP 范围

### 国际化
- MVP 仅中文，不做 i18n
- 所有文案集中到 `src/locales/zh-CN.ts` 常量文件，为后续 i18n 预留结构

---

## 8. 风险与权衡

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| Tailwind 学习成本（utility-first 思维转变） | 低 | 低 | Tailwind 文档优秀，MVP 的 class 组合简单（间距+颜色+字体），非团队协作场景下成本可控 |
| Vue → Uni-app 迁移不达预期 | 中 | 低 | MVP 先验证核心价值，v1.4 迁移时评估；Composition API 代码可直接复用到 Uni-app |
| 后端 API 不可用（跨域或服务宕机） | 高 | 低 | 前端展示明确错误提示和重试按钮；fetch 封装捕获网络异常；非致命错误不阻塞页面 |
| Vercel + Render 双平台运维复杂 | 低 | 中 | MVP 阶段平台配置已确定，后续变更少；CI/CD 通过 GitHub Actions 自动化 |
| 浏览器兼容性（旧版浏览器 fetch 支持） | 低 | 低 | 目标用户为个人投资者，通常使用现代浏览器；Vite 默认目标为 `es2015+` |

### 权衡记录
- **选择 Vue 3** 意味着获得 Uni-app 小程序迁移路径和中文本地化生态优势，**但放弃了** React 生态的图表库丰富度和国际市场人才池
- **选择 Tailwind CSS（不引入组件库）** 意味着 MVP 完全控制样式和设计自由度，**但放弃了** 开箱即用的组件（表单校验、加载骨架、弹窗）——需手写少量简单组件
- **选择原生 fetch** 意味着零依赖和最小体积，**但放弃了** axios 的拦截器和取消令牌生态——MVP 接口少，封装 30 行即可弥补
- **如果未来确定不做移动端**，Vue → React 的技术选择仍然成立（Vue 本身在 Web 端足够优秀），没有后悔成本

---

## 9. 实施建议

### 第一阶段：项目骨架
- `npm create vite@latest client -- --template vue-ts`
- 安装依赖：`vue-router` `pinia` `tailwindcss` `@tailwindcss/vite`
- 配置 Tailwind、TypeScript、Vite
- 目录结构初始化
- 配置 Vercel SPA 路由重定向（`vercel.json`: `{ "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }] }`）

### 第二阶段：基础组件
- `api/index.ts` fetch 封装
- `stores/fund.ts` Pinia store
- `router/index.ts` 路由配置
- 所有组件的骨架模板 + Tailwind class

### 第三阶段：API 对接
- 接入后端真实接口（开发环境 `localhost:8000`）
- 基金查询流程（输入 → 校验 → 预览 → 确认）
- 计算触发流程（刷新按钮 → loading → 结果展示）
- 异常状态处理（网络错误、代码无效、类型不匹配、数据缺失）

### 第四阶段：打磨与部署
- 免责声明文案植入
- 移动端基础适配验证
- Vercel 部署 + 自定义域名（可选）
- 与后端联调完整流程

### 依赖关系
```
阶段 1（骨架）
  └─→ 阶段 2（基础组件）
        └─→ 阶段 3（API 对接）
              └─→ 阶段 4（打磨部署）

注：阶段 3 依赖后端阶段 4 完成（后端 API 可用）
```

| 里程碑 | 关键产出 | 预估工作量 |
|--------|---------|-----------|
| 骨架完成 | Vite 项目可运行，路由跳转正常 | 0.5 天 |
| 基础组件完成 | 所有组件静态渲染，样式符合模板 | 1 天 |
| API 对接完成 | 与后端联调通过，完整用户流程跑通 | 1 天 |
| 打磨部署完成 | Vercel 可访问，移动端可读 | 0.5 天 |
