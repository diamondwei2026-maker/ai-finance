# Task 1.2: 数据模型定义

| 属性 | 值 |
|------|-----|
| ID | 1.2 |
| 状态 | pending |
| 优先级 | P0 |
| 依赖 | 1.1 |
| 阶段 | 阶段1: 后端数据层 |
| 预估工时 | 1-2 小时 |

## 描述

定义 Pydantic/Beanie 文档模型（Fund、Calculation、MarketData）和 API 请求/响应 Schema。模型设计遵循 ADR 第六章数据模型定义，为后续 repository 层提供数据结构基础。

## 验收标准

- [ ] `models/fund.py` — Beanie Document：`fund_code`（唯一索引）、`name`、`fund_type`、`updated_at`
- [ ] `models/calculation.py` — Beanie Document：8 项指标字段（均为 `float | None`）+ `fund_code`、`data_date`、`is_trading_day`、`created_at`，复合索引 `(fund_code, created_at)`
- [ ] `models/market_data.py` — Beanie Document：`indicator_name`、`value`、`unit`、`fetched_at`，复合索引 `(indicator_name, fetched_at)`
- [ ] `models/schemas.py` — Pydantic BaseModel：API 请求/响应 Schema（`FundInfoResponse`、`CalculationRequest`、`CalculationResponse`、`ApiResponse[T]` 泛型包装）
- [ ] 所有响应 Schema 含 `disclaimer: str` 免责声明字段
- [ ] Beanie Document 的 `Settings` 类正确配置 collection name 和 indexes

## 子任务

### SUB-1.2.1: Fund 文档模型
- **描述**: 创建基金信息 MongoDB 文档模型
- **验收标准**:
  - [ ] `models/fund.py` 含 `Fund` 类（继承 `Document`），字段：`fund_code`（Indexed, unique）、`name`、`fund_type`、`updated_at`
  - [ ] Collection name 为 `funds`

### SUB-1.2.2: Calculation 文档模型
- **描述**: 创建计算结果 MongoDB 文档模型
- **验收标准**:
  - [ ] `models/calculation.py` 含 `Calculation` 类，8 项指标字段为 `float | None`，`data_date` 为 `str`，`created_at` 为 `datetime`
  - [ ] 复合索引 `(fund_code, created_at)` 降序
  - [ ] Collection name 为 `calculations`

### SUB-1.2.3: MarketData 文档模型 + API Schema
- **描述**: 创建市场数据文档模型和 API 请求/响应 Schema
- **验收标准**:
  - [ ] `models/market_data.py` 含 `MarketData` 类，复合索引 `(indicator_name, fetched_at)`
  - [ ] `models/schemas.py` 含所有请求/响应 Pydantic 模型，含 `ApiResponse[T]` 泛型
  - [ ] `FundInfoResponse` 含 `disclaimer` 字段；`CalculationResponse` 含 `disclaimer` 字段
