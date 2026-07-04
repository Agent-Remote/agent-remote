# agent-remote 远端 AI Agent 运行平台方案

## 1. 项目目标

本项目用于将 Claude 等 AI Agent 工具运行在 VPS 等国外可信环境中，通过可控的网络、时区、系统环境和命令执行环境，满足工具自身的地区限制要求，同时让本地用户获得接近原生命令行的使用体验。

项目性质为开源自部署项目，主要面向个人用户和小团队内部使用，不按大型商业多租户 SaaS 的复杂度设计。系统仍需要具备基础的多用户隔离、权限控制、审计和节点管理能力，但优先保证部署简单、依赖清晰、可维护性强。

项目名称为 `agent-remote`。本地统一配置、登录、设备、同步和账户管理命令使用 `agent-remote`；具体 AI Agent 的启动命令按工具拆分，例如 Claude 使用 `fclaude`，后续 Codex 可使用 `fcodex`。

用户在本地执行类似 `fclaude` 的工具启动命令后，系统应自动完成以下动作：

1. 选择合适的远端 VPS 节点。
2. 建立或复用本地到远端的 WireGuard 隧道。
3. 准备远端 Docker sandbox 运行环境。
4. 同步项目文件、工具配置、skills、插件、记忆等状态。
5. 通过 SSH 连接到远端 tmux session。
6. 在 tmux 中启动或恢复目标工具 shell。

最终体验目标是：用户像在本机打开 `claude` 一样使用 `fclaude`，但实际 Claude 运行在合规的远端环境中；后续支持其他工具时，也应保持类似体验，例如通过 `fcodex` 使用远端 Codex。

## 2. 已确定约束

- 项目性质：开源自部署。
- 项目名称：`agent-remote`。
- 项目许可证：所有仓库统一使用 `GPL-3.0-only`。
- 本地统一管理命令：`agent-remote`。
- Claude 专用启动命令：`fclaude`。
- 后续工具启动命令按工具扩展，例如 `fcodex`。
- 目标用户：个人用户和小团队。
- 管理端用户角色：管理员和普通用户。
- 远端用户隔离：所有 agent-remote 用户共用节点上的同一个 Linux 系统用户，通过 Docker sandbox、目录规范和应用层权限做隔离。
- 文件同步范围：默认只同步用户当前 workspace，额外路径必须显式配置；不得默认同步用户 home、磁盘根目录或其他大范围目录。
- session 恢复范围：工具启动命令默认只恢复当前启动路径对应项目和工具类型的最近可用 session。
- 本地与服务器隧道：WireGuard。
- WireGuard 拓扑：本地设备和 VPS 节点均作为 peer，由管理端生成、分发和撤销配置。
- 文件同步：Mutagen。
- 外部依赖策略：各端发布包应内置或托管运行所需外部程序，避免用户手动安装和自行处理版本兼容。
- 第三方许可证策略：WireGuard、Mutagen 等托管或内置外部程序必须在发布产物中标明实际 artifact 的许可证、来源、版本和 checksum。
- 管理端与节点端通信：节点端主动连接管理端，管理端不要求节点暴露公网 API 端口。
- 远端长期 shell：tmux。
- 远程交互：SSH 直连 tmux，尽量减少 Claude 上方的中间层。
- SSH 认证：使用设备级 SSH key，并通过受控入口脚本限制可执行动作。
- CLI 参数策略：`agent-remote` 负责统一管理操作；工具启动命令只消费明确的 session 命令，其余参数默认透传给远端原生工具。
- 终端入口：首期不做 Web 终端，只支持本地 CLI + SSH + tmux。
- 远端临时浏览器：管理端需要支持创建短期无痕浏览器会话，通过 VPS 节点网络、地区、时区和 locale 访问邮箱、Claude Web 等页面；该能力不持久化浏览器用户信息，也不作为 Web 终端使用。
- 工具运行隔离：Docker sandbox。
- 用户端语言：Rust。
- 用户端本地数据库：如需要，使用 SQLite。
- 用户端首期支持平台：macOS + Linux。
- 管理端语言：Python。
- 安全模型：自部署可信管理员 + 基础安全加固，不按商业 SaaS 强多租户模型设计。
- 首期主要支持 Claude，后续需要支持其他 AI Agent 工具。
- 支持多用户。
- 支持单用户多个工具账户。
- 支持多 VPS 节点和自动分流。

## 3. 推荐技术选型

### 3.1 用户端

- 语言：Rust。
- 首期平台：macOS + Linux。
- CLI 框架：`clap`。
- 本地状态：SQLite，建议使用 `sqlx` 或 `rusqlite`。
- 配置格式：TOML 或 YAML，优先 TOML。
- SSH 调用：首期优先调用系统 `ssh`，避免重新实现终端兼容细节。
- 外部依赖：`agent-remote-cli` 必须内置或托管安装 WireGuard、Mutagen 等运行依赖，不要求用户手动安装。
- WireGuard 控制：由 CLI 调用随包携带的 WireGuard helper 或受控安装的 WireGuard 组件；必要时请求系统授权或提权。
- Mutagen 控制：由 CLI 调用随包携带的固定版本 Mutagen binary。

### 3.2 管理端

- 语言：Python。
- Web 框架：FastAPI。
- ORM / 迁移：SQLAlchemy 2.x + Alembic。
- 任务队列：Celery / Dramatiq / RQ 三选一，首选 Dramatiq 或 RQ，复杂调度再引入 Celery。
- 管理端数据库：PostgreSQL。
- 缓存、锁与任务状态：Redis，MVP 必须依赖。

选择 PostgreSQL 的原因：

- 多用户、多账户、多节点、审计日志、配额、会话状态都属于关系型数据。
- 后续需要报表、查询、约束和事务一致性。
- 比 SQLite 更适合作为中心管理端数据库。

### 3.3 节点端

推荐语言：Go。

原因：

- 适合部署为单文件静态二进制。
- 对 Docker、网络、进程、SSH、系统服务管理等运维场景生态成熟。
- 并发模型适合管理多个 sandbox、tmux session 和同步任务。
- 相比 Rust，节点端迭代和运维开发成本更低。

节点端职责应尽量保持清晰：只负责本节点资源、容器、session、账号运行环境和健康上报，不直接承担中心管理业务。

### 3.4 管理端前端

推荐语言与框架：TypeScript + React + Vite。

推荐组件方案：

- UI：shadcn/ui + Tailwind CSS。
- 数据请求：TanStack Query。
- 表格：TanStack Table。
- 路由：TanStack Router 或 React Router。

原因：

- 后台管理系统需要表格、筛选、表单、详情页、状态监控，React 生态成熟。
- shadcn/ui 适合构建现代管理端，同时可控性强。
- Vite 足够轻量，适合独立管理前端仓库。

## 4. 仓库拆分

建议至少拆分为以下仓库：

1. `agent-remote-cli`
   - Rust 用户端。
   - 提供 `agent-remote` 统一管理命令。
   - 提供 `fclaude` Claude 专用启动命令。
   - 后续可提供 `fcodex` 等其他工具启动命令。
   - 负责本地配置、本地凭证、WireGuard/Mutagen/SSH 编排。

2. `agent-remote-server`
   - Python 管理端 API。
   - 负责用户、角色、权限、节点、用户自有工具账户、策略、审计、调度。

3. `agent-remote-admin-web`
   - TypeScript + React 管理前端。
   - 供管理员管理系统资源，也供普通用户自助绑定和管理自己的工具账户。

4. `agent-remote-node`
   - Go 节点端 Agent。
   - 部署在各个 VPS 节点。
   - 负责 Docker sandbox、tmux session、节点心跳、资源上报、节点本地账号环境管理。

5. `agent-remote-protocol`
   - 可选。
   - 放置 OpenAPI schema、共享协议、事件定义、错误码、配置规范。
   - 如果团队规模较小，初期可并入 `agent-remote-server`，等协议稳定后再拆。

## 5. 核心运行链路草案

### 5.1 首次使用

1. 用户安装 `agent-remote-cli`，获得 `agent-remote` 和 `fclaude` 命令。
2. 用户执行 `agent-remote login`。
3. CLI 调用管理端完成认证。
4. CLI 获取用户可用节点、WireGuard 配置、同步策略和可用工具账户列表。
5. CLI 初始化本地 SQLite 和配置目录。
6. CLI 建立 WireGuard 隧道。
7. CLI 为当前 workspace 创建 Mutagen 同步 session。
8. CLI 请求管理端分配一个节点和 Claude 运行实例。
9. 管理端调度节点端创建 Docker sandbox 和 tmux session。
10. CLI 通过 SSH 连接到该 tmux session。
11. 用户进入 Claude 原生命令行体验。

### 5.2 再次进入

1. 用户执行 `fclaude`。
2. CLI 根据当前启动路径计算项目 key。
3. CLI 检查本地状态、WireGuard、Mutagen session。
4. CLI 查询管理端确认该项目最近可用 session 是否仍可恢复。
5. 若可恢复，直接 SSH attach 到远端 tmux。
6. 若不可恢复，按策略为该项目创建新 session。

### 5.3 终端接入方式

首期不计划提供 Web 终端。

实际进入 Claude session 的方式固定为：

```text
local fclaude launcher -> ssh -> remote tmux -> docker sandbox -> claude
```

管理端前端只负责展示：

- session 状态。
- 所属用户和工具账户。
- 所在节点。
- tmux/session 标识。
- 推荐连接命令。
- 异常状态和清理操作。

不在管理端前端中直接承载交互式终端，避免引入 WebSocket 终端代理、浏览器兼容、安全暴露面、审计和权限穿透等复杂度。

### 5.4 网络中断恢复

1. 本地 SSH 断开不代表远端 Claude 停止。
2. Claude 仍运行在远端 tmux session 中。
3. 用户在同一项目路径重新执行 `fclaude` 后，默认优先恢复该项目最近活跃 session。
4. 如检测到 Mutagen 或 WireGuard 异常，CLI 先修复隧道与同步，再 attach。

### 5.5 工具账户绑定

工具账户绑定采用通用远端交互式登录状态机。Claude 是首期实现。

1. 普通用户在管理端创建工具账户绑定请求，选择 `tool_type`。
2. 管理端选择一个可用节点，创建临时绑定任务。
3. 节点端创建临时 Docker sandbox 和临时 tmux session。
4. 用户通过 CLI 或管理端提供的连接指令进入该临时 session。
5. 用户在远端环境内执行目标工具的登录命令，例如 Claude 使用 `claude login`。
6. 节点端通过该工具的 verifier 检测登录是否完成。
7. 节点端将生成的工具配置、登录态、必要缓存归档到该用户的账户目录。
8. 管理端将该工具账户状态标记为 `active`。
9. 临时绑定 sandbox 和 tmux session 被销毁。

该方案确保工具登录态产生在实际运行地区和实际网络环境中，避免本地地区、浏览器、系统环境影响登录结果。

### 5.6 远端临时浏览器

管理端需要提供内嵌远端浏览器能力，用于用户在 VPS 网络和系统环境中临时访问网页，例如邮箱验证码、Claude Web 页面、账号安全确认页面等。

该能力的定位：

- 它是远端临时浏览器，不是 Web 终端。
- 浏览器运行在目标 VPS 节点上的独立 Docker sandbox 中。
- 管理端前端只嵌入浏览器画面和输入通道，不暴露宿主 shell。
- 浏览器会话默认无痕、短时、一次性。
- 默认不持久化 cookie、localStorage、浏览历史、密码、下载文件和浏览器 profile。
- 会话结束后销毁容器和临时目录。

创建流程：

1. 用户在管理端选择创建浏览器会话。
2. 用户可选择目标工具账户、地区、节点或目标 URL。
3. 管理端根据工具账户地区、时区、locale 和节点亲和规则选择节点。
4. 管理端创建 `create_browser_session` 节点任务。
5. 节点端启动专用浏览器容器，注入时区、locale、浏览器语言和网络策略。
6. 节点端返回一次性连接信息。
7. 管理端前端在页面中嵌入该浏览器会话。
8. 用户关闭或 TTL 到期后，管理端创建 `stop_browser_session` 任务并清理资源。

推荐实现：

- 浏览器运行时使用独立镜像，例如 `agent-remote/browser:latest`。
- 首期可选择 Chromium + noVNC/websockify，后续可评估 WebRTC 低延迟方案。
- 连接端点必须由管理端签发短期 token，禁止节点直接暴露公开访问入口。
- 浏览器容器不挂载用户 workspace 和工具账户目录。
- 如需要打开 Claude Web，默认只打开页面，不读取或保存 Claude CLI 账户目录。

网络与检测规避要求：

- 浏览器流量必须从目标 VPS 节点出口发出。
- `timezone`、`locale`、浏览器语言、默认地区应与工具账户或用户选择的地区一致。
- 同一工具账户发起浏览器会话时，优先使用该账户的 `affinity_node_id`，避免同一账户在不同出口 IP 间频繁切换。
- 浏览器会话可以绑定 `tool_account_id`，但不自动复用工具账户登录态。

安全边界：

- 默认阻断访问控制面内网、节点本机管理端口、云厂商 metadata 地址和 WireGuard 管理网段中不必要的目标。
- 默认禁用持久下载目录；如后续支持下载，必须进入专门的临时文件区并由用户显式导出。
- 日志只记录会话生命周期、目标域名摘要、节点和用户，不记录页面内容、输入内容、cookie、token 或截图。
- 管理员可以强制停止任意异常浏览器会话。

## 6. 初始架构边界

### 6.1 用户隔离模型

项目首期采用轻量隔离模型：

- 每个 VPS 节点只要求准备一个运行 agent-remote-node 的 Linux 用户。
- 所有 agent-remote 用户共享这个宿主 Linux 用户。
- 每个 agent-remote 用户在节点上拥有独立的数据根目录。
- 每个工具 session 运行在独立 Docker sandbox 中。
- tmux session、workspace、工具配置目录、Mutagen 同步目录都按用户 ID、账户 ID、session ID 分层命名。
- 管理端负责校验用户只能访问自己的 session、账号和同步目录。

建议节点目录结构：

```text
/var/lib/agent-remote/
  users/
    {user_id}/
      accounts/
        {account_id}/
          claude-config/
          claude-home/
      workspaces/
        {workspace_id}/
      sessions/
        {session_id}/
          runtime/
          logs/
          tmux/
```

该模型的边界：

- 适合个人和小团队自部署。
- 不提供强商业多租户隔离。
- 节点管理员天然可以访问节点上的所有用户数据。
- 如果不同用户之间存在强不信任关系，后续应提供“每用户独立 Linux 用户”作为增强模式。

配套限制：

- Docker 容器默认不以 privileged 模式运行。
- 容器内用户应使用非 root 用户。
- 容器挂载目录必须限制在该 session 所需 workspace 和配置目录。
- 节点端不得接受 CLI 直接传来的任意宿主路径。
- session 创建、恢复、终止必须经过管理端授权。

### 6.2 管理端角色模型

管理端首期包含两类用户：

1. 管理员
   - 管理 VPS 节点。
   - 管理系统配置和默认策略。
   - 管理普通用户启用、禁用、配额和权限。
   - 查看全局 session 状态、节点健康和审计日志。
   - 可在必要时协助清理异常 session 和同步任务。

2. 普通用户
   - 登录管理端查看自己的状态。
   - 创建、绑定、禁用和删除自己的工具账户配置。
   - 查看自己的 session、workspace、同步状态和使用记录。
   - 配置自己的默认工具账户、默认 workspace 和启动偏好。
   - 不能访问其他用户的账户、配置、文件和 session。

用户注册建议：

- 自部署默认采用“管理员创建用户”或“管理员邀请注册”。
- 可提供开放注册开关，但默认关闭，避免管理端暴露到公网后被滥用。
- 首次部署时通过 bootstrap 命令创建第一个管理员。

### 6.3 认证模型

管理端首期采用用户名/密码认证，不引入 OAuth、SSO 或企业身份系统。

用户认证：

- 用户使用用户名/密码登录管理端。
- 密码使用 Argon2id 哈希存储。
- 支持 TOTP 二步验证，首期可作为可选功能。
- 默认关闭开放注册。
- 首个管理员通过 bootstrap 命令创建。

CLI 认证：

- `agent-remote login` 引导用户完成登录。
- 首期可采用网页登录后生成 CLI token，或 device code 流程。
- CLI token 绑定用户和设备。
- CLI token 应可撤销、可过期、可轮换。
- 用户登出或设备禁用时，撤销对应 CLI token、WireGuard peer 和 SSH key。

会话与 token：

- 管理端 Web session 应设置合理过期时间。
- CLI token 应只具备 CLI 所需权限。
- 节点 token 与用户 token 分离。
- token 不应明文记录到日志。

暂不做：

- OAuth 登录。
- SAML / OIDC SSO。
- 企业目录同步。
- 第三方身份提供商。

### 6.4 安全模型

项目按开源自部署、小团队可信管理员场景设计。

安全原则：

- 管理员默认可信。
- 普通用户之间通过应用层权限、Docker sandbox 和目录规范隔离。
- 不承诺商业 SaaS 级别的强多租户隔离。
- 节点管理员天然可以访问节点上的所有用户数据。
- 管理端是唯一控制面，节点端只信任管理端下发的任务。
- CLI 不直接在节点上创建 Docker 容器、tmux session 或宿主目录。

敏感数据：

- Claude 登录态、cookies、tokens 必须加密落盘。
- WireGuard 私钥、SSH 凭证、API token 必须加密落盘。
- 管理端数据库中的敏感字段应使用应用层加密。
- 节点端本地敏感文件应限制文件权限。
- 日志中不得输出 token、cookie、私钥和完整登录态路径。

密钥管理：

- 管理端通过 `AGENT_REMOTE_SECRET_KEY` 提供应用层加密主密钥。
- 管理端敏感字段使用该主密钥派生出的数据加密密钥加密。
- 首期可直接使用应用层对称加密，后续再演进到 envelope encryption。
- 节点端使用独立 node secret 加密本地敏感文件。
- node secret 可以由管理端下发，也可以在节点注册时生成后安全保存。
- 部署文档必须要求管理员备份 `AGENT_REMOTE_SECRET_KEY` 和节点 secret。
- 主密钥丢失后，已保存的 Claude 登录态、token 和其他加密数据将无法恢复。
- 首期不接入 KMS、Vault 或云厂商密钥管理服务。

访问控制：

- 默认关闭开放注册。
- 管理员创建用户或邀请用户。
- 普通用户只能访问自己的工具账户、workspace、session 和同步状态。
- 管理员可以管理节点、用户、策略和异常 session，但默认不提供读取用户明文登录态的功能。
- 所有资源创建、恢复、终止操作都需要管理端鉴权。

审计：

- 登录、登出、token 刷新。
- 工具账户绑定、禁用、删除。
- session 创建、恢复、终止。
- 节点注册、禁用、维护状态变更。
- 管理员操作。
- 同步异常和恢复动作。

### 6.5 工具账户模型

工具账户归普通用户所有，不作为全局共享账号池优先设计。Claude 是首期支持的工具类型，但核心数据模型必须支持后续扩展到 Codex 等其他 AI Agent。

核心关系：

```text
User
  -> ToolAccount
       -> ToolAccountProfile
       -> ToolRuntimeProfile
       -> Session
```

核心字段：

- `tool_type`：工具类型，例如 `claude`、`codex`。
- `display_name`：用户自定义账户名称。
- `owner_user_id`：账户所属用户。
- `region_code`：账户所属地区。
- `timezone`：容器默认时区。
- `locale`：容器默认 locale。
- `preferred_node_tags`：节点标签偏好。
- `affinity_node_id`：账户当前亲和节点。
- `status`：账户状态。

设计规则：

- 一个普通用户可以绑定多个工具账户。
- 每个工具账户拥有独立的远端配置目录和登录态目录。
- 启动 `fclaude` 时只能选择 `tool_type=claude` 的账户。
- 后续启动 `fcodex` 时只能选择 `tool_type=codex` 的账户。
- 管理员可以看到账号的存在、所属用户、状态和占用情况，但不应默认读取明文登录态。
- 账号登录态、cookies、tokens、工具配置等敏感数据需要在服务端或节点端加密落盘。
- 工具配置、skills、插件、记忆、登录态等账户配置数据以远端账户目录为权威来源。
- 本地 CLI 只保存必要索引、缓存和可选备份，不默认用本地配置覆盖远端账户目录。
- 同一个工具账户允许同时启动多个 session。
- 同一个工具账户的所有活跃 session 必须运行在同一台 VPS 节点上，确保出口 IP 一致。
- 工具账户应记录 `affinity_node_id`，用于约束并发 session 的调度位置。
- 工具账户应配置所属地区，用于匹配节点地区、出口 IP、容器时区和 locale。

工具特有 profile：

- Claude 特有字段放入 `ClaudeAccountProfile`。
- Codex 特有字段后续放入 `CodexAccountProfile`。
- 核心调度、设备、workspace、session 表只依赖 `ToolAccount` 和 `tool_type`，不直接依赖 Claude 专用字段。

账户地区配置建议字段：

- `region_code`：账户所属地区，例如 `US`、`JP`、`SG`。
- `timezone`：容器默认时区，例如 `America/Los_Angeles`。
- `locale`：容器默认 locale，例如 `en_US.UTF-8`。
- `preferred_node_tags`：可选，匹配具有指定地区或线路标签的节点。
- `affinity_node_id`：账户当前亲和节点，用于保证多开时出口 IP 一致。

绑定状态机：

- `binding_requested`：用户已创建绑定请求。
- `binding_session_starting`：管理端正在调度节点并创建临时绑定 session。
- `binding_waiting_user_login`：临时 session 已就绪，等待用户完成工具登录。
- `binding_verifying`：节点端正在执行工具 verifier。
- `active`：绑定成功，可用于启动 session。
- `expired`：登录态失效，需要重新绑定。
- `disabled`：用户或管理员禁用。
- `failed`：绑定失败，需要用户重试或查看错误。
- `node_unavailable`：账户亲和节点不可用，暂时无法为该账户创建或恢复 session。

状态流转：

```text
binding_requested
  -> binding_session_starting
  -> binding_waiting_user_login
  -> binding_verifying
  -> active

binding_verifying -> failed
active -> expired
active -> disabled
active -> node_unavailable
node_unavailable -> active
```

工具 verifier：

- 每个 `tool_type` 必须提供自己的登录态 verifier。
- Claude verifier 负责检测 `claude login` 后配置、登录态和必要缓存是否生成。
- 后续 Codex verifier 负责检测 Codex 自身登录态。
- verifier 只返回状态、错误摘要和必要元数据，不应把敏感 token 写入日志。

运行状态：

- `active`：可用于启动 session。
- `disabled`：用户或管理员禁用。
- `expired`：登录态失效，需要重新绑定。
- `node_unavailable`：账户亲和节点不可用，暂时无法为该账户创建或恢复 session。

账户并发规则：

- 同一账户可以多开多个 session。
- 如果该账户已有活跃 session，新 session 必须调度到已有 session 所在节点。
- 如果该账户没有活跃 session，优先调度到该账户的 `affinity_node_id`。
- 如果 `affinity_node_id` 不可用，默认不自动切换节点，避免登录态和出口 IP 突然变化。
- 如用户或管理员需要切换账户节点，应提供显式的账户迁移或重新绑定流程。

### 6.6 账户配置同步模型

账户配置数据独立于 workspace 文件同步，远端账户目录是权威来源。

账户配置数据包括：

- 工具登录态。
- 工具 CLI 配置。
- skills。
- 插件。
- 记忆。
- 与具体工具账户绑定的必要缓存和状态。

运行时规则：

- 账户绑定完成后，节点端将登录态和配置归档到该用户的账户目录。
- 启动工具 session 时，节点端从账户目录注入配置到 Docker sandbox。
- session 运行期间产生的账户配置变更应回写到账户目录。
- 回写可以先采用 session 结束时同步，后续再加入定时快照。
- 本地 CLI 可以拉取账户配置摘要或备份，但不作为默认写入源。
- 如后续支持本地导入配置，必须作为显式高级操作，并提示可能覆盖远端状态。

建议远端目录：

```text
/var/lib/agent-remote/
  users/
    {user_id}/
      accounts/
        {account_id}/
          tool-home/
          tool-config/
          profiles/
          snapshots/
```

### 6.7 Docker sandbox 模型

AI Agent 运行环境使用 Docker sandbox，首期由节点端统一创建和管理。Claude 是首期工具实现，后续工具应复用同一套 sandbox 生命周期。

默认安全边界：

- 容器内使用非 root 用户运行目标工具。
- 不使用 `--privileged`。
- 不挂载宿主机 Docker socket。
- 不允许普通用户任意指定容器镜像。
- 容器镜像由节点端或管理员统一维护。
- 只挂载当前 workspace、账户配置副本和必要缓存目录。
- 不挂载用户 home、节点数据根目录或未授权宿主路径。
- 默认限制 CPU、内存和 PID 数。
- 容器文件系统尽量最小化，运行所需工具通过基础镜像提供。
- 容器默认允许访问外网，出口使用所在 VPS 节点网络。

运行环境配置：

- 容器时区来自工具账户的 `timezone` 配置。
- 容器 locale 来自工具账户的 `locale` 配置。
- 节点调度应优先匹配工具账户的 `region_code` 或 `preferred_node_tags`。
- 容器环境变量由节点端根据工具模板生成，普通用户只能修改允许列表中的变量。
- 工作目录默认为远端 workspace 文件目录。

工具模板：

- 每个 `tool_type` 应定义自己的镜像模板、启动命令、配置注入规则和配置归档规则。
- `claude` 模板负责执行原生 `claude`。
- 后续 `codex` 模板负责执行原生 Codex。
- 工具模板由管理员或节点端版本管理，普通用户不能任意上传执行模板。

挂载建议：

```text
/workspace                -> 当前 workspace
/home/claude/.claude      -> 账户配置副本
/home/claude/.cache       -> session 或账户级缓存
```

资源限制建议：

- CPU：按用户或 session 配额配置。
- 内存：按用户或 session 配额配置。
- PID：设置上限，避免 fork 风险。
- 磁盘：通过 workspace 目录和 Docker 存储清理策略控制。

### 6.8 Workspace 同步模型

文件同步必须采用显式 workspace 模型。

默认规则：

- 用户执行 `fclaude` 时，默认 workspace 为当前命令所在目录。
- CLI 第一次遇到全新 workspace 目录时，必须询问用户是否为该目录创建同步关系。
- 用户确认后，CLI 才能创建 workspace 记录和 Mutagen 同步 session。
- 用户拒绝后，CLI 不应启动会修改该目录的远端工具 session，除非用户显式使用只读或无同步模式。
- 用户可以通过 `fclaude --workspace /path/to/project` 指定 workspace。
- 用户可以在本地配置文件中声明额外 include/exclude 规则。
- 系统不得默认同步用户 home、磁盘根目录、父级大目录或未声明路径。
- 工具配置、skills、插件、记忆、登录态等数据不混入 workspace 同步，统一走账户配置同步和注入逻辑。

推荐本地配置示例：

```toml
[workspace]
path = "."

include = [
  ".",
]

exclude = [
  ".git",
  "node_modules",
  "target",
  "dist",
  ".venv",
  "__pycache__",
]
```

Mutagen 同步规则：

- 每个 workspace 对应独立 Mutagen session。
- Mutagen session 名称应包含用户 ID、workspace ID、节点 ID 和 session ID。
- 同步模式首期建议使用双向同步。
- 对常见构建产物、依赖目录、缓存目录提供默认 exclude。
- CLI 在 attach tmux 前必须确认同步 session 存在且健康。
- 如果同步异常，CLI 应先提示并尝试修复，再进入工具 session。

冲突处理：

- 出现文件冲突时，不自动覆盖本地或远端任何一端。
- CLI 应清晰提示冲突状态和涉及路径。
- 进入工具 session 前如果存在未解决冲突，默认阻止 attach。
- 用户必须先解决冲突，或显式选择高级覆盖策略。
- 覆盖策略必须是显式命令，不允许静默默认执行。

建议 CLI 命令：

- `agent-remote sync status`
- `agent-remote sync pause`
- `agent-remote sync resume`
- `agent-remote sync resolve`
- `agent-remote sync reset`

远端目录建议：

```text
 /var/lib/agent-remote/
  users/
    {user_id}/
      workspaces/
        {workspace_id}/
          files/
```

### 6.9 项目与 session 生命周期模型

session 必须绑定到项目，项目 key 由本地启动路径决定。

项目 key 规则：

- 用户执行 `fclaude` 时，CLI 取当前启动路径作为项目识别来源。
- 启动路径应先转为规范化绝对路径，再生成项目 key。
- 同一用户在同一设备上从同一路径启动，应命中同一个项目。
- 不同路径即使内容相同，也默认视为不同项目。
- 用户通过 `--workspace /path/to/project` 指定 workspace 时，该路径作为项目 key 来源。
- 管理端保存 `project_key`、`workspace_id`、`local_start_path`、`device_id` 和 `user_id` 的关联。

默认恢复规则：

- `fclaude` 无参数时，不恢复全局最近 session。
- `fclaude` 无参数时，只查找当前项目最近可用 session。
- 如果当前项目存在可恢复 session，CLI attach 到该 session。
- 如果当前项目没有可恢复 session，CLI 按策略创建该项目的新 session。
- `fclaude new` 为当前项目创建新 session。
- `fclaude list` 默认只列出当前项目的 session。
- `fclaude list --all` 可列出当前用户全部 session。
- `fclaude attach <session_id>` 可指定恢复某个有权限的 session。
- `fclaude stop <session_id>` 可停止指定 session。

session 状态建议：

- `starting`：正在创建 Docker sandbox 和 tmux。
- `active`：可 attach。
- `detached`：远端仍运行，但当前没有本地 SSH 连接。
- `stopped`：用户主动停止。
- `failed`：创建或运行异常。
- `orphaned`：管理端记录与节点实际状态不一致，等待对账。

空闲策略：

- SSH 断开不停止 session。
- 默认保持 session 长期在线。
- 可提供管理员配置项，用于限制最大空闲时间、最大运行时间和异常清理策略。
- 用户可以主动停止自己的 session。
- 管理员可以清理异常 session。

### 6.10 CLI 命令与工具启动模型

本地 CLI 包含两类命令：

1. `agent-remote`
   - 统一管理命令。
   - 负责登录、登出、设备、同步、账户、诊断等与具体工具无关的操作。

2. `fclaude`
   - Claude 专用启动命令。
   - 负责当前项目的 Claude session 创建、恢复、attach 和 Claude 参数透传。
   - 后续支持 Codex 时，应新增 `fcodex`，而不是把 Codex 逻辑塞进 `fclaude`。

`fclaude` 必须尽量保持原生 `claude` 的命令体验。

核心规则：

- `agent-remote` 消费统一管理命令。
- `fclaude` 只消费明确属于 Claude session 生命周期的少量命令。
- 不属于 `fclaude` 的参数、子命令和选项，默认透传给远端原生 `claude`。
- 透传参数必须保持顺序和内容，不应被 CLI 重写。
- `fclaude -- <args>` 强制将 `<args>` 全部透传给远端 `claude`。
- 进入远端 tmux 后，实际执行的仍是原生 `claude`。

首期 `agent-remote` 管理命令建议：

- `agent-remote login`
- `agent-remote logout`
- `agent-remote device ...`
- `agent-remote account ...`
- `agent-remote sync ...`
- `agent-remote doctor`

首期 `fclaude` 命令建议：

- `fclaude`
- `fclaude new`
- `fclaude list`
- `fclaude attach <session_id>`
- `fclaude stop <session_id>`

示例：

```text
agent-remote login
  登录管理端并绑定本地设备

agent-remote sync status
  查看当前 workspace 的同步状态

fclaude
  恢复当前项目最近 Claude session，或创建当前项目 Claude session

fclaude new
  为当前项目创建新的 Claude session

fclaude -- --model opus
  将 --model opus 透传给远端 claude

fclaude --model opus
  如果 --model 不是 fclaude session 参数，也应透传给远端 claude
```

冲突处理：

- 如果未来 Claude 原生命令与 `fclaude` session 命令重名，用户可以通过 `fclaude -- <claude_args>` 强制透传。
- `fclaude` 新增命令时应谨慎，避免占用 Claude 常见命令和参数。
- 跨工具通用管理能力优先放到 `agent-remote`，不要放到 `fclaude`。
- 工具启动命令的管理参数应尽量使用少量稳定名称，例如 `--workspace`、`--account`。

### 6.11 工具扩展模型

agent-remote 的核心架构必须围绕工具扩展点设计，避免把 Claude 写死在控制面、节点端和 CLI 中。

核心抽象：

- `ToolType`：工具类型，例如 `claude`、`codex`。
- `ToolAccount`：通用账户。
- `ToolAccountProfile`：工具特有账户 profile。
- `ToolRuntimeTemplate`：工具运行模板。
- `ToolLauncher`：本地工具启动命令，例如 `fclaude`、`fcodex`。
- `ToolSession`：带 `tool_type` 的运行 session。

每个工具类型需要定义：

- 账户绑定流程。
- 登录态检测方式。
- 登录态 verifier。
- 配置目录结构。
- 配置注入规则。
- 配置归档规则。
- Docker 镜像模板。
- 容器启动命令。
- 默认环境变量。
- 默认 exclude/include 规则补充。
- CLI 启动器名称和参数透传策略。

Claude 首期实现：

- `tool_type = "claude"`。
- 本地启动器：`fclaude`。
- 远端执行命令：原生 `claude`。
- 账户 profile：`ClaudeAccountProfile`。
- 绑定方式：远端临时 sandbox 交互式执行 `claude login`。

未来 Codex 示例：

- `tool_type = "codex"`。
- 本地启动器：`fcodex`。
- 远端执行命令：原生 Codex CLI。
- 账户 profile：`CodexAccountProfile`。
- 绑定方式由 Codex 自身登录机制决定。

禁止事项：

- 管理端核心 session 表不应出现 Claude 专用字段。
- 节点端通用 Docker 生命周期不应依赖 Claude 专用路径。
- CLI 的统一管理命令不应绑定 Claude 语义。
- 新工具不应通过修改 `fclaude` 实现。

### 6.12 CLI 边界

CLI 负责本地编排，不直接做远端资源决策：

- 本地登录与 token 管理。
- 本地配置读取。
- 本地 WireGuard 启停。
- 本地 Mutagen session 管理。
- 调用管理端 API。
- 调用系统 SSH 进入远端 tmux。

### 6.13 CLI 本地状态模型

用户端本地状态由配置文件、SQLite 和系统凭据存储共同组成。

本地目录：

```text
~/.config/agent-remote/
  config.toml
  state.sqlite
  logs/
```

SQLite 保存：

- `device_id`。
- `server_url`。
- 当前登录用户摘要。
- 工具账户索引和默认选择。
- workspace 映射。
- project key 映射。
- Mutagen sync session 映射。
- WireGuard peer 配置引用。
- SSH key 引用。
- 最近 session 索引。

敏感数据规则：

- CLI token 优先保存到系统 keychain/libsecret。
- WireGuard 私钥优先保存到系统 keychain/libsecret。
- SSH 私钥优先保存到系统 keychain/libsecret 或系统 SSH agent 管理位置。
- SQLite 默认只保存敏感数据引用，不保存明文敏感值。
- 如果 keychain/libsecret 不可用，才允许加密落 SQLite。
- 加密落 SQLite 时，必须使用本地设备密钥或用户口令派生密钥。

本地不保存：

- 工具账户登录态。
- cookies。
- 远端工具 tokens。
- 完整工具配置目录。

本地可保存：

- 工具账户 ID、显示名、`tool_type`、默认选择。
- 最近使用的 workspace 和 session 索引。
- 便于 CLI 快速启动的非敏感缓存。

### 6.14 CLI 依赖分发模型

`agent-remote-cli` 必须托管本地运行依赖，避免用户手动安装 WireGuard、Mutagen 等外部程序。

原则：

- CLI 发布包内置或配套下载受控版本的 Mutagen。
- CLI 发布包内置或配套安装受控版本的 WireGuard helper。
- CLI 负责版本检查、安装位置、升级和回滚。
- 用户不需要手动安装 Mutagen。
- 用户不需要手动安装 WireGuard 命令行工具。
- `agent-remote doctor` 必须检查内置依赖是否可用。

建议本地目录：

```text
~/.config/agent-remote/
  bin/
    mutagen
    wireguard-helper
  deps.json
```

WireGuard 边界：

- macOS 和 Linux 上创建隧道可能需要系统网络权限或提权。
- CLI 可以内置 helper，但不能绕过操作系统授权模型。
- 如果需要安装系统服务、NetworkExtension、TUN/TAP 或设置路由，CLI 应给出明确授权提示。
- 授权流程由 `agent-remote setup network` 或 `agent-remote doctor --fix` 触发。

Mutagen 边界：

- Mutagen binary 由 CLI 管理固定版本。
- Mutagen session 的创建、暂停、恢复、冲突检查由 CLI 封装。
- 用户不直接调用 Mutagen。

升级策略：

- CLI 与内置依赖版本应在 release manifest 中绑定。
- CLI 检测到依赖版本不匹配时，可自动替换受控目录中的 binary。
- 不应覆盖用户系统中已有的全局 `mutagen`、`wg`、`wg-quick`。
- 系统全局依赖只作为高级 fallback，不作为默认要求。

### 6.15 全组件依赖分发模型

agent-remote 各端都应尽量内置或托管运行所需外部依赖，避免用户手动安装造成版本漂移和部署失败。

通用原则：

- 每个发布包声明自己的依赖 manifest。
- 外部二进制优先随包携带或由安装器下载固定版本。
- 组件启动前执行依赖检查。
- `doctor` 或等价命令提供自动修复能力。
- 不覆盖用户系统中已有的全局工具。
- 系统全局工具只作为 fallback。

CLI 端托管：

- Mutagen binary。
- WireGuard helper。
- 依赖 manifest。

节点端托管：

- tmux binary 或受控安装版本。
- Mutagen binary。
- WireGuard helper 或受控安装版本。
- `agent-remote-attach`。
- 工具 runtime helper。
- 工具镜像模板和版本 manifest。

控制面托管：

- Docker Compose 镜像内封装 Python runtime、前端静态资源和迁移工具。
- PostgreSQL、Redis、反向代理通过 Compose 服务固定镜像版本。

系统级边界：

- Docker Engine 通常仍是节点宿主级依赖。
- OpenSSH server 通常仍是节点宿主级依赖。
- Linux 内核、TUN/WireGuard 内核能力和防火墙规则仍受宿主系统控制。
- 这些系统级依赖应由安装脚本检测、引导安装或给出明确错误，而不是让用户自行排查。

节点安装器要求：

- `agent-remote-node install` 或安装脚本应准备受控依赖目录。
- 安装器应生成 systemd service。
- 安装器应检查 Docker、OpenSSH server、TUN/WireGuard 能力。
- 安装器应输出缺失依赖和修复建议。

### 6.16 WireGuard 网络模型

WireGuard 采用设备级 peer 模型。

基本规则：

- 每台本地用户设备是一个独立 WireGuard peer。
- 每个 VPS 节点是一个独立 WireGuard peer。
- 不同设备不得共用 WireGuard 私钥。
- 每个节点拥有固定 WireGuard 内网 IP。
- 每个用户设备拥有固定 WireGuard 内网 IP。
- 管理端负责生成、分发、更新和撤销 peer 配置。
- CLI 本地保存该设备的 peer 配置，并负责启动或停止 WireGuard。

访问控制：

- 用户设备只允许访问被授权节点的必要端口。
- 必要端口首期包括 SSH 和 Mutagen 所需端口。
- 管理端应记录设备、用户、peer、公钥、分配 IP 和撤销状态。
- 用户登出、设备丢失或管理员禁用用户时，应支持撤销对应 peer。

连接策略：

- CLI 启动工具 session 前，根据管理端分配的目标节点确认 WireGuard 可达。
- 如果 WireGuard 未连接，CLI 尝试启动。
- 如果 WireGuard 已连接但目标节点不可达，CLI 尝试重连或提示用户处理。
- CLI 只连接当前任务需要访问的 WireGuard 网络和目标节点。

推荐资源关系：

```text
User
  -> Device
       -> WireGuardPeer

Node
  -> WireGuardPeer
```

### 6.17 SSH 接入模型

SSH 只作为进入远端 tmux 的传输层，不向用户提供通用 VPS shell 权限。

认证规则：

- CLI 首次登录或注册设备时，为当前设备生成独立 SSH key。
- 不同设备不得共用 SSH 私钥。
- SSH 公钥上传到管理端。
- 管理端根据用户、设备和 session 授权，将公钥同步到目标节点的受控 `authorized_keys`。
- 用户禁用设备、登出设备或管理员禁用用户时，应撤销对应 SSH key。

入口限制：

- 节点上的 `authorized_keys` 不应直接授予普通 shell。
- 每个受控 key 应使用 forced command，指向 agent-remote 受控入口脚本。
- 入口脚本只允许 attach 到管理端授权的 tmux session。
- 入口脚本不得允许用户任意执行宿主机命令。
- 实际 Claude 命令执行发生在 Docker sandbox 中。

推荐 SSH 命令形态：

```text
ssh agent-remote@{node_wg_ip} agent-remote-attach --session {session_id}
```

实际实现中，`agent-remote-attach` 应校验：

- SSH key 对应的设备是否有效。
- 用户是否仍有权限访问该 session。
- session 是否属于该用户。
- session 是否位于当前节点。
- tmux session 是否存在。

### 6.18 管理端边界

管理端负责全局控制面：

- 用户和组织管理。
- 用户权限、配额和审计。
- 用户自有工具账户管理。
- 工具账户地区、时区和节点亲和配置。
- 用户设备、WireGuard peer 和 SSH key 管理。
- VPS 节点注册、健康检查和分流策略。
- session 分配、恢复、终止策略。
- 配置模板和策略下发。

### 6.19 管理端 API 模块

管理端 API 按功能模块拆分，并区分用户/CLI/前端 API 与节点端专用 API。

推荐模块：

1. `/auth`
   - Web 登录、登出、token 刷新。
   - CLI login/device code 或 CLI token 签发。
   - TOTP 绑定和验证。

2. `/users`
   - 管理员管理用户。
   - 普通用户查看和更新自己的基础信息。

3. `/devices`
   - 用户设备注册、查看、禁用。
   - 设备关联的 CLI token、WireGuard peer、SSH key 撤销。

4. `/tool-accounts`
   - 工具账户创建、绑定、禁用、删除。
   - 工具 profile 管理。
   - 绑定状态机查询。

5. `/nodes`
   - 管理员创建节点、生成注册 token。
   - 节点状态、标签、权重、维护状态管理。

6. `/workspaces`
   - workspace 注册、查询、项目 key 映射。
   - 当前用户 workspace 列表。

7. `/sync-sessions`
   - Mutagen 同步状态。
   - 冲突状态查询。
   - pause、resume、reset、resolve 等同步控制入口。

8. `/sessions`
   - 工具 session 创建、恢复、停止、列表。
   - 当前项目 session 查询。
   - session 连接信息获取。

9. `/audit-logs`
   - 管理员查看审计日志。
   - 普通用户查看与自己相关的安全事件。

10. `/node-api`
    - 节点端专用 API。
    - 节点注册、心跳、任务拉取、任务结果上报、状态对账。

权限边界：

- `/node-api` 只接受节点凭证，不接受用户 CLI token。
- 用户/CLI/前端 API 不接受节点凭证。
- 普通用户只能访问自己的设备、工具账户、workspace、sync session 和 session。
- 管理员 API 操作必须写入审计日志。

### 6.20 管理端与节点端通信模型

管理端与节点端采用“节点主动连接管理端”的控制面模型。

基本原则：

- 节点端主动向管理端注册、认证和发送心跳。
- 管理端不主动 SSH 到节点。
- 管理端不要求节点暴露公网 API 端口。
- 节点端只信任管理端下发的任务。
- CLI 不直接调用节点端创建资源。

推荐通信方式：

- 节点注册：HTTPS API。
- 节点心跳：HTTPS 周期上报。
- 节点任务获取：首期使用 HTTPS 长轮询或普通轮询。
- 后续优化：可升级为 WebSocket 或 gRPC streaming。

节点注册流程：

1. 管理员在管理端创建节点，生成一次性注册 token。
2. 在 VPS 上安装并启动 `agent-remote-node`。
3. 节点端使用注册 token 调用管理端注册 API。
4. 管理端签发节点长期凭证。
5. 节点端保存凭证并开始心跳。
6. 管理员在管理端确认节点状态、标签、权重和可调度状态。

心跳内容建议：

- 节点版本。
- 支持的工具类型，例如 `claude`。
- CPU、内存、磁盘、负载。
- Docker 状态。
- tmux 状态。
- 当前容器数和 session 数。
- 最近错误摘要。

任务类型建议：

- 创建账号绑定临时 session。
- 创建工具运行 session。
- 恢复 session 状态。
- 终止 session。
- 清理异常容器和 tmux。
- 准备 workspace 目录。
- 注入或归档账户配置。
- 上报 Mutagen 远端目录状态。

故障处理：

- 管理端超过心跳阈值未收到节点上报时，将节点标记为 `offline`。
- `offline` 节点不可创建新 session。
- 运行中 session 不做自动跨节点迁移。
- 节点恢复后，节点端应重新上报本地容器和 tmux 状态，管理端进行状态对账。

### 6.21 节点任务模型

节点任务采用管理端持久任务 + 节点轮询 + 幂等 `task_id` 模型。

核心规则：

- 管理端创建 `node_tasks` 记录。
- 每个任务拥有全局唯一 `task_id`。
- 节点通过 `/node-api/tasks/poll` 拉取属于自己的任务。
- 节点执行任务前必须检查本地是否已执行过该 `task_id`。
- 节点执行结果写入 `node_task_results`。
- 节点断线重连后可以继续拉取未完成任务，并通过 `task_id` 保证幂等。

任务状态：

- `pending`：等待节点拉取。
- `leased`：已被节点领取，租约未过期。
- `running`：节点已开始执行。
- `succeeded`：任务成功。
- `failed`：任务失败。
- `cancelled`：管理端取消。
- `expired`：任务过期。

任务类型：

- `create_binding_session`：创建工具账户绑定临时 session。
- `create_tool_session`：创建工具运行 session。
- `stop_session`：停止工具 session。
- `create_browser_session`：创建远端临时浏览器会话。
- `stop_browser_session`：停止远端临时浏览器会话。
- `sync_ssh_keys`：同步受控 `authorized_keys`。
- `prepare_workspace`：准备远端 workspace 目录。
- `archive_account_config`：归档工具账户配置。
- `inject_account_config`：注入工具账户配置。
- `cleanup_resources`：清理异常容器、tmux 和临时目录。
- `reconcile_state`：节点状态对账。

Redis 用途：

- 任务短期租约。
- 分布式锁。
- 节点轮询节流。
- 临时任务状态缓存。
- 后台任务队列。

PostgreSQL 用途：

- 任务权威记录。
- 任务结果。
- 审计和可追溯历史。

### 6.22 多节点调度模型

多 VPS 节点分流采用综合评分模型，不使用单纯随机或单一负载指标。

硬性过滤条件：

- 节点必须处于 `healthy` 状态。
- 节点不能处于 `disabled` 或 `maintenance` 状态。
- 节点可用磁盘、内存、CPU 必须高于最低阈值。
- 节点必须支持目标工具类型，例如 `claude`。
- 节点必须满足目标 session 的资源需求。
- 节点地区或标签应匹配工具账户的 `region_code` 或 `preferred_node_tags`。
- 如果目标工具账户已有活跃 session，候选节点必须是该账户当前活跃 session 所在节点。
- 如果目标工具账户没有活跃 session 但存在 `affinity_node_id`，候选节点应优先限制为该亲和节点。

推荐评分维度：

- 当前 CPU、内存、磁盘和容器数量。
- 当前活跃 session 数。
- 节点管理员配置权重。
- 用户或工具账户最近使用过且稳定的节点加分。
- 最近失败、重启、心跳抖动的节点扣分。
- 后续可加入地区、网络延迟、带宽成本、节点费用等权重。

调度原则：

- 新建 session 时由管理端选择节点。
- 恢复 session 时优先回到原节点。
- 如果原节点不可用，首期不迁移正在运行的 session，只提示不可恢复或创建新 session。
- 账号绑定任务也走同一套调度，但可以优先选择空闲节点。
- 同一工具账户允许多开，但所有活跃 session 必须在同一 VPS 节点上运行。
- 同一工具账户的节点亲和关系默认由首次绑定或首次成功运行的节点确定。
- 账户亲和节点不可用时，不自动把该账户调度到其他节点，除非用户或管理员显式执行迁移或重新绑定。
- 管理员可以手动禁用节点、设置维护状态、调整节点权重。

节点状态建议：

- `healthy`：可调度。
- `degraded`：可恢复已有 session，但不优先创建新 session。
- `maintenance`：不创建新 session，可按策略允许已有 session 继续运行。
- `disabled`：不可调度。
- `offline`：心跳超时，不可调度。

### 6.23 节点端边界

节点端负责单节点数据面：

- Docker sandbox 生命周期。
- tmux session 生命周期。
- 节点资源监控。
- 本节点上用户运行目录准备。
- 工具配置注入。
- Mutagen 远端目录管理。
- 受控 SSH authorized_keys 和入口脚本管理。
- 心跳和运行状态上报。

### 6.24 前端边界

前端负责可视化管理：

- 用户管理。
- 节点管理。
- 用户设备、WireGuard peer 和 SSH key 管理。
- 用户自有工具账户管理。
- 工具账户地区、时区和节点亲和配置。
- session 管理。
- session 连接命令展示。
- 远端临时浏览器创建、连接、停止和状态展示。
- 节点健康展示。
- 节点任务失败展示。
- session 状态展示。
- 同步冲突展示。
- 配额和审计查看。
- 全局配置策略管理。

### 6.25 日志与观测模型

MVP 提供基础日志与观测能力，不首期接入完整监控平台。

日志格式：

- 管理端使用结构化 JSON 日志。
- 节点端使用结构化 JSON 日志。
- CLI 默认输出人类可读日志。
- CLI debug 模式可输出 JSON 日志。

关联 ID：

- 管理端每个请求生成或透传 `request_id`。
- 节点任务全链路必须包含 `task_id`。
- 工具 session 全链路必须包含 `session_id`。
- workspace 同步相关日志应包含 `workspace_id` 和 `sync_session_id`。
- 工具账户相关日志应包含 `tool_account_id` 和 `tool_type`。

脱敏规则：

- 日志默认脱敏 token、cookie、私钥、登录态。
- 路径中包含用户名、账户 ID、token 片段时应部分脱敏。
- 错误摘要可以记录，但不得包含完整敏感值。
- verifier 不得把工具登录态写入日志。

管理端前端展示：

- 节点健康状态。
- 节点最近心跳。
- 节点任务失败。
- session 状态。
- 同步冲突。
- 账户绑定失败摘要。

暂不做：

- Prometheus。
- Grafana。
- OpenTelemetry tracing。
- 集中日志平台。

### 6.26 管理端数据库核心实体

管理端数据库使用 PostgreSQL。MVP 核心实体如下：

1. `users`
   - 管理员和普通用户。
   - 保存身份、角色、状态、密码哈希、TOTP 状态等。

2. `user_devices`
   - 用户本地设备。
   - 绑定 CLI token、WireGuard peer、SSH key 和设备撤销状态。

3. `tool_accounts`
   - 通用工具账户。
   - 包含 `tool_type`、所属用户、状态、地区、时区、locale、亲和节点等字段。

4. `tool_account_profiles`
   - 工具特有 profile。
   - 按 `tool_type` 保存 Claude、Codex 等工具的专属配置元数据。
   - 敏感字段必须加密。

5. `nodes`
   - VPS 节点。
   - 保存节点状态、标签、权重、WireGuard IP、支持的工具类型和调度配置。

6. `node_heartbeats`
   - 节点心跳与资源快照。
   - 保存 CPU、内存、磁盘、Docker、tmux、session 数等状态。

7. `node_tasks`
   - 管理端下发给节点的持久任务。
   - 保存 `task_id`、节点、任务类型、payload、状态、租约和重试信息。

8. `node_task_results`
   - 节点任务执行结果。
   - 保存任务状态、错误摘要、结果 payload 和节点执行时间。

9. `wireguard_peers`
   - WireGuard peer。
   - 同时覆盖用户设备 peer 和节点 peer。

10. `ssh_keys`
   - 设备级 SSH 公钥。
   - 保存授权状态、撤销状态和同步到节点的状态。

11. `workspaces`
   - 用户项目 workspace。
   - 保存项目 key、本地启动路径、设备、用户和远端目录映射。

12. `sync_sessions`
    - Mutagen 同步 session。
    - 保存本地路径、远端路径、状态、冲突状态和同步策略。

13. `sessions`
    - 工具运行 session。
    - 必须包含 `tool_type`、`tool_account_id`、`workspace_id`、`node_id`、`status`、`tmux_session_name` 等字段。

14. `session_events`
    - session 生命周期事件。
    - 用于记录创建、attach、detach、停止、失败、节点对账等事件。

15. `browser_sessions`
    - 远端临时浏览器会话。
    - 保存用户、节点、可选工具账户、地区、时区、locale、状态、过期时间和连接状态。

16. `audit_logs`
    - 安全和管理审计日志。
    - 记录登录、账户绑定、设备撤销、节点操作、管理员操作等。

关键关系：

```text
users
  -> user_devices
  -> tool_accounts
       -> tool_account_profiles
       -> sessions
  -> workspaces
       -> sync_sessions
       -> sessions

nodes
  -> node_heartbeats
  -> node_tasks
  -> sessions
  -> browser_sessions

node_tasks
  -> node_task_results

user_devices
  -> wireguard_peers
  -> ssh_keys

sessions
  -> session_events

browser_sessions
  -> audit_logs
```

设计要求：

- `sessions` 必须以 `tool_type` 区分工具类型。
- `tool_accounts` 是通用账户表，不创建 `claude_accounts` 作为核心表。
- Claude 专属字段进入 `tool_account_profiles` 或后续专用 profile 表。
- `browser_sessions` 不存储页面内容、cookie、浏览器 profile 或用户输入。
- 敏感 profile 字段必须应用层加密。
- 审计日志不可存储明文 token、cookie、私钥或登录态。

### 6.27 部署模型

MVP 采用 Docker Compose 部署控制面，节点端独立安装为 systemd 服务。

控制面 Docker Compose 服务：

- `agent-remote-server`
  - Python FastAPI 管理端 API。
  - 连接 PostgreSQL 和 Redis。
  - 负责用户、节点、账户、session、调度和审计。

- `postgres`
  - 管理端主数据库。
  - 保存用户、节点、账户、session、设备、审计日志等结构化数据。

- `redis`
  - MVP 必须依赖。
  - 用于缓存、短期任务状态、分布式锁和后台任务队列。

- `agent-remote-admin-web`
  - React 管理端前端。
  - 可由独立容器提供静态资源，也可以构建后交给反向代理托管。

- `reverse-proxy`
  - 可选。
  - 文档推荐 Caddy 或 Nginx。
  - 负责 HTTPS、域名、静态资源和 API 反向代理。

控制面环境变量：

- `AGENT_REMOTE_SECRET_KEY`：应用层加密主密钥，必须备份。
- `DATABASE_URL`：PostgreSQL 连接。
- `REDIS_URL`：Redis 连接。
- `PUBLIC_BASE_URL`：管理端外部访问 URL。
- `BOOTSTRAP_ADMIN_*`：首次部署创建管理员所需配置，或使用 bootstrap 命令代替。

节点端部署：

- `agent-remote-node` 在每台 VPS 节点上以 systemd 服务运行。
- 节点端通过注册 token 主动连接管理端。
- 节点端不要求暴露公网 API 端口。

节点端依赖：

- Docker Engine，系统级依赖，安装器检测和引导。
- OpenSSH server，系统级依赖，安装器检测和引导。
- TUN/WireGuard 内核能力，系统级依赖，安装器检测和引导。
- tmux，由 `agent-remote-node` 发布包或安装器托管固定版本。
- Mutagen，由 `agent-remote-node` 发布包或安装器托管固定版本。
- WireGuard helper，由 `agent-remote-node` 发布包或安装器托管固定版本。
- agent-remote-node 二进制。

节点端建议目录：

```text
/etc/agent-remote/
  node.toml
  node.secret

/var/lib/agent-remote/
  users/
  workspaces/
  sessions/
  accounts/

/var/log/agent-remote/
```

部署边界：

- 控制面可以部署在单独 VPS，也可以和某个节点共机部署。
- 首期不要求 Kubernetes。
- 首期不要求高可用数据库。
- 首期不做自动跨节点迁移。

## 7. 后续需要补齐的关键问题

1. 项目的目标用户是个人自用、小团队内部，还是面向商业多租户服务？
2. 已确认：首期所有用户共用同一个节点 Linux 用户，仅通过 Docker sandbox、目录规范和应用层权限隔离。
3. 已确认：管理端包含管理员和普通用户两类角色；普通用户在管理端绑定和管理自己的工具账户。
4. 已确认：首期 Claude 账户绑定使用远端临时 sandbox 交互式执行 `claude login`，登录态归档到用户账户目录。
5. 已确认：文件同步必须采用显式 workspace 模型，默认只同步当前目录，额外路径必须显式配置；首次遇到全新目录必须询问用户是否创建同步。
6. 已确认：工具配置、skills、插件、记忆、登录态等账户配置数据以远端账户目录为权威来源。
7. 已确认：首期不做 Web 终端，只支持本地 CLI + SSH + tmux 进入 session。
8. 已确认：多节点调度采用综合评分模型，结合健康状态、负载、活跃 session、节点权重、历史稳定性等因素。
9. 已确认：安全模型按自部署可信管理员 + 基础安全加固设计，不按商业 SaaS 强多租户模型设计。
10. 已确认：同一个工具账户允许多开，但同一账户的所有活跃 session 必须运行在同一 VPS 节点上。
11. 已确认：用户端首期只支持 macOS + Linux，不支持原生 Windows。
12. 已确认：节点端主动连接管理端，管理端不主动 SSH 节点，也不要求节点暴露公网 API 端口。
13. 已确认：WireGuard 采用设备级 peer 模型，本地设备和 VPS 节点均作为 peer，由管理端生成、分发和撤销配置。
14. 已确认：SSH 使用设备级 key，并通过 forced command/受控入口脚本限制为进入授权 tmux session。
15. 已确认：Docker sandbox 默认非 root、非 privileged、受限挂载和资源限制；工具账户可配置地区、时区和 locale，用于匹配节点与运行环境。
16. 已确认：session 绑定项目，项目 key 由启动路径生成；`fclaude` 默认只恢复当前项目最近可用 session。
17. 已确认：`agent-remote` 负责统一管理命令；工具启动命令只消费明确 session 命令，其余参数默认透传给远端原生工具。
18. 已确认：Mutagen 使用双向同步；冲突不自动覆盖，未解决冲突默认阻止进入工具 session。
19. 已确认：管理端首期使用用户名/密码认证，密码 Argon2id 哈希；TOTP 可选；CLI 使用可撤销、可过期 token；首期不做 OAuth/SSO。
20. 已确认：加密主密钥使用环境变量 `AGENT_REMOTE_SECRET_KEY`，节点端使用独立 node secret；管理员必须备份密钥；首期不接入 KMS/Vault。
21. 已确认：项目名称为 `agent-remote`；`agent-remote` 是统一管理命令；`fclaude` 是 Claude 专用启动命令；未来其他工具使用独立启动命令，例如 `fcodex`。
22. 已确认：MVP 控制面使用 Docker Compose 部署；节点端 `agent-remote-node` 在各 VPS 以 systemd 服务运行。
23. 已确认：核心模型必须面向扩展设计，使用 `ToolAccount`、`tool_type`、工具 profile、工具运行模板和工具启动器抽象；Claude 只是首期 `tool_type=claude` 实现。
24. 已确认：工具账户绑定使用通用状态机，每个 `tool_type` 提供自己的登录态 verifier；Claude verifier 首期检测 `claude login` 结果。
25. 已确认：MVP 管理端核心表包括 `users`、`user_devices`、`tool_accounts`、`tool_account_profiles`、`nodes`、`node_heartbeats`、`node_tasks`、`node_task_results`、`wireguard_peers`、`ssh_keys`、`workspaces`、`sync_sessions`、`sessions`、`session_events`、`browser_sessions`、`audit_logs`。
26. 已确认：管理端 API 模块包括 `/auth`、`/users`、`/devices`、`/tool-accounts`、`/nodes`、`/workspaces`、`/sync-sessions`、`/sessions`、`/browser-sessions`、`/audit-logs`、`/node-api`。
27. 已确认：节点任务采用管理端持久任务 + 节点轮询 + 幂等 `task_id` 模型，任务结果写入 `node_task_results`。
28. 已确认：Redis 是 MVP 必须依赖，用于缓存、短期任务状态、分布式锁和后台任务队列。
29. 已确认：CLI 本地目录为 `~/.config/agent-remote/`，本地状态使用 SQLite；敏感值优先保存到系统 keychain/libsecret，SQLite 只保存引用；本地不保存工具账户登录态。
30. 已确认：MVP 使用结构化日志、`request_id`、`task_id`、`session_id` 做基础观测，日志默认脱敏；首期不接 Prometheus/Grafana/OpenTelemetry。
31. 已确认：项目按 Phase Roadmap 推进，从协议冻结、控制面、节点端、CLI、网络、同步、Claude 绑定、Claude session、远端浏览器、管理前端、打包部署到 E2E 发布逐步完成。
32. 已确认：需要实施级附录细化协议冻结内容，包含 OpenAPI、节点任务 payload、CLI 命令规范、数据库字段草案、端到端测试场景和部署文档大纲。
33. 已确认：需要在主方案补充风险清单和非目标清单，明确 MVP 不解决的问题和主要风险缓解措施。
34. 已确认：管理端提供远端临时无痕浏览器会话，浏览器运行在 VPS 节点 Docker sandbox 中，使用节点出口网络和匹配的地区、时区、locale；会话不持久化浏览器用户信息，也不提供 shell。

## 8. 第一阶段建议范围

为了降低复杂度，MVP 建议只做：

1. 单管理端。
2. 多节点。
3. 多用户。
4. 每个用户可绑定多个工具账户，MVP 首期实现 Claude 账户。
5. 每次 CLI 命令进入一个工具 session；同一工具账户允许多开，但必须固定在同一 VPS 节点。
6. Docker sandbox + tmux 持久 session。
7. WireGuard + Mutagen + SSH 由 CLI 调用本机命令编排。
8. 管理前端只做节点、用户、账号、session 的基础管理。
9. 安全模型按自部署可信管理员 + 基础安全加固设计，不引入复杂租户、计费、企业 SSO 和跨组织隔离。
10. 用户端首期只支持 macOS + Linux。
11. `fclaude` 默认恢复当前项目 session，项目 key 由启动路径生成。
12. `agent-remote` 负责统一管理命令；`fclaude` session 命令以外的参数默认透传给远端原生 `claude`。
13. Mutagen 双向同步和基础冲突处理命令。
14. 用户名/密码登录、CLI token、设备撤销和可选 TOTP。
15. 环境变量主密钥和节点本地 secret 的基础加密方案。
16. Docker Compose 控制面部署和 systemd 节点端部署。
17. 面向多工具扩展的 `ToolAccount`、`tool_type`、profile、模板和启动器抽象。
18. 通用工具账户绑定状态机和 Claude verifier。
19. PostgreSQL 核心实体和关系。
20. 管理端 API 模块边界和 `/node-api` 节点专用接口。
21. 节点任务队列、幂等 `task_id`、任务结果和 Redis 必选依赖。
22. CLI 本地状态 SQLite、配置目录和系统凭据存储集成。
23. 结构化日志、关联 ID、脱敏和管理端基础健康展示。
24. 分阶段实现路线图。
25. 风险清单和非目标清单。
26. 各端内置或托管安装外部运行依赖，不要求用户手动安装；CLI 托管 WireGuard/Mutagen，节点端托管 tmux/Mutagen/WireGuard helper 等。
27. 管理端远端临时浏览器，用于访问邮箱、Claude Web 等页面；浏览器会话无痕、短期、容器化，走 VPS 节点网络和地区环境。

暂不建议首期做：

1. 浏览器内的 Web 终端或交互式 shell 代理。
2. 复杂计费。
3. 跨区域高可用控制面。
4. 自动迁移正在运行的工具 session 到其他节点。
5. 自研文件同步。
6. 原生 Windows 客户端和 WSL2 专项适配。
7. OAuth、SAML、OIDC SSO 和企业身份目录同步。
8. KMS、Vault 或云厂商密钥管理服务接入。
9. Kubernetes 和高可用数据库部署。
10. Prometheus、Grafana、OpenTelemetry 和集中日志平台。

## 9. Phase Roadmap

本项目按 Phase 推进。每个 Phase 必须满足以下规则：

- 先改 `agent-remote-protocol`，再改服务端、节点端、CLI 和前端。
- 每个 Phase 都要有可运行的本地验证方式。
- 跨仓库接口变更必须同时更新 OpenAPI、JSON Schema、服务端测试和调用方适配。
- 未完成验收标准时，不进入依赖它的下一个 Phase。
- Phase 可以在人员足够时并行，但只能并行实现不共享未冻结协议的部分。

### 9.1 Phase 总览

| Phase | 主要仓库 | 目标 | 完成标志 |
| --- | --- | --- | --- |
| Phase 0 | `agent-remote` / `agent-remote-protocol` | 冻结方案和协议基线 | 文档、OpenAPI、schema、示例 payload 已提交 |
| Phase 1 | `agent-remote-server` | 控制面项目骨架 | FastAPI、配置、日志、健康检查、数据库迁移可运行 |
| Phase 2 | `agent-remote-server` | 核心数据模型 | PostgreSQL 表、索引、Alembic 迁移和基础 repository/service 完成 |
| Phase 3 | `agent-remote-server` / `agent-remote-cli` | 认证、用户、设备和密钥 | 管理员初始化、普通用户登录、CLI token、设备注册可用 |
| Phase 4 | `agent-remote-node` / `agent-remote-server` | 节点注册、心跳和任务轮询 | 节点可注册、上报资源、拉取任务并回写结果 |
| Phase 5 | `agent-remote-cli` | CLI 本地基础能力 | `agent-remote login/status/doctor`、SQLite、keychain/libsecret、托管依赖目录完成 |
| Phase 6 | `agent-remote-cli` / `agent-remote-node` / `agent-remote-server` | WireGuard 与 SSH 受控连接 | 设备 peer、节点 peer、SSH forced command 和 attach 入口可用 |
| Phase 7 | `agent-remote-cli` / `agent-remote-node` / `agent-remote-server` | Mutagen workspace 同步 | 首次同步确认、双向同步、冲突阻止进入 session 完成 |
| Phase 8 | `agent-remote-server` / `agent-remote-node` | 工具账户抽象和 Claude 绑定 | `tool_type=claude` 账户创建、远端登录、verifier、配置归档完成 |
| Phase 9 | `agent-remote-cli` / `agent-remote-node` / `agent-remote-server` | Claude 工具 session | `fclaude` 创建、恢复、停止、参数透传和同账户同节点约束完成 |
| Phase 10 | `agent-remote-admin-web` / `agent-remote-node` / `agent-remote-server` | 远端临时浏览器 | `/browser-sessions`、浏览器容器、内嵌连接、TTL 清理完成 |
| Phase 11 | `agent-remote-admin-web` | 管理前端 | 用户、设备、账号、节点、session、同步、浏览器和审计页面完成 |
| Phase 12 | 全部仓库 | 打包与部署 | Docker Compose、systemd、CLI 安装包、节点安装器和升级文档完成 |
| Phase 13 | 全部仓库 | 端到端验收和 MVP 发布 | 从空环境部署到 `fclaude` 可用的 E2E 测试通过 |
| Phase 14 | 全部仓库 | v1.0 稳定化 | 安全加固、故障恢复、备份、升级兼容和文档补齐 |
| Phase 15 | 全部仓库 | 多工具扩展验证 | 至少接入第二个工具原型，验证 `ToolAccount` 抽象可复用 |

### 9.2 Phase 0：方案和协议基线

目标：

- 将当前方案转化为跨仓库契约。
- 避免各端先行实现导致接口反复返工。

完成记录见 [phase-0-completion.md](phase-0-completion.md)。

交付物：

- 主方案文档。
- 实施级附录。
- `agent-remote-protocol` 仓库。
- OpenAPI 草案。
- JSON Schema。
- 节点任务 payload 示例。
- 错误码、API 约定和版本策略。

验收标准：

- `agent-remote-protocol` 至少包含 `openapi/openapi.yaml`、`schemas/`、`docs/` 和 `examples/`。
- JSON 示例可以被标准 JSON parser 解析。
- OpenAPI YAML 可以被标准 YAML parser 解析。
- 所有实现仓库都能以协议仓库作为开发参考。

### 9.3 Phase 1：控制面项目骨架

目标：

- 建立 `agent-remote-server` 的可运行基础。
- 为后续 API、数据库和任务系统提供统一工程结构。

完成记录见 [phase-1-completion.md](phase-1-completion.md)。

交付物：

- FastAPI 项目结构。
- 配置加载。
- 结构化日志。
- `request_id` middleware。
- 健康检查接口。
- PostgreSQL、Redis 连接检查。
- Alembic 初始化。
- 基础测试框架。
- Dockerfile 和本地 Compose 开发环境。

验收标准：

- 本地执行服务后 `/healthz` 返回健康状态。
- `DATABASE_URL` 和 `REDIS_URL` 错误时有明确错误。
- 测试命令可以在干净环境运行。
- CI 能执行 lint、type check 和测试。

### 9.4 Phase 2：核心数据模型

目标：

- 建立管理端权威数据模型。
- 确保多用户、多设备、多节点、多账户、多 session 的关系明确。

交付物：

- `users`
- `user_devices`
- `tool_accounts`
- `tool_account_profiles`
- `nodes`
- `node_heartbeats`
- `node_tasks`
- `node_task_results`
- `wireguard_peers`
- `ssh_keys`
- `workspaces`
- `sync_sessions`
- `sessions`
- `session_events`
- `browser_sessions`
- `audit_logs`

验收标准：

- Alembic 可以从空库迁移到最新版本。
- 关键唯一约束和索引存在。
- 敏感字段有加密标记或加密封装。
- 基础 repository/service 测试覆盖创建、查询、更新和约束冲突。

完成记录见 [phase-2-completion.md](phase-2-completion.md)。

### 9.5 Phase 3：认证、用户、设备和密钥

目标：

- 让管理员和普通用户能够安全进入系统。
- 让 CLI 设备成为可撤销的受控身份。

交付物：

- 管理员 bootstrap。
- 用户名/密码登录。
- Argon2id 密码哈希。
- 可选 TOTP 基础结构。
- CLI device-code 或 browser login 流程。
- CLI token 签发、刷新、撤销。
- 设备注册。
- SSH 公钥注册。
- WireGuard peer 记录。
- 审计日志。

验收标准：

- 第一个管理员可以初始化。
- 普通用户可以登录管理端。
- CLI 可以注册设备并拿到可撤销 token。
- 禁用设备后 CLI token、SSH key 和 WireGuard peer 都进入不可用状态。
- 审计日志不记录密码、token、私钥或登录态。

完成记录见 [phase-3-completion.md](phase-3-completion.md)。

### 9.6 Phase 4：节点注册、心跳和任务轮询

目标：

- 让 `agent-remote-node` 成为受控执行节点。
- 建立管理端到节点端的持久任务模型。

完成记录见 [phase-4-completion.md](phase-4-completion.md)。

交付物：

- Go 节点端项目骨架。
- 节点配置文件。
- 节点注册命令。
- 节点 secret 管理。
- 心跳上报。
- 资源快照。
- `/node-api/tasks/poll`。
- task lease。
- task start/complete/fail。
- 节点本地 task ledger。
- `reconcile_state` 基础实现。

验收标准：

- 节点可以用注册 token 加入控制面。
- 管理端能看到节点在线、地区、标签、资源和支持工具。
- 节点断线后管理端能标记 `offline`。
- 节点恢复后能重新对账。
- 重复投递同一 `task_id` 不会创建重复资源。

### 9.7 Phase 5：CLI 本地基础能力

目标：

- 建立用户端统一管理命令。
- 准备后续网络、同步和工具启动所需本地状态。

完成记录见 [phase-5-completion.md](phase-5-completion.md)。

交付物：

- Rust CLI 项目结构。
- `agent-remote login`
- `agent-remote logout`
- `agent-remote status`
- `agent-remote doctor`
- `agent-remote doctor --fix`
- 本地目录 `~/.config/agent-remote/`。
- 本地 SQLite。
- keychain/libsecret 集成。
- 托管依赖目录和 manifest。
- Mutagen、WireGuard helper 的版本检查框架。

验收标准：

- macOS 和 Linux 上 CLI 能登录并持久化本地状态。
- 敏感 token 优先进入系统凭据存储。
- SQLite 不保存工具账户登录态。
- `agent-remote doctor` 能输出服务端、设备、依赖和网络状态。
- 用户不需要手动安装 Mutagen。

### 9.8 Phase 6：WireGuard 与 SSH 受控连接

完成记录见 [phase-6-completion.md](phase-6-completion.md)。

目标：

- 打通本地设备到 VPS 节点的受控网络和交互链路。
- 保证 SSH 只能进入授权 session，不提供通用 shell。

交付物：

- WireGuard peer 生成、分配和撤销。
- CLI 托管 WireGuard helper。
- 节点 WireGuard 配置。
- 设备 WireGuard 配置。
- 节点受控 `authorized_keys`。
- `agent-remote-attach`。
- SSH forced command。
- CLI 网络检查和 SSH 检查。

验收标准：

- CLI 能启动或检查 WireGuard。
- 本地设备能访问节点 WireGuard IP。
- SSH key 被禁用后无法连接。
- SSH 不带授权 session 时无法获得 shell。
- `agent-remote-attach` 校验用户、设备、节点和 session。

### 9.9 Phase 7：Mutagen workspace 同步

完成记录见 [phase-7-completion.md](phase-7-completion.md)。

目标：

- 保证本地项目文件与远端 workspace 双向同步。
- 避免未确认目录被静默同步。

交付物：

- workspace 创建 API。
- sync session 创建 API。
- CLI workspace 首次确认。
- Mutagen session 创建、暂停、恢复、重置。
- 默认 ignore 规则。
- 冲突检测。
- `agent-remote sync status`
- `agent-remote sync resolve`
- 节点端远端目录准备。

验收标准：

- 新目录首次执行 `fclaude` 前必须询问是否同步。
- 用户拒绝时不启动会写入该目录的远端 session。
- 本地修改能同步远端。
- 远端修改能同步本地。
- 发生冲突时默认阻止进入工具 session。

### 9.10 Phase 8：工具账户抽象和 Claude 绑定

完成记录见 [phase-8-completion.md](phase-8-completion.md)。

目标：

- 实现通用 `ToolAccount` 账户模型。
- 完成 Claude 作为首个工具类型的绑定闭环。

交付物：

- `tool_type` registry。
- 工具运行模板。
- 工具登录态 verifier 接口。
- Claude verifier。
- `agent-remote account create`。
- `agent-remote account bind`。
- 绑定临时 sandbox。
- 绑定临时 tmux session。
- 账户配置归档。
- 账户地区、时区、locale 配置。
- 同账户节点亲和记录。

验收标准：

- 普通用户可以创建多个 Claude 账户。
- 绑定过程发生在远端目标节点和目标地区环境。
- Claude 登录态归档到远端账户目录。
- 登录态不落到本地 CLI。
- verifier 成功后账户状态变为 `active`。

### 9.11 Phase 9：Claude session 和 `fclaude`

目标：

- 让用户通过 `fclaude` 获得接近原生 `claude` 的体验。
- 保证 session 与项目路径绑定，断线可恢复。

交付物：

- `fclaude`
- `fclaude new`
- `fclaude list`
- `fclaude attach`
- `fclaude stop`
- 参数透传。
- 项目 key 生成。
- session 创建 API。
- attach-info API。
- 节点端 Docker sandbox。
- 节点端 tmux session。
- 工具账户配置注入。
- 同账户多开同节点约束。

验收标准：

- 在项目目录执行 `fclaude` 可以进入 Claude。
- SSH 断开后 tmux session 继续运行。
- 同一路径再次执行 `fclaude` 恢复当前项目最近 session。
- 不是恢复全局最近 session。
- `fclaude -- <args>` 原样透传给远端 `claude`。
- 同一 Claude 账户多个活跃 session 位于同一节点。

### 9.12 Phase 10：远端临时浏览器

目标：

- 在管理端提供内嵌远端无痕浏览器。
- 支持用户通过 VPS 节点网络访问邮箱、Claude Web 和账号确认页面。

交付物：

- `/browser-sessions` API。
- `browser_sessions` 表。
- `create_browser_session` 节点任务。
- `stop_browser_session` 节点任务。
- 浏览器运行时镜像。
- noVNC/websockify 或 WebRTC 连接方案。
- 管理端短期 `embed_url` 签发。
- TTL 自动清理。
- 浏览器网络策略。
- 时区、locale、浏览器语言注入。

验收标准：

- 浏览器出口 IP 是目标 VPS 节点。
- 浏览器时区、locale 和语言匹配工具账户或显式配置。
- 浏览器容器不挂载 workspace 和工具账户目录。
- 会话结束后临时 profile 被删除。
- 日志不包含页面内容、用户输入、cookie、token 或截图。
- 该能力不提供 Web 终端或 shell。

### 9.13 Phase 11：管理前端

目标：

- 让管理员和普通用户可以通过 Web 管理系统。
- 把核心运维、账号、节点和 session 状态可视化。

交付物：

- React + Vite 项目。
- 登录页。
- 用户和设备页面。
- 工具账户页面。
- 节点列表与节点详情。
- session 列表与详情。
- sync session 和冲突页面。
- 远端浏览器页面。
- 节点任务失败展示。
- 审计日志页面。
- 基础设置页面。

验收标准：

- 管理员可以管理用户、节点、设备和异常任务。
- 普通用户只能查看和管理自己的账户、设备、workspace、session 和浏览器会话。
- 前端所有操作调用正式 API，不使用临时 mock。
- 关键危险操作有确认。
- 失败状态能给出可执行的修复提示。

### 9.14 Phase 12：打包、安装和部署

目标：

- 让自部署用户能按文档完成安装。
- 各端外部依赖由发布包或安装器托管，减少手动安装。

交付物：

- 控制面 Docker Compose。
- `agent-remote-server` 镜像。
- `agent-remote-admin-web` 静态构建。
- PostgreSQL 和 Redis Compose 服务。
- Caddy 或 Nginx 示例。
- `agent-remote-node` systemd service。
- 节点安装器。
- CLI macOS 包。
- CLI Linux 包。
- 托管 Mutagen、WireGuard helper、tmux、浏览器运行时依赖。
- 部署文档。
- 升级文档。
- 备份与恢复文档。

验收标准：

- 新控制面服务器可按文档完成部署。
- 新 VPS 节点可按文档加入集群。
- 新 macOS/Linux 客户端可安装 CLI 并登录。
- `agent-remote doctor` 能检查关键依赖。
- Docker/OpenSSH/TUN 等系统级依赖缺失时，安装器给出明确处理方式。

### 9.15 Phase 13：端到端验收和 MVP 发布

目标：

- 证明项目从空环境到可用体验完整闭环。
- 冻结 MVP release。

交付物：

- E2E 测试脚本。
- 手工验收清单。
- release notes。
- 已知限制。
- 故障排查文档。
- 最小演示环境。

验收标准：

- 从空控制面部署到第一个管理员创建通过。
- 节点注册和心跳通过。
- CLI 登录和设备注册通过。
- WireGuard 和 SSH 可达性通过。
- Mutagen 同步通过。
- Claude 账户绑定通过。
- `fclaude` 创建、恢复、停止通过。
- 远端浏览器访问 Claude Web 或邮箱通过。
- 设备撤销和节点断线恢复测试通过。

### 9.16 Phase 14：v1.0 稳定化

目标：

- 将 MVP 从可用提升到可长期自部署维护。
- 降低升级、故障恢复和安全误配置风险。

交付物：

- 数据库迁移回滚策略。
- 协议版本兼容检查。
- 节点滚动升级策略。
- CLI 版本兼容提示。
- 备份恢复演练。
- 密钥丢失风险检查。
- 更完整的审计事件。
- 默认安全配置检查。
- 性能和资源限制基线。

验收标准：

- 小版本升级不会破坏已有账户、session 和节点注册。
- 文档能覆盖常见故障排查。
- 控制面重启后任务和 session 状态可对账。
- 节点重启后容器、tmux、浏览器会话和目录状态可对账。
- 管理员能明确知道哪些密钥和数据必须备份。

### 9.17 Phase 15：多工具扩展验证

目标：

- 验证架构不是 Claude 专用。
- 用第二个工具证明 `ToolAccount`、runtime template、verifier 和启动器抽象可复用。

推荐验证对象：

- Codex。

交付物：

- `tool_type=codex` profile。
- Codex runtime template。
- Codex verifier。
- `fcodex` 启动命令。
- Codex session E2E。
- 文档补充工具接入指南。

验收标准：

- 接入 Codex 不需要修改 `sessions` 核心表结构。
- 接入 Codex 不需要复制 Claude 专用业务模型。
- `fcodex` 与 `fclaude` 拥有一致的项目 key、同步、节点调度和 session 恢复模型。
- 工具差异只落在 profile、template、verifier 和 launcher 层。

## 10. 风险清单

### 10.1 地区和账号风险

风险：

- 工具服务方的地区、账号、设备、登录态策略可能变化。
- 同一账户多开虽然固定同一节点出口 IP，但仍可能触发工具自身限制。

缓解：

- 每个工具账户配置地区、时区和 locale。
- 同一工具账户所有活跃 session 固定同一节点。
- 账户节点迁移必须显式执行。
- 绑定和运行都发生在目标远端环境。

### 10.2 文件同步冲突风险

风险：

- Mutagen 双向同步可能出现冲突。
- AI Agent 在冲突状态下继续修改文件会扩大损坏范围。

缓解：

- 首次 workspace 必须询问用户。
- 默认排除依赖、构建和缓存目录。
- 冲突不自动覆盖。
- 未解决冲突默认阻止进入工具 session。

### 10.3 共享 Linux 用户隔离风险

风险：

- 所有用户共享节点宿主 Linux 用户，不是强多租户安全边界。
- 节点管理员可以访问节点本地数据。

缓解：

- 明确项目定位为自部署个人/小团队。
- 每个 session 独立 Docker sandbox。
- 容器非 root、非 privileged、受限挂载。
- 后续可增加每用户独立 Linux 用户增强模式。

### 10.4 SSH 权限扩大风险

风险：

- 如果 SSH key 配置错误，用户可能获得普通 shell。

缓解：

- 使用设备级 SSH key。
- 节点端受控管理 `authorized_keys`。
- forced command 指向 `agent-remote-attach`。
- `agent-remote-attach` 必须校验设备、用户、session、节点。

### 10.5 节点任务重复执行风险

风险：

- 节点断线重连、HTTP 重试或任务租约过期可能导致任务重复执行。

缓解：

- 每个任务有唯一 `task_id`。
- 节点执行前检查本地执行记录。
- 管理端持久化 `node_tasks` 和 `node_task_results`。
- 任务设计必须幂等。

### 10.6 密钥丢失风险

风险：

- `AGENT_REMOTE_SECRET_KEY` 或 node secret 丢失会导致已加密登录态无法恢复。

缓解：

- 部署文档强制提示备份。
- 启动时检查密钥存在。
- 管理端健康检查提示密钥配置风险。

### 10.7 本地系统依赖风险

风险：

- macOS/Linux 上 WireGuard、Mutagen、SSH、keychain/libsecret 行为不一致。
- WireGuard 隧道创建仍可能需要系统授权或提权。
- 节点端 Docker、OpenSSH、TUN/WireGuard 能力仍依赖宿主系统。

缓解：

- MVP 只支持 macOS + Linux。
- CLI 内置或托管安装 WireGuard、Mutagen 等依赖。
- 节点端发布包或安装器托管 tmux、Mutagen、WireGuard helper 等依赖。
- Docker Engine、OpenSSH server、内核网络能力由安装器检查和引导。
- `agent-remote doctor` 检查内置依赖。
- `agent-remote doctor --fix` 或 `agent-remote setup network` 处理需要授权的网络配置。
- SSH 可继续优先使用系统 `ssh`，减少自研 PTY/SSH 复杂度。

### 10.8 工具扩展复杂度风险

风险：

- 后续 Codex 等工具的登录、配置、缓存、运行方式可能与 Claude 差异很大。

缓解：

- 核心模型使用 `ToolAccount`、`tool_type`、profile、模板和启动器抽象。
- 工具特有逻辑放到 verifier 和 runtime template。
- 核心 session 表不写入 Claude 专用字段。

### 10.9 远端浏览器滥用与检测风险

风险：

- 远端浏览器可能被误用为普通代理浏览器。
- 浏览器指纹、时区、语言、字体、WebRTC、DNS 等细节仍可能影响服务方检测结果。
- 如果浏览器连接端点暴露不当，可能扩大管理端和节点端攻击面。

缓解：

- 浏览器会话默认短 TTL、无痕、一次性，不保存 profile。
- 浏览器网络、时区、locale、语言与工具账户地区保持一致。
- 默认禁用或限制 WebRTC、本地网络访问、下载持久化和宿主挂载。
- 连接 URL 使用短期 token，由管理端鉴权后下发。
- 日志只记录生命周期和域名摘要，不记录页面内容和用户输入。

## 11. 非目标清单

MVP 明确不做：

1. 商业 SaaS 级强多租户隔离。
2. 每用户独立 Linux 系统用户。
3. Web 终端或浏览器内 shell。
4. 原生 Windows 客户端。
5. WSL2 专项适配。
6. Kubernetes 部署。
7. 高可用 PostgreSQL。
8. 跨区域控制面高可用。
9. 运行中 session 跨节点自动迁移。
10. 自研文件同步。
11. OAuth、SAML、OIDC SSO。
12. 企业目录同步。
13. 计费系统。
14. KMS、Vault 或云厂商密钥管理。
15. Prometheus、Grafana、OpenTelemetry。
16. 集中日志平台。
17. 任意工具的通用自动适配。
18. 允许普通用户任意指定 Docker 镜像或宿主挂载路径。
19. 持久化远端浏览器 profile、密码管理器、浏览历史或下载目录。

## 12. 待确认结论记录

本节用于在问答后记录已经确认的方案决策。

- 项目面向个人和小团队自部署，不作为大型商业 SaaS 设计。
- 远端多用户隔离采用轻量模型：共享宿主 Linux 用户，通过 Docker sandbox、目录规范和应用层权限隔离。
- 管理端用户分为管理员和普通用户；普通用户可以在管理端绑定和管理自己的工具账户。
- 首期 Claude 账户绑定采用远端临时 sandbox 交互式登录，登录态归档到该用户的账户目录。
- 文件同步必须采用显式 workspace 模型，默认只同步当前目录，额外路径必须显式配置；首次遇到全新目录必须询问用户是否创建同步。
- 工具配置、skills、插件、记忆、登录态等账户配置数据以远端账户目录为权威来源；本地 CLI 不默认覆盖远端账户配置。
- 工具终端入口首期不做 Web 终端，只支持本地 CLI + SSH + tmux；管理端对工具 session 展示状态和连接命令。
- 管理端提供远端临时无痕浏览器会话，用于通过 VPS 节点网络访问邮箱、Claude Web 等页面；该能力不提供 shell，不持久化浏览器用户信息。
- 多节点调度采用综合评分模型，结合健康状态、负载、活跃 session、管理员权重和历史稳定性等因素。
- 同一个工具账户允许多开，但同一账户的所有活跃 session 必须运行在同一 VPS 节点上，保证出口 IP 一致。
- 用户端首期只支持 macOS + Linux，不支持原生 Windows。
- 节点端主动连接管理端，管理端不主动 SSH 节点，也不要求节点暴露公网 API 端口。
- WireGuard 采用设备级 peer 模型，本地设备和 VPS 节点均作为 peer，由管理端生成、分发和撤销配置。
- SSH 使用设备级 key，并通过 forced command/受控入口脚本限制为进入授权 tmux session，不提供通用 VPS shell。
- Docker sandbox 默认非 root、非 privileged、受限挂载和资源限制；工具账户可配置地区、时区和 locale，用于匹配节点与运行环境。
- session 绑定项目，项目 key 由启动路径生成；`fclaude` 默认只恢复当前项目最近可用 session。
- `agent-remote` 负责统一管理命令；工具启动命令只消费明确 session 命令，其余参数默认透传给远端原生工具。
- Mutagen 使用双向同步；冲突不自动覆盖，未解决冲突默认阻止进入工具 session。
- 管理端首期使用用户名/密码认证，密码 Argon2id 哈希；TOTP 可选；CLI 使用可撤销、可过期 token；首期不做 OAuth/SSO。
- 加密主密钥使用环境变量 `AGENT_REMOTE_SECRET_KEY`，节点端使用独立 node secret；管理员必须备份密钥；首期不接入 KMS/Vault。
- 项目名称为 `agent-remote`；`agent-remote` 是统一管理命令；`fclaude` 是 Claude 专用启动命令；未来其他工具使用独立启动命令，例如 `fcodex`。
- MVP 控制面使用 Docker Compose 部署；节点端 `agent-remote-node` 在各 VPS 以 systemd 服务运行。
- 核心模型面向多工具扩展设计，使用 `ToolAccount`、`tool_type`、工具 profile、工具运行模板和工具启动器抽象；Claude 只是首期 `tool_type=claude` 实现。
- 工具账户绑定使用通用状态机，每个 `tool_type` 提供自己的登录态 verifier；Claude verifier 首期检测 `claude login` 结果。
- MVP 管理端核心表包括 `users`、`user_devices`、`tool_accounts`、`tool_account_profiles`、`nodes`、`node_heartbeats`、`node_tasks`、`node_task_results`、`wireguard_peers`、`ssh_keys`、`workspaces`、`sync_sessions`、`sessions`、`session_events`、`browser_sessions`、`audit_logs`。
- 管理端 API 模块包括 `/auth`、`/users`、`/devices`、`/tool-accounts`、`/nodes`、`/workspaces`、`/sync-sessions`、`/sessions`、`/browser-sessions`、`/audit-logs`、`/node-api`。
- 节点任务采用管理端持久任务 + 节点轮询 + 幂等 `task_id` 模型，任务结果写入 `node_task_results`。
- Redis 是 MVP 必须依赖，用于缓存、短期任务状态、分布式锁和后台任务队列。
- CLI 本地目录为 `~/.config/agent-remote/`，本地状态使用 SQLite；敏感值优先保存到系统 keychain/libsecret，SQLite 只保存引用；本地不保存工具账户登录态。
- MVP 使用结构化日志、`request_id`、`task_id`、`session_id` 做基础观测，日志默认脱敏；首期不接 Prometheus/Grafana/OpenTelemetry。
- 项目按 Phase Roadmap 推进，从协议冻结、控制面、节点端、CLI、网络、同步、Claude 绑定、Claude session、远端浏览器、管理前端、打包部署到 E2E 发布逐步完成。
- 已创建实施级附录，细化 OpenAPI、节点任务 payload、CLI 命令规范、数据库字段草案、端到端测试场景和部署文档大纲。
- 已补充风险清单和非目标清单，明确 MVP 不解决强多租户、Web 终端、Windows、Kubernetes、高可用、自动迁移、自研同步、SSO、计费、KMS/Vault、完整监控等问题。
- 各端必须内置或托管安装外部运行依赖，不要求用户手动安装；CLI 托管 WireGuard/Mutagen，节点端托管 tmux/Mutagen/WireGuard helper 等；系统级 Docker/OpenSSH/TUN 能力由安装器检测和引导。
- 安全模型按自部署可信管理员 + 基础安全加固设计，不按商业 SaaS 强多租户模型设计。
