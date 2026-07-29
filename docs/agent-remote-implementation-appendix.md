# agent-remote 实施级附录

## 1. CLI 命令规范草案

### 1.1 `agent-remote`

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
agent-remote account import-config --tool claude --account <account_id>
agent-remote account import-config --tool claude --account <account_id> --include-resume-history
agent-remote account export-config --tool claude --account <account_id>
agent-remote account disable <account_id>

agent-remote credentials list
agent-remote credentials create --name personal
agent-remote credentials bind --account <account_id> --profile <profile_id>
agent-remote credentials unbind --account <account_id>

agent-remote sync status
agent-remote sync pause
agent-remote sync resume
agent-remote sync resolve
agent-remote sync reset
agent-remote sync git enable
agent-remote sync git disable
agent-remote sync git check

agent-remote forward <remote_port> --session <session_id>
agent-remote forward <remote_port> --session <session_id> --local-port auto --open
agent-remote forward list
agent-remote forward stop <forward_id>
```

### 1.2 `fclaude`

```text
fclaude
fclaude new
fclaude list
fclaude list --all
fclaude attach <session_id>
fclaude stop <session_id>
fclaude forward <remote_port>
fclaude forward <remote_port> --local-port auto --open
fclaude forward list
fclaude forward stop <forward_id>
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
- `fclaude new` 复用当前项目已有 workspace 同步关系，只创建新的工具 session。
- 同一 workspace 的多个 Claude session 挂载同一个远端项目目录。
- 同一 Claude 账户的多个 session 挂载同一个远端账户配置目录。
- `forward` 为指定 session 创建受控的 runtime loopback 端口隧道，不启用 OpenSSH 标准 TCP forwarding；完整规范见 `docs/session-port-forwarding-design.md`。

## 2. 数据库字段草案

字段类型以 PostgreSQL 为准，具体长度可在迁移实现时调整。

### 2.1 `users`

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

### 2.2 `user_devices`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| user_id | uuid | FK users |
| name | text | 设备名 |
| platform | text | `macos` / `linux` |
| status | text | `active` / `revoked` |
| last_seen_at | timestamptz | 最近使用 |
| created_at | timestamptz | 创建时间 |

### 2.3 `tool_accounts`

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

### 2.3.1 `developer_credential_profiles`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| user_id | uuid | FK users |
| display_name | text | 显示名 |
| status | text | `active` / `disabled` |
| git_identity | jsonb | 非敏感 git identity 和安全配置 |
| github_cli_mode | text | `remote_login` / `import_token` / `disabled` |
| ssh_mode | text | `agent_forwarding` / `deploy_key` / `disabled` |
| secret_ref | text | 加密凭据引用，不直接暴露 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 2.3.2 `tool_account_developer_credential_profiles`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| tool_account_id | uuid | FK tool_accounts |
| developer_credential_profile_id | uuid | FK developer_credential_profiles |
| created_at | timestamptz | 创建时间 |

### 2.4 `tool_account_profiles`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid | 主键 |
| tool_account_id | uuid | FK tool_accounts |
| tool_type | text | 工具类型 |
| profile_json | jsonb | 非敏感 profile |
| encrypted_secrets | bytea | 加密敏感字段 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

### 2.5 `nodes`

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

### 2.6 `node_tasks`

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

### 2.7 `sessions`

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

### 2.8 `browser_sessions`

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

### 2.9 推荐索引

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

### 2.10 `port_forwards`

Session 端口转发需要新增 `port_forwards` 持久化实体以及 Redis 中的一次性 connection token 和短期 authorization lease。字段、索引、状态机、API 和不落盘敏感数据约束以 `docs/session-port-forwarding-design.md` 为准，避免在两处维护可漂移的协议副本。

## 3. 部署文档大纲

### 3.1 前置要求

- 一台控制面服务器。
- 一台或多台 VPS 节点。
- 域名和 HTTPS。
- 控制面需要 Docker 和 Docker Compose。
- PostgreSQL 和 Redis 由 Compose 提供。
- Native 节点使用 Debian/Ubuntu、systemd、cgroup v2，以及支持 user/mount/network namespace 的 Linux 内核；不要求 KVM 或 Docker。
- 节点端 OpenSSH、tmux、Bubblewrap、nftables、iproute2、ACL、locale、Claude、Mutagen 和 WireGuard helper 等由 `agent-remote-node` 发布包或安装器托管。
- Docker Engine 仅在节点显式启用 Docker Sandbox 兼容 backend 时需要。
- 节点端浏览器运行时镜像和 noVNC/websockify 或后续 WebRTC 组件由 `agent-remote-node` 发布包、安装器或受控镜像托管。
- 本地客户端为 macOS 或 Linux。
- 本地客户端不要求用户手动安装 Mutagen 或 WireGuard；由 `agent-remote-cli` 托管。

### 3.2 控制面部署

1. 下载 `agent-remote-server`、`agent-remote-admin-web` 和 Compose 文件。
2. 创建 `.env`。
3. 设置 `AGENT_REMOTE_SECRET_KEY`。
4. 设置 `PUBLIC_BASE_URL`。
5. 启动 Docker Compose。
6. 执行数据库迁移。
7. 创建第一个管理员。
8. 登录管理端。

### 3.3 反向代理与 HTTPS

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

### 3.4 节点端部署

1. 在管理端创建节点，配置 backend 策略并获取注册 token。
2. 在 VPS 上执行发布页提供的一键安装命令，传入控制面 URL、节点 ID 和注册 token。
3. 安装器校验平台、安装依赖与受控 Claude、写入配置和 sudoers，并启动 `agent-remote-node`、`agent-remote-runtime`。
4. 在管理端确认节点健康、runtime probe 正常且所需 backend 可调度。
5. 升级或修复时重复运行同一命令；安装流程保持幂等并复用已有注册信息。

### 3.5 WireGuard 配置

文档应说明：

- 管理端如何分配 peer。
- 节点 peer 如何生成。
- 用户设备 peer 如何生成。
- 如何撤销设备 peer。
- 防火墙建议。

### 3.6 SSH forced command 配置

文档应说明：

- 节点 Linux 用户建议为 `agent-remote`。
- `authorized_keys` 由节点端管理。
- 用户不得手工编辑受控段。
- `agent-remote-attach` 如何校验 session。

### 3.7 Claude Runtime

文档应说明：

- Native Runtime 使用安装器固定并校验的 Claude 可执行文件。
- 每个账户使用独立 Linux UID/GID、home、workspace 和配置目录。
- Bubblewrap、cgroup v2、network namespace 与 nftables 的隔离边界。
- 时区、locale、DNS/出口策略和资源限制的注入方式。
- 特权 runtime helper 与非特权 worker 的调用边界及 sudoers 白名单。
- Docker Sandbox 作为显式启用的兼容 backend，使用固定镜像和同等控制面状态机。

### 3.8 远端浏览器运行时

文档应说明：

- 浏览器镜像构建方式。
- Chromium 版本和依赖固定方式。
- noVNC/websockify 或 WebRTC 组件的受控版本。
- 无痕 profile 和临时目录清理策略。
- 时区、locale、浏览器语言和字体包配置。
- 网络策略，包括禁止访问 metadata 地址和不必要内网段。
- 管理端短期 `embed_url` 签发和过期策略。

### 3.9 本地 CLI 安装

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

### 3.10 首个 Claude 账户绑定

文档应说明：

- 管理端创建账户。
- CLI 创建账户。
- 远端临时绑定 session。
- 执行 `claude login`。
- verifier 成功后的状态。

### 3.11 常见故障排查

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

### 3.12 备份与恢复

文档必须强调：

- 必须备份 PostgreSQL。
- 必须备份 `AGENT_REMOTE_SECRET_KEY`。
- 必须备份节点 `node.secret`。
- 主密钥丢失后无法恢复已加密登录态。
- 节点本地账户目录需要按策略备份。

### 3.13 升级

文档应说明：

- 控制面升级顺序。
- 数据库迁移。
- 节点端滚动升级。
- CLI 版本兼容。
- 协议版本检查。
