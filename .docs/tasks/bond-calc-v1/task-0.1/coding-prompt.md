# Coding Prompt — Task 0.1: 后端项目脚手架与核心模块

### 1. 任务目标

搭建 FastAPI 后端项目骨架：创建分层目录结构，实现四大核心模块（配置、日志、异常、缓存），完成 MongoDB Atlas + Beanie ODM 初始化，锁定项目依赖。

### 2. 技术上下文

- **语言/框架**: Python 3.11+ / FastAPI / Uvicorn
- **数据库**: MongoDB Atlas（M0 免费层）+ Beanie ODM（底层 Motor 异步驱动）
- **配置管理**: pydantic-settings（`pydantic_settings.BaseSettings`），`.env` 文件自动加载
- **日志**: loguru（彩色终端 + 文件归档 10MB 轮转）
- **缓存**: cachetools.TTLCache（内存缓存，按 key 前缀区分 TTL）
- **异常体系**: 自定义 `AppException` 基类 → `RecoverableError`（可恢复，标 N/A）+ `FatalError`（致命，返回 503）
- **API 规范**: RESTful，URL 路径版本 `/api/v1/`，统一响应格式 `{code, message, data}`
- **涉及文件**（全部新建）:
  - `server/core/__init__.py`
  - `server/core/config.py` — 配置管理（环境变量读取）
  - `server/core/logging.py` — loguru 日志配置
  - `server/core/exceptions.py` — 异常类定义
  - `server/core/cache.py` — TTLCache 封装
  - `server/api/__init__.py`
  - `server/api/main.py` — FastAPI 应用入口
  - `server/api/routes/__init__.py`
  - `server/services/__init__.py`
  - `server/repositories/__init__.py`
  - `server/models/__init__.py`
  - `server/external/__init__.py`
  - `server/requirements.txt` — 依赖锁定
  - `server/.env.example` — 环境变量模板
  - `server/.gitignore` — 后端专用 gitignore

### 3. 实现要求

#### 3.1 项目根目录

后端代码放在 `server/` 目录下，与前端代码 `client/` 平级。本次只创建后端部分。

目录结构：
```
server/
├── api/
│   ├── __init__.py
│   ├── main.py
│   └── routes/
│       └── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── logging.py
│   ├── exceptions.py
│   └── cache.py
├── services/
│   └── __init__.py
├── repositories/
│   └── __init__.py
├── models/
│   └── __init__.py
├── external/
│   └── __init__.py
├── logs/              ← 运行时自动创建，加入 .gitignore
├── requirements.txt
├── .env.example
└── .gitignore
```

#### 3.2 文件 `server/core/config.py`

- **类名**: `Settings(BaseSettings)`
- **职责**: 从 `.env` 文件和环境变量读取所有配置项
- **关键字段**:
  ```python
  from pydantic_settings import BaseSettings

  class Settings(BaseSettings):
      # MongoDB
      MONGODB_URL: str  # 必填，无默认值，缺失时启动报错

      # CORS
      CORS_ORIGINS: list[str] = ["http://localhost:5173"]

      # Cache TTL (seconds)
      CACHE_TTL_FUND: int = 1800       # 基金信息 30min
      CACHE_TTL_CALC: int = 300        # 计算结果 5min
      CACHE_TTL_MARKET: int = 120      # 市场利率 2min

      # App
      APP_NAME: str = "债券收益计算工具"
      APP_VERSION: str = "1.0.0"
      DEBUG: bool = False

      model_config = SettingsConfigDict(
          env_file=".env",
          env_file_encoding="utf-8",
          case_sensitive=True,
      )
  ```
- **关键逻辑**:
  1. 使用 `pydantic_settings.BaseSettings`，自动从 `.env` 加载
  2. `MONGODB_URL` 不设默认值——缺失时 pydantic 自动抛出 `ValidationError`，应用启动失败并给出明确提示
  3. 模块级单例：`settings = Settings()` 在模块底部创建，其他模块 `from core.config import settings` 即可
  4. `CORS_ORIGINS` 使用 `list[str]`，pydantic-settings 会自动解析逗号分隔的环境变量

#### 3.3 文件 `server/core/logging.py`

- **函数**: `setup_logging()`
- **签名**: `def setup_logging() -> None`
- **职责**: 配置 loguru，移除默认 handler，添加控制台 + 文件双输出
- **关键逻辑**:
  1. `logger.remove()` — 移除 loguru 默认 handler
  2. 控制台输出：`logger.add(sys.stdout, colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level="DEBUG" if settings.DEBUG else "INFO")`
  3. 文件输出：`logger.add("logs/bond_tool.log", rotation="10 MB", retention=5, encoding="utf-8", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}", level="INFO")`
  4. 自动创建 `logs/` 目录（`Path("logs").mkdir(exist_ok=True)`）
  5. `api/main.py` 启动时调用 `setup_logging()` 即全局生效

#### 3.4 文件 `server/core/exceptions.py`

- **类定义**（3 个类）:

  1. **`AppException(Exception)`** — 基类
     ```python
     class AppException(Exception):
         def __init__(self, message: str, code: int = 50000, status_code: int = 500):
             self.message = message
             self.code = code
             self.status_code = status_code
             super().__init__(self.message)
     ```

  2. **`RecoverableError(AppException)`** — 可恢复错误（单源失败，指标标 N/A）
     - 默认 `code=40001`，默认 `status_code=200`
     - 用于：单个数据源超时/返回异常 → 该指标返回 `null`（N/A），其余指标正常

  3. **`FatalError(AppException)`** — 致命错误（全部数据源不可用）
     - 默认 `code=50001`，默认 `status_code=503`
     - 用于：所有数据源均失败 → 返回 503，提示用户稍后重试

- **额外**: 定义业务错误码常量类 `ErrorCode`:
  ```python
  class ErrorCode:
      FUND_NOT_FOUND = 40001       # 基金不存在
      TYPE_MISMATCH = 40002        # 基金类型不匹配（非债券型）
      DATA_SOURCE_FAILED = 40003   # 数据源获取失败（可恢复）
      ALL_SOURCES_FAILED = 50001   # 所有数据源不可用（致命）
      CALCULATION_FAILED = 50002   # 计算失败
  ```

#### 3.5 文件 `server/core/cache.py`

- **依赖**: `cachetools.TTLCache`
- **核心类/函数**:
  1. **`get_cache(prefix: str) -> TTLCache`** — 工厂函数，按前缀返回对应 TTL 的缓存实例
  2. **`get_or_set(cache: TTLCache, key: str, factory: Callable[[], Any]) -> Any`** — 从缓存取值，未命中则调用 factory 写入后返回
- **关键逻辑**:
  1. 维护内部字典 `_caches: dict[str, TTLCache]`，按前缀缓存实例
  2. TTL 映射：
     - `"fund:"` → `settings.CACHE_TTL_FUND`（1800s）
     - `"calc:"` → `settings.CACHE_TTL_CALC`（300s）
     - `"market:"` → `settings.CACHE_TTL_MARKET`（120s）
     - 其他前缀 → 默认 300s
  3. `get_or_set` 实现：
     ```python
     def get_or_set(cache: TTLCache, key: str, factory: Callable[[], Any]) -> Any:
         if key in cache:
             return cache[key]
         value = factory()
         cache[key] = value
         return value
     ```
  4. `maxsize` 统一设为 256（单用户场景足够）
- **错误处理**: 空字符串 key 抛出 `ValueError("Cache key must not be empty")`

#### 3.6 文件 `server/api/main.py`

- **职责**: FastAPI 应用入口，包含 lifespan 事件处理、CORS 中间件、健康检查路由
- **关键逻辑**:
  1. **lifespan 上下文管理器**（`@asynccontextmanager`）:
     - **startup**:
       1. 调用 `setup_logging()`
       2. `logger.info("Starting {} v{}", settings.APP_NAME, settings.APP_VERSION)`
       3. 初始化 MongoDB 连接：`motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)`
       4. 初始化 Beanie：`await init_beanie(database=client.get_default_database(), document_models=[])`（document_models 先传空列表，后续 Task 逐步添加 Document 模型）
       5. `logger.info("MongoDB connected, Beanie initialized")`
       6. MongoDB 连接失败时：记录 ERROR 日志，不崩溃，健康检查返回降级状态
     - **shutdown**:
       1. 关闭 MongoDB 连接
       2. `logger.info("Application shutting down")`
  2. **CORS 中间件**:
     ```python
     app.add_middleware(
         CORSMiddleware,
         allow_origins=settings.CORS_ORIGINS,
         allow_credentials=True,
         allow_methods=["*"],
         allow_headers=["*"],
     )
     ```
  3. **根路径健康检查**:
     ```python
     @app.get("/")
     async def health_check():
         return {"status": "ok"}
     ```
  4. `app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)`
  5. Swagger 文档路径默认 `/docs`，ReDoc 默认 `/redoc`

#### 3.7 文件 `server/requirements.txt`

锁定的依赖及版本（使用 `>=` 约束最低版本，兼容小版本更新）：

```
# Web Framework
fastapi>=0.110.0
uvicorn[standard]>=0.29.0

# Database
motor>=3.4.0
beanie>=1.25.0

# Configuration
pydantic-settings>=2.2.0
python-dotenv>=1.0.0

# HTTP Client
httpx>=0.27.0

# Data Sources
akshare>=1.14.0
exchange_calendars>=4.5.0

# Logging
loguru>=0.7.0

# Caching
cachetools>=5.3.0

# Utilities
python-dateutil>=2.9.0
```

#### 3.8 文件 `server/.env.example`

```ini
# MongoDB Atlas 连接串（必填）
# 在 MongoDB Atlas → Database → Connect → Drivers → 复制连接串
# 将 <password> 替换为你的数据库用户密码
MONGODB_URL=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/bond_tool?retryWrites=true&w=majority

# CORS 允许的源（逗号分隔）
# 开发环境
CORS_ORIGINS=http://localhost:5173
# 生产环境示例：
# CORS_ORIGINS=https://your-app.vercel.app

# 缓存 TTL（秒），以下为默认值，可根据需要调整
# CACHE_TTL_FUND=1800
# CACHE_TTL_CALC=300
# CACHE_TTL_MARKET=120

# 调试模式（生产环境请设为 false）
# DEBUG=false
```

#### 3.9 文件 `server/.gitignore`

```
# Python
__pycache__/
*.py[cod]
*.so
*.egg-info/
dist/
build/
.eggs/
*.egg

# Virtual Environment
venv/
.venv/
env/

# Environment
.env

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test
.pytest_cache/
.coverage
htmlcov/
```

### 4. 代码规范要求

- 所有 Python 文件使用 UTF-8 编码
- 使用 `async/await` 而非回调或 `Promise.then`
- 类型注解：所有函数参数和返回值必须标注类型（Python 3.10+ union 语法 `X | None`）
- Import 顺序：标准库 → 第三方库 → 本地模块，每组间空一行
- 模块级 logger：`from loguru import logger`，不重复配置
- 异常处理：不裸 `except:`，至少 `except Exception as e:` 并记录日志
- 配置读取统一通过 `from core.config import settings`，不直接读 `os.environ`
- docstring：类和公共函数需有简短中文 docstring

### 5. 测试要求

代码必须能通过以下测试用例（详见 `test-cases.md`）：

| 编号 | 测试内容 | 关键点 |
|------|---------|--------|
| TC-001 | 项目目录结构符合 ADR 定义 | 6 个目录 + `__init__.py` |
| TC-002 | FastAPI 应用启动，Swagger 可访问 | `uvicorn api.main:app` 无 ERROR |
| TC-003 | 根路径健康检查返回 ok | `GET /` → `{"status": "ok"}` |
| TC-004 | 配置模块通过环境变量读取 MongoDB 连接串 | `settings.MONGODB_URL` 与 `.env` 一致 |
| TC-005 | 缺少必填配置时启动报错 | 无 `MONGODB_URL` → `ValidationError` |
| TC-006 | loguru 控制台 + 文件输出 | `logs/bond_tool.log` 生成，含日志内容 |
| TC-007 | AppException 基类实例化 | 属性 `message`、`code`、`status_code` |
| TC-008 | RecoverableError / FatalError 默认 status_code | 200 / 503 |
| TC-009 | Cache get_or_set 基本功能 | factory 仅调用一次 |
| TC-010 | Cache 按前缀区分 TTL | fund: 1800s / calc: 300s / market: 120s |
| TC-011 | MongoDB 连接 + Beanie 初始化 | 启动日志含连接成功信息 |
| TC-012 | requirements.txt 依赖可成功安装 | `pip install -r requirements.txt` 退出码 0 |
| TC-013 | Cache 过期后重新拉取 | 过期后 factory 被调用生成新值 |
| TC-014 | Cache 空键处理 | 抛出 ValueError，不静默 |
| TC-015 | 日志文件 10MB 轮转 | loguru `rotation="10 MB"` |
| TC-016 | MongoDB 连接失败时应用不崩溃 | 日志打印警告，不崩溃退出 |
| TC-017 | .env.example 模板文件存在且内容完整 | 含所有必需键名 + 注释 |

### 6. 注意事项

- **pydantic-settings 版本差异**: `pydantic_settings.BaseSettings` 在 v2.x 中使用 `model_config = SettingsConfigDict(...)`（不是旧版的 `class Config`），确保与 `pydantic>=2.0` 兼容
- **Beanie 初始化时 document_models 为空**: 本 Task 尚未定义 Document 模型，`init_beanie` 的 `document_models=[]` 是合法的，后续 Task 逐步添加
- **MongoDB 连接失败不崩溃**: 使用 `try/except` 包裹 MongoDB 初始化，失败时记录 ERROR 日志但不 `sys.exit()`，让应用以降级模式运行
- **日志文件目录**: `logs/` 目录不在版本控制中，`setup_logging()` 需自动创建
- **`.env` 绝不提交**: `.gitignore` 中必须包含 `.env`
- **CORS 默认仅 localhost:5173**: 生产环境通过 `CORS_ORIGINS` 环境变量覆盖
- **缓存非线程安全**: TTLCache 非线程安全，但单用户 Uvicorn 单 worker 场景下无竞争问题
- **所有 `__init__.py` 可以为空文件**，仅用于标识 Python 包
