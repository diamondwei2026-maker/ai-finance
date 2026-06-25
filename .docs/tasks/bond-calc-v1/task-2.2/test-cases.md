# 测试用例 — Task 2.2: 计算 API 路由

> 生成日期：2025-06-25 | 关联 Task：[task.md](./task.md)

---

## 一、功能测试

### TC-001: POST 有效基金代码触发计算

- **类型**: 功能测试
- **关联验收标准**: `POST /api/v1/calculations` — 接收 `{"fund_code": "020741"}`，触发异步计算，返回 `{"calculation_id": "...", "status": "processing"}`
- **前置条件**: 数据源可正常访问，MongoDB 可用
- **输入**:
  - 请求体：`{"fund_code": "020741"}`
  - Content-Type: `application/json`
- **执行步骤**:
  1. 向 `POST /api/v1/calculations` 发送请求
  2. 检查 HTTP 状态码
  3. 检查响应体结构
  4. 检查 MongoDB `calculations` 集合是否新增文档
- **预期输出**:
  - HTTP 状态码：`200`
  - 响应体：`{"code": 0, "message": "success", "data": {"calculation_id": "<MongoDB ObjectId 字符串>", "status": "processing"}}`
  - `calculation_id` 为 24 字符十六进制字符串（MongoDB ObjectId）
  - MongoDB `calculations` 集合中存在 `_id` 等于 `calculation_id` 的文档
  - 该文档 `status` 字段为 `"processing"`
- **清理**: 删除 MongoDB 中本次测试创建的 calculation 文档

---

### TC-002: GET 已完成计算返回完整 8 项指标

- **类型**: 功能测试
- **关联验收标准**: `GET /api/v1/calculations/{id}` — 状态 `completed` 时返回所有指标 + `data_date` + `is_trading_day` + `disclaimer`
- **前置条件**: MongoDB 中存在一条 `status` 为 `"completed"` 的 calculation 文档（可手动插入）
- **输入**:
  - 路径参数：`{id}` = 有效的 calculation_id
- **执行步骤**:
  1. 向 `GET /api/v1/calculations/{id}` 发送请求
  2. 检查 HTTP 状态码
  3. 检查响应体中是否包含所有 8 项指标字段
  4. 检查元数据字段是否存在
- **预期输出**:
  - HTTP 状态码：`200`
  - 响应体 `data` 包含以下字段：
    - `fund_code`（string）
    - `fund_name`（string）
    - `nav`（float 或 null）
    - `daily_change_pct`（float 或 null）
    - `seven_day_annual_yield`（float 或 null）
    - `wanfen_income`（float 或 null）
    - `one_month_return`（float 或 null）
    - `three_month_max_drawdown`（float 或 null）
    - `ten_year_treasury`（float 或 null）
    - `credit_spread_aa_plus`（float 或 null）
    - `data_date`（string，格式 `YYYY-MM-DD`）
    - `is_trading_day`（bool）
    - `disclaimer`（string，非空）
- **清理**: 无（使用预置数据）

---

### TC-003: GET 计算中状态返回 processing 提示

- **类型**: 功能测试
- **关联验收标准**: 状态 `processing` 时返回 `{"status": "processing", "message": "计算中，请稍后刷新"}`
- **前置条件**: MongoDB 中存在一条 `status` 为 `"processing"` 的 calculation 文档
- **输入**:
  - 路径参数：`{id}` = 有效的 calculation_id（状态为 processing）
- **执行步骤**:
  1. 向 `GET /api/v1/calculations/{id}` 发送请求
  2. 检查 HTTP 状态码
  3. 检查响应体中的 status 和 message
- **预期输出**:
  - HTTP 状态码：`200`
  - 响应体 `data` 包含：
    - `status`: `"processing"`
    - `message`: 包含"计算中"或类似提示文本
- **清理**: 无（使用预置数据）

---

### TC-004: GET 计算失败状态返回错误信息

- **类型**: 功能测试
- **关联验收标准**: 状态 `failed` 时返回错误信息
- **前置条件**: MongoDB 中存在一条 `status` 为 `"failed"` 的 calculation 文档（含 `error_message` 字段）
- **输入**:
  - 路径参数：`{id}` = 有效的 calculation_id（状态为 failed）
- **执行步骤**:
  1. 向 `GET /api/v1/calculations/{id}` 发送请求
  2. 检查 HTTP 状态码
  3. 检查响应体中的 status 和错误信息
- **预期输出**:
  - HTTP 状态码：`200`
  - 响应体 `data` 包含：
    - `status`: `"failed"`
    - `error_message` 或 `message`: 非空错误描述字符串
- **清理**: 无（使用预置数据）

---

### TC-005: 同一基金代码 5 分钟内缓存命中

- **类型**: 功能测试
- **关联验收标准**: 同一基金代码 + 5 分钟内已有缓存结果直接返回已有的 calculation_id
- **前置条件**: 已通过 POST 对基金代码 `"020741"` 触发过一次计算，且该结果仍在 5 分钟缓存期内
- **输入**:
  - 再次发送 `POST /api/v1/calculations`，请求体 `{"fund_code": "020741"}`
- **执行步骤**:
  1. 第一次 POST `{"fund_code": "020741"}` → 获得 `calculation_id_1`
  2. 在 5 分钟内再次 POST `{"fund_code": "020741"}`
  3. 检查第二次响应中的 `calculation_id`
- **预期输出**:
  - HTTP 状态码：`200`
  - 第二次响应的 `calculation_id` 与第一次**相同**
  - 日志中出现缓存命中的 debug 日志
- **清理**: 等待缓存过期或手动清理缓存实例

---

### TC-006: 计算结果持久化到 MongoDB

- **类型**: 功能测试
- **关联验收标准**: 计算结果持久化到 MongoDB `calculations` 集合
- **前置条件**: MongoDB 可用，`calculations` 集合存在
- **输入**:
  - 触发一次完整计算流程（POST → 等待完成 → GET）
- **执行步骤**:
  1. POST `{"fund_code": "020741"}` 触发计算
  2. 等待计算完成（或直接查询数据库确认文档写入）
  3. 直接查询 MongoDB `calculations` 集合
  4. 验证文档字段完整性
- **预期输出**:
  - MongoDB `calculations` 集合中存在对应文档
  - 文档包含字段：`fund_code`, `nav`, `daily_change_pct`, `seven_day_annual_yield`, `wanfen_income`, `one_month_return`, `three_month_max_drawdown`, `ten_year_treasury`, `credit_spread_aa_plus`, `data_date`, `is_trading_day`, `created_at`, `status`
  - `created_at` 为 ISODate 类型
- **清理**: 删除本次测试创建的 calculation 文档

---

### TC-007: Swagger 文档可见两个接口

- **类型**: 功能测试
- **关联验收标准**: Swagger 文档中可看到两个接口定义
- **前置条件**: 应用正常运行
- **输入**: 无（浏览器/HTTP 客户端访问）
- **执行步骤**:
  1. 访问 `GET /docs`（Swagger UI）
  2. 检查页面中是否列出 `POST /api/v1/calculations`
  3. 检查页面中是否列出 `GET /api/v1/calculations/{id}`
- **预期输出**:
  - 页面中存在 `POST /api/v1/calculations` 路由条目
  - 页面中存在 `GET /api/v1/calculations/{id}` 路由条目
  - 每个路由有 `summary` 描述文本
  - 可在 Swagger UI 中展开并查看请求/响应 Schema
- **清理**: 无

---

## 二、边界测试

### TC-008: fund_code 边界值校验

- **类型**: 边界测试
- **关联验收标准**: 基金代码格式校验（6 位数字）
- **前置条件**: 无
- **输入**:
  - 用例 A：`{"fund_code": "000001"}`（6 位最小）
  - 用例 B：`{"fund_code": "999999"}`（6 位最大）
  - 用例 C：`{"fund_code": "020741"}`（6 位正常）
  - 用例 D：`{"fund_code": "12345"}`（5 位数字，应拒绝）
  - 用例 E：`{"fund_code": "1234567"}`（7 位数字，应拒绝）
  - 用例 F：`{"fund_code": "02074a"}`（含字母，应拒绝）
  - 用例 G：`{"fund_code": ""}`（空字符串，应拒绝）
- **执行步骤**:
  1. 依次发送各用例的 POST 请求
  2. 检查每个请求的响应
- **预期输出**:
  - 用例 A/B/C：HTTP `200`，正常处理
  - 用例 D/E/F/G：返回业务错误（code 非 0），`message` 包含格式提示
- **清理**: 删除成功创建的 calculation 文档

---

### TC-009: 数值字段为 None 时响应保留该字段

- **类型**: 边界测试
- **关联验收标准**: 数值字段 `None` 时在响应中保留（前端展示为 N/A）
- **前置条件**: MongoDB 中存在一条 calculation 文档，其中部分数值字段为 `null`（如 `seven_day_annual_yield`、`wanfen_income`）
- **输入**:
  - `GET /api/v1/calculations/{id}`
- **执行步骤**:
  1. 查询该 calculation 文档
  2. 检查响应 JSON 中 `null` 字段是否存在键名
  3. 确认值为 JSON `null` 而非字段缺失
- **预期输出**:
  - HTTP 状态码：`200`
  - 响应 JSON 中 `seven_day_annual_yield` 键存在，值为 `null`
  - 响应 JSON 中 `wanfen_income` 键存在，值为 `null`
  - 前端可据此展示 "N/A"
- **清理**: 无

---

## 三、异常测试

### TC-010: fund_code 格式非法返回业务错误

- **类型**: 异常测试
- **关联验收标准**: 基金代码格式校验（6 位数字）
- **前置条件**: 无
- **输入**:
  - `{"fund_code": "abc"}`
- **执行步骤**:
  1. 向 `POST /api/v1/calculations` 发送请求
  2. 检查 HTTP 状态码和业务错误码
- **预期输出**:
  - HTTP 状态码：`200`（业务错误走统一 ApiResponse 包装）
  - 响应体：`{"code": 40003, "message": "<含格式说明的中文错误信息>", "data": null}`
- **清理**: 无

---

### TC-011: POST 缺少 fund_code 字段返回 422

- **类型**: 异常测试
- **关联验收标准**: `fund_code` 必填
- **前置条件**: 无
- **输入**:
  - 请求体：`{}`（空对象，缺少 fund_code）
- **执行步骤**:
  1. 向 `POST /api/v1/calculations` 发送空请求体
  2. 检查 HTTP 状态码
- **预期输出**:
  - HTTP 状态码：`422`（FastAPI 自动 Pydantic 校验失败）
  - 响应体 `detail` 中包含字段缺失提示
- **清理**: 无

---

### TC-012: GET 不存在的 calculation_id 返回 404

- **类型**: 异常测试
- **关联验收标准**: 不存在时返回 404
- **前置条件**: 确保该 ID 在 MongoDB 中不存在
- **输入**:
  - 路径参数：`{id}` = `"aaaaaaaaaaaaaaaaaaaaaaaa"`（格式合法但不存在的 ObjectId）
- **执行步骤**:
  1. 向 `GET /api/v1/calculations/aaaaaaaaaaaaaaaaaaaaaaaa` 发送请求
  2. 检查 HTTP 状态码
- **预期输出**:
  - HTTP 状态码：`404`
  - 响应体包含提示信息（如 "计算结果不存在"）
- **清理**: 无

---

### TC-013: GET 无效格式 ID 返回错误

- **类型**: 异常测试
- **关联验收标准**: 健壮的错误处理（非标准 ObjectId 格式输入）
- **前置条件**: 无
- **输入**:
  - 路径参数：`{id}` = `"not-a-valid-id"`（非 24 字符十六进制字符串）
- **执行步骤**:
  1. 向 `GET /api/v1/calculations/not-a-valid-id` 发送请求
  2. 检查 HTTP 状态码
- **预期输出**:
  - HTTP 状态码：`404` 或 `400`（有意义的错误响应）
  - 不应返回 500（内部错误）
- **清理**: 无

---

## 四、集成测试

### TC-014: 路由注册到 main.py 并挂载 /api/v1 前缀

- **类型**: 集成测试
- **关联验收标准**: `api/routes/calculations.py` 注册到 main.py
- **前置条件**: 应用正常启动
- **输入**: 无（代码层面验证）
- **执行步骤**:
  1. 检查 `server/api/main.py` 中是否有 `from api.routes import calculations` 导入
  2. 检查是否有 `app.include_router(calculations.router, prefix="/api/v1")` 调用
  3. 启动应用后访问 `/api/v1/calculations` 相关端点
- **预期输出**:
  - `api/main.py` 中包含 calculations 路由的导入和注册
  - 路由注册使用 `prefix="/api/v1"`
  - 接口可通过 `/api/v1/calculations` 路径访问
- **清理**: 无

---

### TC-015: 缓存过期后重新计算

- **类型**: 集成测试
- **关联验收标准**: 使用 `core/cache.py` 对同一基金代码的计算结果缓存 5 分钟
- **前置条件**: 可模拟缓存过期（手动清除缓存或等待 5 分钟）
- **输入**:
  - 对同一基金代码触发两次计算，间隔 > 5 分钟
- **执行步骤**:
  1. POST `{"fund_code": "020741"}` → 获得 `calculation_id_1`
  2. 手动清除 `calc:` 前缀缓存（或等待配置的 TTL 过期）
  3. 再次 POST `{"fund_code": "020741"}` → 获得 `calculation_id_2`
  4. 对比两次 calculation_id
- **预期输出**:
  - `calculation_id_1` ≠ `calculation_id_2`（生成了新的计算记录）
  - 两次均返回 HTTP `200`
- **清理**: 删除 MongoDB 中创建的两条 calculation 文档

---

## 测试用例统计

| 类型 | 数量 |
|------|------|
| 功能测试 | 7 |
| 边界测试 | 2 |
| 异常测试 | 4 |
| 集成测试 | 2 |
| **合计** | **15** |

## 覆盖验收标准

| 验收标准 | 覆盖用例 |
|----------|----------|
| POST 接收 fund_code，返回 calculation_id + status | TC-001 |
| 基金代码格式校验（6 位数字） | TC-008, TC-010 |
| 同一基金代码 5 分钟内缓存命中 | TC-005, TC-015 |
| GET 返回完整 8 项指标（completed） | TC-002 |
| GET processing 状态返回提示 | TC-003 |
| GET failed 状态返回错误 | TC-004 |
| 计算结果持久化到 MongoDB | TC-006 |
| 路由注册到 main.py | TC-014 |
| Swagger 文档可见两个接口 | TC-007 |
| 使用 cache.py 缓存 5 分钟 | TC-005, TC-015 |
| 数值字段 None 时保留 | TC-009 |
| 不存在 ID 返回 404 | TC-012 |
