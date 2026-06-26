# 测试用例 — Task 4.2: 前端 Vercel 部署

> 生成日期：2026-06-26 | 关联 Task：[task.md](./task.md)

---

## 覆盖概览

| 类型 | 数量 | 说明 |
|------|------|------|
| 功能测试 | 8 | 构建、配置、部署、路由验证 |
| 异常测试 | 3 | 404 处理、缺失环境变量、构建失败 |
| 边界测试 | 2 | 深层路径、尾部斜杠 |
| 集成测试 | 2 | 与 Render 后端 API 通信 |
| **合计** | **15** | |

---

## 功能测试

### TC-001: vercel.json SPA 重定向配置正确
- **类型**: 功能测试
- **关联验收标准**: vercel.json SPA 路由重定向配置正确
- **前置条件**: 项目根目录存在 `client/vercel.json`
- **输入**: 无
- **执行步骤**:
  1. 读取 `client/vercel.json` 文件内容
  2. 检查是否包含 `rewrites` 字段
  3. 检查 `rewrites` 中是否有一条规则：`source: "/(.*)"` → `destination: "/index.html"`
- **预期输出**:
  - `vercel.json` 存在且为合法 JSON
  - `rewrites` 数组包含至少一条 SPA fallback 规则
  - source 匹配所有路径，destination 指向 `/index.html`
- **清理**: 无

### TC-002: .env.production 文件创建成功
- **类型**: 功能测试
- **关联验收标准**: .env.production 创建，含 VITE_API_BASE_URL=<Render URL>
- **前置条件**: 项目根目录 `client/` 下
- **输入**: 无
- **执行步骤**:
  1. 检查 `client/.env.production` 文件是否存在
  2. 读取文件内容
  3. 检查是否包含 `VITE_API_BASE_URL=` 键
  4. 检查值是否为有效 HTTPS URL（指向 Render 后端）
- **预期输出**:
  - `client/.env.production` 文件存在
  - 文件包含 `VITE_API_BASE_URL=https://...`（非空、非 localhost）
  - URL 格式为 `https://<service-name>.onrender.com` 或 Render 分配的域名
- **清理**: 无

### TC-003: VITE_API_BASE_URL 值有效性
- **类型**: 功能测试
- **关联验收标准**: 生产环境 VITE_API_BASE_URL 指向 Render 后端公网 URL
- **前置条件**: `.env.production` 已创建
- **输入**: 无
- **执行步骤**:
  1. 从 `.env.production` 提取 `VITE_API_BASE_URL` 的值
  2. 使用 curl/浏览器尝试访问 `<VITE_API_BASE_URL>/api/health`（如果后端有健康检查端点）
  3. 或至少验证该域名可解析（DNS 解析成功）
- **预期输出**:
  - URL 可解析（非 404 DNS）
  - 如果后端已部署，健康检查返回 2xx
  - URL 以 `https://` 开头（生产环境必须 HTTPS）
- **清理**: 无

### TC-004: npm run build 构建成功
- **类型**: 功能测试
- **关联验收标准**: Vite 构建成功（npm run build），产物无报错
- **前置条件**: 依赖已安装（`node_modules` 存在）
- **输入**: 无
- **执行步骤**:
  1. 在 `client/` 目录执行 `npm run build`
  2. 观察构建过程输出
  3. 检查退出码是否为 0
  4. 检查 `client/dist/` 目录是否生成
- **预期输出**:
  - 构建命令退出码为 0
  - 无 TypeScript 编译错误
  - 无 ESLint 警告（或仅有已知可忽略的警告）
  - `client/dist/` 目录存在，包含 `index.html` + `assets/` 子目录
- **清理**: 可保留 dist 目录用于后续测试，或 `rm -rf client/dist`

### TC-005: 构建产物包含必需文件
- **类型**: 功能测试
- **关联验收标准**: 构建产物大小合理（gzip < 100KB）
- **前置条件**: `npm run build` 已成功执行
- **输入**: 无
- **执行步骤**:
  1. 检查 `client/dist/index.html` 是否存在
  2. 检查 `client/dist/assets/` 下是否有 JS 和 CSS 文件
  3. 使用 `gzip -c client/dist/assets/*.js | wc -c` 检查压缩后 JS 大小（或用 PowerShell `Compress-Archive` 估算）
  4. 检查 `index.html` 中是否正确引用了 assets
- **预期输出**:
  - `dist/index.html` 存在
  - JS 文件 gzip 后 < 100KB（或总体积合理，不包含未使用的依赖）
  - `index.html` 中 `<script>` 和 `<link>` 标签引用路径正确（相对路径或绝对路径 `/assets/...`）
- **清理**: 无

### TC-006: npm run preview 本地预览正常
- **类型**: 功能测试
- **关联验收标准**: SPA 路由重定向在本地 preview 中验证
- **前置条件**: `npm run build` 已成功
- **输入**: 无
- **执行步骤**:
  1. 执行 `npm run preview` 启动本地预览服务器
  2. 浏览器访问 `http://localhost:4173`（Vite preview 默认端口）
  3. 检查首页是否正常加载
  4. 直接访问 `http://localhost:4173/fund/020741`
  5. 检查是否返回首页（SPA fallback），而非 404
- **预期输出**:
  - 本地预览服务器正常启动
  - 首页可访问，无白屏或 JS 报错
  - `/fund/020741` 路径不返回 404，页面正常渲染（由前端路由接管）
- **清理**: 停止 preview 服务器

### TC-007: Vercel 部署后公网 URL 可访问
- **类型**: 功能测试
- **关联验收标准**: Vercel 部署成功，公网 URL 可访问
- **前置条件**: Vercel 项目已关联 GitHub 仓库，部署已完成
- **输入**: Vercel 分配的公网 URL（如 `https://<project>.vercel.app`）
- **执行步骤**:
  1. 浏览器访问 Vercel 公网 URL
  2. 检查页面是否正常加载
  3. 打开浏览器 DevTools → Network 标签，检查无 4xx/5xx 错误
  4. 检查 Console 无 JS 运行时错误
- **预期输出**:
  - 页面正常渲染，非空白页
  - Network 中所有资源请求返回 200
  - Console 无未捕获异常
- **清理**: 无

### TC-008: 环境变量在 Vercel Dashboard 中配置
- **类型**: 功能测试
- **关联验收标准**: 环境变量 VITE_API_BASE_URL 在 Vercel Dashboard 中配置
- **前置条件**: Vercel 项目已创建
- **输入**: 无
- **执行步骤**:
  1. 登录 Vercel Dashboard
  2. 进入项目 → Settings → Environment Variables
  3. 检查是否存在 `VITE_API_BASE_URL` 变量
  4. 检查其值是否与 `.env.production` 一致
- **预期输出**:
  - `VITE_API_BASE_URL` 环境变量已配置
  - 作用于 Production 环境
  - 值与 Render 后端 URL 一致
- **清理**: 无

---

## 异常测试

### TC-009: 直接访问不存在路径不返回 404
- **类型**: 异常测试
- **关联验收标准**: 直接访问 /<any-path> 不返回 404（SPA 重定向工作）
- **前置条件**: Vercel 部署完成或本地 preview 可用
- **输入**: 任意不存在的前端路由路径（如 `/nonexistent-page`）
- **执行步骤**:
  1. 浏览器直接访问 `<base-url>/nonexistent-page`
  2. 检查 HTTP 响应状态码
  3. 检查页面内容
- **预期输出**:
  - HTTP 状态码为 200（由 SPA fallback 返回 index.html）
  - 页面加载 Vue 应用，由前端路由显示 404 页面或回退到首页
  - 不是 Vercel/Nginx 的默认 404 页面
- **清理**: 无

### TC-010: 未设置 VITE_API_BASE_URL 时构建警告
- **类型**: 异常测试
- **关联验收标准**: 生产环境 VITE_API_BASE_URL 指向 Render 后端（验证缺失时的行为）
- **前置条件**: 无
- **输入**: 临时移除或注释 `.env.production` 中的 `VITE_API_BASE_URL`
- **执行步骤**:
  1. 临时备份 `.env.production`
  2. 移除 `VITE_API_BASE_URL` 行，或设为空值
  3. 执行 `npm run build`
  4. 检查构建输出是否有相关警告
  5. 恢复 `.env.production`
- **预期输出**:
  - 构建可能成功（Vite 不强制要求环境变量）
  - 但部署后 API 请求会失败（请求发到相对路径或 undefined）
  - **验证目的**: 确认部署前检查流程能捕获此问题
- **清理**: 恢复 `.env.production` 文件

### TC-011: Vite 构建失败时 Vercel 部署应中止
- **类型**: 异常测试
- **关联验收标准**: Vite 构建成功（npm run build），产物无报错（验证失败场景）
- **前置条件**: 无
- **输入**: 人为引入 TypeScript 编译错误（如类型不匹配）
- **执行步骤**:
  1. 在任一 `.ts` 文件中引入类型错误（如 `const x: number = "string"`）
  2. 执行 `npm run build`
  3. 观察构建是否失败（非零退出码）
  4. 如果是 Vercel + GitHub 集成，推送此错误提交
  5. 检查 Vercel 是否阻止部署
- **预期输出**:
  - 本地构建失败，退出码非 0
  - `vue-tsc` 报告类型错误
  - Vercel 部署日志显示 Build Failed，不会替换生产部署
- **清理**: 撤销引入的类型错误

---

## 边界测试

### TC-012: 深层嵌套路径的 SPA 回退
- **类型**: 边界测试
- **关联验收标准**: SPA 路由重定向对所有路径生效
- **前置条件**: 部署环境可用
- **输入**: 深层嵌套路径（如 `/a/b/c/d/e`）
- **执行步骤**:
  1. 直接访问 `<base-url>/a/b/c/d/e`
  2. 检查是否返回 index.html
  3. 检查页面是否正常初始化 Vue 应用
- **预期输出**:
  - 返回 200，内容为 index.html
  - Vue 应用正常加载
  - 前端路由将 URL 解析为 `/a/b/c/d/e`（可能显示 404 页面但由前端控制）
- **清理**: 无

### TC-013: 带尾部斜杠的路径
- **类型**: 边界测试
- **关联验收标准**: SPA 路由重定向对所有路径生效
- **前置条件**: 部署环境可用
- **输入**: 带尾部斜杠的路径（如 `/fund/020741/`）
- **执行步骤**:
  1. 直接访问 `<base-url>/fund/020741/`
  2. 检查是否正常返回页面
  3. 检查是否发生重定向（如 301 到 `/fund/020741`）
- **预期输出**:
  - 页面正常加载（200 或 301→200）
  - 不返回 404
  - 前端路由能正确处理尾部斜杠
- **清理**: 无

---

## 集成测试

### TC-014: 前端通过 VITE_API_BASE_URL 调用后端 API
- **类型**: 集成测试
- **关联验收标准**: 生产环境 VITE_API_BASE_URL 指向 Render 后端公网 URL
- **前置条件**: Render 后端已部署且可访问，前端已部署
- **输入**: 有效的基金代码（如 `020741`）
- **执行步骤**:
  1. 访问部署后的前端页面
  2. 在基金输入框中输入 `020741`
  3. 提交查询
  4. 通过 DevTools Network 标签观察 API 请求
  5. 检查请求 URL 是否以 `VITE_API_BASE_URL` 为前缀
- **预期输出**:
  - API 请求发往 `https://<render-backend>.onrender.com/api/...`
  - 请求不因 CORS 失败（Task 4.1 已配置 CORS）
  - 响应正常返回基金数据
  - 前端正确展示结果
- **清理**: 无

### TC-015: 跨域请求在生产环境正常工作
- **类型**: 集成测试
- **关联验收标准**: 前后端联调通过（前端 Vercel → 后端 Render 的 CORS）
- **前置条件**: 前端 Vercel 已部署，后端 Render 已部署（Task 4.1 完成）
- **输入**: 任意合法 API 请求
- **执行步骤**:
  1. 从前端部署域名发起 API 请求到后端 Render 域名
  2. 检查响应头中的 `Access-Control-Allow-Origin`
  3. 检查是否返回预期数据
- **预期输出**:
  - 响应头包含 `Access-Control-Allow-Origin: <vercel-app-domain>`（或 `*`）
  - 无 CORS 相关错误
  - API 数据正常返回
- **清理**: 无
