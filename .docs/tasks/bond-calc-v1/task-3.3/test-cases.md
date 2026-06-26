# 测试用例 — Task 3.3: 计算结果页与组件

> 生成日期：2025-06-26 | 用例总数：30

---

## 测试范围总览

| 维度 | 数量 | 覆盖组件 |
|------|------|----------|
| 功能测试 | 15 | 全部 6 个组件 |
| 边界测试 | 8 | ResultHeader / NavGrid / YieldMetrics / MarketRates |
| 异常测试 | 4 | FundResult / RefreshButton |
| 集成测试 | 3 | 页面整体 / Store / Router |

---

## 一、FundResult.vue — 页面主组件

### TC-001: 进入页面自动触发计算
- **类型**: 功能测试
- **关联验收标准**: FundResult — 进入页面自动触发计算
- **前置条件**:
  - Store 初始状态无数据（fundInfo / calculation 均为 null）
  - 路由已注册 `/fund/:code`
- **输入**:
  - 路由跳转到 `/fund/020741`（或任意有效基金代码）
- **执行步骤**:
  1. 组件挂载（`onMounted` 触发）
  2. 观察 Store 的 `refreshCalculation` 是否被调用
- **预期输出**:
  - `fundStore.refreshCalculation("020741")` 被调用一次
  - `loading` 状态变为 `true`
  - 页面展示骨架屏（Skeleton），不展示空白
- **清理**: 无

### TC-002: query 参数 ?refresh=1 时重新触发计算
- **类型**: 功能测试
- **关联验收标准**: FundResult — query 参数 `?refresh=1` 时重新触发计算
- **前置条件**:
  - Store 中已有历史计算结果（calculation 不为 null）
  - 路由携带 query: `/fund/020741?refresh=1`
- **输入**:
  - 导航到 `/fund/020741?refresh=1`
- **执行步骤**:
  1. 组件挂载
  2. 检测到 `route.query.refresh === '1'`
  3. 调用 `fundStore.refreshCalculation("020741")`
- **预期输出**:
  - 即使已有旧计算结果，仍重新触发计算
  - `loading` 变为 `true`
  - 旧结果被新结果覆盖
- **清理**: 无

### TC-003: 加载中显示骨架屏
- **类型**: 功能测试
- **关联验收标准**: FundResult — 加载中显示骨架屏
- **前置条件**:
  - `loading = true`，`calculation = null`
- **输入**:
  - 页面处于加载状态
- **执行步骤**:
  1. 挂载 FundResult 组件
  2. 模拟 Store `loading = true`
- **预期输出**:
  - 显示 3 个骨架屏占位卡片（分别对应 ResultHeader / YieldMetrics / MarketRates 区域）
  - 骨架屏有脉冲动画（`animate-pulse`）
  - 不展示实际数据内容
- **清理**: 无

### TC-004: 计算完成后展示完整结果
- **类型**: 集成测试
- **关联验收标准**: FundResult — 计算完成后展示完整结果
- **前置条件**:
  - Store 中 `calculation` 为 completed 状态，含完整 8 项指标
  - `fundInfo` 已填充
- **输入**:
  - `calculation.status = 'completed'`，所有字段有值
- **执行步骤**:
  1. 挂载 FundResult
  2. 等待 Store 计算完成
- **预期输出**:
  - 骨架屏消失
  - ResultHeader 渲染（基金名称、代码、日期）
  - NavGrid 渲染（净值、日涨跌）
  - YieldMetrics 渲染（4 项收益指标）
  - MarketRates 渲染（2 项市场利率）
  - DisclaimerBar 渲染在底部
  - RefreshButton 渲染且可用
- **清理**: 无

### TC-005: 错误状态展示
- **类型**: 异常测试
- **关联验收标准**: FundResult — 错误状态下展示错误提示 + 重试按钮
- **前置条件**:
  - Store 中 `error` 不为 null（如 `"计算失败，请稍后重试"`）
  - `calculation = null`
- **输入**:
  - Store `error = "计算失败，请稍后重试"`
- **执行步骤**:
  1. 挂载 FundResult
  2. 模拟 Store 返回错误状态
- **预期输出**:
  - 显示错误消息文案（红色警告样式）
  - 显示"重试"按钮
  - 点击重试按钮 → 调用 `fundStore.refreshCalculation` + 清除旧错误
  - 骨架屏不显示（因为 loading 已结束）
- **清理**: 无

### TC-006: 直接 URL 访问（无 fundInfo）
- **类型**: 边界测试
- **关联验收标准**: FundResult — 从路由参数获取基金代码
- **前置条件**:
  - `fundInfo = null`（用户未通过 FundInput 查询，直接访问 URL）
  - `calculation = null`
- **输入**:
  - 直接在地址栏输入 `/fund/020741`
- **执行步骤**:
  1. 挂载 FundResult
  2. `onMounted` 中调用 `refreshCalculation("020741")`
- **预期输出**:
  - 正常触发计算
  - 计算完成后 `fundInfo` 和 `calculation` 均被填充
  - `ResultHeader` 从 `calculation.fund_name` / `calculation.fund_code` 获取展示内容
- **清理**: 无

---

## 二、ResultHeader.vue — 结果头部组件

### TC-007: 展示基金名称、代码、数据日期
- **类型**: 功能测试
- **关联验收标准**: ResultHeader — 展示基金名称、代码 + 数据日期标注
- **前置条件**:
  - `calculation` 包含 `fund_name = "国泰嘉睿纯债债券A"`，`fund_code = "020741"`，`data_date = "2025-06-24"`
- **输入**:
  - 传入上述 calculation 数据
- **执行步骤**:
  1. 渲染 ResultHeader 组件
  2. 检查 DOM 结构
- **预期输出**:
  - 基金名称 "国泰嘉睿纯债债券A" 可见
  - 基金代码 "020741" 可见
  - 日期 "昨日净值 2025年6月24日" 可见
  - 日期使用 `<time datetime="2025-06-24">` 语义标签
- **清理**: 无

### TC-008: 非交易日标注
- **类型**: 功能测试
- **关联验收标准**: ResultHeader — 非交易日标注
- **前置条件**:
  - `calculation.is_trading_day = false`
- **输入**:
  - 传入非交易日数据
- **执行步骤**:
  1. 渲染 ResultHeader
  2. 检查提示信息
- **预期输出**:
  - 显示黄色/橙色警告文字："非交易日，数据可能有延迟"
  - 不阻塞正常数据展示
- **清理**: 无

### TC-009: 交易日无警告
- **类型**: 边界测试
- **关联验收标准**: ResultHeader — 非交易日标注（反向验证）
- **前置条件**:
  - `calculation.is_trading_day = true`
- **输入**:
  - 传入交易日数据
- **执行步骤**:
  1. 渲染 ResultHeader
- **预期输出**:
  - 不显示"非交易日"警告文字
- **清理**: 无

### TC-010: 日期为 null 时显示 N/A
- **类型**: 边界测试
- **关联验收标准**: ResultHeader — `<time>` 语义标签
- **前置条件**:
  - `calculation.data_date = null`
- **输入**:
  - 传入缺失日期的数据
- **执行步骤**:
  1. 渲染 ResultHeader
- **预期输出**:
  - 日期区域显示 "N/A"
  - 不使用 `<time>` 标签（或使用但 datetime 为空不展示）
- **清理**: 无

---

## 三、NavGrid.vue — 净值网格组件

### TC-011: 正常展示净值 4 位小数 + 日涨跌正负号颜色
- **类型**: 功能测试
- **关联验收标准**: NavGrid — 展示最新净值和日涨跌幅
- **前置条件**:
  - `calculation.nav = 1.0234`，`calculation.daily_change_pct = 0.02`
- **输入**:
  - 传入正常净值和正涨跌幅
- **执行步骤**:
  1. 渲染 NavGrid
- **预期输出**:
  - "最新净值" 标签可见
  - 净值显示 "1.0234"（保留 4 位小数）
  - "日涨跌幅" 标签可见
  - 涨跌幅显示 "+0.02%"（带正号）且文字颜色为绿色
- **清理**: 无

### TC-012: 正涨跌幅绿色
- **类型**: 功能测试
- **关联验收标准**: NavGrid — 日涨跌幅正值绿色
- **前置条件**:
  - `calculation.daily_change_pct = 0.15`
- **输入**:
  - 传入正涨跌幅
- **执行步骤**:
  1. 渲染 NavGrid
- **预期输出**:
  - 显示 "+0.15%"
  - 文字颜色为绿色（如 `text-green-600`）
- **清理**: 无

### TC-013: 负涨跌幅红色
- **类型**: 功能测试
- **关联验收标准**: NavGrid — 日涨跌幅负值红色
- **前置条件**:
  - `calculation.daily_change_pct = -0.08`
- **输入**:
  - 传入负涨跌幅
- **执行步骤**:
  1. 渲染 NavGrid
- **预期输出**:
  - 显示 "-0.08%"
  - 文字颜色为红色（如 `text-red-600`）
- **清理**: 无

### TC-014: 涨跌幅为 0
- **类型**: 边界测试
- **关联验收标准**: NavGrid — 日涨跌幅正值绿色、负值红色
- **前置条件**:
  - `calculation.daily_change_pct = 0`
- **输入**:
  - 传入零涨跌幅
- **执行步骤**:
  1. 渲染 NavGrid
- **预期输出**:
  - 显示 "0%"
  - 颜色为中性色（灰色或黑色），非红非绿
- **清理**: 无

### TC-015: 净值为 null → N/A
- **类型**: 边界测试
- **关联验收标准**: NavGrid — 数值为 null 时显示"N/A"
- **前置条件**:
  - `calculation.nav = null`
  - `calculation.daily_change_pct = 0.02`
- **输入**:
  - 传入净值缺失的数据
- **执行步骤**:
  1. 渲染 NavGrid
- **预期输出**:
  - 净值显示 "N/A"
  - 涨跌幅正常展示
- **清理**: 无

### TC-016: 涨跌幅为 null → N/A
- **类型**: 边界测试
- **关联验收标准**: NavGrid — 数值为 null 时显示"N/A"
- **前置条件**:
  - `calculation.nav = 1.0234`
  - `calculation.daily_change_pct = null`
- **输入**:
  - 传入涨跌幅缺失的数据
- **执行步骤**:
  1. 渲染 NavGrid
- **预期输出**:
  - 净值正常展示
  - 涨跌幅显示 "N/A"
- **清理**: 无

---

## 四、YieldMetrics.vue — 收益指标卡片

### TC-017: 4 项指标 2×2 网格布局
- **类型**: 功能测试
- **关联验收标准**: YieldMetrics — 展示 4 项指标，每项含 emoji + 标签 + 数值
- **前置条件**:
  - 4 项指标均有值：`seven_day_annual_yield=2.31`, `wanfen_income=0.6321`, `one_month_return=0.31`, `three_month_max_drawdown=-1.52`
- **输入**:
  - 传入完整收益数据
- **执行步骤**:
  1. 渲染 YieldMetrics
- **预期输出**:
  - 2×2 网格布局（`grid grid-cols-2`）
  - 左上卡片：📈 七日年化 2.31%
  - 右上卡片：💵 万份收益 0.6321元
  - 左下卡片：📉 近1月收益 0.31%
  - 右下卡片：⚠️ 近3月最大回撤 -1.52%
- **清理**: 无

### TC-018: 全部值为 null
- **类型**: 边界测试
- **关联验收标准**: YieldMetrics — 数值缺失时显示"N/A"
- **前置条件**:
  - 4 项指标均为 null
- **输入**:
  - 传入全 null 的收益数据
- **执行步骤**:
  1. 渲染 YieldMetrics
- **预期输出**:
  - 4 张卡片均正常渲染
  - 每张卡片数值区域显示 "N/A"
  - emoji 和标签仍正常展示
- **清理**: 无

### TC-019: 部分字段有值，部分为 null
- **类型**: 边界测试
- **关联验收标准**: YieldMetrics — 数值缺失时显示"N/A"
- **前置条件**:
  - `seven_day_annual_yield=2.31`, `wanfen_income=null`, `one_month_return=0.31`, `three_month_max_drawdown=null`
- **输入**:
  - 传入混合数据
- **执行步骤**:
  1. 渲染 YieldMetrics
- **预期输出**:
  - 七日年化 → "2.31%"
  - 万份收益 → "N/A"
  - 近1月收益 → "0.31%"
  - 近3月最大回撤 → "N/A"
- **清理**: 无

### TC-020: formatPercent 正确应用于百分比字段
- **类型**: 功能测试
- **关联验收标准**: YieldMetrics — 百分比字段使用 `formatPercent` 格式化
- **前置条件**:
  - `seven_day_annual_yield=2.31`, `one_month_return=0.31`, `three_month_max_drawdown=-0.5`
- **输入**:
  - 传入百分比类型数据
- **执行步骤**:
  1. 渲染 YieldMetrics
- **预期输出**:
  - `seven_day_annual_yield` → `2.31%`（调用 `formatPercent`）
  - `one_month_return` → `0.31%`（调用 `formatPercent`）
  - `three_month_max_drawdown` → `-0.5%`（调用 `formatPercent`）
  - `wanfen_income` → `0.6321元`（非百分比，不调用 `formatPercent`，直接展示数值 + "元"）
- **清理**: 无

---

## 五、MarketRates.vue — 市场利率卡片

### TC-021: 2 项指标横排布局
- **类型**: 功能测试
- **关联验收标准**: MarketRates — 展示 10 年期国债收益率和 AA+ 信用利差
- **前置条件**:
  - `calculation.ten_year_treasury = 1.72`，`calculation.credit_spread_aa_plus = 85`
- **输入**:
  - 传入完整市场利率数据
- **执行步骤**:
  1. 渲染 MarketRates
- **预期输出**:
  - 标题 "当前市场" + 📡 emoji
  - 横排（flex-row）展示两项
  - 左：10年期国债 1.72%
  - 右：信用利差 85bp
- **清理**: 无

### TC-022: 两项均为 null
- **类型**: 边界测试
- **关联验收标准**: MarketRates — 数值缺失时显示"N/A"
- **前置条件**:
  - `calculation.ten_year_treasury = null`，`calculation.credit_spread_aa_plus = null`
- **输入**:
  - 传入全 null 市场利率数据
- **执行步骤**:
  1. 渲染 MarketRates
- **预期输出**:
  - 两项数值均显示 "N/A"
  - 标题、emoji、标签仍正常展示
- **清理**: 无

### TC-023: 国债收益率 % 和信用利差 bp 单位正确
- **类型**: 功能测试
- **关联验收标准**: MarketRates — 展示 10 年期国债收益率（%）和 AA+ 信用利差（bp）
- **前置条件**:
  - `calculation.ten_year_treasury = 1.72`，`calculation.credit_spread_aa_plus = 85`
- **输入**:
  - 传入带单位的数据
- **执行步骤**:
  1. 渲染 MarketRates
- **预期输出**:
  - 10 年期国债 → "1.72%"（`formatPercent` 处理或手动加 %）
  - 信用利差 → "85bp"（手动加 "bp" 后缀）
- **清理**: 无

---

## 六、RefreshButton.vue — 刷新计算按钮

### TC-024: 点击触发刷新计算
- **类型**: 功能测试
- **关联验收标准**: RefreshButton — 点击触发重新计算
- **前置条件**:
  - `loading = false`，基金代码为 "020741"
- **输入**:
  - 用户点击刷新按钮
- **执行步骤**:
  1. 渲染 RefreshButton
  2. 点击按钮
- **预期输出**:
  - 触发 `fundStore.refreshCalculation("020741")`
  - `loading` 变为 `true`
- **清理**: 无

### TC-025: Loading 状态禁用 + spinner + "计算中…"
- **类型**: 功能测试
- **关联验收标准**: RefreshButton — 计算中 loading 状态禁用 + spinner
- **前置条件**:
  - `loading = true`
- **输入**:
  - 页面处于计算中
- **执行步骤**:
  1. 渲染 RefreshButton（`loading = true`）
- **预期输出**:
  - 按钮 `disabled` 属性为 `true`
  - 显示旋转 spinner（如 `animate-spin` 图标）
  - 按钮文案为 "计算中…"
  - 点击按钮无响应
- **清理**: 无

### TC-026: 空闲状态可点击 + 无 spinner
- **类型**: 功能测试
- **关联验收标准**: RefreshButton — 空闲状态
- **前置条件**:
  - `loading = false`
- **输入**:
  - 页面处于空闲状态
- **执行步骤**:
  1. 渲染 RefreshButton（`loading = false`）
- **预期输出**:
  - 按钮可点击（`disabled = false`）
  - 无 spinner 图标
  - 按钮文案为 "刷新计算"
- **清理**: 无

---

## 七、集成测试

### TC-027: 所有组件包含 DisclaimerBar
- **类型**: 集成测试
- **关联验收标准**: 各组件复用 DisclaimerBar
- **前置条件**:
  - FundResult 页面渲染完成（calculation completed 状态）
- **输入**:
  - 完整计算结果数据
- **执行步骤**:
  1. 渲染 FundResult 完整页面
  2. 检查底部是否存在 DisclaimerBar
- **预期输出**:
  - 页面底部存在 DisclaimerBar 组件
  - 显示免责声明文本："本工具计算结果仅供参考，不构成任何投资建议…"
  - 页面主体有 `pb-16` 或 `pb-20` 底部留白以避免被固定底栏遮挡
- **清理**: 无

### TC-028: 计算结果页布局与 PRD 模板一致
- **类型**: 集成测试
- **关联验收标准**: 结果展示布局与 PRD 模板一致
- **前置条件**:
  - 完整计算结果数据可用
- **输入**:
  - 渲染完整 FundResult 页面
- **执行步骤**:
  1. 渲染 FundResult
  2. 检查各级组件渲染顺序和层级
- **预期输出**:
  - 自上而下依次：ResultHeader → NavGrid → YieldMetrics → MarketRates → RefreshButton → DisclaimerBar
  - 所有样式使用 Tailwind CSS class
  - 最大宽度 `max-w-lg` 或 `max-w-xl` 且居中（`mx-auto`）
- **清理**: 无

### TC-029: 轮询超时处理
- **类型**: 异常测试
- **关联验收标准**: FundResult — 错误状态下展示错误提示 + 重试按钮
- **前置条件**:
  - Store 轮询超时（120 秒后仍未 completed）
  - `error = "计算超时，请稍后重试"`，`loading = false`
- **输入**:
  - 模拟 Store 超时错误
- **执行步骤**:
  1. 挂载 FundResult，触发 `refreshCalculation`
  2. 等待 > 120 秒（或 mock 超时）
- **预期输出**:
  - 显示错误提示 "计算超时，请稍后重试"
  - 显示"重试"按钮
  - `loading = false`，骨架屏已消失
- **清理**: 无

### TC-030: 服务端返回 failed 状态
- **类型**: 异常测试
- **关联验收标准**: FundResult — 错误状态
- **前置条件**:
  - 后端返回 `status: 'failed'`，`error_message: "数据源暂时不可用"`
- **输入**:
  - 轮询到 failed 状态
- **执行步骤**:
  1. 挂载 FundResult，触发 `refreshCalculation`
  2. Store 收到 `status: 'failed'`
- **预期输出**:
  - Store `error` 被设为 `"数据源暂时不可用"`
  - 页面展示错误提示 + "重试"按钮
  - `loading = false`
- **清理**: 无

---

## 未覆盖项说明

以下项不在本 Task 前端测试范围，由其他 Task 覆盖：

| 项 | 覆盖 Task |
|----|-----------|
| 后端计算逻辑正确性 | Task 2.1 |
| API 路由响应格式 | Task 2.2 |
| 基金查询 API 功能 | Task 1.3 |
| 前端 API 层请求封装 | Task 3.1 |
| 基金搜索页功能 | Task 3.2 |
| CORS 配置 | Task 4.1 |
| 前后端联调 | Task 4.3 |
