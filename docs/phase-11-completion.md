# agent-remote Phase 11 完成记录

## 状态

Phase 11：管理前端，状态为完成。

本阶段目标是把 `agent-remote-admin-web` 从远端浏览器单页工具扩展为可实际施行的管理控制台，并补齐前端必须依赖的正式只读管理 API。

## 完成内容

### `agent-remote-admin-web`

- 重构为 React + Vite + TypeScript 管理控制台。
- 新增登录和初始化入口：
  - `/auth/login`
  - `/auth/bootstrap`
- 新增统一侧边导航和资源刷新流程。
- 新增 Overview 页面：
  - 用户、设备、账号、节点、workspace、sync session、工具 session、浏览器 session 计数。
  - 管理员可见失败节点任务摘要。
  - 当前用户可见审计摘要。
- 新增 Users 页面：
  - 管理员列出用户。
  - 管理员创建用户。
  - 管理员禁用用户。
- 新增 Devices 页面：
  - 列出可见设备。
  - 注册设备。
  - 撤销设备。
  - 轮换设备 token。
- 新增 Accounts 页面：
  - 创建工具账户。
  - 启动绑定。
  - 校验绑定。
  - 禁用账户。
- 新增 Nodes 页面：
  - 管理员列出节点。
  - 管理员创建节点。
  - 管理员设置维护状态。
  - 管理员禁用节点。
  - 管理员轮换节点注册 token。
  - 管理员查看节点任务和失败详情。
- 新增 Sessions 页面：
  - 列出工具 session。
  - 创建工具 session。
  - 获取 SSH attach 命令。
  - 停止 session。
- 新增 Sync 页面：
  - 列出 workspace。
  - 创建 workspace。
  - 创建 sync session。
  - 暂停、恢复、解决冲突、重置 sync session。
- 新增 Browser 页面：
  - 创建远端临时浏览器 session。
  - 连接 ready 浏览器 session。
  - 停止浏览器 session。
- 新增 Audit 页面：
  - 列出当前用户可见审计日志。
  - 展示审计详情。
- 新增 Settings 页面：
  - 管理 API base。
  - 更新当前用户显示名。
- 危险操作均通过确认弹窗保护。
- 失败状态会展示 API 返回的错误内容或可执行命令。

### `agent-remote-server`

- 新增 `/api/v1/audit-logs` API：
  - `GET /audit-logs`
  - `GET /audit-logs/{audit_log_id}`
- 审计日志可见性：
  - 管理员可查看全部审计日志。
  - 普通用户只可查看自己的审计日志。
- 新增节点任务只读管理 API：
  - `GET /nodes/tasks`
  - `GET /nodes/tasks/{task_id}`
- 节点任务 API 仅管理员可访问。
- 节点任务响应包含任务 payload、状态、租约、重试次数和任务结果或错误详情。

## 权限边界

- 普通用户前端仍会加载个人可见资源：设备、工具账户、workspace、sync session、工具 session、浏览器 session 和自己的审计日志。
- 管理员专用资源使用正式 API 权限控制：用户管理、节点管理和节点任务查看。
- 前端对 403/404 等失败响应直接展示错误，避免静默失败。

## 验证

已完成以下验证：

- `agent-remote-admin-web`
  - `pnpm build`
- `agent-remote-server`
  - `uv run ruff check ...`
  - `uv run mypy ...`
  - `uv run pytest tests/test_identity_api.py tests/test_node_api.py`

当前 server 测试仍存在 1 个上游依赖 warning：FastAPI/Starlette `TestClient` 提示未来应迁移到 `httpx2`。该 warning 不影响 Phase 11 验收。

## Phase 12 进入条件

Phase 12 可以开始，前提是：

- Phase 11 提交已推送。
- 管理控制台与 server 权限边界确认无误。
- 打包部署方案需要同时覆盖 server、node、admin-web 和 cli。

进入 Phase 12：打包、安装和部署。
