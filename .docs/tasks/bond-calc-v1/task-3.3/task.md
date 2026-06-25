# Task 3.3: 计算结果页与组件

| 属性 | 值 |
|------|-----|
| ID | 3.3 |
| 状态 | pending |
| 优先级 | P0 |
| 依赖 | 3.1 |
| 阶段 | 阶段3: 前端组件 |
| 预估工时 | 3-4 小时 |

## 描述

实现计算结果展示页（`FundResult.vue`）及其子组件：结果头部（`ResultHeader.vue`）、净值网格（`NavGrid.vue`）、收益指标卡片（`YieldMetrics.vue`）、市场利率卡片（`MarketRates.vue`）和刷新按钮（`RefreshButton.vue`）。页面展示完整的 8 项指标计算结果，布局与 PRD 结果模板一致。

## 验收标准

- [ ] `FundResult.vue` — 页面主组件：
  - 从路由参数获取基金代码（`route.params.code`）
  - 进入页面自动触发计算（`onMounted` 中调用 `fundStore.refreshCalculation`）
  - query 参数 `?refresh=1` 时重新触发计算
  - 加载中显示骨架屏（Skeleton）而非空白等待
  - 计算完成后展示完整结果
  - 错误状态下展示错误提示 + 重试按钮
- [ ] `ResultHeader.vue` — 结果头部组件：
  - 展示基金名称、代码 + 数据日期标注（"昨日净值 YYYY-MM-DD" / "当前 HH:MM"）
  - 非交易日标注："非交易日，数据可能有延迟"
- [ ] `NavGrid.vue` — 净值网格组件：
  - 展示"最新净值"和"日涨跌幅"
  - 日涨跌幅正值绿色（`+0.02%`），负值红色（`-0.02%`）
- [ ] `YieldMetrics.vue` — 收益指标卡片：
  - 展示七日年化、万份收益、近1月收益、近3月最大回撤
  - 每项指标含图标（emoji：📈 💵 📉 ⚠️）+ 标签 + 数值
  - 数值缺失时显示"N/A"
- [ ] `MarketRates.vue` — 市场利率卡片：
  - 展示 10 年期国债收益率（%）和 AA+ 信用利差（bp）
  - 含 📡 图标标题"当前市场"
- [ ] `RefreshButton.vue` — 刷新计算按钮：
  - 点击触发重新计算（loading 状态禁用 + spinner）
  - 计算中显示"计算中…"
- [ ] 各组件复用 `DisclaimerBar.vue`
- [ ] 所有样式使用 Tailwind CSS，结果展示布局与 PRD 模板一致
- [ ] 使用 `<time>` 语义标签包裹日期

## 子任务

### SUB-3.3.1: ResultHeader + NavGrid 组件
- **描述**: 实现结果头部和净值展示组件
- **验收标准**:
  - [ ] ResultHeader 展示基金名称、代码、`<time>` 数据日期
  - [ ] NavGrid 展示净值（保留 4 位小数）和日涨跌（带正负号和颜色）
  - [ ] 数值为 null 时显示"N/A"

### SUB-3.3.2: YieldMetrics + MarketRates 组件
- **描述**: 实现收益指标和市场利率展示组件
- **验收标准**:
  - [ ] YieldMetrics 4 项指标网格布局（2×2），每项含 emoji + 标签 + 数值
  - [ ] MarketRates 2 项指标横排布局
  - [ ] 所有数值字段 null 时显示"N/A"
  - [ ] 百分比字段使用 `formatPercent` 格式化

### SUB-3.3.3: FundResult 页面 + RefreshButton
- **描述**: 组装结果页组件，实现刷新逻辑
- **验收标准**:
  - [ ] FundResult 在 `onMounted` 触发计算，loading 时显示骨架屏
  - [ ] 骨架屏含 3 个占位卡片（对应 ResultHeader/YieldMetrics/MarketRates）
  - [ ] RefreshButton 点击触发 `fundStore.refreshCalculation`，loading 时显示 spinner
  - [ ] 计算完成后各子组件自动响应式渲染
  - [ ] 错误状态显示错误消息 + "重试"按钮
  - [ ] 页面底部含 DisclaimerBar
