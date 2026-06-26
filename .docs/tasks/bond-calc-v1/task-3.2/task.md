# Task 3.2: 基金输入页与组件

| 属性 | 值 |
|------|-----|
| ID | 3.2 |
| 状态 | done |
| 优先级 | P0 |
| 依赖 | 3.1 |
| 阶段 | 阶段3: 前端组件 |
| 预估工时 | 3-4 小时 |

## 描述

实现基金输入页（`FundInput.vue`）及其子组件：搜索栏（`SearchBar.vue`）、基金预览卡片（`FundPreview.vue`）和全局免责声明横幅（`DisclaimerBar.vue`）。页面负责接收用户输入、调用 API 查询基金信息、展示确认预览。

## 验收标准

- [ ] `FundInput.vue` — 页面主组件：
  - 包含基金代码输入区域和基金信息预览区域
  - 输入有效代码后自动展示基金基本信息预览
  - 输入无效代码 → 显示错误提示（基金不存在 / 非债券型 / 格式错误）
  - 输入框 300ms 防抖
  - 本地格式校验：非 6 位数字即时提示，不触发 API 调用
  - 确认基金后跳转到结果页 `/fund/:code`
- [ ] `SearchBar.vue` — 搜索栏组件：
  - 输入框（仅数字，maxlength=6）+ 查询按钮
  - 支持 Enter 键触发查询
  - 输入框绑定 `<label>`，支持屏幕阅读器
  - 加载中显示 loading 状态（按钮禁用 + spinner）
- [ ] `FundPreview.vue` — 基金预览卡片组件：
  - 展示基金名称、代码、类型、最新净值、七日年化
  - 非债券型基金显示警告样式
  - 含"确认并查看详情"按钮，点击跳转结果页
- [ ] `DisclaimerBar.vue` — 免责声明横幅：
  - 固定在页面底部
  - 显示免责声明文字："本工具提供的收益数据基于公开数据计算，仅供参考，不构成投资建议。投资有风险，操作需谨慎。"
  - 半透明样式，不遮挡主要内容
- [ ] 所有组件使用 Tailwind CSS 编写样式
- [ ] 错误提示使用 `role="alert"` 属性

## 子任务

### SUB-3.2.1: SearchBar 组件
- **描述**: 实现基金代码输入搜索栏
- **验收标准**:
  - [ ] 输入框限制 6 位数字，`<label>` 关联
  - [ ] `@input` 事件 300ms 防抖后 emit `search` 事件
  - [ ] 本地校验：非 6 位数字时显示"请输入 6 位基金代码"
  - [ ] Enter 键触发查询（`@keyup.enter`）
  - [ ] Props: `loading: boolean`，loading 时按钮禁用 + 显示 spinner

### SUB-3.2.2: FundPreview 组件
- **描述**: 实现基金信息预览卡片
- **验收标准**:
  - [ ] 接收 `FundInfo` prop，展示名称、代码、类型、净值、七日年化
  - [ ] 含"确认并查看详情"按钮，emit `confirm` 事件
  - [ ] 非债券型基金使用橙色警告样式，显示类型不匹配提示
  - [ ] 无数据时不渲染（`v-if="fundInfo"`）

### SUB-3.2.3: FundInput 页面 + DisclaimerBar
- **描述**: 组装输入页并实现 DisclaimerBar 全局组件
- **验收标准**:
  - [ ] FundInput 调用 `fundStore.fetchFundInfo`，管理查询流程
  - [ ] 错误信息从 store 读取并展示（区分 40001/40002/40003）
  - [ ] 确认后 `router.push({ name: 'FundResult', params: { code } })`
  - [ ] DisclaimerBar 固定底部，含完整免责文案
  - [ ] 页面整体布局使用 Tailwind，居中最大宽度约束（`max-w-2xl mx-auto`）
