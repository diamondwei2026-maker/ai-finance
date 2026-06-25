# Task 1.1: 外部数据源适配（akshare）

| 属性 | 值 |
|------|-----|
| ID | 1.1 |
| 状态 | done |
| 优先级 | P0 |
| 依赖 | 0.1 |
| 阶段 | 阶段1: 后端数据层 |
| 预估工时 | 3-4 小时 |

## 描述

封装 akshare 作为统一的外部数据源适配层。通过 `external/data_fetcher.py` 实现对天天基金、东方财富、中债信息网等上游数据源的调用封装，提供基金信息、历史净值和市场利率三类数据获取能力，并内置异常分级处理。

## 验收标准

- [ ] `external/data_fetcher.py` 提供以下异步函数（使用 `asyncio.to_thread` 包装同步 akshare 调用）：
  - `fetch_fund_info(code: str) -> dict` — 获取基金名称、类型、最新净值、七日年化等
  - `fetch_fund_nav_history(code: str, days: int = 90) -> list[dict]` — 获取历史净值序列
  - `fetch_treasury_yield() -> dict` — 获取 10 年期国债收益率
  - `fetch_credit_spread() -> dict` — 获取信用利差（AA+）
- [ ] 每个函数内置 try/except，单个数据源异常抛出 `RecoverableError`（含指标名称标识）
- [ ] 返回数据结构统一：`{"indicator": str, "value": float | None, "unit": str, "source": str, "fetched_at": datetime}`
- [ ] 函数调用验证：使用真实基金代码（如 `020741`）调用 `fetch_fund_info`，返回有效数据
- [ ] akshare 已在 `requirements.txt` 中锁定版本

## 子任务

### SUB-1.1.1: 基金信息数据获取
- **描述**: 使用 akshare 的 `fund_open_fund_info_em` 或等价接口获取基金基本信息
- **验收标准**:
  - [ ] `fetch_fund_info` 返回基金名称、代码、类型、最新净值、七日年化
  - [ ] 无效代码返回 `RecoverableError("基金不存在")`

### SUB-1.1.2: 历史净值数据获取
- **描述**: 使用 akshare 获取基金历史净值序列（近 90 日）
- **验收标准**:
  - [ ] `fetch_fund_nav_history` 返回日期 + 单位净值列表，按日期降序
  - [ ] 新基金历史不足时返回已有数据（不抛异常）

### SUB-1.1.3: 市场利率数据获取
- **描述**: 获取 10 年期国债收益率和信用利差
- **验收标准**:
  - [ ] `fetch_treasury_yield` 返回当前 10 年期国债收益率
  - [ ] `fetch_credit_spread` 返回 AA+ 信用利差（bp）
  - [ ] 单个指标获取失败抛出 `RecoverableError`（不影响其他指标）
