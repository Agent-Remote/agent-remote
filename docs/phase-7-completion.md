# agent-remote Phase 7 完成记录

## 状态

Phase 7：Mutagen workspace 同步，状态为完成。

Phase 7 的目标是建立显式 workspace 模型，避免本地目录被静默同步；用户首次在新目录启用远端工具前必须确认同步关系，控制面创建 workspace 和 sync session，节点端准备远端目录，CLI 使用托管 Mutagen 二进制创建和管理同步 session。

本阶段完成源码、协议和本地验证闭环。真实跨机器文件同步仍需要发布包内置 Mutagen、可用 SSH/WireGuard 连接、真实 VPS 节点和 Mutagen 远端 agent 执行环境；这些进入部署验收时执行，不要求用户手动安装 Mutagen。

## 已完成交付物

- [x] workspace 创建、读取、列表、更新 API
- [x] sync session 创建、读取、列表 API
- [x] sync session pause/resume/resolve/reset API
- [x] server 侧 workspace 幂等创建
- [x] server 侧 sync session 创建并生成 `prepare_workspace` 节点任务
- [x] server 侧 attach 前 sync 冲突阻止
- [x] CLI workspace 首次确认
- [x] CLI 项目 key 使用规范化绝对路径 SHA-256
- [x] CLI 本地 SQLite workspace/sync 元数据缓存
- [x] CLI `agent-remote sync ensure`
- [x] CLI `agent-remote sync status`
- [x] CLI `agent-remote sync pause`
- [x] CLI `agent-remote sync resume`
- [x] CLI `agent-remote sync resolve`
- [x] CLI `agent-remote sync reset`
- [x] CLI Mutagen wrapper 和默认 ignore 规则
- [x] 节点端 `prepare_workspace` 任务执行
- [x] 节点端 workspace 目录 marker 文件
- [x] 节点端 workspace root 配置

## 仓库提交

```text
fd90990 feat: add workspace sync contract
```

`agent-remote-server`：

```text
e1f5388 feat(sync): add workspace sync api
```

`agent-remote-cli`：

```text
87bead0 feat: add workspace sync commands
```

`agent-remote-node`：

```text
74ba1d6 feat: prepare workspace directories
```

## 控制面能力

新增 API：

```text
GET    /api/v1/workspaces
POST   /api/v1/workspaces
GET    /api/v1/workspaces/{workspace_id}
PATCH  /api/v1/workspaces/{workspace_id}
GET    /api/v1/sync-sessions
POST   /api/v1/sync-sessions
GET    /api/v1/sync-sessions/{sync_session_id}
POST   /api/v1/sync-sessions/{sync_session_id}/pause
POST   /api/v1/sync-sessions/{sync_session_id}/resume
POST   /api/v1/sync-sessions/{sync_session_id}/resolve
POST   /api/v1/sync-sessions/{sync_session_id}/reset
```

workspace 创建要求当前 token 是设备 token，且请求中的 `device_id` 必须和 token 绑定设备一致。相同用户、相同 `project_key` 重复创建时返回已有 workspace，避免重复远端目录。

sync session 创建会选择可用节点，写入远端路径，并创建 `prepare_workspace:{sync_session_id}` 节点任务。返回数据包含 Mutagen session name、远端路径、SSH endpoint 和准备任务 ID。

`POST /api/v1/sessions/{session_id}/attach` 现在会检查 session 对应 workspace 的同步状态。如果存在未解决冲突或失败状态，返回 `SYNC_CONFLICT`，默认阻止进入远端工具 session。

## CLI 能力

新增命令：

```sh
agent-remote sync ensure
agent-remote sync status
agent-remote sync pause
agent-remote sync resume
agent-remote sync resolve
agent-remote sync reset
```

`sync ensure` 行为：

1. 规范化 workspace 路径，默认是当前目录。
2. 使用路径计算 `sha256:<digest>` 项目 key。
3. 如果本地没有该 workspace 记录，先询问用户是否创建同步关系。
4. 用户拒绝时直接退出，不创建远端 sync session。
5. 用户确认后调用控制面创建 workspace 和 sync session。
6. 使用托管 `bin/mutagen` 创建双向同步。

默认 ignore：

```text
.git
node_modules
target
dist
.venv
__pycache__
```

`sync status --fail-on-conflict` 可用于后续 `fclaude` 进入 session 前检查。只要控制面或本地 Mutagen 输出显示冲突，该命令会失败退出。

## 节点端能力

节点端新增 workspace 目录准备逻辑。`prepare_workspace` payload：

```json
{
  "user_id": "user_...",
  "workspace_id": "workspace_...",
  "sync_session_id": "sync_...",
  "remote_path": "/var/lib/agent-remote/users/user_.../workspaces/workspace_.../files"
}
```

节点会：

- 校验 `remote_path` 位于 `workspace_root` 下
- 创建远端 workspace 文件目录
- 写入 `.agent-remote-workspace.json` marker
- 返回实际目录和 marker 路径

新增节点配置：

```json
{
  "workspace_root": "/var/lib/agent-remote/users",
  "mutagen_binary_path": "mutagen"
}
```

## 验证命令


在 `agent-remote-server` 仓库执行：

```sh
scripts/run-quality-checks.sh
```

```sh
UV_CACHE_DIR=/Users/rem/Documents/Git/agent-remote-server/.uv-cache uv run alembic heads
```

```sh
docker compose config
docker compose build server
```

server 仓库执行禁用词扫描，排除 `.git`、虚拟环境和工具缓存目录。

在 `agent-remote-cli` 仓库执行：

```sh
scripts/run-quality-checks.sh
```

在 `agent-remote-node` 仓库执行：

```sh
go test ./...
```

```sh
docker build -t agent-remote-node:phase7 .
```

## 验收结果

- server：24 个测试通过，包含 workspace 幂等创建、sync session 创建、节点任务生成和 sync 冲突阻止 attach。
- server：Alembic head 仍为 `0004_connection_fields`，本阶段复用既有 `workspaces` 和 `sync_sessions` 表，无新增迁移。
- server：Docker Compose 配置和 server 镜像构建通过。
- server：禁用词扫描通过。
- CLI：10 个 Rust 测试通过，包含 project key、Mutagen session name、本地 workspace/sync 元数据。
- node：Go 测试通过，包含 workspace 目录创建、越界路径拒绝和 worker `prepare_workspace` 任务执行。
- node：Docker 镜像构建通过。

当前未在真实 VPS 上执行 Mutagen 双向文件同步。该测试需要实际打包的 Mutagen binary、WireGuard/SSH 连通性和可写远端 workspace 目录，进入部署验收时执行。

## Phase 8 进入条件

Phase 8 可以开始，前提是：

- Phase 7 提交已推送。
- server、CLI、node 仓库保持干净。
- 后续 `fclaude` 启动链路调用 `agent-remote sync ensure` 或同等内部函数，并在 attach 前执行 conflict check。

进入 Phase 8：工具账户抽象和 Claude 绑定。

Phase 8 目标：

- 建立工具账户 registry 和运行模板。
- 实现 `tool_type=claude` 账户创建与绑定状态机。
- 节点端创建远端登录 sandbox 和临时 tmux。
- Claude verifier 检测登录态。
- 登录态归档到远端账户目录，不落到本地 CLI。
