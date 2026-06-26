# Coding Prompt — Task 4.2: 前端 Vercel 部署

> 生成日期：2026-06-26 | 关联：[task.md](./task.md) | [test-cases.md](./test-cases.md)

---

## 1. 任务目标

验证前端 SPA 重定向配置，创建生产环境配置文件，执行构建验证，将前端应用部署到 Vercel 并确保公网可访问。

## 2. 技术上下文

- **框架**: Vue 3 + Vite + TypeScript
- **路由模式**: Hash 模式（`createWebHashHistory`），实际 URL 为 `/#/fund/:code`
- **样式方案**: Tailwind CSS 4.3（`@tailwindcss/vite` 插件，零配置）
- **状态管理**: Pinia
- **部署目标**: Vercel（Vite preset 自动识别）
- **后端依赖**: Task 4.1 已完成后端 Render 部署，CORS 已配置
- **构建命令**: `npm run build`（先 `vue-tsc -b` 类型检查，再 `vite build`）

### 关键现有文件

| 文件 | 状态 | 说明 |
|------|------|------|
| `client/vercel.json` | ✅ 已存在 | SPA fallback 规则：`source: "/(.*)"` → `destination: "/index.html"` |
| `client/vite.config.ts` | ✅ 已存在 | Vue + Tailwind CSS 插件，`@` 别名 → `./src` |
| `client/package.json` | ✅ 已存在 | 含 `build` / `preview` 脚本 |
| `client/src/api/index.ts` | ✅ 已存在 | `BASE_URL` 读取 `import.meta.env.VITE_API_BASE_URL`，默认 `http://localhost:8000` |
| `client/src/router/index.ts` | ✅ 已存在 | Hash 模式，路由：`/` + `/fund/:code` |
| `client/.env.production` | ❌ 需创建 | 含 `VITE_API_BASE_URL` 指向 Render 后端 |

## 3. 实现要求

### SUB-4.2.1: 构建验证

#### 3.1 文件 `client/.env.production`（新建）

- **职责**: 生产环境环境变量，Vite 构建时自动注入 `import.meta.env.VITE_API_BASE_URL`
- **内容**:
  ```
  VITE_API_BASE_URL=<Render 后端公网 URL>
  ```
- **注意事项**:
  - Render URL 格式：`https://<service-name>.onrender.com`（不带尾部斜杠）
  - 确认这是 Task 4.1 部署后的实际 URL
  - 如果 Render 使用了自定义域名，使用自定义域名
  - **必须 HTTPS**——生产环境不应使用 HTTP
  - Vite 仅会注入 `VITE_` 前缀的环境变量，其他前缀不会暴露给前端代码
  - 此文件不应提交到 Git（包含部署特定信息），确认 `.gitignore` 中已包含 `.env*.local` 或显式添加 `.env.production`

#### 3.2 构建产物验证

- **验证项**:
  1. 在 `client/` 目录执行 `npm run build`
  2. 确认退出码为 0（无 TypeScript 类型错误、无 Vite 构建错误）
  3. 确认 `client/dist/` 目录生成，包含：
     - `index.html`（入口文件）
     - `assets/` 子目录（JS、CSS 文件）
  4. 检查构建日志，确认无警告（或仅有可忽略的警告）
- **产物大小检查**:
  - 主要 JS bundle gzip 后应 < 100KB
  - 使用 `npx vite-bundle-visualizer` 或手动检查 `dist/` 大小
  - 如过大，检查是否引入了未使用的依赖
- **本地预览验证**:
  1. 执行 `npm run preview`（Vite 内置，默认端口 4173）
  2. 浏览器访问 `http://localhost:4173`——首页正常渲染
  3. 访问 `http://localhost:4173/#/fund/020741`——结果页正常渲染
  4. 打开 DevTools Console——无 JS 运行时错误
- **注意**: `npm run preview` 不会应用 `vercel.json` 的 rewrites 规则（那是 Vercel 平台级配置），但 Hash 模式下直接路径访问天然可用（所有路由都在 `/#/` 下）

#### 3.3 vercel.json 配置验证

当前 `client/vercel.json` 内容：
```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

- **验证项**:
  1. 确认文件位于 `client/` 根目录（Vercel 默认从此目录部署时读取）
  2. 确认 JSON 语法有效
  3. 确认 `rewrites` 规则：任意路径 → `index.html`
  4. 虽然当前使用 Hash 模式路由（`/#/...`），SPA fallback 仍为安全兜底——防止未来切换 history 模式或直接路径访问

### SUB-4.2.2: Vercel 部署

#### 3.4 Vercel 部署流程

**前置条件**:
- GitHub 仓库已包含完整前端代码（`client/` 目录）
- Vercel 账号已注册（推荐 GitHub 登录）
- Task 4.1 已完成（后端 Render URL 已知）

**部署步骤**:

1. **导入项目**:
   - 登录 [vercel.com](https://vercel.com)
   - 点击 "Add New" → "Project"
   - 选择 GitHub 仓库（如 `ai-finance`）
   - 点击 "Import"

2. **配置项目**:
   - **Root Directory**: 点击 "Edit" → 选择 `client`（因为前端代码在 `client/` 子目录）
   - **Framework Preset**: 自动识别为 "Vite"（无需手动选择）
   - **Build Command**: 保持默认 `npm run build`（覆盖 Vite preset 默认值）
   - **Output Directory**: 保持默认 `dist`（Vite 默认输出目录）
   - **Install Command**: 保持默认 `npm install`

3. **设置环境变量**:
   - 展开 "Environment Variables"
   - 添加:
     - Key: `VITE_API_BASE_URL`
     - Value: Render 后端公网 URL（如 `https://bond-calc.onrender.com`）
     - 勾选所有环境（Production / Preview / Development）
   - 注意：`VITE_` 前缀的变量会在构建时静态替换代码中的 `import.meta.env.VITE_API_BASE_URL`，因此每次修改此变量都需要重新构建（Redeploy）

4. **部署**:
   - 点击 "Deploy"
   - 等待构建完成（通常 30-60 秒）
   - Vercel 自动分配域名：`https://<project-name>.vercel.app`

5. **验证部署**:
   - 打开 Vercel 分配的 URL
   - 检查首页正常渲染
   - 访问 `/#/fund/020741`——页面正常（Hash 路由）
   - DevTools Network 标签：无 4xx/5xx 错误
   - DevTools Console：无 JS 运行时错误
   - 检查 `VITE_API_BASE_URL` 是否被正确注入（可在浏览器中查看 `import.meta.env` 或通过网络请求的目标地址验证）

#### 3.5 可选：Vercel CLI 部署（替代方案）

如果偏好 CLI 或 GitHub 集成不可用：

```bash
# 安装 Vercel CLI
npm i -g vercel

# 在 client/ 目录执行
cd client

# 登录（仅首次）
vercel login

# 部署（交互式）
vercel

# 或生产部署（非交互）
vercel --prod \
  --env VITE_API_BASE_URL=https://<render-backend>.onrender.com
```

#### 3.6 部署后检查清单

| 检查项 | 操作 | 预期 |
|--------|------|------|
| 首页可访问 | 访问公网 URL | 输入框、查询按钮正常渲染 |
| 路由跳转 | 输入 `020741` → 点击查询 | 跳转到 `/#/fund/020741` |
| API 连通性 | 在结果页点击"刷新计算" | API 请求发往 Render URL，数据返回 |
| SPA 回退 | 直接访问 `<url>/#/nonexistent` | 不返回空白页（前端路由处理） |
| 环境变量生效 | DevTools Network 检查请求域名 | API 请求域名为 Render URL（非 localhost） |

## 4. 代码规范要求

- `.env.production` 不应提交 Git——在 `.gitignore` 中确认 `*.production` 或显式条目
- 不要在代码中硬编码 Render URL——始终通过 `import.meta.env.VITE_API_BASE_URL` 读取
- 保持 `vercel.json` 内容简洁——MVP 仅需 SPA fallback 规则

## 5. 测试要求

代码（配置）必须满足以下测试用例：

| 编号 | 名称 | 类型 |
|------|------|------|
| TC-001 | vercel.json SPA 重定向配置正确 | 功能 |
| TC-002 | .env.production 文件创建成功 | 功能 |
| TC-003 | VITE_API_BASE_URL 值有效性 | 功能 |
| TC-004 | npm run build 构建成功 | 功能 |
| TC-005 | 构建产物包含必需文件 | 功能 |
| TC-006 | npm run preview 本地预览正常 | 功能 |
| TC-007 | Vercel 部署后公网 URL 可访问 | 功能 |
| TC-008 | 环境变量在 Vercel Dashboard 配置 | 功能 |
| TC-009 | 直接访问不存在路径不返回 404 | 异常 |
| TC-012 | 深层嵌套路径的 SPA 回退 | 边界 |
| TC-013 | 带尾部斜杠路径 | 边界 |
| TC-014 | 前端通过 VITE_API_BASE_URL 调用后端 API | 集成 |
| TC-015 | 跨域请求在生产环境正常工作 | 集成 |

## 6. 注意事项

1. **Hash 路由 vs vercel.json**: 路由使用 `createWebHashHistory()`——所有前端路由在 `/#/` 下，天然不需要服务端 SPA 重定向。`vercel.json` 的 rewrites 规则是安全兜底，防止未来切换 history 模式时遗漏配置。
2. **Root Directory 设置**: Vercel 默认从仓库根目录构建，但本项目前端目录是 `client/`。必须在 Vercel Dashboard 中将 Root Directory 设为 `client`，否则 Vercel 会尝试在根目录找 `package.json`。
3. **环境变量作用域**: `VITE_` 前缀的环境变量在 Vite 构建时通过静态替换注入——修改后必须重新部署（Redeploy）才能生效，仅重启无效。
4. **CORS 依赖**: 后端 Task 4.1 必须已完成（CORS 配置了 Vercel 域名白名单），否则前端部署后 API 请求会因跨域失败。如果 4.1 已完成，确认其 CORS 白名单中已包含 Vercel 域名。
5. **Render 冷启动**: Render 免费层在 15 分钟无请求后会休眠，首次请求有 5-10 秒冷启动延迟。前端 fetch 封装设置了 15 秒超时，可以覆盖此场景。
6. **Vercel 免费层限制**: 带宽 100GB/月，构建时间 100 小时/月——MVP 单用户场景完全够用。
7. **自定义域名**（可选）: 如需要自定义域名，在 Vercel Dashboard → Settings → Domains 中添加。但 MVP 阶段使用 Vercel 默认域名即可。
