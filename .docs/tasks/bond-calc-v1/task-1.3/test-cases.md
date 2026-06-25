# 测试用例 — Task 1.3: 基金查询 API

> 生成日期：2025-06-25 | 共 13 个用例

---

## 一、功能测试

### TC-001: 查询存在的债券型基金 — 完整查询链路
- **类型**: 功能测试
- **关联验收标准**: `services/fund_service.py` — 基金查询编排；`GET /api/v1/funds/{code}` 正常返回
- **前置条件**:
  - MongoDB 已连接，`funds` 集合中无该基金缓存
  - akshare 数据源可用
- **输入**:
  - `GET /api/v1/funds/020741`（债券型基金代码）
- **执行步骤**:
  1. 发送 GET 请求到 `/api/v1/funds/020741`
  2. 验证 HTTP 响应
  3. 查询 MongoDB `funds` 集合确认数据已缓存
- **预期输出**:
  - HTTP 状态码：`200`
  - 响应体结构：
    ```json
    {
      "code": 0,
      "message": "success",
      "data": {
        "fund_code": "020741",
        "name": "（非空字符串）",
        "fund_type": "（含"债"字的类型，如"中长期纯债"）",
        "nav": null 或正浮点数,
        "seven_day_annual_yield": null 或正浮点数,
        "updated_at": "ISO 8601 时间字符串",
        "disclaimer": "（免责声明固定文本）"
      }
    }
    ```
  - MongoDB `funds` 集合中存在 `fund_code = "020741"` 的文档
- **清理**: 删除 MongoDB 中该基金的测试数据

### TC-002: 查询已缓存的基金 — 跳过外部数据源
- **类型**: 功能测试
- **关联验收标准**: `services/fund_service.py` — 查缓存/DB 路径
- **前置条件**:
  - MongoDB `funds` 集合中已存在 `fund_code = "020741"` 的文档
  - fund_type 含"债"字
- **输入**:
  - `GET /api/v1/funds/020741`
- **执行步骤**:
  1. 预先在 DB 中插入基金文档（模拟已缓存）
  2. 发送 GET 请求
  3. 验证响应中的 `updated_at` 与缓存一致（未触发外部数据源刷新）
- **预期输出**:
  - HTTP 状态码：`200`
  - `data.name` 与缓存文档一致
  - `data.updated_at` 与缓存文档的 `updated_at` 一致
- **清理**: 删除预插入的测试文档

### TC-003: 响应体包含 disclaimer 免责声明字段
- **类型**: 功能测试
- **关联验收标准**: `GET /api/v1/funds/{code}` 返回含 `disclaimer` 字段
- **前置条件**: 同 TC-001
- **输入**: `GET /api/v1/funds/020741`
- **执行步骤**:
  1. 发送 GET 请求
  2. 检查响应体 `data.disclaimer` 字段
- **预期输出**:
  - `data.disclaimer` 为非空字符串，内容包含免责声明文案
- **清理**: 同 TC-001

---

## 二、边界测试

### TC-004: 基金代码恰好 6 位数字
- **类型**: 边界测试
- **关联验收标准**: 输入校验 — 非 6 位数字返回 400
- **前置条件**: 无
- **输入**: `GET /api/v1/funds/000001`（恰好 6 位数字，边界有效值）
- **执行步骤**:
  1. 发送 GET 请求
  2. 验证格式校验通过（不返回 400 格式错误）
- **预期输出**:
  - HTTP 状态码：`200`（格式校验通过；基金是否存在由后续逻辑判断）
  - 如基金不存在，返回 `code: 40001` 而非 `40003`
- **清理**: 如写入 DB 则清理

### TC-005: 基金代码位数不足/超出
- **类型**: 边界测试
- **关联验收标准**: 输入校验 — 非 6 位数字返回 400
- **前置条件**: 无
- **输入**:
  - `GET /api/v1/funds/12345`（5 位）
  - `GET /api/v1/funds/1234567`（7 位）
  - `GET /api/v1/funds/`（空字符串）
- **执行步骤**:
  1. 依次发送以上 3 个请求
  2. 验证每个请求的响应
- **预期输出**:
  - 每个请求：HTTP 状态码 `400`
  - `code: 40003`
  - `message` 含"格式"相关中文提示
  - `data: null`
- **清理**: 无

### TC-006: 基金代码含非数字字符
- **类型**: 边界测试
- **关联验收标准**: 输入校验 — 非 6 位数字返回 400
- **前置条件**: 无
- **输入**:
  - `GET /api/v1/funds/02074A`（含字母）
  - `GET /api/v1/funds/02074-`（含特殊字符）
  - `GET /api/v1/funds/ 02074`（含空格）
- **执行步骤**:
  1. 依次发送以上请求
  2. 验证每个请求的响应
- **预期输出**:
  - 每个请求：HTTP 状态码 `400`
  - `code: 40003`
  - `data: null`
- **清理**: 无

---

## 三、异常测试

### TC-007: 基金代码格式错误 — INVALID_CODE_FORMAT
- **类型**: 异常测试
- **关联验收标准**: 输入校验 — 非 6 位数字返回 400；`INVALID_CODE_FORMAT = 40003`
- **前置条件**: 无
- **输入**: `GET /api/v1/funds/abc`
- **执行步骤**:
  1. 发送 GET 请求
  2. 验证错误响应结构
  3. 确认未访问外部数据源（无网络请求）
- **预期输出**:
  - HTTP 状态码：`400`
  - 响应体：
    ```json
    {
      "code": 40003,
      "message": "基金代码格式错误，请输入6位数字代码",
      "data": null
    }
    ```
- **清理**: 无

### TC-008: 基金不存在 — FUND_NOT_FOUND
- **类型**: 异常测试
- **关联验收标准**: 不存在的代码返回 40001；`FUND_NOT_FOUND = 40001`
- **前置条件**: akshare 数据源可用
- **输入**: `GET /api/v1/funds/999999`（不存在的基金代码）
- **执行步骤**:
  1. 发送 GET 请求
  2. 验证错误响应
- **预期输出**:
  - HTTP 状态码：`200`（业务错误，非 HTTP 错误）
  - 响应体：
    ```json
    {
      "code": 40001,
      "message": "基金不存在（代码：999999），请检查后重新输入",
      "data": null
    }
    ```
- **清理**: 无（不应写入 DB）

### TC-009: 非债券型基金 — FUND_TYPE_MISMATCH
- **类型**: 异常测试
- **关联验收标准**: 非债券型返回 40002；`FUND_TYPE_MISMATCH = 40002`
- **前置条件**:
  - akshare 数据源可用
  - 使用混合型/股票型基金代码（如 `000001` — 华夏成长混合）
- **输入**: `GET /api/v1/funds/000001`（混合型基金，类型不含"债"）
- **执行步骤**:
  1. 发送 GET 请求
  2. 验证返回错误码 40002
- **预期输出**:
  - HTTP 状态码：`200`（业务错误，非 HTTP 错误）
  - 响应体：
    ```json
    {
      "code": 40002,
      "message": "（含实际基金类型的中文提示，如"仅支持债券型基金，当前类型：混合型"）",
      "data": null
    }
    ```
- **清理**: 如意外写入 DB 则清理

### TC-010: 外部数据源不可用时的优雅降级
- **类型**: 异常测试
- **关联验收标准**: `services/fund_service.py` — 调用 data_fetcher 异常处理
- **前置条件**:
  - MongoDB 中无该基金缓存
  - 模拟 akshare 网络超时/不可用（可通过 mock 或断网测试）
- **输入**: `GET /api/v1/funds/020741`
- **执行步骤**:
  1. Mock `data_fetcher.fetch_fund_info` 抛出 `RecoverableError`
  2. 发送 GET 请求
  3. 验证异常被正确转换为错误响应
- **预期输出**:
  - HTTP 状态码：`200` 或 `503`（根据异常类型：单个数据源失败为 200，全部不可用为 503）
  - `code` 为非 0 错误码
  - `message` 含中文错误描述
  - `data: null`
- **清理**: 恢复 mock

---

## 四、集成测试

### TC-011: Repository → Service → Route 端到端链路
- **类型**: 集成测试
- **关联验收标准**: 全部（端到端验证）
- **前置条件**:
  - MongoDB 已连接，Beanie 已初始化（Fund 模型已注册）
  - akshare 数据源可用
- **输入**: `GET /api/v1/funds/020741`
- **执行步骤**:
  1. 首次请求：走完整链路（外部数据源 → Service → Repository 写入 → Route 响应）
  2. 二次请求：走缓存链路（Repository 读取 → Service → Route 响应）
  3. 对比两次响应的 `fund_code`、`name`、`fund_type` 是否一致
  4. 验证首次请求的 `updated_at` ≤ 二次请求的 `updated_at`
- **预期输出**:
  - 两次请求均返回 `200`，`code: 0`
  - 两次 `fund_code`、`name`、`fund_type` 相同
  - 首次写入 DB 成功，二次从 DB 读取成功
- **清理**: 删除 MongoDB 中该基金的测试数据

### TC-012: 交易日历 is_trading_day() 函数
- **类型**: 集成测试
- **关联验收标准**: `core/trading_calendar.py` — `is_trading_day()` 默认按非交易日处理
- **前置条件**: `exchange_calendars` 已安装
- **输入**: 调用 `is_trading_day(date)` 函数
- **执行步骤**:
  1. 调用 `is_trading_day()` 不传参数（默认当天）
  2. 调用 `is_trading_day(datetime.date(2025, 6, 21))` — 周六
  3. 调用 `is_trading_day(datetime.date(2025, 6, 23))` — 周一
  4. 模拟 `exchange_calendars` 抛出异常，验证返回 `False`（保守策略）
- **预期输出**:
  - 周六 → `False`
  - 周一（非节假日）→ `True`
  - 异常时 → `False`（默认非交易日，保守策略）
- **清理**: 无

### TC-013: Swagger 文档可见性
- **类型**: 集成测试
- **关联验收标准**: Swagger 文档中可看到 `GET /api/v1/funds/{code}` 接口定义
- **前置条件**: 应用已启动
- **输入**: 访问 `/docs` (Swagger UI)
- **执行步骤**:
  1. 启动应用
  2. 浏览器/HTTP 客户端访问 `GET /docs`
  3. 检查 OpenAPI JSON：`GET /openapi.json`
- **预期输出**:
  - OpenAPI JSON 的 `paths` 中包含 `/api/v1/funds/{code}`
  - 接口包含 `get` 方法
  - `parameters` 中包含 `code`（path 参数，string 类型）
  - `responses` 包含 `200` 和 `400` 状态码定义
- **清理**: 无

---

## 附录：错误码速查

| 错误码 | 常量名 | HTTP 状态码 | 含义 |
|--------|--------|------------|------|
| 0 | — | 200 | 成功 |
| 40001 | `FUND_NOT_FOUND` | 200 | 基金代码不存在 |
| 40002 | `FUND_TYPE_MISMATCH` | 200 | 基金类型不匹配（非债券型） |
| 40003 | `INVALID_CODE_FORMAT` | 400 | 基金代码格式错误 |
