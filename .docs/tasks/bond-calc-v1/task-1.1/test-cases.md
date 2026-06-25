# 测试用例 — Task 1.1: 外部数据源适配（akshare）

> 生成日期：2025-06-25 | 关联 Task：[task.md](./task.md)

---

## 测试范围概述

| 维度 | 覆盖说明 |
|------|----------|
| 功能测试 | 验证 4 个数据获取函数正常返回、数据结构统一、字段完整 |
| 边界测试 | 无效代码、新基金历史不足、参数边界 |
| 异常测试 | 网络不可达、akshare 抛异常、数据源返回空 |
| 集成测试 | 与 `RecoverableError` 异常体系集成、asyncio 事件循环兼容 |

---

## 功能测试

### TC-001: fetch_fund_info 返回完整基金信息（真实代码）
- **类型**: 功能测试
- **关联验收标准**: `fetch_fund_info` 返回基金名称、类型、最新净值、七日年化；真实代码 `020741` 调用验证
- **前置条件**: 网络可达，akshare 已安装
- **输入**:
  - `code = "020741"`
- **执行步骤**:
  1. 调用 `await fetch_fund_info("020741")`
  2. 检查返回 dict 的字段完整性
- **预期输出**:
  - 返回 dict，字段包含：
    - `indicator` = `"fund_info"`
    - `value` = `None`（复合数据，value 为 None 合理）
    - `name` 字段：非空字符串
    - `code` 字段 = `"020741"`
    - `type` 字段：非空字符串
    - `nav` 字段（最新净值）：float
    - `seven_day_yield` 字段（七日年化）：float 或 None
    - `source` = `"akshare"`
    - `fetched_at`：datetime 类型
- **清理**: 无

### TC-002: fetch_fund_nav_history 返回历史净值序列（默认 90 天）
- **类型**: 功能测试
- **关联验收标准**: `fetch_fund_nav_history` 返回日期 + 单位净值列表，按日期降序
- **前置条件**: 网络可达
- **输入**:
  - `code = "020741"`, `days = 90`（默认）
- **执行步骤**:
  1. 调用 `await fetch_fund_nav_history("020741")`
  2. 检查返回结构
- **预期输出**:
  - 返回 dict，字段包含：
    - `indicator` = `"fund_nav_history"`
    - `value` = `None`（列表数据，value 为 None）
    - `data` 字段：`list[dict]`，每项含 `date`（date/str）、`nav`（float）
    - `data` 按日期降序排列（最新在前）
    - `data` 长度 ≤ 90
    - `source` = `"akshare"`
    - `fetched_at`：datetime 类型
- **清理**: 无

### TC-003: fetch_treasury_yield 返回 10 年期国债收益率
- **类型**: 功能测试
- **关联验收标准**: `fetch_treasury_yield` 返回当前 10 年期国债收益率
- **前置条件**: 网络可达
- **输入**:
  - 无参数
- **执行步骤**:
  1. 调用 `await fetch_treasury_yield()`
  2. 验证返回值
- **预期输出**:
  - 返回 dict：
    - `indicator` = `"treasury_yield_10y"`
    - `value`：float，典型范围 1.5 ~ 5.0（%）
    - `unit` = `"%"`
    - `source` = `"akshare"`
    - `fetched_at`：datetime 类型
- **清理**: 无

### TC-004: fetch_credit_spread 返回 AA+ 信用利差
- **类型**: 功能测试
- **关联验收标准**: `fetch_credit_spread` 返回 AA+ 信用利差（bp）
- **前置条件**: 网络可达
- **输入**:
  - 无参数
- **执行步骤**:
  1. 调用 `await fetch_credit_spread()`
  2. 验证返回值
- **预期输出**:
  - 返回 dict：
    - `indicator` = `"credit_spread_aa_plus"`
    - `value`：float，典型范围 50 ~ 300（bp）
    - `unit` = `"bp"`
    - `source` = `"akshare"`
    - `fetched_at`：datetime 类型
- **清理**: 无

### TC-005: 返回数据结构统一格式校验
- **类型**: 功能测试
- **关联验收标准**: 返回数据结构统一 — `{"indicator": str, "value": float | None, "unit": str, "source": str, "fetched_at": datetime}`
- **前置条件**: 所有函数可正常返回
- **输入**:
  - 依次调用 4 个函数
- **执行步骤**:
  1. 对每个函数的返回值逐一校验
  2. 检查必含字段 `indicator`、`value`、`unit`、`source`、`fetched_at`
  3. 校验字段类型
- **预期输出**:
  - 每个返回值均包含 5 个顶层必含字段
  - `indicator`：str 类型，非空
  - `value`：float | None
  - `unit`：str 类型，非空
  - `source`：str 类型 = `"akshare"`
  - `fetched_at`：datetime 类型
- **清理**: 无

---

## 边界测试

### TC-006: fetch_fund_info 无效基金代码抛 RecoverableError
- **类型**: 边界测试
- **关联验收标准**: SUB-1.1.1 — 无效代码返回 `RecoverableError("基金不存在")`
- **前置条件**: 网络可达
- **输入**:
  - `code = "000000"`（不存在的基金代码）
- **执行步骤**:
  1. 调用 `await fetch_fund_info("000000")`
  2. 捕获异常
- **预期输出**:
  - 抛出 `RecoverableError`
  - `exception.message` 包含 "基金不存在"
  - `exception.code` = `40001`（FUND_NOT_FOUND）
- **清理**: 无

### TC-007: fetch_fund_info 空字符串代码抛 RecoverableError
- **类型**: 边界测试
- **关联验收标准**: 每个函数内置 try/except，返回 `RecoverableError`
- **前置条件**: 无
- **输入**:
  - `code = ""`
- **执行步骤**:
  1. 调用 `await fetch_fund_info("")`
  2. 捕获异常
- **预期输出**:
  - 抛出 `RecoverableError`（含指标名称标识）
- **清理**: 无

### TC-008: fetch_fund_nav_history 新基金历史不足返回已有数据
- **类型**: 边界测试
- **关联验收标准**: SUB-1.1.2 — 新基金历史不足时返回已有数据（不抛异常）
- **前置条件**: 网络可达
- **输入**:
  - `code = "020741"`（或任意成立时间较短的基金），`days = 365`
- **执行步骤**:
  1. 调用 `await fetch_fund_nav_history("020741", days=365)`
  2. 检查返回数据长度
- **预期输出**:
  - 正常返回 dict（不抛异常）
  - `data` 列表长度 < 365（返回实际可获取的天数）
  - 无错误
- **清理**: 无

### TC-009: fetch_fund_nav_history days=0 参数处理
- **类型**: 边界测试
- **关联验收标准**: 函数内置异常处理
- **前置条件**: 无
- **输入**:
  - `code = "020741"`, `days = 0`
- **执行步骤**:
  1. 调用 `await fetch_fund_nav_history("020741", days=0)`
- **预期输出**:
  - 返回空列表，或抛出 `RecoverableError`
  - 不应导致未捕获异常
- **清理**: 无

---

## 异常测试

### TC-010: akshare 网络不可达时抛 RecoverableError
- **类型**: 异常测试
- **关联验收标准**: 每个函数内置 try/except，抛出 `RecoverableError`（含指标名称标识）
- **前置条件**: 模拟网络不可达（mock akshare 导出异常），或断网环境
- **输入**:
  - 任意有效基金代码
- **执行步骤**:
  1. Mock akshare 底层函数使其抛出 `ConnectionError`
  2. 调用 `await fetch_fund_info("020741")`
- **预期输出**:
  - 抛出 `RecoverableError`
  - `exception.message` 包含指标名称标识（如 "fund_info"）
  - `exception.code` = `40003`（DATA_SOURCE_FAILED）
- **清理**: 恢复 mock

### TC-011: akshare 返回空 DataFrame 时抛 RecoverableError
- **类型**: 异常测试
- **关联验收标准**: 每个函数内置 try/except
- **前置条件**: Mock akshare 返回空 DataFrame
- **输入**:
  - Mock `fund_open_fund_info_em` 返回空 DataFrame
- **执行步骤**:
  1. 调用 `await fetch_fund_info("020741")`
- **预期输出**:
  - 抛出 `RecoverableError`
  - `exception.message` 包含 "数据为空" 或类似描述
- **清理**: 恢复 mock

### TC-012: 单个利率指标获取失败不影响其他指标
- **类型**: 异常测试
- **关联验收标准**: SUB-1.1.3 — 单个指标获取失败抛出 `RecoverableError`（不影响其他指标）
- **前置条件**: Mock `fetch_treasury_yield` 对应的 akshare 调用失败
- **输入**:
  - 分别调用 `fetch_treasury_yield()` 和 `fetch_credit_spread()`
- **执行步骤**:
  1. Mock 国债收益率数据源使其失败
  2. 调用 `await fetch_treasury_yield()` → 验证抛 `RecoverableError`
  3. 调用 `await fetch_credit_spread()` → 验证正常返回
- **预期输出**:
  - `fetch_treasury_yield` 抛 `RecoverableError`
  - `fetch_credit_spread` 正常返回（不受前者影响）
  - 两个函数相互独立
- **清理**: 恢复 mock

---

## 集成测试

### TC-013: 异步调用兼容性（asyncio 事件循环）
- **类型**: 集成测试
- **关联验收标准**: 使用 `asyncio.to_thread` 包装同步 akshare 调用
- **前置条件**: 网络可达
- **输入**:
  - 4 个异步函数
- **执行步骤**:
  1. 在 asyncio 事件循环中调用 `await fetch_fund_info("020741")`
  2. 在 asyncio 事件循环中调用 `await fetch_fund_nav_history("020741")`
  3. 在 asyncio 事件循环中调用 `await fetch_treasury_yield()`
  4. 在 asyncio 事件循环中调用 `await fetch_credit_spread()`
- **预期输出**:
  - 所有调用均在事件循环中正常完成，不阻塞事件循环
  - 返回值类型正确
- **清理**: 无

### TC-014: 与 RecoverableError 异常体系集成
- **类型**: 集成测试
- **关联验收标准**: 每个函数抛出的异常可被 FastAPI 全局异常处理器识别
- **前置条件**: `server.core.exceptions` 中的 `RecoverableError` 已定义
- **输入**:
  - Mock 数据源失败
- **执行步骤**:
  1. Mock akshare 使其抛异常
  2. 调用 `await fetch_fund_info("020741")`
  3. 验证抛出的异常为 `RecoverableError` 实例
  4. 验证 `isinstance(exception, AppException)` 为 True
- **预期输出**:
  - 异常为 `RecoverableError` 类型
  - `exception.status_code` = `200`
  - `exception.code` 为有效错误码
- **清理**: 恢复 mock

### TC-015: akshare 版本锁定验证
- **类型**: 集成测试
- **关联验收标准**: akshare 已在 `requirements.txt` 中锁定版本
- **前置条件**: `requirements.txt` 已存在
- **输入**:
  - 读取 `server/requirements.txt`
- **执行步骤**:
  1. 检查 `requirements.txt` 中 `akshare` 行
  2. 验证版本已锁定（使用 `>=` 或 `==` 固定最低版本）
- **预期输出**:
  - `akshare` 行存在且固定版本号
  - 版本号 ≥ 1.14.0
- **清理**: 无

---

## 测试汇总

| 编号 | 名称 | 类型 | 关联验收标准 |
|------|------|------|-------------|
| TC-001 | fetch_fund_info 返回完整基金信息 | 功能 | 验收标准 1、4 |
| TC-002 | fetch_fund_nav_history 返回历史净值序列 | 功能 | 验收标准 1 |
| TC-003 | fetch_treasury_yield 返回国债收益率 | 功能 | 验收标准 1 |
| TC-004 | fetch_credit_spread 返回信用利差 | 功能 | 验收标准 1 |
| TC-005 | 返回数据结构统一格式校验 | 功能 | 验收标准 3 |
| TC-006 | fetch_fund_info 无效代码抛 RecoverableError | 边界 | SUB-1.1.1 |
| TC-007 | fetch_fund_info 空字符串代码 | 边界 | 验收标准 2 |
| TC-008 | 新基金历史不足返回已有数据 | 边界 | SUB-1.1.2 |
| TC-009 | days=0 参数处理 | 边界 | 验收标准 2 |
| TC-010 | 网络不可达时抛 RecoverableError | 异常 | 验收标准 2 |
| TC-011 | 返回空 DataFrame 时抛 RecoverableError | 异常 | 验收标准 2 |
| TC-012 | 单个利率指标失败不影响其他 | 异常 | SUB-1.1.3 |
| TC-013 | 异步调用兼容性 | 集成 | 验收标准 1 |
| TC-014 | 与 RecoverableError 异常体系集成 | 集成 | 验收标准 2 |
| TC-015 | akshare 版本锁定验证 | 集成 | 验收标准 5 |

---

## 统计

| 类型 | 数量 |
|------|------|
| 功能测试 | 5 |
| 边界测试 | 4 |
| 异常测试 | 3 |
| 集成测试 | 3 |
| **合计** | **15** |
