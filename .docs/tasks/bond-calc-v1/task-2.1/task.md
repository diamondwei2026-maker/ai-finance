# Task 2.1: 计算引擎与市场数据服务

| 属性 | 值 |
|------|-----|
| ID | 2.1 |
| 状态 | pending |
| 优先级 | P0 |
| 依赖 | 1.3 |
| 阶段 | 阶段2: 计算引擎 |
| 预估工时 | 3-4 小时 |

## 描述

实现收益计算编排服务（`calculation_service.py`）和市场数据服务（`market_service.py` + `market_repo.py`）。计算引擎并行拉取多个数据源，计算 8 项收益指标，支持数据缺失优雅降级。市场数据服务负责获取和缓存市场利率数据。

## 验收标准

- [ ] `services/calculation_service.py` — 核心方法 `calculate(fund_code: str) -> CalculationResult`
  - 使用 `asyncio.gather` 并行拉取基金信息、历史净值、市场利率数据
  - 单源失败不中断整体流程（`return_exceptions=True`），缺失指标标 N/A
  - 所有数据源全挂时抛出 `FatalError`
- [ ] 8 项指标计算逻辑完整实现（见子任务明细）
- [ ] `services/market_service.py` — 市场利率数据获取与缓存
- [ ] `repositories/market_repo.py` — 市场数据的 MongoDB CRUD（`save_market_data`、`get_latest`）
- [ ] 计算结果含 `disclaimer` 免责声明字段和 `data_date` 数据时效标注
- [ ] 交易日判断：调用 `core/trading_calendar.is_trading_day()`，非交易日标注提示

## 子任务

### SUB-2.1.1: 8 项指标计算逻辑
- **描述**: 实现所有指标的单函数计算
- **验收标准**:
  - [ ] 最新单位净值：直接获取
  - [ ] 日涨跌幅：`(当日净值 - 前一日净值) / 前一日净值 × 100`
  - [ ] 七日年化收益率：直接获取或按监管公式计算
  - [ ] 万份收益：直接获取
  - [ ] 近1月收益率：`(最新净值 - 30日前净值) / 30日前净值 × 100`
  - [ ] 近3月最大回撤：`max(1 - 当日净值 / 区间最高净值) × 100`
  - [ ] 10年期国债收益率：直接获取
  - [ ] 信用利差（AA+）：AA+企业债收益率 - 同期限国债收益率
  - [ ] 每个指标独立计算，单个失败不影响其他指标

### SUB-2.1.2: 计算编排服务
- **描述**: 实现并行拉取 + 指标计算编排
- **验收标准**:
  - [ ] `asyncio.gather` 并行调用 3-4 个数据获取函数
  - [ ] `return_exceptions=True` 处理单源失败，失败指标标 `None`
  - [ ] 全部失败时抛出 `FatalError`
  - [ ] 计算结果通过缓存检查，5 分钟内重复请求返回缓存（`core/cache.py`）

### SUB-2.1.3: 市场数据服务
- **描述**: 实现市场利率数据获取、缓存和持久化
- **验收标准**:
  - [ ] `market_service.get_market_rates()` 返回 `{"ten_year_treasury": ..., "credit_spread_aa_plus": ...}`
  - [ ] 优先从内存缓存读取（TTL 2min），缓存未命中则调 data_fetcher 并写缓存
  - [ ] `market_repo` 持久化到 MongoDB（供后续历史查询扩展）
