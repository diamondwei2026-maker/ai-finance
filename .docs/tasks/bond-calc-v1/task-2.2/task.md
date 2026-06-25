# Task 2.2: 计算 API 路由

| 属性 | 值 |
|------|-----|
| ID | 2.2 |
| 状态 | done |
| 优先级 | P0 |
| 依赖 | 2.1 |
| 阶段 | 阶段2: 计算引擎 |
| 预估工时 | 2-3 小时 |

## 描述

实现计算触发与结果查询的 REST API：`POST /api/v1/calculations`（触发计算）和 `GET /api/v1/calculations/{id}`（获取结果）。计算结果持久化到 MongoDB，支持后续查询。

## 验收标准

- [ ] `POST /api/v1/calculations` — 接收 `{"fund_code": "020741"}`，触发异步计算，返回 `{"calculation_id": "...", "status": "processing"}`
  - 基金代码格式校验（6 位数字）
  - 同一基金代码 + 5 分钟内已有缓存结果直接返回已有的 calculation_id
- [ ] `GET /api/v1/calculations/{id}` — 返回完整 8 项指标计算结果
  - 状态 `processing` 时返回 `{"status": "processing", "message": "计算中，请稍后刷新"}`
  - 状态 `completed` 时返回所有指标 + `data_date` + `is_trading_day` + `disclaimer`
  - 状态 `failed` 时返回错误信息
- [ ] 计算结果持久化到 MongoDB `calculations` 集合
- [ ] `api/routes/calculations.py` 注册到 main.py
- [ ] Swagger 文档中可看到两个接口定义
- [ ] 使用 `core/cache.py` 对同一基金代码的计算结果缓存 5 分钟

## 子任务

### SUB-2.2.1: 计算触发接口
- **描述**: 实现 POST /api/v1/calculations
- **验收标准**:
  - [ ] 请求体校验：`fund_code` 必填，格式为 6 位数字
  - [ ] 调用 `calculation_service.calculate()` 执行计算
  - [ ] 计算结果持久化到 MongoDB
  - [ ] 返回 `calculation_id`（MongoDB 文档 `_id` 字符串）
  - [ ] 缓存命中时直接返回已有结果

### SUB-2.2.2: 计算结果查询接口
- **描述**: 实现 GET /api/v1/calculations/{id}
- **验收标准**:
  - [ ] 根据 ID 查询 MongoDB `calculations` 集合
  - [ ] 不存在时返回 404
  - [ ] 存在时返回完整 CalculationResponse（含 disclaimer）
  - [ ] 数值字段 `None` 时在响应中保留（前端展示为 N/A）

### SUB-2.2.3: 路由注册与 Swagger 验证
- **描述**: 注册路由、添加接口文档注解
- **验收标准**:
  - [ ] 路由注册到 main.py，路径前缀 `/api/v1`
  - [ ] 每个接口含 FastAPI 装饰器文档（`summary`、`response_model`、`responses`）
  - [ ] Swagger 文档可查看并测试两个接口
