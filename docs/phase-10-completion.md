# agent-remote Phase 10 完成记录

## 状态

Phase 10：远端临时浏览器，状态为完成。

本阶段目标是在管理端提供一个短生命周期的远端浏览器入口，让用户可以通过 VPS 节点网络和节点环境访问 Claude Web、邮箱和账号确认页面。浏览器会话不复用工具账户登录目录，不挂载 workspace，不保存浏览器 profile。

## 完成内容

### `agent-remote-server`

- 新增 `/api/v1/browser-sessions` API：
  - `GET /browser-sessions`
  - `POST /browser-sessions`
  - `GET /browser-sessions/{browser_session_id}`
  - `POST /browser-sessions/{browser_session_id}/connect-info`
  - `GET /browser-sessions/{browser_session_id}/stream`
  - `POST /browser-sessions/{browser_session_id}/stop`
- 新增 browser session schema、repository 和 service。
- 创建浏览器 session 时：
  - 可绑定 `tool_account_id`。
  - 绑定工具账户时继承地区、时区、locale 和节点偏好。
  - 未绑定工具账户时要求显式给出地区、时区和 locale。
  - 自动投递 `create_browser_session` 节点任务。
- 停止浏览器 session 时自动投递 `stop_browser_session` 节点任务。
- 节点任务完成后回写：
  - `create_browser_session` -> `ready`
  - `stop_browser_session` -> `stopped`
  - 失败任务 -> `failed`
- `connect-info` 签发短期 opaque token，并将 token scope 写入 Redis。
- `/stream` 通过 Redis 校验短期 token 后返回内嵌浏览器页面。
- 日志和数据库不保存页面内容、用户输入、cookie、token、截图或 profile 路径。

### `agent-remote-node`

- 新增 `internal/browser` runtime。
- 支持节点任务：
  - `create_browser_session`
  - `stop_browser_session`
- 默认浏览器镜像改为真实存在的现成镜像：
  - `kasmweb/chrome:1.18.0`
- 浏览器容器启动时注入：
  - `TZ`
  - `LANG`
  - `LC_ALL`
  - `LAUNCH_URL`
  - `APP_ARGS`
  - `VNC_PW`
- 默认 Chrome 参数包含：
  - `--incognito`
  - `--no-first-run`
  - `--no-default-browser-check`
  - `--lang=<locale>`
  - `--force-webrtc-ip-handling-policy=disable_non_proxied_udp`
- 浏览器容器不挂载 workspace 和工具账户目录。
- 临时 profile 只放在 `browser_root` 下，停止任务会删除。
- 新增配置：
  - `browser_root`
  - `browser_image`
  - `browser_public_base_url`

### `agent-remote-admin-web`

- 初始化 Vite + React + TypeScript 前端。
- 提供远端浏览器工作台：
  - 配置 API base 和 Bearer token。
  - 创建浏览器 session。
  - 刷新 session 列表。
  - 连接 ready session。
  - 停止 session。
  - iframe 内嵌短期 `embed_url`。
- 构建产物和 TypeScript 缓存已加入 `.gitignore`。

### `agent-remote-protocol`

- 浏览器任务示例默认镜像更新为 `kasmweb/chrome:1.18.0`。

### `agent-remote`

- 主方案和实施附录中的浏览器镜像说明更新为 `kasmweb/chrome:1.18.0`。

## 验证

已完成以下验证：

- `agent-remote-server`
  - `uv run ruff check .`
  - `uv run mypy`
  - `uv run pytest`
- `agent-remote-node`
  - `go test ./...`
- `agent-remote-admin-web`
  - `npm run build`
- `agent-remote-protocol`
  - OpenAPI YAML 解析通过

当前 server 测试仍存在 1 个上游依赖 warning：FastAPI/Starlette `TestClient` 提示未来应迁移到 `httpx2`。该 warning 不影响 Phase 10 验收。

## 注意事项

- `kasmweb/chrome:1.18.0` 是外部可配置运行时镜像，不作为本项目自建镜像发布。
- 生产环境需要给 `browser_public_base_url` 配置节点侧 HTTPS 反向代理，使 server 签发的 `/stream` 页面可以嵌入实际 KasmVNC 端点。
- Redis 是短期 browser embed token 的校验依赖；真实部署中必须可用。

## Phase 11 进入条件

Phase 11 可以开始，前提是：

- Phase 10 提交已推送。
- 部署环境准备好浏览器运行时镜像和节点侧反向代理方案。
- 管理前端继续扩展用户、设备、工具账户、节点、session、同步和审计页面。

进入 Phase 11：管理前端。
