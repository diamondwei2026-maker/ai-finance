# 测试用例 — Task 4.1: 后端 CORS 配置与 Render 部署

> 共 25 个测试用例，覆盖 CORS 中间件、Render 部署配置、环境变量、部署验证四大维度。

---

## 一、CORS 中间件配置（SUB-4.1.1）

### TC-001: 开发环境 CORS — 本地 localhost 允许跨域
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.1-1, SUB-4.1.1-3
- **前置条件**: 
  - 后端服务运行在 `localhost:8000`
  - `CORS_ORIGINS` 未设置或设置为默认值 `http://localhost:5173`
- **输入**:
  - 请求来源 Origin: `http://localhost:5173`
  - 请求方法: GET
  - 请求路径: `/api/v1/funds/000001`
- **执行步骤**:
  1. 启动后端服务 `uvicorn api.main:app --host 0.0.0.0 --port 8000`
  2. 使用浏览器或 curl 从前端地址 `http://localhost:5173` 发起跨域 GET 请求
  3. 检查响应头中的 CORS 相关字段
- **预期输出**:
  - HTTP 状态码: 200
  - 响应头包含 `Access-Control-Allow-Origin: http://localhost:5173`
  - 响应头包含 `Access-Control-Allow-Credentials: true`
  - 响应体正常返回基金信息
- **清理**: 无

### TC-002: 生产环境 CORS — 通过环境变量 CORS_ORIGINS 配置白名单
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.1-2, SUB-4.1.1-4
- **前置条件**: 
  - 设置环境变量 `CORS_ORIGINS=https://your-app.vercel.app`
  - 后端服务启动
- **输入**:
  - 请求来源 Origin: `https://your-app.vercel.app`
  - 请求方法: GET
  - 请求路径: `/`
- **执行步骤**:
  1. 设置 `CORS_ORIGINS=https://your-app.vercel.app`
  2. 启动后端服务
  3. 从 `https://your-app.vercel.app` 发起跨域请求
  4. 从其他 Origin（如 `http://evil.com`）发起跨域请求
- **预期输出**:
  - `https://your-app.vercel.app` 请求成功，响应头 `Access-Control-Allow-Origin: https://your-app.vercel.app`
  - 非白名单 Origin 请求失败，响应头中无 `Access-Control-Allow-Origin`（或被拒绝）
- **清理**: 清除环境变量

### TC-003: CORS 多源白名单 — 逗号分隔多域名
- **类型**: 边界测试
- **关联验收标准**: SUB-4.1.1-2
- **前置条件**: 
  - 设置环境变量 `CORS_ORIGINS=https://app1.vercel.app,https://app2.vercel.app`
- **输入**:
  - Origin 1: `https://app1.vercel.app`
  - Origin 2: `https://app2.vercel.app`
  - Origin 3: `https://app3.vercel.app`（不在白名单）
- **执行步骤**:
  1. 设置 `CORS_ORIGINS` 含两个域名
  2. 分别以三个 Origin 发起 GET 请求到 `/`
  3. 检查每个请求的 CORS 响应头
- **预期输出**:
  - Origin 1、2 返回正确的 `Access-Control-Allow-Origin`
  - Origin 3 无 CORS 头，浏览器拦截
- **清理**: 清除环境变量

### TC-004: CORS 允许方法 — GET/POST/OPTIONS 通过
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.1-1（允许方法：GET、POST、OPTIONS）
- **前置条件**: 
  - `CORS_ORIGINS=http://localhost:5173`，后端服务运行
- **输入**:
  - 请求方法: GET、POST、OPTIONS（各一次）
  - Origin: `http://localhost:5173`
- **执行步骤**:
  1. 发起 OPTIONS 预检请求到 `/api/v1/calculations`，带 `Access-Control-Request-Method: POST`
  2. 发起 GET 请求到 `/api/v1/funds/000001`
  3. 发起 POST 请求到 `/api/v1/calculations`
- **预期输出**:
  - OPTIONS 预检: 200，响应头 `Access-Control-Allow-Methods` 包含 GET, POST, OPTIONS
  - GET 请求: 200，正常返回
  - POST 请求: 正常处理（或 422 因无 body，但不被 CORS 拒绝）
- **清理**: 无

### TC-005: CORS 拒绝非允许方法（如 PUT/DELETE）
- **类型**: 异常测试
- **关联验收标准**: SUB-4.1.1-1（仅允许 GET、POST、OPTIONS）
- **前置条件**: 
  - `CORS_ORIGINS=http://localhost:5173`，后端服务运行
- **输入**:
  - 请求方法: PUT
  - Origin: `http://localhost:5173`
  - 请求路径: `/api/v1/funds/000001`
- **执行步骤**:
  1. 发起 OPTIONS 预检，`Access-Control-Request-Method: PUT`
  2. 检查预检响应
- **预期输出**:
  - OPTIONS 预检响应中 `Access-Control-Allow-Methods` 不包含 PUT
  - 浏览器拦截 PUT 请求（或返回 CORS 错误）
- **清理**: 无

### TC-006: CORS 允许头 — Content-Type 白名单
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.1-1（允许头部：Content-Type）
- **前置条件**: 
  - `CORS_ORIGINS=http://localhost:5173`，后端服务运行
- **输入**:
  - 预检请求带 `Access-Control-Request-Headers: Content-Type`
  - 实际 POST 请求带 `Content-Type: application/json`
- **执行步骤**:
  1. 发起 OPTIONS 预检，带 `Access-Control-Request-Headers: Content-Type`
  2. 发起 POST 请求，带 `Content-Type: application/json` body
- **预期输出**:
  - OPTIONS 响应头 `Access-Control-Allow-Headers` 包含 Content-Type
  - POST 请求正常处理
- **清理**: 无

### TC-007: CORS 拒绝非白名单请求头
- **类型**: 异常测试
- **关联验收标准**: SUB-4.1.1-1（仅允许 Content-Type）
- **前置条件**: 
  - `CORS_ORIGINS=http://localhost:5173`，后端服务运行
- **输入**:
  - 预检请求带 `Access-Control-Request-Headers: X-Custom-Header`
- **执行步骤**:
  1. 发起 OPTIONS 预检，带非白名单头 `X-Custom-Header`
  2. 检查预检响应
- **预期输出**:
  - OPTIONS 响应头 `Access-Control-Allow-Headers` 不包含 `X-Custom-Header`
  - 浏览器拦截后续实际请求
- **清理**: 无

### TC-008: CORS — 未设置 CORS_ORIGINS 时的降级行为
- **类型**: 边界测试
- **关联验收标准**: SUB-4.1.1-3
- **前置条件**: 
  - 不设置 `CORS_ORIGINS` 环境变量（使用默认值）
- **输入**:
  - Origin: `http://localhost:5173`
- **执行步骤**:
  1. 确保 `CORS_ORIGINS` 未设置
  2. 启动后端服务
  3. 从 `localhost:5173` 发起请求
- **预期输出**:
  - 使用默认值 `["http://localhost:5173"]`，跨域请求正常
- **清理**: 无

---

## 二、Render 部署配置（SUB-4.1.2）

### TC-009: render.yaml 文件存在且结构正确
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.2-1
- **前置条件**: 无
- **输入**: 检查文件系统中的 `render.yaml`
- **执行步骤**:
  1. 确认 `render.yaml` 文件存在于后端项目根目录
  2. 使用 YAML 解析器验证文件格式
  3. 检查关键字段
- **预期输出**:
  - 文件存在且为合法 YAML
  - `services[0].type` = `web`
  - `services[0].runtime` = 正确的 Python 版本
  - `services[0].buildCommand` 包含 `pip install -r requirements.txt`
  - `services[0].startCommand` 包含 `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- **清理**: 无

### TC-010: render.yaml 环境变量占位
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.2-3
- **前置条件**: 无
- **输入**: 检查 `render.yaml` 的 envVars 段
- **执行步骤**:
  1. 读取 `render.yaml` 的环境变量定义
  2. 确认关键变量是否声明（可设为 sync: false 或 explainer 说明）
- **预期输出**:
  - `MONGODB_URL` 被声明为环境变量（含说明注释或 `sync: false`）
  - `CORS_ORIGINS` 被声明为环境变量
  - 无硬编码的敏感值
- **清理**: 无

### TC-011: render.yaml startCommand 使用 $PORT 动态端口
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.2-2
- **前置条件**: 无
- **输入**: 检查 `render.yaml` 的 `startCommand`
- **执行步骤**:
  1. 读取 `startCommand` 字段
  2. 确认端口部分使用了 `$PORT` 引用
- **预期输出**:
  - startCommand 中包含 `--port $PORT`（不是硬编码端口号如 8000）
- **清理**: 无

### TC-012: requirements.txt 与 render.yaml buildCommand 路径一致
- **类型**: 集成测试
- **关联验收标准**: SUB-4.1.2-4
- **前置条件**: `requirements.txt` 存在于项目根目录
- **输入**: 检查 `render.yaml` 的 `buildCommand` 路径
- **执行步骤**:
  1. 读取 `render.yaml` 中 `buildCommand` 指定的 requirements.txt 路径
  2. 验证该路径的文件存在
  3. 验证 `requirements.txt` 包含 FastAPI、uvicorn、beanie、akshare 等核心依赖
- **预期输出**:
  - buildCommand 路径指向真实存在的 requirements.txt
  - requirements.txt 包含所有必需依赖
- **清理**: 无

### TC-013: render.yaml 缺失时的行为 — 无法部署
- **类型**: 异常测试
- **关联验收标准**: SUB-4.1.2-1
- **前置条件**: 删除 `render.yaml`（模拟缺失）
- **输入**: Render Dashboard 中没有 `render.yaml` 的仓库
- **执行步骤**:
  1. 移除 `render.yaml`
  2. 尝试 Push 到 Render 关联的 Git 仓库
  3. 观察 Render 是否自动检测到项目配置
- **预期输出**:
  - 缺少 `render.yaml` 时，Render 无法自动配置（或需手动配置）
  - Task 完成后 `render.yaml` 存在，Render 自动识别
- **清理**: 恢复 `render.yaml`

---

## 三、环境变量配置（SUB-4.1.3）

### TC-014: .env.example 包含所有必需变量
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.3-1
- **前置条件**: 无
- **输入**: 读取 `.env.example` 文件
- **执行步骤**:
  1. 检查 `.env.example` 中变量列表
  2. 逐一核对是否有 `MONGODB_URL`、`CORS_ORIGINS`、`ENVIRONMENT`、`LOG_LEVEL`
- **预期输出**:
  - 所有 4 个变量均存在
  - `MONGODB_URL` 有示例值及说明
  - `CORS_ORIGINS` 有开发/生产环境的示例
  - `ENVIRONMENT` 有 development / production 选项说明
  - `LOG_LEVEL` 有 DEBUG / INFO / WARNING 选项说明
- **清理**: 无

### TC-015: .env.example 每个变量有中文注释说明
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.3-2
- **前置条件**: 无
- **输入**: 读取 `.env.example`
- **执行步骤**:
  1. 统计文件中所有环境变量
  2. 检查每个变量上方是否有 `# ` 开头的注释行
  3. 验证注释语言和内容
- **预期输出**:
  - 每个环境变量均有上方注释说明其用途
  - 关键变量注释包含默认值说明
  - 注释使用中文
- **清理**: 无

### TC-016: ENVIRONMENT 变量的可接受值
- **类型**: 边界测试
- **关联验收标准**: SUB-4.1.3-1
- **前置条件**: 设置 `ENVIRONMENT` 为不同值
- **输入**:
  - 值 1: `development`
  - 值 2: `production`
  - 值 3: `staging`（非标准值）
- **执行步骤**:
  1. 分别设置 `ENVIRONMENT=development`、`production`、`staging`
  2. 启动后端服务
  3. 检查服务日志级别和 CORS 行为
- **预期输出**:
  - `development`: 日志详细（DEBUG 级别），CORS 宽松
  - `production`: 日志精简（INFO 级别），CORS 仅限白名单
  - `staging`: 取默认行为（如视为 development），不崩溃
- **清理**: 清除环境变量

### TC-017: 缺失 MONGODB_URL 时应用降级启动
- **类型**: 异常测试
- **关联验收标准**: SUB-4.1.3-1
- **前置条件**: 
  - 不设置 `MONGODB_URL`（但代码中该字段为必填）
- **输入**: 启动时缺少 `MONGODB_URL`
- **执行步骤**:
  1. 删除或注释 .env 中的 `MONGODB_URL`
  2. 启动后端服务
  3. 检查根路径 `/` 是否仍可访问
- **预期输出**:
  - 健康检查 `/` 返回 200（应用不因数据库缺失完全崩溃）
  - 日志输出 MongoDB 连接失败的警告
  - 或 Pydantic 抛出 ValidationError 阻止启动（取决于设计决策，记录实际行为）
- **清理**: 恢复 `MONGODB_URL`

### TC-018: LOG_LEVEL 控制日志输出级别
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.3-1
- **前置条件**: 日志模块支持 LOG_LEVEL 配置
- **输入**:
  - `LOG_LEVEL=DEBUG`
  - `LOG_LEVEL=INFO`
  - `LOG_LEVEL=ERROR`
- **执行步骤**:
  1. 分别设置 `LOG_LEVEL` 为 DEBUG、INFO、ERROR
  2. 发起一次 API 请求
  3. 检查日志输出内容
- **预期输出**:
  - `DEBUG`: 输出详细请求/响应日志
  - `INFO`: 输出请求摘要和关键事件
  - `ERROR`: 仅输出错误日志
- **清理**: 清除环境变量

---

## 四、部署验证（SUB-4.1.3）

### TC-019: 健康检查端点 `/` 返回 200
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.2-5
- **前置条件**: 后端服务启动
- **输入**: GET 请求到 `/`
- **执行步骤**:
  1. 本地启动后端服务
  2. `curl http://localhost:8000/`
- **预期输出**:
  - HTTP 状态码: 200
  - 响应体: `{"status": "ok"}`
  - Content-Type: `application/json`
- **清理**: 无

### TC-020: 健康检查不依赖数据库
- **类型**: 集成测试
- **关联验收标准**: SUB-4.1.2-5
- **前置条件**: MongoDB 不可用（如未设置 MONGODB_URL 或数据库离线）
- **输入**: GET 请求到 `/`
- **执行步骤**:
  1. 断开 MongoDB 连接（或使用无效 URL）
  2. 启动后端服务
  3. 访问 `/`
- **预期输出**:
  - HTTP 状态码: 200
  - 不因数据库连接失败而崩溃
  - 日志中有关"降级模式"相关警告
- **清理**: 恢复数据库连接

### TC-021: Render 部署后 Swagger `/docs` 可访问
- **类型**: 集成测试
- **关联验收标准**: SUB-4.1.3-4
- **前置条件**: 后端已成功部署到 Render
- **输入**: GET 请求到 `https://<render-app>.onrender.com/docs`
- **执行步骤**:
  1. 部署完成后获取 Render 公网 URL
  2. 浏览器访问 `/docs`
  3. 检查 Swagger UI 是否正常加载
- **预期输出**:
  - HTTP 状态码: 200
  - Swagger UI 完整展示所有 API 端点
  - `/api/v1/funds/{code}`、`/api/v1/calculations` 等端点可见
- **清理**: 无

### TC-022: Render 部署后 API 请求正常处理
- **类型**: 集成测试
- **关联验收标准**: SUB-4.1.3-4
- **前置条件**: 后端已成功部署到 Render，MongoDB 配置正确
- **输入**: 
  - GET 请求到 `https://<render-app>.onrender.com/api/v1/funds/000001`
- **执行步骤**:
  1. 获取 Render 公网 URL
  2. `curl https://<render-app>.onrender.com/api/v1/funds/000001`
- **预期输出**:
  - HTTP 状态码: 200
  - 响应体包含基金信息 JSON
- **清理**: 无

### TC-023: Render 冷启动后可用
- **类型**: 功能测试
- **关联验收标准**: SUB-4.1.3-4
- **前置条件**: 后端部署在 Render 免费层（冷启动 5-10s）
- **输入**: 长时间未访问后的首次请求
- **执行步骤**:
  1. 等待 Render 服务休眠（约 15 分钟无请求）
  2. 发起新的 HTTP 请求
  3. 记录响应时间
- **预期输出**:
  - 首次请求可能延迟 5-10 秒
  - 最终返回 200（不超时 504）
  - 后续请求响应快速
- **清理**: 无

---

## 五、端到端与安全

### TC-024: CORS + Render 端到端 — 前端成功跨域调用
- **类型**: 集成测试
- **关联验收标准**: 全部
- **前置条件**: 
  - 后端已部署到 Render，`CORS_ORIGINS` 包含前端 Vercel 域名
  - 前端已部署到 Vercel
- **输入**: 
  - 从 Vercel 前端发起 `GET /api/v1/funds/000001`
- **执行步骤**:
  1. 在 Vercel 前端页面的浏览器 Console 中执行 fetch 请求
  2. 检查 Network 面板中的请求/响应
- **预期输出**:
  - 请求不被 CORS 阻止
  - 正常返回基金数据
  - `Access-Control-Allow-Origin` 匹配前端域名
- **清理**: 无

### TC-025: 敏感信息不通过响应头泄露
- **类型**: 安全测试
- **关联验收标准**: SUB-4.1.2-3
- **前置条件**: 后端服务运行
- **输入**: GET 请求到 `/` 和 `/api/v1/calculations`
- **执行步骤**:
  1. 发起请求
  2. 检查响应头中是否包含 `Server`、`X-Powered-By` 等可能泄露技术栈的信息
  3. 检查响应体中是否包含数据库连接串、环境变量等敏感信息
- **预期输出**:
  - 响应体中无 `MONGODB_URL`、密码等敏感信息
  - 可选：隐藏 `Server` 头或设为通用值
- **清理**: 无

---

## 测试用例统计

| 维度 | 数量 | 用例编号 |
|------|------|---------|
| 功能测试 | 13 | TC-001~004, TC-006, TC-009~011, TC-014, TC-015, TC-018, TC-019, TC-023 |
| 边界测试 | 3 | TC-003, TC-008, TC-016 |
| 异常测试 | 4 | TC-005, TC-007, TC-013, TC-017 |
| 集成测试 | 4 | TC-012, TC-020~022, TC-024 |
| 安全测试 | 1 | TC-025 |
