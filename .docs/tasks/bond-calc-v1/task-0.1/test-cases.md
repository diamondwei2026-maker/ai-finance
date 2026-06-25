# 测试用例 — Task 0.1: 后端项目脚手架与核心模块

| 属性 | 值 |
|------|-----|
| 关联 Task | [task.md](./task.md) |
| 生成日期 | 2025-06-25 |
| 总用例数 | 17 |

---

## 测试用例

### TC-001: 项目目录结构符合 ADR 定义
- **类型**: 功能测试
- **关联验收标准**: SUB-0.1.1
- **前置条件**: 执行过项目初始化命令（如 `pip install -r requirements.txt`）
- **输入**:
  - 检查目录：`api/routes/`、`services/`、`repositories/`、`models/`、`external/`、`core/`
- **执行步骤**:
  1. 进入后端项目根目录
  2. 列出 `api/routes/`、`services/`、`repositories/`、`models/`、`external/`、`core/` 目录
  3. 检查每个目录下是否存在 `__init__.py` 文件
- **预期输出**:
  - 6 个目录均存在
  - 每个目录下均有 `__init__.py` 文件（可为空文件）
- **清理**: 无

---

### TC-002: FastAPI 应用成功启动，Swagger 文档可访问
- **类型**: 功能测试
- **关联验收标准**: 主验收标准第 2 条 + SUB-0.1.3
- **前置条件**: MongoDB Atlas 连接串已配置在 `.env` 中
- **输入**:
  - 启动命令：`uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload`
- **执行步骤**:
  1. 确保 `.env` 文件含有效 `MONGODB_URL`
  2. 启动 Uvicorn 服务
  3. 浏览器访问 `http://localhost:8000/docs`
  4. 浏览器访问 `http://localhost:8000/redoc`
- **预期输出**:
  - Uvicorn 启动日志无 ERROR
  - `http://localhost:8000/docs` 返回 Swagger UI 页面（HTTP 200）
  - `http://localhost:8000/redoc` 返回 ReDoc 页面（HTTP 200）
- **清理**: 停止 Uvicorn 进程

---

### TC-003: 根路径健康检查返回 ok
- **类型**: 功能测试
- **关联验收标准**: SUB-0.1.3 第 3 条
- **前置条件**: FastAPI 应用已启动
- **输入**:
  - 请求：`GET http://localhost:8000/`
- **执行步骤**:
  1. 发送 `GET /` 请求
  2. 检查响应体
- **预期输出**:
  - HTTP 状态码：`200`
  - 响应体：`{"status": "ok"}`
- **清理**: 无

---

### TC-004: 配置模块通过环境变量读取 MongoDB 连接串
- **类型**: 功能测试
- **关联验收标准**: SUB-0.1.2 第 1 条（config.py）
- **前置条件**: `.env` 文件中已设置 `MONGODB_URL=mongodb+srv://test:test@cluster.mongodb.net/test`
- **输入**:
  - 在 Python 中 `from core.config import settings` 并读取 `settings.MONGODB_URL`
- **执行步骤**:
  1. 设置环境变量 `MONGODB_URL`（或通过 `.env` 文件）
  2. 在 Python REPL 中导入 settings
  3. 检查 `settings.MONGODB_URL` 的值
- **预期输出**:
  - `settings.MONGODB_URL` 返回值与 `.env` 中设置一致
- **清理**: 无

---

### TC-005: 缺少必填配置时启动报错
- **类型**: 异常测试
- **关联验收标准**: 主验收标准第 3 条（环境变量管理）
- **前置条件**: `.env` 文件中缺少 `MONGODB_URL`
- **输入**:
  - 启动 FastAPI 应用（无 MONGODB_URL 配置）
- **执行步骤**:
  1. 移除或注释 `.env` 中的 `MONGODB_URL`
  2. 尝试启动 Uvicorn
- **预期输出**:
  - 应用启动失败，抛出明确的配置错误信息（如 `MONGODB_URL is required`）
  - 或应用启动但明确日志提示 MongoDB 连接配置缺失
- **清理**: 恢复 `.env` 中的 `MONGODB_URL`

---

### TC-006: 日志模块 loguru 控制台 + 文件输出
- **类型**: 功能测试
- **关联验收标准**: 主验收标准第 4 条 + SUB-0.1.2 第 2 条
- **前置条件**: FastAPI 应用已启动
- **输入**:
  - 日志写入操作：`logger.info("测试日志消息")`
- **执行步骤**:
  1. 启动 FastAPI 应用
  2. 发送一个 API 请求（如 `GET /`）
  3. 检查终端输出是否包含彩色日志
  4. 检查 `logs/bond_tool.log` 文件是否生成
  5. 检查日志文件内容是否包含请求日志
- **预期输出**:
  - 终端有带时间戳和颜色的日志输出
  - `logs/bond_tool.log` 文件存在
  - 日志文件中包含对应的 INFO 级别日志条目
- **清理**: 无

---

### TC-007: AppException 基类可正常实例化
- **类型**: 功能测试
- **关联验收标准**: SUB-0.1.2 第 3 条
- **前置条件**: `core/exceptions.py` 已实现
- **输入**:
  - Python 代码：`raise AppException(message="测试异常", code=50001, status_code=500)`
- **执行步骤**:
  1. 导入 `AppException`
  2. 实例化并 raise
  3. 捕获并检查属性
- **预期输出**:
  - 异常消息为 `"测试异常"`
  - `code` 属性为 `50001`
  - `status_code` 属性为 `500`
  - 继承自 `Exception`
- **清理**: 无

---

### TC-008: RecoverableError 和 FatalError 分类正确
- **类型**: 功能测试
- **关联验收标准**: 主验收标准第 5 条 + SUB-0.1.2 第 3 条
- **前置条件**: `core/exceptions.py` 已实现
- **输入**:
  - `raise RecoverableError(message="单源失败", code=40001)`
  - `raise FatalError(message="全部不可用", code=50001)`
- **执行步骤**:
  1. 分别 raise `RecoverableError` 和 `FatalError`
  2. 检查两者均继承自 `AppException`
  3. 检查默认 `status_code`：RecoverableError 应为 200（数据 N/A 但不中断），FatalError 应为 503
- **预期输出**:
  - `RecoverableError` 默认 `status_code` 为 `200`，错误信息包含 "部分数据不可用"
  - `FatalError` 默认 `status_code` 为 `503`，错误信息包含 "服务暂时不可用"
  - 两者均 `isinstance(app_exc, AppException)` 为 `True`
- **清理**: 无

---

### TC-009: Cache 模块 get_or_set 基本功能
- **类型**: 功能测试
- **关联验收标准**: 主验收标准第 6 条 + SUB-0.1.2 第 4 条
- **前置条件**: `core/cache.py` 已实现
- **输入**:
  - 缓存键 `"fund:000001"`，值 `{"name": "测试基金"}`
- **执行步骤**:
  1. 调用 `cache.get_or_set("fund:000001", lambda: {"name": "测试基金"})`
  2. 首次调用：应执行 factory 函数，返回 `{"name": "测试基金"}`
  3. 再次调用同一 key：应直接返回缓存值，不执行 factory
  4. 验证第二次调用时 factory 未被调用
- **预期输出**:
  - 首次返回 `{"name": "测试基金"}`
  - 第二次返回同样的值（来自缓存）
  - factory 函数仅被调用 1 次
- **清理**: 清理缓存实例

---

### TC-010: Cache 按 key 前缀区分 TTL
- **类型**: 功能测试
- **关联验收标准**: 主验收标准第 6 条（基金 30min、计算结果 5min、市场利率 2min）
- **前置条件**: `core/cache.py` 已实现，支持按前缀配置不同 TTL
- **输入**:
  - 键 `"fund:000001"`（TTL 30min）、`"calc:abc"`（TTL 5min）、`"market:10y"`（TTL 2min）
- **执行步骤**:
  1. 分别写入 3 个不同前缀的缓存
  2. 读取各缓存实例的 `maxsize` 和 `ttl` 属性
  3. 验证 `fund:` 前缀 TTL = 1800s（30min）
  4. 验证 `calc:` 前缀 TTL = 300s（5min）
  5. 验证 `market:` 前缀 TTL = 120s（2min）
- **预期输出**:
  - 3 种前缀的 TTL 分别符合 PRD 要求的时长
- **清理**: 清理缓存实例

---

### TC-011: MongoDB 连接 + Beanie 初始化
- **类型**: 集成测试
- **关联验收标准**: 主验收标准第 7 条 + SUB-0.1.3 第 1 条
- **前置条件**: `.env` 中 `MONGODB_URL` 指向有效 MongoDB Atlas 集群
- **输入**:
  - 启动 FastAPI 应用
- **执行步骤**:
  1. 启动 FastAPI 应用
  2. 查看启动日志
  3. 在 lifespan 的 startup 中初始化 Beanie
  4. 发送 `GET /` 请求确认应用健康
- **预期输出**:
  - 启动日志含 MongoDB 连接成功信息（如 "Connected to MongoDB"）
  - Beanie ODM 初始化完成（日志含 "Beanie initialized" 或类似信息）
  - 健康检查返回 `{"status": "ok"}`
- **清理**: 停止应用，MongoDB 连接自动关闭

---

### TC-012: requirements.txt 依赖可成功安装
- **类型**: 功能测试
- **关联验收标准**: SUB-0.1.4
- **前置条件**: Python 3.11+ 环境已安装
- **输入**:
  - 在虚拟环境中执行 `pip install -r requirements.txt`
- **执行步骤**:
  1. 创建并激活 Python 虚拟环境
  2. 执行 `pip install -r requirements.txt`
  3. 检查安装是否成功（无报错）
  4. 验证关键包可导入：`fastapi`、`uvicorn`、`motor`、`beanie`、`httpx`、`akshare`、`exchange_calendars`、`loguru`、`python-dotenv`
- **预期输出**:
  - `pip install` 成功完成，退出码 0
  - 所有关键包导入成功
- **清理**: 删除虚拟环境（可选）

---

### TC-013: Cache 过期后重新拉取
- **类型**: 边界测试
- **关联验收标准**: SUB-0.1.2 第 4 条（TTLCache）
- **前置条件**: `core/cache.py` 已实现，可使用较短 TTL 的缓存实例测试
- **输入**:
  - 缓存键 `"test:expire"`，值 `"v1"`，TTL 设为 1 秒
- **执行步骤**:
  1. 创建 TTL=1s 的缓存实例
  2. 写入值 `"v1"`
  3. 立即读取，确认返回 `"v1"`
  4. 等待 2 秒后再次读取
  5. 传入新的 factory 返回 `"v2"`
- **预期输出**:
  - 过期后读取返回 `"v2"`（factory 被调用生成新值）
- **清理**: 清理缓存实例

---

### TC-014: Cache 空键处理
- **类型**: 边界测试
- **关联验收标准**: SUB-0.1.2 第 4 条（cache.py）
- **前置条件**: `core/cache.py` 已实现
- **输入**:
  - 空字符串 `""` 作为缓存键
- **执行步骤**:
  1. 尝试 `cache.get_or_set("", lambda: "value")`
- **预期输出**:
  - 抛出 `ValueError` 或返回正常值（取决于实现选择）
  - 不得静默产生不可预期的行为
- **清理**: 无

---

### TC-015: 日志文件轮转（10MB 限制）
- **类型**: 边界测试
- **关联验收标准**: 主验收标准第 4 条（10MB 轮转）
- **前置条件**: `core/logging.py` 配置了 `rotation="10 MB"`
- **输入**:
  - 持续写入大量日志 > 10MB
- **执行步骤**:
  1. 确认 `core/logging.py` 中 loguru 配置了 `rotation="10 MB"`
  2. 循环写入大量日志使文件超过 10MB
  3. 检查 `logs/` 目录
- **预期输出**:
  - 原日志文件被轮转（如 `bond_tool.log` → `bond_tool.1.log`）
  - 新日志继续写入 `bond_tool.log`
- **清理**: 删除测试日志文件

---

### TC-016: MongoDB 连接失败时应用不崩溃
- **类型**: 异常测试
- **关联验收标准**: SUB-0.1.3
- **前置条件**: `.env` 中 `MONGODB_URL` 指向不可达的地址
- **输入**:
  - 设置 `MONGODB_URL=mongodb://invalid-host:27017/test?serverSelectionTimeoutMS=3000`
- **执行步骤**:
  1. 修改 `.env` 的 `MONGODB_URL` 为无效地址
  2. 启动 FastAPI 应用
  3. 发送 `GET /` 请求
- **预期输出**:
  - 启动日志打印连接失败警告（不崩溃退出）
  - 健康检查可返回降级状态（如 `{"status": "degraded", "mongodb": "disconnected"}`）
  - 或应用启动失败但给出清晰错误信息
- **清理**: 恢复正确的 `MONGODB_URL`

---

### TC-017: .env.example 模板文件存在且内容完整
- **类型**: 功能测试
- **关联验收标准**: 主验收标准第 3 条（`.env.example` 提供模板）
- **前置条件**: 项目根目录已初始化
- **输入**:
  - 检查文件 `.env.example`
- **执行步骤**:
  1. 检查项目根目录存在 `.env.example` 文件
  2. 读取文件内容
  3. 检查是否包含所有必需的环境变量键名（带注释说明）
- **预期输出**:
  - `.env.example` 文件存在
  - 包含以下键的说明：`MONGODB_URL`、`CORS_ORIGINS`、`CACHE_TTL_FUND`、`CACHE_TTL_CALC`、`CACHE_TTL_MARKET`（或等效配置项）
  - 不包含真实密钥/密码
- **清理**: 无
