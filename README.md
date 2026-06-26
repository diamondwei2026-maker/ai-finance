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

### 1. 数据库准备

1. 注册 [MongoDB Atlas](https://www.mongodb.com/atlas)（免费 M0 集群 512MB）
2. 创建集群后，在 **Database Access** 中添加数据库用户
3. 在 **Network Access** 中添加 `0.0.0.0/0`（允许所有 IP）
4. 复制连接串：`mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority`
5. 将数据库名 `bond_tool` 拼入连接串：`...mongodb.net/bond_tool?retryWrites=true&w=majority`

### 2. 后端

```bash
cd server

# 创建 .env 文件
cp .env.example .env

# 编辑 .env，填入 MongoDB Atlas 连接串（必填）
# MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/bond_tool?retryWrites=true&w=majority

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器（--reload 模式，代码变更自动重启）
uvicorn api.main:app --reload
```

启动后访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

### 3. 前端

```bash
cd client

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 `http://localhost:5173`，前端默认请求 `http://localhost:8000` 的后端 API。

---

## 配置参数

### 后端 `.env` 变量（`server/.env`）

| 变量 | 必填 | 默认值 | 说明 |
|------|:--:|------|------|
| `MONGODB_URL` | ✅ | — | MongoDB Atlas 连接串 |
| `CORS_ORIGINS` | — | `http://localhost:5173` | 允许的前端域名（逗号分隔） |
| `ENVIRONMENT` | — | `development` | 运行环境：`development` / `production` |
| `LOG_LEVEL` | — | `DEBUG` | 日志级别：`DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `CACHE_TTL_FUND` | — | `1800` | 基金信息缓存（秒），默认 30 分钟 |
| `CACHE_TTL_CALC` | — | `300` | 计算结果缓存（秒），默认 5 分钟 |
| `CACHE_TTL_MARKET` | — | `120` | 市场利率缓存（秒），默认 2 分钟 |

### 前端环境变量（Vercel 部署时设置）

| 变量 | 必填 | 说明 |
|------|:--:|------|
| `VITE_API_BASE_URL` | ✅ | 后端 API 地址（如 `https://bond-calc-api.onrender.com`） |

> 本地开发无需设置 `VITE_API_BASE_URL`，默认使用 `http://localhost:8000`。

---

## 部署

### 后端 → Render

项目根目录的 [`render.yaml`](render.yaml) 定义了 Render Blueprint：

```yaml
services:
  - type: web
    name: bond-calc-api
    runtime: python
    buildCommand: pip install -r server/requirements.txt
    startCommand: cd server && uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MONGODB_URL
        sync: false           # 需在 Dashboard 手动填写（含密码，不入仓库）
      - key: CORS_ORIGINS
        sync: false           # 需在 Dashboard 手动填写（Vercel 域名）
      - key: ENVIRONMENT
        value: production
      - key: LOG_LEVEL
        value: INFO
```

部署步骤：

1. 将项目推送到 GitHub
2. Render Dashboard → **Blueprints** → 连接仓库
3. Render 自动识别 `render.yaml` 创建 Web Service
4. 在服务的 **Environment** 页面手动填入：
   - `MONGODB_URL`：你的 MongoDB Atlas 连接串
   - `CORS_ORIGINS`：前端 Vercel 域名（如 `https://your-app.vercel.app`）

> `sync: false` 表示该变量不从 yaml 同步，必须在 Dashboard 手动填写，避免密码泄露。

### 前端 → Vercel

[`client/vercel.json`](client/vercel.json) 配置了 SPA 路由重定向（所有路径指向 `index.html`）：

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

部署步骤：

1. 在 Vercel Dashboard → **Add Project** → 连接 GitHub 仓库
2. 设置以下参数：
   - **Root Directory**：`client`
   - **Framework Preset**：Vite
3. 在 **Environment Variables** 中添加：
   - `VITE_API_BASE_URL` = Render 后端 URL（如 `https://bond-calc-api.onrender.com`）
4. 点击 Deploy

> 也可在 `client/` 目录下运行 `npx vercel` 通过 CLI 部署。

### 数据库 → MongoDB Atlas

1. 注册 [MongoDB Atlas](https://www.mongodb.com/atlas)（免费 M0 集群，512MB 永久免费）
2. 创建集群 → **Database Access** 添加数据库用户（用户名/密码）
3. **Network Access** 添加 `0.0.0.0/0`（允许所有 IP，Render 出口 IP 不固定）
4. 点击 **Connect** → **Drivers**，复制连接串模板
5. 替换 `<password>` 并将数据库名改为 `bond_tool`：
   ```
   mongodb+srv://<user>:<password>@<cluster>.mongodb.net/bond_tool?retryWrites=true&w=majority
   ```
6. 将此连接串作为 `MONGODB_URL` 填入 Render 和本地 `.env`

---

---

## 使用指南

### 基本操作

1. 打开前端页面，在输入框中输入 **6 位基金代码**（如 `020741`）
2. 点击查询，系统展示基金基本信息（名称、类型、最新净值、七日年化）
3. 确认无误后，点击 **「刷新计算」**，系统拉取最新数据并展示 8 项收益指标

### 结果页面字段说明

| 指标 | 说明 |
|------|------|
| 最新净值 | 基金当前单位净值，每日更新 |
| 日涨跌幅 | 相比上一个交易日的净值变化百分比 |
| 七日年化 | 过去 7 天折算的年化收益率 |
| 万份收益 | 每 1 万份基金的当日收益（元） |
| 近 1 月收益 | 最近一个月的累计收益率 |
| 近 3 月最大回撤 | 最近三个月从最高点到最低点的最大跌幅 |
| 10 年期国债 | 当前 10 年期国债收益率（市场基准） |
| 信用利差 AA+ | AA+ 级别信用债与国债的利差（bp） |

### 注意事项

- 仅支持**债券型基金**，非债券基金（股票型、混合型等）将提示类型不匹配
- 非交易日（周末/节假日）数据为最近交易日数据，页面会标注"非交易日"
- 部分指标可能因数据源缺失显示 `N/A`
- 计算结果 **5 分钟内缓存**，重复请求同一基金代码直接返回已有结果
- 页面底部有**免责声明**：数据仅供参考，不构成投资建议

### API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/funds/{code}` | 查询基金基本信息 |
| POST | `/api/v1/calculations` | 触发收益计算（同步） |
| GET | `/api/v1/calculations/{id}` | 获取计算结果详情 |
| GET | `/docs` | Swagger API 文档 |
| GET | `/` | 健康检查 |

---

## 目录结构

```
ai-finance/
├── client/                     # 前端 — Vue 3 + Vite SPA
│   ├── src/
│   │   ├── api/                # HTTP 请求封装层（baseFetch + 接口函数）
│   │   │   ├── index.ts        #   fetch 封装（超时、错误处理、响应类型）
│   │   │   ├── funds.ts        #   基金查询 API
│   │   │   └── calculations.ts #   收益计算 API
│   │   ├── components/         # 可复用 UI 组件（9 个）
│   │   │   ├── SearchBar.vue       # 基金代码输入框 + 查询按钮
│   │   │   ├── FundPreview.vue     # 基金基本信息确认卡片
│   │   │   ├── ResultHeader.vue    # 基金名称 + 数据日期标注
│   │   │   ├── NavGrid.vue         # 最新净值 + 日涨跌幅
│   │   │   ├── YieldMetrics.vue    # 收益指标卡片组
│   │   │   ├── MarketRates.vue     # 市场利率展示
│   │   │   ├── RefreshButton.vue   # 刷新计算按钮
│   │   │   ├── ErrorAlert.vue      # 错误提示横幅
│   │   │   └── DisclaimerBar.vue   # 免责声明横幅
│   │   ├── locales/            # 中文文案常量（预留 i18n）
│   │   ├── pages/              # 路由页面
│   │   │   ├── FundInput.vue   #   基金代码输入页
│   │   │   └── FundResult.vue  #   计算结果展示页
│   │   ├── router/             # Vue Router 配置（hash 模式）
│   │   ├── stores/             # Pinia 状态管理
│   │   ├── types/              # TypeScript 类型定义
│   │   └── utils/              # 工具函数（格式化等）
│   ├── vercel.json             # Vercel SPA 路由重定向配置
│   └── vite.config.ts          # Vite 配置（含 Tailwind 插件）
├── server/                     # 后端 — FastAPI
│   ├── api/                    # API 层
│   │   ├── main.py             #   FastAPI 应用入口（CORS、lifespan、路由注册）
│   │   └── routes/             #   路由定义
│   │       ├── funds.py        #     GET /api/v1/funds/{code}
│   │       └── calculations.py #     POST + GET /api/v1/calculations
│   ├── core/                   # 核心模块
│   │   ├── config.py           #   配置管理（环境变量、TTL 常量）
│   │   ├── cache.py            #   TTLCache 封装
│   │   ├── exceptions.py       #   分级异常（RecoverableError / FatalError）
│   │   ├── error_codes.py      #   业务错误码常量
│   │   ├── logging.py          #   loguru 配置
│   │   └── trading_calendar.py #   交易日历
│   ├── external/               # 外部数据源适配
│   │   └── data_fetcher.py     #   akshare 调用封装
│   ├── models/                 # 数据模型
│   │   ├── fund.py             #   Beanie Fund 文档
│   │   ├── calculation.py      #   Beanie Calculation 文档
│   │   ├── market_data.py      #   Beanie MarketData 文档
│   │   └── schemas.py          #   Pydantic 请求/响应 Schema
│   ├── repositories/           # 数据访问层
│   │   ├── fund_repo.py        #   基金 MongoDB CRUD
│   │   └── market_repo.py      #   市场数据 MongoDB CRUD
│   └── services/               # 业务逻辑层
│       ├── fund_service.py     #   基金信息查询与校验
│       ├── calculation_service.py  # 收益指标计算编排
│       └── market_service.py   #   市场利率数据处理
├── .docs/                      # 项目文档
│   ├── prd/prd.md              #   产品需求文档
│   ├── adr/server.md           #   后端架构决策记录
│   ├── adr/client.md           #   前端架构决策记录
│   └── tasks/                  #   开发任务拆分明细
└── README.md
```

---

## 部署检查清单

部署前逐项确认：

- [ ] MongoDB Atlas 集群已创建，用户和网络访问已配置
- [ ] 本地 `server/.env` 中 `MONGODB_URL` 已填写，后端可正常启动
- [ ] 本地前后端联调通过（输入基金代码 → 查询 → 计算 → 展示结果）
- [ ] Render 服务 `MONGODB_URL` 已填写（不含密码明文）
- [ ] Render 服务 `CORS_ORIGINS` 已填写 Vercel 域名
- [ ] Vercel `VITE_API_BASE_URL` 指向 Render 后端
- [ ] Vercel Root Directory 设置为 `client`
- [ ] Vercel 部署后访问测试完整流程

---

## 用户流程

```
输入基金代码 → 确认基金信息 → 点击「刷新计算」→ 等待加载 → 展示结果
```

MVP 结果展示涵盖 8 项指标：最新净值、日涨跌幅、七日年化、万份收益、近1月收益、近3月最大回撤、10年期国债收益率、信用利差。
