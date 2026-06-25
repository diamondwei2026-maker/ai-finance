# 债券收益计算工具 — 后端架构决策记录

| 属性 | 值 |
|------|-----|
| 版本 | v1.0 |
| 状态 | 草稿 |
| 作者 | Claude (ADR Architect) |
| 日期 | 2025-06-25 |
| 关联文档 | [前端 ADR](./client.md) |

## 1. 需求概述

### 1.1 项目名称
**债券收益计算工具**（Bond Yield Calculation Tool）

### 1.2 目标用户
个人债券基金投资者——持有债券基金，关注核心收益指标，需要快速获取数据辅助判断，操作要求简单。

### 1.3 核心功能（MVP）

| 优先级 | 功能 | 描述 |
|--------|------|------|
| P0 | 基金信息查询 | 输入 6 位基金代码 → 展示名称、类型、最新净值、七日年化 |
| P0 | 一键收益计算 | 拉取净值 + 历史数据 + 市场利率 → 计算 8 项指标 |
| P0 | 屏幕展示结果 | 格式化展示净值、七日年化、万份收益、近1月收益、最大回撤、市场利率 |

### 1.4 闭环流程
```
输入基金代码 → 确认基金 → 点击刷新计算 → 屏幕展示结果
```

### 1.5 非功能性约束
- **性能**：基金查询 ≤ 5 秒，完整计算 ≤ 2 分钟
- **合规**：展示免责声明（数据仅供参考，不构成投资建议）
- **数据来源**：仅使用公开可获取的基金数据和市场数据
- **架构**：预留扩展点，为后续版本做结构准备

### 1.6 MVP 明确不做
策略建议、推送通知、趋势图表、日内净值预估、多基金监控、多用户体系

---

## 2. 跨切面决策

### 2.1 应用形态与部署架构
- **选定方案**：Web 应用（前后端分离）
- **候选方案**：CLI 命令行工具 / Electron 桌面应用
- **选择理由**：展示效果最佳，与后续版本路线（图表 v1.1、推送 v1.3、多基金 v1.4、多用户 v2.0）高度契合，技术栈通用，后续部署服务器无需重构
- **部署目标**：后端 Render，前端 Vercel
- **影响范围**：前后端均受影响——后端提供 HTTP API，前端为独立 Web 应用

### 2.2 基金与市场数据源
- **选定方案**：akshare（Python 开源金融数据库）
- **候选方案**：直接调用公开 API / 自建爬虫
- **选择理由**：一次接入覆盖 3-4 个上游数据源（天天基金、东方财富、中债信息网），API 稳定由社区维护，代码量最小，保留降级为直连的灵活性
- **影响范围**：锁定后端语言为 Python（akshare 仅支持 Python）

### 2.3 后端 Web 框架
- **选定方案**：FastAPI
- **候选方案**：Flask / Django
- **选择理由**：异步原生支持（多数据源并发拉取缩短总耗时 50%+），自动生成 Swagger 文档便于前后端联调，Type-hints 驱动参数校验，WebSocket 原生支持（v1.3 推送用）
- **影响范围**：前后端均受影响——API 文档自动生成，前端可直接参考 Swagger 定义

### 2.4 数据持久化方案
- **选定方案**：MongoDB Atlas（云托管）+ Beanie ODM
- **候选方案**：零持久化 / SQLite + SQLAlchemy 双模
- **选择理由**：Atlas 免费层 512MB 永久免费，满足 MVP；Beanie 与 FastAPI + Pydantic 技术栈天然一体；本地开发零配置（直连 Atlas）；部署无需管理数据库实例
- **影响范围**：后端数据层基于文档模型设计，前端无直接影响

### 2.5 API 风格与规范
- **选定方案**：RESTful API
- **候选方案**：RESTful + JSON-RPC 混合 / GraphQL
- **选择理由**：MVP 2-3 个端点完全够用；FastAPI 对 REST 支持最好；"触发计算"用 `POST /calculations` 表达清晰（创建计算结果资源）；版本策略为 URL 路径版本 `GET /api/v1/...`
- **影响范围**：前端请求封装遵循 REST 约定；后续 WebSocket 作为独立端点补充

### 2.6 缓存策略
- **选定方案**：内存缓存（TTLCache）+ MongoDB 兜底
- **候选方案**：仅 MongoDB 查重 / Redis
- **选择理由**：单用户单进程场景，内存缓存延迟 <1ms，最适合 MVP；基金基础信息 TTL 30 分钟，收益计算 TTL 5 分钟，市场利率 TTL 2 分钟；MongoDB 存结构化结果用于后续历史查询，与内存缓存各司其职
- **影响范围**：后端缓存层为独立模块，后续多实例部署时可替换为 Redis

---

## 3. 技术选型

### 3.1 编程语言与框架
- **选定方案**：Python 3.11+ / FastAPI / Uvicorn
- **约束来源**：akshare 仅支持 Python；FastAPI 是 Python 异步 Web 框架的最优选择

### 3.2 数据库
- **选定方案**：MongoDB Atlas（免费层 M0）+ Beanie ODM
- **候选对比**：

| 维度 | MongoDB Atlas + Beanie | SQLite + SQLAlchemy | PostgreSQL + SQLAlchemy |
|------|----------------------|---------------------|------------------------|
| 部署复杂度 | 零配置（云托管） | 零配置（单文件） | 需管理实例 |
| 免费额度 | 512MB 永久免费 | 无限制（本地） | Render 90 天 / Supabase 500MB |
| Python 集成 | Beanie（异步原生） | SQLAlchemy + aiosqlite | SQLAlchemy + asyncpg |
| 数据模型灵活性 | 文档模型，Schema-less | 关系模型，需建表 | 关系模型，需建表 |

- **选择理由**：云托管零部署负担，文档模型与基金数据（嵌套结构、指标字段灵活性高）天然匹配，免费额度足够 MVP + 多版本迭代

### 3.3 数据访问层
- **选定方案**：Beanie ODM
- **选择理由**：Motor（MongoDB 异步驱动）上层封装；与 Pydantic 模型共用定义；语法接近 SQLAlchemy 体验；内置索引生成和迁移支持

### 3.4 异步 HTTP 客户端
- **选定方案**：httpx（异步模式）
- **选择理由**：akshare 底层基于 requests（同步），在 service 层使用 `httpx.AsyncClient` 并发调用多个数据源，通过 `asyncio.gather` 实现并行获取

### 3.5 交易日历
- **选定方案**：exchange_calendars
- **选择理由**：覆盖上交所/深交所交易日历，`is_session()` 一行判断，BR-01 交易日判定需求直接满足

### 3.6 日志方案
- **选定方案**：loguru
- **选择理由**：一行配置即用，彩色终端输出 + 文件归档，零样板代码

---

## 4. 架构设计

### 4.1 分层架构

```
┌─────────────────────────────────────────┐
│                  客户端                   │
│           (Vue 3 + Vite SPA)             │
└──────────────┬──────────────────────────┘
               │ HTTP (RESTful API)
┌──────────────▼──────────────────────────┐
│           api/routes/  (路由层)           │
│  GET  /api/v1/funds/{code}              │
│  POST /api/v1/calculations              │
│  GET  /api/v1/calculations/{id}         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         services/  (业务层)              │
│  fund_service    — 基金信息查询与校验     │
│  calculation_service — 收益指标计算编排   │
│  market_service  — 市场利率数据获取       │
└──────┬──────────────┬───────────────────┘
       │              │
┌──────▼──────┐ ┌─────▼───────────────────┐
│ repositories│ │ external/               │
│ fund_repo   │ │ akshare 数据源适配       │
│ market_repo │ │ (天天基金/东方财富/中债)  │
└──────┬──────┘ └─────────────────────────┘
       │
┌──────▼──────────────────────────────────┐
│         MongoDB Atlas (数据层)           │
│  funds / calculations / market_data     │
└─────────────────────────────────────────┘
```

### 4.2 模块划分

| 模块 | 路径 | 职责 |
|------|------|------|
| 入口 | `api/main.py` | FastAPI 应用实例化，CORS 配置，路由注册 |
| 路由-基金 | `api/routes/funds.py` | 基金查询接口 |
| 路由-计算 | `api/routes/calculations.py` | 计算触发与结果查询接口 |
| 业务-基金 | `services/fund_service.py` | 基金信息校验、类型判断 |
| 业务-计算 | `services/calculation_service.py` | 编排 8 项指标计算流程，交易日判断 |
| 业务-市场 | `services/market_service.py` | 市场利率数据获取与处理 |
| 数据-基金 | `repositories/fund_repo.py` | 基金 MongoDB 文档 CRUD |
| 数据-市场 | `repositories/market_repo.py` | 市场数据 MongoDB 文档 CRUD |
| 外部适配 | `external/data_fetcher.py` | akshare 调用封装，数据源异常处理 |
| 模型 | `models/` | Pydantic/Beanie 文档模型定义 |
| 核心 | `core/config.py` | 配置管理（环境变量、数据库连接串、TTL 常量） |
| 核心 | `core/cache.py` | TTLCache 封装（基金信息 30min / 计算结果 5min / 市场利率 2min） |
| 核心 | `core/exceptions.py` | RecoverableError / FatalError 异常类定义 |
| 核心 | `core/logging.py` | loguru 配置（彩色输出 + `logs/bond_tool.log` 文件归档） |

---

## 5. 接口设计

### 5.1 API 风格与规范
- **风格**：RESTful
- **版本策略**：URL 路径版本 `/api/v1/`
- **命名规范**：资源名复数，小写下划线（`funds`, `calculations`）
- **响应格式**：
  ```json
  {
    "code": 0,
    "message": "success",
    "data": { ... }
  }
  ```
- **错误响应**：
  ```json
  {
    "code": 40001,
    "message": "未找到该基金（代码：XXXXXX），请检查后重新输入",
    "data": null
  }
  ```

### 5.2 核心接口列表

| 方法 | 路径 | 说明 | 请求/响应要点 |
|------|------|------|--------------|
| GET | `/api/v1/funds/{code}` | 查询基金基本信息 | 返回名称、类型、最新净值、七日年化；非债券型返回 type_mismatch |
| POST | `/api/v1/calculations` | 触发收益计算 | 请求体 `{"fund_code": "020741"}`；返回计算任务 ID |
| GET | `/api/v1/calculations/{id}` | 获取计算结果 | 返回 8 项指标 + 数据时效性标注 + 交易日状态 |

### 5.3 响应字段说明

```json
{
    "fund_name": "华泰保兴安悦债券C",
    "fund_code": "020741",
    "fund_type": "中长期纯债",
    "nav": 1.0234,
    "daily_change_pct": 0.02,
    "seven_day_annual_yield": 3.82,
    "wanfen_income": 0.85,
    "one_month_return": 0.31,
    "three_month_max_drawdown": 0.45,
    "ten_year_treasury": 2.68,
    "credit_spread_aa_plus": 58,
    "data_date": "2025-06-23",
    "is_trading_day": true,
    "disclaimer": "本工具提供的收益数据基于公开数据计算，仅供参考，不构成投资建议。投资有风险，操作需谨慎。"
}
```

---

## 6. 数据模型

### 6.1 核心实体
- **Fund（基金）** — 基金基本信息，以 `fund_code` 为唯一标识
- **Calculation（计算结果）** — 一次计算产生的完整指标快照，关联基金代码
- **MarketData（市场数据）** — 10年期国债收益率、信用利差，有时间戳

### 6.2 核心集合结构

| 集合 | 核心字段 | 索引策略 | 说明 |
|------|---------|---------|------|
| `funds` | `fund_code`, `name`, `type`, `updated_at` | `fund_code` 唯一索引 | 基金基本信息缓存 |
| `calculations` | `fund_code`, `nav`, `daily_change_pct`, `seven_day_annual_yield`, `wanfen_income`, `one_month_return`, `three_month_max_drawdown`, `ten_year_treasury`, `credit_spread_aa_plus`, `data_date`, `is_trading_day`, `created_at` | `fund_code` + `created_at` 复合索引 | 每次计算的完整结果快照 |
| `market_data` | `indicator_name`, `value`, `unit`, `fetched_at` | `indicator_name` + `fetched_at` 复合索引 | 市场利率数据时间序列 |

### 6.3 Beanie 文档模型示例

```python
from beanie import Document, Indexed
from datetime import datetime
from pydantic import BaseModel

class Fund(Document):
    fund_code: Indexed(str, unique=True)
    name: str
    fund_type: str
    updated_at: datetime

    class Settings:
        name = "funds"

class Calculation(Document):
    fund_code: str
    nav: float | None = None
    daily_change_pct: float | None = None
    seven_day_annual_yield: float | None = None
    wanfen_income: float | None = None
    one_month_return: float | None = None
    three_month_max_drawdown: float | None = None
    ten_year_treasury: float | None = None
    credit_spread_aa_plus: float | None = None
    data_date: str
    is_trading_day: bool
    created_at: datetime

    class Settings:
        name = "calculations"
        indexes = [
            [("fund_code", 1), ("created_at", -1)],
        ]
```

---

## 7. 非功能性设计

### 安全
- **CORS**：仅允许前端 Vercel 域名（生产）或 `localhost:5173`（开发）
- **认证**：MVP 阶段无用户体系，无需认证
- **环境变量**：MongoDB 连接串、CORS 域名等敏感配置通过 `.env` 注入，不提交代码仓库
- **输入校验**：基金代码格式校验（6 位数字），FastAPI + Pydantic 自动校验

### 性能
- **并发拉取**：`asyncio.gather` 并行请求 3-4 个外部数据源，串行 6-8s → 并行 2-3s
- **内存缓存**：TTLCache 分级缓存，命中时 <1ms 返回
- **数据库连接**：MongoDB Atlas 连接池（默认 100 连接上限，满足单用户工具需求）
- **按需索引**：仅建必要索引（fund_code 唯一索引、时间复合索引），避免写入性能损耗

### 可扩展性
- **无状态设计**：后端服务不持有会话状态，天然支持水平扩展（未来多实例部署）
- **分层架构**：router → service → repository 三层解耦，新功能加文件不动老代码
- **配置外置**：所有可变参数（TTL、数据库 URL、CORS）通过环境变量管理
- **缓存可替换**：内存缓存封装为独立模块（`core/cache.py`），未来可替换为 Redis

### 可观测性
- **日志**：loguru 彩色终端输出 + `logs/bond_tool.log` 文件归档（10MB 轮转）
- **异常分级**：
  - `RecoverableError`：单个数据源失败 → 记录 WARNING 日志，该指标标 N/A
  - `FatalError`：所有数据源全挂 → 记录 ERROR 日志，返回 503
- **请求追踪**：每个请求自动记录方法、路径、耗时、状态码（FastAPI 中间件）

---

## 8. 风险与权衡

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| akshare 上游数据源接口变动 | 高 | 中 | 异常分级（单源失败标 N/A）；`external/data_fetcher.py` 封装隔离变化；保留直连 API 降级路径 |
| MongoDB Atlas 免费层超限或降级 | 低 | 低 | 512MB 对 MVP 绰绰有余；数据模型设计精简（仅 3 个集合）；未来可迁移至 Supabase PG |
| Render 免费层服务休眠（15 分钟无请求） | 低 | 中 | 冷启动延迟可接受（5-10s）；告诉用户首次访问稍等；后续可升级 Render 付费或迁移 |
| akshare 版本更新导致不兼容 | 中 | 低 | `requirements.txt` 锁定版本；升级前本地验证 |
| 交易日历库节假日数据更新延迟 | 低 | 低 | 默认按非交易日处理（保守策略）；用户仍可手动触发计算 |

### 权衡记录
- **选择 FastAPI + MongoDB + Beanie** 意味着获得异步性能、文档模型灵活性、零运维数据库，**但放弃了** SQL 生态的成熟 ORM（SQLAlchemy）、复杂聚合查询的便利性（MongoDB 聚合管道学习成本高）
- **选择 akshare** 意味着获得多数据源统一接入、社区维护，**但放弃了** 数据源的完全自主可控——上游接口变动需等社区修复
- **选择内存缓存而非 Redis** 意味着 MVP 部署零额外组件，**但放弃了** 跨进程/跨实例的缓存共享能力——未来多实例部署时需替换
- **如果 Render 免费层不稳定**，可能需要重新评估部署方案（Railway / Fly.io 等替代平台）

---

## 9. 实施建议

### 第一阶段：项目骨架
- 初始化 FastAPI 项目，分层目录结构
- 配置 loguru、环境变量管理
- MongoDB Atlas 连接 + Beanie 初始化
- 核心异常类 + 缓存模块

### 第二阶段：数据层
- akshare 数据源适配（`external/data_fetcher.py`）
- 基金信息查询接口（`GET /api/v1/funds/{code}`）
- 交易日历集成
- 数据校验与异常处理

### 第三阶段：计算引擎
- 收益计算编排服务（并行拉取 + 指标计算）
- 计算触发与结果查询接口（`POST/GET /api/v1/calculations`）
- 结果缓存策略

### 第四阶段：部署与联调
- CORS 配置
- Render 部署配置（`render.yaml` + 环境变量）
- 与前端联调，Swagger 文档验证
- 免责声明与合规文字植入

### 依赖关系
```
阶段 1（骨架）
  └─→ 阶段 2（数据层）
        └─→ 阶段 3（计算引擎）
              └─→ 阶段 4（部署联调）
```

| 里程碑 | 关键产出 | 预估工作量 |
|--------|---------|-----------|
| 骨架完成 | `main.py` + 分层目录 + 配置 + 日志 | 0.5 天 |
| 数据层完成 | 基金查询 API 可用，外部数据源打通 | 1 天 |
| 计算引擎完成 | 8 项指标计算全部跑通 | 1 天 |
| 部署联调完成 | Render 可访问，前端对接成功 | 0.5 天 |

### 关键依赖
- **akshare** 需在目标 Python 环境中成功安装（依赖体积约 70MB）
- **MongoDB Atlas** 需提前注册账号并创建免费集群（M0）
- **Render** 需关联 GitHub 仓库并配置环境变量
