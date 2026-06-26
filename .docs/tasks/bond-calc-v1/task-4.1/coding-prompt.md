# Coding Prompt — Task 4.1: 后端 CORS 配置与 Render 部署

---

## 1. 任务目标

配置 FastAPI 后端的 CORS 中间件（区分开发/生产环境），编写 Render 部署配置文件 `render.yaml`，补充环境变量模板，确保后端可通过 Render 公网访问。

---

## 2. 技术上下文

- **语言/框架**: Python 3.11+ / FastAPI / Uvicorn
- **配置管理**: pydantic-settings（自动从 `.env` / 环境变量加载）
- **日志**: loguru（已在 `core/logging.py` 配置）
- **部署目标**: Render（`type: web`）

### 2.1 涉及文件

| 操作 | 路径 | 说明 |
|------|------|------|
| **修改** | `server/api/main.py` | 收敛 CORS 中间件的 `allow_methods`、`allow_headers` |
| **修改** | `server/core/config.py` | 新增 `ENVIRONMENT`、`LOG_LEVEL` 配置字段 |
| **修改** | `server/core/logging.py` | 日志级别支持 `LOG_LEVEL` 字符串控制 |
| **修改** | `server/.env.example` | 补充 `ENVIRONMENT`、`LOG_LEVEL` 及完善注释 |
| **新建** | `render.yaml` | Render 部署描述文件（放项目根目录 `d:\Users\weij\ai-finance\`） |

### 2.2 已有基础设施

- `api/main.py` 已经有 `CORSMiddleware` 和 `allow_origins=settings.CORS_ORIGINS`
- 健康检查端点 `/` 已返回 `{"status": "ok"}`
- `requirements.txt` 已有所有依赖（fastapi、uvicorn、beanie 等）
- `core/config.py` 已有 `CORS_ORIGINS: list[str] = ["http://localhost:5173"]`（默认开发环境值）

---

## 3. 实现要求

### 3.1 文件 `server/core/config.py`（修改）

需新增两个 Settings 字段：

```python
# 运行环境: development | production
ENVIRONMENT: str = "development"

# 日志级别: DEBUG | INFO | WARNING | ERROR
LOG_LEVEL: str = "DEBUG"
```

**具体修改位置**: `Settings` 类内部，放在 `CORS_ORIGINS` 之后、`CACHE_TTL_*` 之前。

**关键约束**:
- `ENVIRONMENT` 默认 `"development"`，用于日志细节 + CORS 宽松判断
- `LOG_LEVEL` 默认 `"DEBUG"`，替代现有 `DEBUG: bool` 对日志的控制

---

### 3.2 文件 `server/api/main.py`（修改）

收敛 CORS 中间件的 `allow_methods` 和 `allow_headers`：

**修改位置**: `app.add_middleware(CORSMiddleware, ...)` 调用

**当前代码**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**修改为**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
```

**约束**:
- `allow_methods` 仅允许 `GET`、`POST`、`OPTIONS`（满足 ADR 安全要求）
- `allow_headers` 仅允许 `Content-Type`（前端 POST JSON 所需）
- `allow_origins` 保持不变，继续从 `settings.CORS_ORIGINS` 读取

---

### 3.3 文件 `server/core/logging.py`（修改）

支持通过 `settings.LOG_LEVEL` 字符串控制日志级别，替代单一的 `DEBUG` 布尔开关。

**当前代码**（第 20 行）:
```python
console_level = "DEBUG" if settings.DEBUG else "INFO"
```

**修改为**: 直接使用 `settings.LOG_LEVEL` 的值（注意转为大写以兼容 loguru）:
```python
console_level = settings.LOG_LEVEL.upper()
```

**同时修改** `setup_logging()` 函数末尾的启动日志（第 50 行），从:
```python
logger.info("Logging configured successfully")
```
改为输出当前级别:
```python
logger.info("Logging configured — level: {}", console_level)
```

---

### 3.4 文件 `server/.env.example`（修改）

补充缺失的环境变量并增强注释说明。

**当前文件内容**（见附件）需要：

1. **新增 `ENVIRONMENT` 变量**（放在 `CORS_ORIGINS` 之后、缓存 TTL 之前）:
```
# 运行环境（development / production）
# development: 日志详细、CORS 允许 localhost
# production: 日志精简、CORS 仅白名单域名
ENVIRONMENT=development
```

2. **新增 `LOG_LEVEL` 变量**:
```
# 日志级别：DEBUG / INFO / WARNING / ERROR
# development 建议 DEBUG，production 建议 INFO
LOG_LEVEL=DEBUG
```

3. **保留并增强注释** `CORS_ORIGINS` 段（已有，确认注释清晰即可）:
   - 开发环境默认值保留
   - 生产环境示例注释保留

4. **保留所有已有变量**（MONGODB_URL、CACHE_TTL_*、DEBUG），不做删除

---

### 3.5 文件 `render.yaml`（新建）

创建于项目**根目录** `d:\Users\weij\ai-finance\render.yaml`（与 `server/` 同级），内容是 Render Blueprint 格式的服务定义。

```yaml
services:
  - type: web
    name: bond-calc-api
    runtime: python
    buildCommand: pip install -r server/requirements.txt
    startCommand: cd server && uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: MONGODB_URL
        sync: false
      - key: CORS_ORIGINS
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: LOG_LEVEL
        value: INFO
```

**关键约束**:
- `type: web` — Render Web Service
- `runtime: python` — Python 运行时（Render 自动检测版本）
- `buildCommand` — 路径 `server/requirements.txt`（因为 render.yaml 在项目根目录）
- `startCommand` — 需先 `cd server` 再启动 uvicorn，端口使用 `$PORT`（Render 动态分配）
- `envVars` — `MONGODB_URL` 和 `CORS_ORIGINS` 使用 `sync: false`（敏感值不进仓库，由用户在 Render Dashboard 手动填写）；`ENVIRONMENT` 和 `LOG_LEVEL` 可直接设默认生产值
- **不要**硬编码数据库连接串或 Vercel 域名

---

## 4. 代码规范要求

- 遵循 ADR 已确立的分层架构，本次修改不破坏路由/业务/数据层的任何接口
- Python 类型注解保持完整，新增字段必须有类型标注
- 日志输出使用 `loguru` 的 `{}` 占位符（非 f-string，以保留结构化日志能力）
- YAML 文件使用 2 空格缩进
- 所有配置通过环境变量进入，代码中零硬编码

---

## 5. 测试要求

代码必须能通过以下测试用例（详见 `test-cases.md`）：

| 用例 | 覆盖点 |
|------|--------|
| TC-001 | 开发环境 CORS — localhost:5173 跨域通过 |
| TC-002 | 生产环境 CORS — CORS_ORIGINS 白名单生效 |
| TC-004 | CORS 允许方法 — GET/POST/OPTIONS 通过 |
| TC-005 | CORS 拒绝非允许方法 — PUT/DELETE 被拦截 |
| TC-006 | CORS 允许头 — Content-Type 通过 |
| TC-009 | render.yaml 结构正确 |
| TC-010 | render.yaml 环境变量占位（无硬编码敏感值） |
| TC-014 | .env.example 包含所有必需变量 |
| TC-018 | LOG_LEVEL 控制日志输出级别 |
| TC-019 | 健康检查 `/` 返回 200 |

---

## 6. 注意事项

1. **`CORS_ORIGINS` 的类型是 `list[str]`**：pydantic-settings 对逗号分隔的环境变量默认不会自动解析为 list。需要在 `Settings` 类中添加 `field_validator` 或使用自定义解析，确保环境变量 `CORS_ORIGINS=https://a.com,https://b.com` 能正确解析为 `["https://a.com", "https://b.com"]`。**提示**：当前代码中 `CORS_ORIGINS` 定义为 `list[str]` 且默认值为 list，但如果用户通过 Render 环境变量传入逗号分隔字符串，pydantic-settings 会直接赋值为该字符串而非 list。请添加一个 `@field_validator` 处理此情况：
   ```python
   from pydantic import field_validator

   @field_validator("CORS_ORIGINS", mode="before")
   @classmethod
   def parse_cors_origins(cls, v):
       if isinstance(v, str):
           return [origin.strip() for origin in v.split(",") if origin.strip()]
       return v
   ```

2. **`render.yaml` 的位置**：放在项目根目录（即 `d:\Users\weij\ai-finance\render.yaml`），因为 Render Blueprint 要求 `render.yaml` 在仓库根目录。同时 `buildCommand` 和 `startCommand` 的路径要相对于项目根目录。

3. **Render 不会自动创建 `logs/` 目录**：当前 `logging.py` 有 `logs_dir.mkdir(exist_ok=True)`，部署到 Render 时应确保当前工作目录可写（Render 的实例文件系统短暂，但可写）。不需要额外处理。

4. **不要删除 `DEBUG` 字段**：保留 `settings.DEBUG` 在 `config.py` 中，因为其他模块可能已引用（如 Swagger 文档的交互开关）。只是 `logging.py` 不再依赖它来控制日志级别。

5. **MongoDB 连接降级已存在**：`api/main.py` 的 `lifespan` 中已有 `try/except` 降级处理，无需修改。
