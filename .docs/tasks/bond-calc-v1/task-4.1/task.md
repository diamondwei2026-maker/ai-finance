# Task 4.1: 后端 CORS 配置与 Render 部署

| 属性 | 值 |
|------|-----|
| ID | 4.1 |
| 状态 | pending |
| 优先级 | P0 |
| 依赖 | 2.2 |
| 阶段 | 阶段4: 联调部署 |
| 预估工时 | 2-3 小时 |

## 描述

配置后端 CORS（开发环境 + 生产环境），编写 Render 部署配置文件（`render.yaml`），设置环境变量，确保后端服务可通过 Render 公网访问。

## 验收标准

- [ ] `api/main.py` 中 CORS 中间件配置完成：
  - 开发环境：允许 `localhost:5173`
  - 生产环境：通过环境变量 `CORS_ORIGINS` 配置白名单
  - 允许的方法：GET、POST、OPTIONS
  - 允许的头部：Content-Type
- [ ] `render.yaml` 创建于后端项目根目录：
  - `type: web`，Python 运行时
  - `buildCommand: pip install -r requirements.txt`
  - `startCommand: uvicorn api.main:app --host 0.0.0.0 --port $PORT`
  - 环境变量占位：`MONGODB_URL`、`CORS_ORIGINS`
- [ ] `.env.example` 更新，包含所有必需环境变量及说明注释
- [ ] 后端服务在 Render 上成功部署，健康检查 `/` 返回 200
- [ ] Swagger 文档 `/docs` 可通过 Render 公网 URL 访问

## 子任务

### SUB-4.1.1: CORS 配置
- **描述**: 配置 FastAPI CORS 中间件
- **验收标准**:
  - [ ] 使用 `fastapi.middleware.cors.CORSMiddleware`
  - [ ] `allow_origins` 从环境变量 `CORS_ORIGINS` 读取（逗号分隔）
  - [ ] 本地开发默认允许 `http://localhost:5173`
  - [ ] 生产部署通过 Render 环境变量配置 Vercel 域名

### SUB-4.1.2: Render 部署配置
- **描述**: 编写 render.yaml 和部署文档
- **验收标准**:
  - [ ] `render.yaml` 位于后端根目录（或项目根目录），配置正确
  - [ ] `startCommand` 端口使用 `$PORT`（Render 动态分配）
  - [ ] 所有敏感配置（MONGODB_URL 等）通过环境变量注入，不硬编码
  - [ ] `requirements.txt` 位于项目根目录或 `render.yaml` 中指定路径
  - [ ] Render 部署后 `/` 返回 `{"status": "ok"}`

### SUB-4.1.3: 环境变量与部署验证
- **描述**: 完善环境变量模板并验证部署
- **验收标准**:
  - [ ] `.env.example` 含所有变量：`MONGODB_URL`、`CORS_ORIGINS`、`ENVIRONMENT`、`LOG_LEVEL`
  - [ ] 每个变量有中文注释说明用途和默认值
  - [ ] Render Dashboard 中配置对应环境变量
  - [ ] 通过 Render URL 访问 Swagger 文档正常
