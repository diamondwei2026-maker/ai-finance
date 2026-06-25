# Task 1.3: 基金查询 API

| 属性 | 值 |
|------|-----|
| ID | 1.3 |
| 状态 | pending |
| 优先级 | P0 |
| 依赖 | 1.2 |
| 阶段 | 阶段1: 后端数据层 |
| 预估工时 | 3-4 小时 |

## 描述

实现完整的基金查询链路：repository 层（MongoDB CRUD）→ service 层（基金信息校验与类型判断）→ route 层（`GET /api/v1/funds/{code}`），集成交易日历和错误码体系。

## 验收标准

- [ ] `repositories/fund_repo.py` — 基金数据 MongoDB CRUD（`upsert_fund`、`find_by_code`）
- [ ] `services/fund_service.py` — 基金查询编排：调用 `data_fetcher` → 格式校验（6位数字）→ 类型判断（是否债券型）→ 缓存/持久化 → 返回
- [ ] `api/routes/funds.py` — `GET /api/v1/funds/{code}` 接口，返回统一响应格式 `{"code": 0, "message": "success", "data": {...}}`
- [ ] 输入校验：非 6 位数字返回 400；不存在的代码返回 40001；非债券型返回 40002
- [ ] `core/error_codes.py` 定义错误码常量：`FUND_NOT_FOUND = 40001`、`FUND_TYPE_MISMATCH = 40002`、`INVALID_CODE_FORMAT = 40003`
- [ ] `exchange_calendars` 集成：在 `core/trading_calendar.py` 中封装 `is_trading_day()` 判断函数
- [ ] API 路由注册到 `api/main.py`（含 `/api/v1` 前缀）
- [ ] Swagger 文档中可看到 `GET /api/v1/funds/{code}` 接口定义

## 子任务

### SUB-1.3.1: 基金 Repository
- **描述**: 实现基金数据的 MongoDB CRUD 操作
- **验收标准**:
  - [ ] `find_by_code(code)` 异步查询，返回 `Fund | None`
  - [ ] `upsert_fund(fund_data)` 异步插入或更新，返回 `Fund`
  - [ ] 异常时抛出 Beanie/MongoDB 原生异常（由 service 层捕获转换）

### SUB-1.3.2: 基金 Service
- **描述**: 实现基金查询业务逻辑
- **验收标准**:
  - [ ] `query_fund(code)` 方法：格式校验 → 查缓存/DB → 无缓存则调 data_fetcher → 持久化 → 返回
  - [ ] `validate_fund_type(fund_info)` 判断是否为债券型（类型含"债"字）
  - [ ] 基金不存在时抛出异常（含错误码 40001）
  - [ ] 非债券型时抛出异常（含错误码 40002 和实际类型）

### SUB-1.3.3: 基金路由 + 错误码 + 交易日历
- **描述**: 实现 API 路由、错误码常量和交易日历工具
- **验收标准**:
  - [ ] `GET /api/v1/funds/{code}` 正常返回基金信息（含 `disclaimer` 字段）
  - [ ] 异常场景返回对应错误码和中文提示信息
  - [ ] `core/error_codes.py` 含所有错误码常量
  - [ ] `core/trading_calendar.py` 含 `is_trading_day()` 函数，默认按非交易日处理（保守策略）
  - [ ] 路由注册到 main.py，含统一异常处理中间件
