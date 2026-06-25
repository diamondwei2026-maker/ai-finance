# 债券收益计算工具 — 开发任务列表

| 属性 | 值 |
|------|-----|
| 版本 | v1.0 |
| 创建日期 | 2025-06-25 |
| 需求标识 | bond-calc-v1 |
| 关联计划 | [开发计划](./development-plan.md) |
| 总任务数 | 12 |

---

## 任务总览

| Task ID | 名称 | 阶段 | 状态 | 优先级 | 依赖 | 详情 |
|---------|------|------|------|--------|------|------|
| 0.1 | 后端项目脚手架与核心模块 | 阶段0: 项目初始化 | ✅ done | P0 | 无 | [task.md](./tasks/bond-calc-v1/task-0.1/task.md) |
| 0.2 | 前端项目脚手架与基础配置 | 阶段0: 项目初始化 | ✅ done | P0 | 无 | [task.md](./tasks/bond-calc-v1/task-0.2/task.md) |
| 1.1 | 外部数据源适配（akshare） | 阶段1: 后端数据层 | ✅ done | P0 | 0.1 | [task.md](./tasks/bond-calc-v1/task-1.1/task.md) |
| 1.2 | 数据模型定义 | 阶段1: 后端数据层 | ⏳ pending | P0 | 1.1 | [task.md](./tasks/bond-calc-v1/task-1.2/task.md) |
| 1.3 | 基金查询 API | 阶段1: 后端数据层 | ⏳ pending | P0 | 1.2 | [task.md](./tasks/bond-calc-v1/task-1.3/task.md) |
| 2.1 | 计算引擎与市场数据服务 | 阶段2: 计算引擎 | ⏳ pending | P0 | 1.3 | [task.md](./tasks/bond-calc-v1/task-2.1/task.md) |
| 2.2 | 计算 API 路由 | 阶段2: 计算引擎 | ⏳ pending | P0 | 2.1 | [task.md](./tasks/bond-calc-v1/task-2.2/task.md) |
| 3.1 | 前端 API 层与状态管理 | 阶段3: 前端组件 | ⏳ pending | P0 | 0.2 | [task.md](./tasks/bond-calc-v1/task-3.1/task.md) |
| 3.2 | 基金输入页与组件 | 阶段3: 前端组件 | ⏳ pending | P0 | 3.1 | [task.md](./tasks/bond-calc-v1/task-3.2/task.md) |
| 3.3 | 计算结果页与组件 | 阶段3: 前端组件 | ⏳ pending | P0 | 3.1 | [task.md](./tasks/bond-calc-v1/task-3.3/task.md) |
| 4.1 | 后端 CORS 配置与 Render 部署 | 阶段4: 联调部署 | ⏳ pending | P0 | 2.2 | [task.md](./tasks/bond-calc-v1/task-4.1/task.md) |
| 4.2 | 前端 Vercel 部署 | 阶段4: 联调部署 | ⏳ pending | P0 | 3.2, 3.3 | [task.md](./tasks/bond-calc-v1/task-4.2/task.md) |
| 4.3 | 前后端联调与异常处理 | 阶段4: 联调部署 | ⏳ pending | P0 | 4.1, 4.2 | [task.md](./tasks/bond-calc-v1/task-4.3/task.md) |

---

## 依赖关系图

```
Task 0.1 ──► Task 1.1 ──► Task 1.2 ──► Task 1.3 ──► Task 2.1 ──► Task 2.2 ──► Task 4.1 ──┐
                                                                                             │
Task 0.2 ──► Task 3.1 ──┬──► Task 3.2 ───────────────────────────────────────────────────┐  │
                         │                                                                 │  │
                         └──► Task 3.3 ──────────────────────────────────────────────┐    │  │
                                                                                      │    │  │
                                                                                      ▼    │  │
                                                                                 Task 4.2 ◄┘  │
                                                                                      │      │
                                                                                      ▼      │
                                                                                 Task 4.3 ◄──┘
```

## 执行顺序建议

1. **Task 0.1** — 后端项目脚手架与核心模块（无依赖，可立即开始）
2. **Task 0.2** — 前端项目脚手架与基础配置（无依赖，可与 0.1 并行）
3. **Task 1.1** — 外部数据源适配（依赖 0.1）
4. **Task 1.2** — 数据模型定义（依赖 1.1）
5. **Task 1.3** — 基金查询 API（依赖 1.2）
6. **Task 2.1** — 计算引擎与市场数据服务（依赖 1.3）
7. **Task 2.2** — 计算 API 路由（依赖 2.1）
8. **Task 3.1** — 前端 API 层与状态管理（依赖 0.2，可与后端任务并行推进）
9. **Task 3.2** — 基金输入页与组件（依赖 3.1）
10. **Task 3.3** — 计算结果页与组件（依赖 3.1，可与 3.2 并行）
11. **Task 4.1** — 后端 CORS + Render 部署（依赖 2.2）
12. **Task 4.2** — 前端 Vercel 部署（依赖 3.2 + 3.3）
13. **Task 4.3** — 前后端联调与异常处理（依赖 4.1 + 4.2）
