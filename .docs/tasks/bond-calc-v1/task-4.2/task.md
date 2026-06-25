# Task 4.2: 前端 Vercel 部署

| 属性 | 值 |
|------|-----|
| ID | 4.2 |
| 状态 | pending |
| 优先级 | P0 |
| 依赖 | 3.2, 3.3 |
| 阶段 | 阶段4: 联调部署 |
| 预估工时 | 1-2 小时 |

## 描述

验证前端 Vercel 部署配置（`vercel.json` SPA 重定向），设置生产环境 API 地址，将前端部署到 Vercel 并验证可访问。

## 验收标准

- [ ] `vercel.json` SPA 路由重定向配置正确（已在 Task 0.2 创建，此处验证）
- [ ] 生产环境 `VITE_API_BASE_URL` 指向 Render 后端公网 URL
- [ ] `.env.production` 创建，含 `VITE_API_BASE_URL=<Render URL>`
- [ ] Vite 构建成功（`npm run build`），产物无报错
- [ ] Vercel 部署成功，公网 URL 可访问
- [ ] 路由 `/` 和 `/fund/020741` 直接访问均正确（SPA 重定向生效）

## 子任务

### SUB-4.2.1: 构建验证
- **描述**: 验证前端项目构建和配置
- **验收标准**:
  - [ ] `npm run build` 无 TypeScript/ESLint 错误
  - [ ] 构建产物大小合理（gzip < 100KB）
  - [ ] SPA 路由重定向在本地 preview 中验证（`npm run preview`）

### SUB-4.2.2: Vercel 部署
- **描述**: 执行 Vercel 部署
- **验收标准**:
  - [ ] Vercel 关联 GitHub 仓库
  - [ ] 框架预设自动识别为 Vite
  - [ ] 环境变量 `VITE_API_BASE_URL` 在 Vercel Dashboard 中配置
  - [ ] 部署完成后公网 URL 可访问
  - [ ] 直接访问 `/<any-path>` 不返回 404（SPA 重定向工作）
