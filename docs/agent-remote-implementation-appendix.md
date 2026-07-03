# agent-remote 实施级附录

## 1. 协议冻结范围

MVP 第一阶段需要冻结以下内容：

1. 核心术语
   - `User`
   - `Device`
   - `ToolType`
   - `ToolAccount`
   - `Workspace`
   - `Session`
   - `BrowserSession`
   - `Node`
   - `NodeTask`
   - `WireGuardPeer`
   - `SshKey`

2. 管理端 OpenAPI 模块
   - `/auth`
   - `/users`
   - `/devices`
   - `/tool-accounts`
   - `/nodes`
   - `/workspaces`
   - `/sync-sessions`
   - `/sessions`
   - `/browser-sessions`
   - `/audit-logs`
   - `/node-api`

3. 节点任务协议
   - 任务类型。
   - 任务 payload schema。
   - 任务状态。
   - 幂等 `task_id` 规则。
   - 节点任务结果 schema。

4. CLI 命令规范
   - `agent-remote` 管理命令。
   - `fclaude` Claude 启动命令。
   - 参数透传规则。
   - 本地状态目录和 SQLite schema。

5. 数据库字段草案
   - 核心表字段。
   - 索引。
   - 唯一约束。
   - 外键关系。
   - 敏感字段加密标记。

### 1.1 Phase 与附录章节映射

完整 Phase Roadmap 见 [agent-remote-architecture.md](agent-remote-architecture.md) 第 9 节。本附录用于支撑各 Phase 的具体实现。

| Phase | 需要优先参考的附录内容 |
| --- | --- |
| Phase 0：方案和协议基线 | 第 1 节协议冻结范围、第 2 节 OpenAPI、第 3 节节点任务 payload |
| Phase 1-3：控制面、数据模型、认证设备 | 第 2 节 OpenAPI、第 5 节数据库字段草案、第 6.1-6.3 节验收场景 |
| Phase 4：节点注册和任务轮询 | 第 2.12 节 `/node-api`、第 3 节节点任务 payload、第 6.2 节验收场景 |
| Phase 5：CLI 本地基础能力 | 第 4 节 CLI 命令规范、第 6.3 和 6.3.1 节验收场景 |
| Phase 6：WireGuard 与 SSH | 第 2 节设备和节点 API、第 6.4 节验收场景、第 7.5 和 7.6 节部署大纲 |
| Phase 7：Mutagen 同步 | 第 2.7 和 2.8 节、第 6.5 和 6.10 节验收场景 |
| Phase 8：Claude 账户绑定 | 第 2.5 节、第 3.2 节、第 6.6 节验收场景 |
| Phase 9：Claude session 和 `fclaude` | 第 2.9 节、第 3.3 和 3.4 节、第 4.2 节、第 6.7-6.9 节验收场景 |
| Phase 10：远端临时浏览器 | 第 2.10 节、第 3.5 和 3.6 节、第 5.8 节、第 6.11 节验收场景 |
| Phase 11：管理前端 | 第 2 节全部用户侧 API、第 6 节端到端场景 |
| Phase 12-14：部署、发布、稳定化 | 第 7 节部署文档大纲、第 6 节端到端测试场景 |
| Phase 15：多工具扩展验证 | 第 1 节核心术语、第 2.5 和 2.9 节、第 3 节任务协议 |

## 2. OpenAPI 草案

### 2.1 通用约定

路径前缀：

```text
/api/v1
```

认证：

- 用户/CLI/前端 API 使用 Bearer token。
- `/node-api` 使用节点凭证。
- 节点凭证和用户 token 不可互用。

通用响应：

```json
{
  "data": {},
  "request_id": "req_..."
}
```

通用错误：

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  },
  "request_id": "req_..."
}
```

### 2.2 `/auth`

```text
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
POST /api/v1/auth/cli/start
POST /api/v1/auth/cli/complete
POST /api/v1/auth/totp/setup
POST /api/v1/auth/totp/verify
```

`POST /auth/login` request:

```json
{
  "username": "alice",
  "password": "secret",
  "totp_code": "123456"
}
```

`POST /auth/cli/start` response:

```json
{
  "data": {
    "device_code": "dev_...",
    "user_code": "ABCD-EFGH",
    "verification_url": "https://example.com/cli",
    "expires_in": 600,
    "interval": 5
  },
  "request_id": "req_..."
}
```

### 2.3 `/users`

```text
GET    /api/v1/users/me
PATCH  /api/v1/users/me
GET    /api/v1/users
POST   /api/v1/users
GET    /api/v1/users/{user_id}
PATCH  /api/v1/users/{user_id}
POST   /api/v1/users/{user_id}/disable
```

`POST /users` request:

```json
{
  "username": "alice",
  "display_name": "Alice",
  "role": "user",
  "password": "initial-secret"
}
```

### 2.4 `/devices`

```text
GET    /api/v1/devices
POST   /api/v1/devices/register
GET    /api/v1/devices/{device_id}
POST   /api/v1/devices/{device_id}/disable
POST   /api/v1/devices/{device_id}/rotate-token
```

`POST /devices/register` request:

```json
{
  "device_name": "rem-macbook",
  "platform": "macos",
  "ssh_public_key": "ssh-ed25519 ...",
  "wireguard_public_key": "..."
}
```

Response:

```json
{
  "data": {
    "device_id": "dev_...",
    "wireguard_peer_id": "wg_...",
    "ssh_key_id": "ssh_..."
  },
  "request_id": "req_..."
}
```

### 2.5 `/tool-accounts`

```text
GET    /api/v1/tool-accounts
POST   /api/v1/tool-accounts
GET    /api/v1/tool-accounts/{account_id}
PATCH  /api/v1/tool-accounts/{account_id}
POST   /api/v1/tool-accounts/{account_id}/bind/start
GET    /api/v1/tool-accounts/{account_id}/bind/status
POST   /api/v1/tool-accounts/{account_id}/disable
POST   /api/v1/tool-accounts/{account_id}/migrate-node
```

`POST /tool-accounts` request:

```json
{
  "tool_type": "claude",
  "display_name": "Claude US",
  "region_code": "US",
  "timezone": "America/Los_Angeles",
  "locale": "en_US.UTF-8",
  "preferred_node_tags": ["us"]
}
```

Binding status response:

```json
{
  "data": {
    "account_id": "acct_...",
    "status": "binding_waiting_user_login",
    "node_id": "node_...",
    "session_id": "sess_...",
    "connect_command": "agent-remote attach-binding bind_..."
  },
  "request_id": "req_..."
}
```

### 2.6 `/nodes`

```text
GET    /api/v1/nodes
POST   /api/v1/nodes
GET    /api/v1/nodes/{node_id}
PATCH  /api/v1/nodes/{node_id}
POST   /api/v1/nodes/{node_id}/registration-token
POST   /api/v1/nodes/{node_id}/maintenance
POST   /api/v1/nodes/{node_id}/disable
```

Node create request:

```json
{
  "name": "us-west-1",
  "region_code": "US",
  "tags": ["us", "west"],
  "weight": 100,
  "supported_tool_types": ["claude"]
}
```

### 2.7 `/workspaces`

```text
GET    /api/v1/workspaces
POST   /api/v1/workspaces
GET    /api/v1/workspaces/{workspace_id}
PATCH  /api/v1/workspaces/{workspace_id}
```

Create request:

```json
{
  "device_id": "dev_...",
  "project_key": "sha256:...",
  "local_start_path": "/Users/rem/project",
  "display_name": "project"
}
```

### 2.8 `/sync-sessions`

```text
GET    /api/v1/sync-sessions
POST   /api/v1/sync-sessions
GET    /api/v1/sync-sessions/{sync_session_id}
POST   /api/v1/sync-sessions/{sync_session_id}/pause
POST   /api/v1/sync-sessions/{sync_session_id}/resume
POST   /api/v1/sync-sessions/{sync_session_id}/resolve
POST   /api/v1/sync-sessions/{sync_session_id}/reset
```

### 2.9 `/sessions`

```text
GET    /api/v1/sessions
POST   /api/v1/sessions
GET    /api/v1/sessions/current-project
GET    /api/v1/sessions/{session_id}
POST   /api/v1/sessions/{session_id}/attach-info
POST   /api/v1/sessions/{session_id}/stop
```

Create request:

```json
{
  "tool_type": "claude",
  "tool_account_id": "acct_...",
  "workspace_id": "ws_...",
  "project_key": "sha256:...",
  "argv": ["--model", "opus"]
}
```

Attach info response:

```json
{
  "data": {
    "session_id": "sess_...",
    "node_id": "node_...",
    "node_wg_ip": "10.42.0.10",
    "ssh_username": "agent-remote",
    "attach_command": "ssh agent-remote@10.42.0.10 agent-remote-attach --session sess_..."
  },
  "request_id": "req_..."
}
```

### 2.10 `/browser-sessions`

```text
GET    /api/v1/browser-sessions
POST   /api/v1/browser-sessions
GET    /api/v1/browser-sessions/{browser_session_id}
POST   /api/v1/browser-sessions/{browser_session_id}/connect-info
POST   /api/v1/browser-sessions/{browser_session_id}/stop
```

Create request:

```json
{
  "tool_account_id": "acct_...",
  "target_url": "https://claude.ai",
  "region_code": "US",
  "timezone": "America/Los_Angeles",
  "locale": "en_US.UTF-8",
  "ttl_seconds": 1800
}
```

Create response:

```json
{
  "data": {
    "browser_session_id": "bsess_...",
    "status": "starting",
    "node_id": "node_...",
    "expires_at": "2026-07-04T00:30:00Z"
  },
  "request_id": "req_..."
}
```

Connect info response:

```json
{
  "data": {
    "browser_session_id": "bsess_...",
    "status": "ready",
    "embed_url": "https://agent.example.com/api/v1/browser-sessions/bsess_.../stream?token=short_lived_token",
    "expires_at": "2026-07-04T00:30:00Z"
  },
  "request_id": "req_..."
}
```

约束：

- `tool_account_id` 可空；为空时必须显式给出地区、时区和 locale。
- 有 `tool_account_id` 时，默认继承工具账户的 `region_code`、`timezone`、`locale` 和节点亲和。
- 浏览器会话默认无痕，不持久化 cookie、localStorage、密码、浏览历史、下载目录或浏览器 profile。
- `embed_url` 必须短期有效，并绑定当前用户、浏览器会话和 request scope。
- 管理端不得把页面内容、输入内容、cookie 或截图写入日志。

### 2.11 `/audit-logs`

```text
GET /api/v1/audit-logs
GET /api/v1/audit-logs/{audit_log_id}
```

### 2.12 `/node-api`

```text
POST /api/v1/node-api/register
POST /api/v1/node-api/heartbeat
POST /api/v1/node-api/tasks/poll
POST /api/v1/node-api/tasks/{task_id}/start
POST /api/v1/node-api/tasks/{task_id}/complete
POST /api/v1/node-api/tasks/{task_id}/fail
POST /api/v1/node-api/reconcile
```

Heartbeat request:

```json
{
  "node_id": "node_...",
  "version": "0.1.0",
  "supported_tool_types": ["claude"],
  "resources": {
    "cpu_load": 0.42,
    "memory_used_bytes": 1073741824,
    "memory_total_bytes": 4294967296,
    "disk_used_bytes": 21474836480,
    "disk_total_bytes": 85899345920
  },
  "runtime": {
    "docker_ok": true,
    "tmux_ok": true,
    "active_sessions": 3,
    "containers": 3
  }
}
```

## 3. 节点任务 Payload 草案

### 3.1 通用任务 envelope

```json
{
  "task_id": "task_...",
  "node_id": "node_...",
  "task_type": "create_tool_session",
  "idempotency_key": "task_...",
  "payload": {},
  "created_at": "2026-07-04T00:00:00Z",
  "expires_at": "2026-07-04T00:10:00Z"
}
```

### 3.2 `create_binding_session`

```json
{
  "binding_id": "bind_...",
  "tool_account_id": "acct_...",
  "tool_type": "claude",
  "user_id": "user_...",
  "region_code": "US",
  "timezone": "America/Los_Angeles",
  "locale": "en_US.UTF-8",
  "template": {
    "image": "agent-remote/claude:latest",
    "command": ["claude", "login"]
  }
}
```

### 3.3 `create_tool_session`

```json
{
  "session_id": "sess_...",
  "tool_type": "claude",
  "tool_account_id": "acct_...",
  "workspace_id": "ws_...",
  "user_id": "user_...",
  "project_key": "sha256:...",
  "argv": ["--model", "opus"],
  "paths": {
    "workspace_remote_path": "/var/lib/agent-remote/users/user_.../workspaces/ws_.../files",
    "account_remote_path": "/var/lib/agent-remote/users/user_.../accounts/acct_..."
  },
  "runtime": {
    "timezone": "America/Los_Angeles",
    "locale": "en_US.UTF-8",
    "cpu_limit": "2",
    "memory_limit": "4g"
  }
}
```

### 3.4 `stop_session`

```json
{
  "session_id": "sess_...",
  "reason": "user_requested"
}
```

### 3.5 `create_browser_session`

```json
{
  "browser_session_id": "bsess_...",
  "user_id": "user_...",
  "tool_account_id": "acct_...",
  "target_url": "https://claude.ai",
  "region_code": "US",
  "timezone": "America/Los_Angeles",
  "locale": "en_US.UTF-8",
  "ttl_seconds": 1800,
  "browser": {
    "image": "agent-remote/browser:latest",
    "engine": "chromium",
    "mode": "incognito",
    "viewport": {
      "width": 1440,
      "height": 900
    }
  },
  "network_policy": {
    "egress": "node_default",
    "deny_private_networks": true,
    "deny_metadata_service": true,
    "disable_webrtc_local_ip": true
  }
}
```

节点成功后返回：

```json
{
  "browser_session_id": "bsess_...",
  "container_id": "container_...",
  "stream_endpoint": "node-local://browser/bsess_...",
  "status": "ready"
}
```

节点端要求：

- 浏览器必须在独立容器中运行。
- 容器不挂载 workspace 和工具账户目录。
- 临时 profile 目录位于浏览器会话临时目录中，停止后删除。
- 浏览器语言、时区和 locale 必须按 payload 注入。

### 3.6 `stop_browser_session`

```json
{
  "browser_session_id": "bsess_...",
  "reason": "user_requested"
}
```

### 3.7 `sync_ssh_keys`

```json
{
  "authorized_keys": [
    {
      "ssh_key_id": "ssh_...",
      "public_key": "ssh-ed25519 ...",
      "forced_command": "agent-remote-attach"
    }
  ]
}
```

### 3.8 `reconcile_state`

```json
{
  "requested_sections": ["sessions", "browser_sessions", "containers", "tmux", "authorized_keys"]
}
```

### 3.9 任务结果

Success:

```json
{
  "task_id": "task_...",
  "status": "succeeded",
  "result": {
    "session_id": "sess_...",
    "tmux_session_name": "ar_sess_...",
    "container_id": "..."
  }
}
```

Failure:

```json
{
  "task_id": "task_...",
  "status": "failed",
  "error": {
    "code": "docker_create_failed",
    "message": "failed to create container"
  }
}
```

## 4. CLI 命令规范草案

### 4.1 `agent-remote`

```text
agent-remote login --server https://example.com
agent-remote logout
agent-remote status
agent-remote doctor
agent-remote doctor --fix
agent-remote setup network

agent-remote device list
agent-remote device current
agent-remote device revoke <device_id>

agent-remote account list
agent-remote account create --tool claude --name "Claude US" --region US --timezone America/Los_Angeles
agent-remote account bind <account_id>
agent-remote account disable <account_id>

agent-remote sync status
agent-remote sync pause
agent-remote sync resume
agent-remote sync resolve
agent-remote sync reset
```

### 4.2 `fclaude`

```text
fclaude
fclaude new
fclaude list
fclaude list --all
fclaude attach <session_id>
fclaude stop <session_id>
fclaude --workspace /path/to/project
fclaude --account <account_id>
fclaude -- <claude_args...>
```

规则：

- `fclaude` 无参数时，恢复当前项目最近 Claude session。
- 当前项目由启动路径生成 project key。
- `fclaude` 只消费明确 session 命令。
- 其他参数默认透传给原生 `claude`。
- `fclaude -- <args>` 强制透传。

## 5. 数据库字段草案

字段类型以 PostgreSQL 为准，具体长度可在迁移实现时调整。

### 5.1 `users`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| username | text | 唯一 |
| display_name | text | 显示名 |
| role | text | `admin` / `user` |
| status | text | `active` / `disabled` |
| password_hash | text | Argon2id |
| totp_enabled | boolean | 是否启用 TOTP |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 5.2 `user_devices`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| user_id | uuid | FK users |
| name | text | 设备名 |
| platform | text | `macos` / `linux` |
| status | text | `active` / `revoked` |
| last_seen_at | timestamptz | 最近使用 |
| created_at | timestamptz | 创建时间 |

### 5.3 `tool_accounts`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| user_id | uuid | FK users |
| tool_type | text | `claude` / `codex` |
| display_name | text | 显示名 |
| status | text | 绑定状态/运行状态 |
| region_code | text | 地区 |
| timezone | text | 时区 |
| locale | text | locale |
| preferred_node_tags | jsonb | 节点标签偏好 |
| affinity_node_id | uuid | FK nodes，可空 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 5.4 `tool_account_profiles`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| tool_account_id | uuid | FK tool_accounts |
| tool_type | text | 工具类型 |
| profile_json | jsonb | 非敏感 profile |
| encrypted_secrets | bytea | 加密敏感字段 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 5.5 `nodes`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| name | text | 节点名 |
| status | text | `healthy` / `degraded` / `maintenance` / `disabled` / `offline` |
| region_code | text | 地区 |
| tags | jsonb | 标签 |
| weight | integer | 调度权重 |
| wireguard_ip | inet | WG 内网 IP |
| supported_tool_types | jsonb | 支持工具 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 5.6 `node_tasks`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| task_id | text | 唯一任务 ID |
| node_id | uuid | FK nodes |
| task_type | text | 任务类型 |
| status | text | `pending` / `leased` / `running` / `succeeded` / `failed` |
| payload | jsonb | 任务 payload |
| lease_until | timestamptz | 租约过期 |
| retry_count | integer | 重试次数 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 5.7 `sessions`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| tool_type | text | 工具类型 |
| user_id | uuid | FK users |
| tool_account_id | uuid | FK tool_accounts |
| workspace_id | uuid | FK workspaces |
| node_id | uuid | FK nodes |
| project_key | text | 项目 key |
| status | text | session 状态 |
| tmux_session_name | text | tmux 名称 |
| container_id | text | Docker 容器 ID |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 5.8 `browser_sessions`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| user_id | uuid | FK users |
| tool_account_id | uuid | FK tool_accounts，可空 |
| node_id | uuid | FK nodes |
| status | text | `starting` / `ready` / `stopping` / `stopped` / `failed` / `expired` |
| region_code | text | 地区 |
| timezone | text | 时区 |
| locale | text | locale |
| target_url | text | 初始 URL，可空 |
| container_id | text | Docker 容器 ID |
| stream_endpoint | text | 节点本地连接端点或引用，不直接暴露给用户 |
| ttl_seconds | integer | 会话 TTL |
| expires_at | timestamptz | 过期时间 |
| stopped_at | timestamptz | 停止时间 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

字段约束：

- 不保存 cookie、localStorage、浏览历史、页面内容、截图、输入内容或浏览器 profile 路径。
- `stream_endpoint` 只能是服务端内部引用；前端使用的 `embed_url` 必须动态签发短期 token。

### 5.9 推荐索引

```sql
CREATE UNIQUE INDEX users_username_uidx ON users (username);
CREATE INDEX tool_accounts_user_tool_idx ON tool_accounts (user_id, tool_type);
CREATE INDEX sessions_project_idx ON sessions (user_id, tool_type, project_key, status);
CREATE INDEX sessions_account_active_idx ON sessions (tool_account_id, status);
CREATE INDEX browser_sessions_user_status_idx ON browser_sessions (user_id, status, created_at);
CREATE INDEX browser_sessions_node_status_idx ON browser_sessions (node_id, status, expires_at);
CREATE UNIQUE INDEX node_tasks_task_id_uidx ON node_tasks (task_id);
CREATE INDEX node_tasks_poll_idx ON node_tasks (node_id, status, lease_until);
CREATE INDEX audit_logs_actor_idx ON audit_logs (actor_user_id, created_at);
```

## 6. 端到端测试场景

### 6.1 首次部署与管理员初始化

目标：

- 控制面可通过 Docker Compose 启动。
- PostgreSQL 和 Redis 可用。
- 第一个管理员可创建。
- 管理端 Web/API 可访问。

步骤：

1. 配置 `.env`，包含 `AGENT_REMOTE_SECRET_KEY`、`DATABASE_URL`、`REDIS_URL`、`PUBLIC_BASE_URL`。
2. 执行 Docker Compose 启动控制面。
3. 运行 bootstrap 命令创建管理员。
4. 管理员登录管理端。
5. 检查审计日志中存在管理员创建和登录记录。

验收：

- 管理端健康检查通过。
- 管理员可以登录。
- 数据库迁移版本正确。
- Redis 连接正常。

### 6.2 节点注册与心跳

目标：

- `agent-remote-node` 可注册到管理端。
- 节点可持续上报心跳。
- 管理端显示节点健康状态。

步骤：

1. 管理端创建节点并生成注册 token。
2. VPS 准备 Docker、OpenSSH server 和 TUN/WireGuard 内核能力。
3. `agent-remote-node` 安装器准备 tmux、Mutagen、WireGuard helper 等受控依赖。
4. 安装并启动 `agent-remote-node` systemd 服务。
5. 节点使用注册 token 注册。
6. 管理端查看节点状态。

验收：

- 节点状态为 `healthy`。
- `node_heartbeats` 有持续记录。
- 节点支持工具类型包含 `claude`。
- 节点端受控依赖版本记录在节点 manifest 中。

### 6.3 CLI 登录与设备注册

目标：

- 本地设备可通过 `agent-remote login` 登录。
- CLI token、WireGuard peer、SSH key 正确注册。
- 本地 SQLite 和系统 keychain/libsecret 正常工作。

步骤：

1. 执行 `agent-remote login --server <url>`。
2. 完成 Web 或 device code 登录。
3. CLI 注册设备。
4. 查看 `agent-remote status`。

验收：

- `~/.config/agent-remote/state.sqlite` 存在。
- `~/.config/agent-remote/bin/` 中存在 CLI 托管依赖或依赖引用。
- 本地不保存工具账户登录态。
- 管理端可看到设备。
- 设备有 WireGuard peer 和 SSH key。

### 6.3.1 CLI 托管依赖检查

目标：

- 用户不需要手动安装 WireGuard 和 Mutagen。
- CLI 可检查并准备受控依赖。

步骤：

1. 在未手动安装 Mutagen 的本地机器执行 `agent-remote doctor`。
2. 执行 `agent-remote doctor --fix` 或 `agent-remote setup network`。
3. 检查 CLI 托管目录。

验收：

- CLI 能提供受控版本 Mutagen。
- CLI 能提供 WireGuard helper 或明确引导系统授权。
- 用户不需要手动执行包管理器安装 Mutagen/WireGuard。
- 依赖版本记录在本地 manifest 中。

### 6.4 WireGuard 与 SSH 可达性

目标：

- CLI 可启动 WireGuard。
- 本地设备可访问目标节点 WireGuard IP。
- SSH forced command 生效。

步骤：

1. 执行 `agent-remote doctor network`。
2. CLI 启动 WireGuard。
3. CLI 检查节点 WireGuard IP 可达。
4. CLI 检查 SSH 入口可达。

验收：

- WireGuard peer 状态正常。
- SSH 不能进入普通 shell。
- SSH 只能进入受控 `agent-remote-attach`。

### 6.5 Workspace 首次同步确认

目标：

- `fclaude` 第一次在新目录启动时必须询问是否创建同步。
- 用户拒绝时不启动会修改目录的远端 session。
- 用户确认后创建 Mutagen session。

步骤：

1. 在新项目目录执行 `fclaude`.
2. 观察首次同步确认提示。
3. 选择拒绝，确认不会创建可写 session。
4. 再次执行并选择确认。
5. 查看 `agent-remote sync status`。

验收：

- 未确认时不静默同步。
- 确认后 `sync_sessions` 有记录。
- Mutagen session 健康。

### 6.6 Claude 账户绑定

目标：

- 普通用户可创建 `tool_type=claude` 账户。
- 绑定状态机正确流转。
- Claude 登录态归档到远端账户目录。

步骤：

1. 执行 `agent-remote account create --tool claude ...`。
2. 执行 `agent-remote account bind <account_id>`。
3. CLI 或管理端展示连接指令。
4. 用户进入临时绑定 session。
5. 用户执行 `claude login`。
6. 节点 verifier 检测登录态。

验收：

- 状态流转到 `active`。
- 登录态只保存在远端账户目录。
- 日志不含 token/cookie。
- 临时 sandbox 被清理。

### 6.7 Claude session 创建与恢复

目标：

- `fclaude` 可创建 Claude session。
- SSH 断开后 tmux session 保持。
- 同一路径再次执行 `fclaude` 恢复当前项目 session。

步骤：

1. 在项目目录执行 `fclaude`。
2. 等待 Docker sandbox 和 tmux 创建。
3. 进入 Claude。
4. 断开 SSH。
5. 在同一路径再次执行 `fclaude`。

验收：

- 第二次恢复的是当前项目最近 session。
- 不是全局最近 session。
- tmux session 未因 SSH 断开而停止。

### 6.8 参数透传

目标：

- `fclaude` 不破坏原生 `claude` 参数体验。

步骤：

1. 执行 `fclaude -- --model opus`。
2. 执行 `fclaude --model opus`。
3. 执行一个未来可能与 Claude 原生命令重名的参数，使用 `--` 强制透传。

验收：

- 非 fclaude session 参数原样传给远端 `claude`。
- 参数顺序保持不变。

### 6.9 同账户多开同节点

目标：

- 同一个工具账户允许多开。
- 同账户所有活跃 session 必须在同一节点。

步骤：

1. 使用同一个 Claude 账户在项目 A 执行 `fclaude new`。
2. 在项目 B 使用同账户执行 `fclaude new`。
3. 查看两个 session 的节点。

验收：

- 两个 session 可同时 active。
- 两个 session 的 `node_id` 相同。
- 出口 IP 一致。

### 6.10 Mutagen 冲突阻止进入

目标：

- 同步冲突不自动覆盖。
- 未解决冲突默认阻止进入工具 session。

步骤：

1. 本地和远端制造同一文件冲突。
2. 执行 `agent-remote sync status`。
3. 执行 `fclaude`。
4. 执行 `agent-remote sync resolve`。

验收：

- CLI 显示冲突路径。
- 未解决前 `fclaude` 不 attach。
- 解决后可以进入 session。

### 6.11 远端临时浏览器

目标：

- 普通用户可在管理端创建远端临时浏览器。
- 浏览器使用 VPS 节点网络、时区、locale 和浏览器语言。
- 浏览器会话无痕，停止后不保留用户信息。

步骤：

1. 用户在管理端创建浏览器会话，选择 Claude 工具账户并打开 `https://claude.ai`。
2. 管理端创建 `browser_sessions` 记录和 `create_browser_session` 节点任务。
3. 节点启动浏览器容器。
4. 管理端返回短期 `embed_url`。
5. 用户在内嵌浏览器中访问 Claude Web 或邮箱。
6. 用户关闭会话或等待 TTL 到期。
7. 管理端下发 `stop_browser_session` 并清理资源。

验收：

- 浏览器出口 IP 为目标 VPS 节点。
- 浏览器时区、locale、语言与工具账户地区一致。
- 容器没有挂载 workspace 或工具账户目录。
- 停止后临时 profile 目录被删除。
- 日志不包含页面内容、输入内容、cookie、token 或截图。

### 6.12 节点断线与恢复对账

目标：

- 节点断线后管理端标记 offline。
- 节点恢复后重新上报本地状态。
- 管理端进行 session 对账。

步骤：

1. 停止 `agent-remote-node`。
2. 等待心跳超时。
3. 重启 `agent-remote-node`。
4. 触发 `reconcile_state`。

验收：

- 节点进入 `offline`。
- 恢复后重新进入 `healthy` 或 `degraded`。
- session 状态和节点本地 tmux/container 一致。

### 6.13 设备撤销

目标：

- 禁用设备后，CLI token、WireGuard peer、SSH key 同步失效。

步骤：

1. 管理端禁用某个设备。
2. CLI 继续尝试 `fclaude`。
3. 检查 WireGuard 和 SSH 可用性。

验收：

- CLI token 不可用。
- WireGuard peer 被撤销。
- SSH key 被节点移除。
- 相关操作写入审计日志。

## 7. 部署文档大纲

### 7.1 前置要求

- 一台控制面服务器。
- 一台或多台 VPS 节点。
- 域名和 HTTPS。
- Docker 和 Docker Compose。
- PostgreSQL 和 Redis 由 Compose 提供。
- 节点需要 Docker Engine、OpenSSH server 和 TUN/WireGuard 内核能力。
- 节点端 tmux、Mutagen、WireGuard helper 等由 `agent-remote-node` 发布包或安装器托管。
- 节点端浏览器运行时镜像和 noVNC/websockify 或后续 WebRTC 组件由 `agent-remote-node` 发布包、安装器或受控镜像托管。
- 本地客户端为 macOS 或 Linux。
- 本地客户端不要求用户手动安装 Mutagen 或 WireGuard；由 `agent-remote-cli` 托管。

### 7.2 控制面部署

1. 下载 `agent-remote-server`、`agent-remote-admin-web` 和 Compose 文件。
2. 创建 `.env`。
3. 设置 `AGENT_REMOTE_SECRET_KEY`。
4. 设置 `PUBLIC_BASE_URL`。
5. 启动 Docker Compose。
6. 执行数据库迁移。
7. 创建第一个管理员。
8. 登录管理端。

### 7.3 反向代理与 HTTPS

推荐 Caddy：

```text
agent.example.com {
  reverse_proxy agent-remote-server:8000
}
```

也可使用 Nginx。部署文档应说明：

- Web/API 路由。
- 静态前端托管。
- HTTPS 证书。
- 上传大小限制。
- 超时设置。

### 7.4 节点端部署

1. 安装或检查系统级依赖：Docker Engine、OpenSSH server、TUN/WireGuard 能力。
2. 下载 `agent-remote-node`。
3. 运行节点安装器，准备受控 tmux、Mutagen、WireGuard helper 等依赖。
4. 创建 `/etc/agent-remote/node.toml`。
5. 在管理端创建节点并获取注册 token。
6. 运行节点注册命令。
7. 安装 systemd service。
8. 启动节点服务。
9. 在管理端确认节点健康。

### 7.5 WireGuard 配置

文档应说明：

- 管理端如何分配 peer。
- 节点 peer 如何生成。
- 用户设备 peer 如何生成。
- 如何撤销设备 peer。
- 防火墙建议。

### 7.6 SSH forced command 配置

文档应说明：

- 节点 Linux 用户建议为 `agent-remote`。
- `authorized_keys` 由节点端管理。
- 用户不得手工编辑受控段。
- `agent-remote-attach` 如何校验 session。

### 7.7 Claude 工具镜像

文档应说明：

- Claude 基础镜像构建方式。
- 非 root 用户。
- 默认工作目录。
- 配置目录挂载。
- 时区和 locale 注入。
- 资源限制。

### 7.8 远端浏览器运行时

文档应说明：

- 浏览器镜像构建方式。
- Chromium 版本和依赖固定方式。
- noVNC/websockify 或 WebRTC 组件的受控版本。
- 无痕 profile 和临时目录清理策略。
- 时区、locale、浏览器语言和字体包配置。
- 网络策略，包括禁止访问 metadata 地址和不必要内网段。
- 管理端短期 `embed_url` 签发和过期策略。

### 7.9 本地 CLI 安装

文档应说明：

- macOS 安装。
- Linux 安装。
- `agent-remote login`。
- `agent-remote setup network`。
- `agent-remote doctor`。
- CLI 托管 Mutagen 和 WireGuard helper。
- WireGuard 需要系统网络权限时的授权流程。
- `fclaude` 基础使用。
- keychain/libsecret 要求。

### 7.10 首个 Claude 账户绑定

文档应说明：

- 管理端创建账户。
- CLI 创建账户。
- 远端临时绑定 session。
- 执行 `claude login`。
- verifier 成功后的状态。

### 7.11 常见故障排查

必须覆盖：

- 管理端无法连接数据库。
- Redis 不可用。
- 节点无法注册。
- 节点心跳超时。
- WireGuard 不可达。
- SSH forced command 失败。
- Mutagen 冲突。
- Claude 登录态过期。
- session 无法恢复。
- 远端浏览器无法启动、无法连接、TTL 过期或出口环境不匹配。

### 7.12 备份与恢复

文档必须强调：

- 必须备份 PostgreSQL。
- 必须备份 `AGENT_REMOTE_SECRET_KEY`。
- 必须备份节点 `node.secret`。
- 主密钥丢失后无法恢复已加密登录态。
- 节点本地账户目录需要按策略备份。

### 7.13 升级

文档应说明：

- 控制面升级顺序。
- 数据库迁移。
- 节点端滚动升级。
- CLI 版本兼容。
- 协议版本检查。
