# 债券收益计算工具

面向个人债券基金投资者的 Web 应用——输入 6 位基金代码，一键获取关键收益指标（净值、七日年化、万份收益、近1月收益、最大回撤）和当前市场利率数据，帮助投资者快速了解持仓基金的收益表现。

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Tailwind CSS 4 + Pinia + Vue Router 4 |
| 后端 | Python 3.11+ / FastAPI / Uvicorn |
| 数据库 | MongoDB Atlas（M0 免费层） + Beanie ODM |
| 外部数据 | akshare（天天基金 / 东方财富 / 中债信息网） |
| 前端部署 | Vercel |
| 后端部署 | Render |

## 本地运行

### 环境要求

- Node.js >= 18
- Python >= 3.11
- MongoDB Atlas 连接字符串（或本地 MongoDB）

### 后端

```bash
cd server
pip install -r requirements.txt
uvicorn main:app --reload
```

后端默认运行在 `http://localhost:8000`，Swagger 文档访问 `http://localhost:8000/docs`。

### 前端

```bash
cd client
npm install
npm run dev
```

前端默认运行在 `http://localhost:5173`。

## 目录结构

```
ai-finance/
├── client/                 # 前端 — Vue 3 + Vite SPA
│   ├── src/
│   │   ├── api/            # HTTP 请求封装层
│   │   ├── components/     # 可复用 UI 组件
│   │   ├── locales/        # 中文文案常量（预留 i18n）
│   │   ├── pages/          # 路由页面组件
│   │   ├── router/         # Vue Router 配置（hash 模式）
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── types/          # TypeScript 类型定义
│   │   └── utils/          # 工具函数（格式化等）
│   ├── vercel.json         # Vercel SPA 路由重定向
│   └── vite.config.ts      # Vite 配置（含 Tailwind 插件）
├── server/                 # 后端 — FastAPI
│   ├── api/                # API 路由
│   ├── core/               # 核心配置（config、exceptions、logging、cache）
│   ├── external/           # 外部数据源适配（akshare）
│   ├── models/             # Pydantic/Beanie 数据模型
│   ├── repositories/       # MongoDB 数据访问层
│   └── services/           # 业务逻辑层
├── .docs/                  # 项目文档
│   ├── prd/                # 产品需求文档
│   ├── adr/                # 架构决策记录
│   └── tasks/              # 开发任务拆分明细
└── README.md
```

## 部署

- **前端**：Vercel（`vercel.json` 配置 SPA 路由重定向）
- **后端**：Render（`render.yaml` 配置 Web Service）
- **数据库**：MongoDB Atlas（M0 免费层，512MB）

## 用户流程

```
输入基金代码 → 确认基金信息 → 点击「刷新计算」→ 等待加载 → 展示结果
```

MVP 结果展示涵盖 8 项指标：最新净值、日涨跌幅、七日年化、万份收益、近1月收益、近3月最大回撤、10年期国债收益率、信用利差。
