# Task 0.1: 后端项目脚手架与核心模块

| 属性 | 值 |
|------|-----|
| ID | 0.1 |
| 状态 | pending |
| 优先级 | P0 |
| 依赖 | 无 |
| 阶段 | 阶段0: 项目初始化 |
| 预估工时 | 2-3 小时 |

## 描述

初始化 FastAPI 后端项目骨架，搭建分层目录结构，配置所有核心模块（配置管理、日志、异常处理、缓存），完成 MongoDB Atlas 数据库连接与 Beanie ODM 初始化。

## 验收标准

- [ ] 后端项目目录结构符合 ADR 定义（`api/`、`services/`、`repositories/`、`models/`、`external/`、`core/`）
- [ ] `api/main.py` 可启动 FastAPI 应用，`http://localhost:8000/docs` 可访问 Swagger 文档
- [ ] `core/config.py` 通过环境变量管理配置（MongoDB 连接串、CORS 域名、TTL 常量），`.env.example` 提供模板
- [ ] `core/logging.py` 基于 loguru 配置完成：彩色终端输出 + `logs/bond_tool.log` 文件归档（10MB 轮转）
- [ ] `core/exceptions.py` 定义 `RecoverableError`（单源失败标 N/A）和 `FatalError`（全部数据源不可用返回 503）
- [ ] `core/cache.py` 封装 TTLCache：基金信息 30min、计算结果 5min、市场利率 2min
- [ ] MongoDB Atlas 连接成功，Beanie ODM 初始化完成（`api/main.py` 启动时自动连接）
- [ ] `requirements.txt` 锁定依赖版本：fastapi、uvicorn、motor、beanie、httpx、akshare、exchange_calendars、loguru、python-dotenv 等

## 子任务

### SUB-0.1.1: 创建项目目录结构
- **描述**: 按 ADR 定义创建后端分层目录
- **验收标准**:
  - [ ] 目录 `api/routes/`、`services/`、`repositories/`、`models/`、`external/`、`core/` 均已创建，含 `__init__.py`

### SUB-0.1.2: 实现核心模块
- **描述**: 编写 config.py、exceptions.py、logging.py、cache.py
- **验收标准**:
  - [ ] `core/config.py` 使用 pydantic-settings 或 os.environ 读取配置，含 Settings 类
  - [ ] `core/logging.py` 调用 loguru 配置，`api/main.py` 中 import 即生效
  - [ ] `core/exceptions.py` 含 `AppException` 基类 + `RecoverableError` + `FatalError`
  - [ ] `core/cache.py` 封装 `cachetools.TTLCache`，提供 `get_or_set` 方法，按 key 前缀区分 TTL

### SUB-0.1.3: FastAPI 应用初始化 + MongoDB 连接
- **描述**: 创建 main.py，配置应用启动事件中初始化 Beanie
- **验收标准**:
  - [ ] `api/main.py` 含 `lifespan` 上下文管理器，startup 中连接 MongoDB 并初始化 Beanie
  - [ ] Swagger 文档 `/docs` 可访问
  - [ ] 根路径 `/` 返回 `{"status": "ok"}` 健康检查

### SUB-0.1.4: 锁定依赖
- **描述**: 编写 requirements.txt
- **验收标准**:
  - [ ] `requirements.txt` 锁定所有依赖及版本号
  - [ ] `pip install -r requirements.txt` 可成功安装
