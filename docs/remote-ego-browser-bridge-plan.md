# 远端 fclaude 控制本地 ego lite 实施计划

## 1. 文档状态

本文定义一种透明转发方案：远端继续安装和使用 `ego-browser` Skill，但远端的
`ego-browser` 命令不连接远端浏览器，而是把完整 heredoc JavaScript 转发到本地，
由本地真实的 ego lite `ego-browser` 执行。

- 产品决策状态：已确认。
- 方案状态：功能实现、自动化契约、Bridge `0.1.11` promotion、root `0.2.27` 的 tag-bound
  schema 9 evidence 与 development real ego lite canary 已完成；artifact-bound logged-in
  canary 和显式生产开关仍待完成。Bridge component 当前为 `production_ready=true`，但
  capability 默认保持关闭。
- MVP 平台：远端 Linux runtime + 本地 macOS ego lite。
- 远端 backend：同时支持 Linux `native` 与 `docker_sandbox`。两者都必须通过各自的受信
  runtime state、非 root 身份、固定制品 mount、最小 ACL、nonce 与 `SO_PEERCRED` 合同。
- MVP 控制边界：远端 `fclaude` 获得本地 Bridge 用户身份下的任意 Node.js/heredoc
  执行权。该权限包含浏览器控制，也可能包含 `process`、动态 `import`、文件访问和
  子进程启动；不能描述为“仅浏览器权限”。
- 远端浏览器：MVP 不运行远端浏览器。
- 本地浏览器：用户本机已安装并登录的 ego lite。
- 连接方向：本地 Bridge 主动建立到 agent-remote 控制面的出站连接；不监听公网端口。
- 授权要求：每个远端 fclaude session 必须经过用户明确选择和授权。
- 生产发布 profile：默认使用无需 Apple Developer 账号的 `community-local-trust`；在受控
  生产部署中可开启 capability，但必须展示项目自签、非 notarized、非公共分发的信任边界。
- 生产硬约束：不存在“临时 browser binding”或自动绑定路径；任何可执行的 binding 都
  必须由独立 Device Client 完成明确 session 选择、full-trust 确认和服务端原子 claim。
- 终止语义：连接断开、租约过期、用户停止或 session 结束后，Bridge 立即停止接受新请求，
  撤销当前 generation，并从外部终止 Bridge 管理的本地执行单元。已经完成的浏览器、
  文件或网络副作用不能回滚；若没有 OS 级执行边界，也不能声称任意脚本自行脱离监管的
  后台进程一定被清除。
- 涉及仓库：`agent-remote`、`agent-remote-server`、`agent-remote-node`、
  `agent-remote-cli`、`agent-remote-admin-web` 与新建 `agent-remote-ego-browser`；CLI 默认
  集成浏览器状态展示与控制命令，Admin 默认集成 binding 状态和生命周期入口。

其中 `agent-remote-ego-browser` 是 ego lite 的独立扩展仓库，拥有本方案的
本地 Bridge、远端 wrapper、设备注册、授权、共享协议、安装器和跨组件测试。
`agent-remote-device` 完全不属于本方案的安装、运行或授权依赖；用户可以不安装
它而正常使用 ego lite 及本方案的独立 Bridge。

本文是跨仓库实施契约。若本文与旧的通用 GUI 控制设计冲突，以本文中
`ego_browser_script_full_trust` 的独立授权对象和本地脚本全信任语义为准。该模式不授予
通用 GUI 协议能力，但 heredoc 本身拥有 Bridge 运行身份可获得的 Node.js、文件、网络、
子进程和 ego lite 浏览器能力，不能描述为窄化到某个 Tab 或 Task Space。

## 2. 已确认的产品决策

1. 远端 `fclaude` 仍安装官方 `ego-browser` Skill，Agent 的使用方式保持
   `ego-browser nodejs <<'EOF' ... EOF`。
2. 远端命令通过 wrapper 发送完整 stdin 脚本，本地执行真实 `ego-browser`。
3. 一个远端 fclaude tool session 绑定一个独立的 `EgoBrowserBinding`，正常工作流映射到
   一个专用 ego lite Task Space；Task Space 映射是导航和状态复用约定，不是安全边界。
4. 本地 Bridge 通过控制面提供的专用 relay channel 与远端连接，不采用公网监听服务。
5. MVP 接受完整 heredoc 带来的本机任意 Node.js 代码执行权限。
6. 用户必须通过独立的 ego-browser Device 客户端明确选择要绑定的远端 fclaude session；
   不能自动绑定最近 session。
7. 官方 Skill 的正常工作流不主动选择本地用户自己的 Tab 和 user-owned Task Space；
   full-trust heredoc 可以枚举 Tab/Task Space、调用 claim/takeover 或直接调用 CDP，Bridge
   不承诺阻止这些显式行为。
8. 本地浏览器 profile 的持久存储保留在本机，不同步到控制面；授权后的 full-trust
   heredoc 可以读取其可访问的页面、Cookies、扩展、localhost 和局域网数据，并可通过
   stdout、artifact 或网络将数据发出。
9. 页面 Snapshot、截图、脚本输出和错误可能回传到远端 Claude；这些内容属于用户
   明确授权后的数据外发，不进入普通日志。
10. MVP 先支持单设备、单 active browser binding；后续再评估多浏览器并发。
11. MVP 的本地 Bridge 和其 `ego-browser` 子进程与用户当前 macOS 登录会话使用同一 UID，
    不启用 App Sandbox，也不创建独立 macOS 用户；这是为了复用用户现有的 ego lite profile
    和登录态。该选择明确接受 Bridge 运行身份可访问的本机资源风险。
12. 本地 Bridge 允许同一 binding 的多个 heredoc 并行执行；调度器按 Task Space 和 Tab
    作用域使用协作锁，固定按 Task Space -> Tab 顺序取得，未声明或无法解析的作用域使用
    保守的 binding 级锁；MVP 的 `max_parallel_requests` 默认值为 4，冲突不隐式排队。
    full-trust 脚本可以绕过协作锁，因此并行锁不是安全边界。
13. 文件上传采用用户预先配置的 canonical path allowlist；MVP 不提供任意路径上传，
    不在 allowlist 内的 `setInputFiles` 和 `download.saveAs` 直接拒绝。
14. MVP 只使用本地随 Bridge/runtime 携带的签名、固定版本 Site Learning bundle；不接受
    控制面或远端脚本同步、覆盖或运行未验证的 learning 文件。
15. EgoBrowserDevice 使用本方案自有的凭据命名空间和 proof-of-possession；具备受支持
    entitlement 的构建使用本方案独立的 macOS Keychain access group；生产协议中的
    access-group 名称和 credential namespace 始终独立于其他产品。`community-local-trust`
    构建按 community 方案使用 owner-only 的 0600 凭据文件或独立 Keychain service，作为
    没有 Apple provisioning entitlement 时的明确 fallback，不冒充 Apple access group。
    上述 profile 都支持显式轮换、
    撤销和重新注册，不依赖 `agent-remote-device` 的凭据或设备实体。
16. Bridge 和 Device Client 使用用户级 `launchd` agent 常驻；执行请求由独立 supervisor
    启动和回收。没有 Apple Developer 账号也可以使用 `community-local-trust` 作为受控的
    生产 profile：它使用持久项目自签、Hardened Runtime、嵌套签名校验、应用层出口检查、
    owner-only 凭据和证书指纹固定。该 profile 可以开启生产 capability，但不宣称 Apple
    notarization 或公共分发；ad-hoc/未签名的 `development_local` 仍只能用于开发。
17. lease 默认 60 秒，活跃 binding 每 20 秒自动续租，续租失败宽限 10 秒，单次 execute
    最长 120 秒，binding 绝对 TTL 为 8 小时；停止、撤销和用户接管优先于续租。
18. Server 从所选 tool session 派生 canonical `agent-remote:<tool_session_id>`；Device Client
    校验响应并保存在 owner-only handoff，Bridge 只接受匹配 label/scope。独立只读 ownership
    monitor 仅在先观察到 `agent` 后 armed；随后原生 ownership 变为
    `agentDelegatedToUser`/`user` 时先停止本地执行再 pause Server。任何组件都不得自动
    claim/takeover 或以 helper error 代替该信号。

## 3. 目标与非目标

### 3.1 目标

- 让远端 `fclaude` 使用本地 ego lite 的真实浏览器环境。
- 保持官方 `ego-browser` Skill 的 Agent 工作流和 helper API。
- 复用 ego lite 的 Snapshot、locator、Task Space 和登录态。
- 使远端 Agent 可以访问本地 `localhost` Web 应用和用户授权的本地网络。
- 不要求本地设备暴露公网或局域网监听端口。
- 复用控制面的通用用户、tool session、Node、relay、lease、generation、撤销和审计能力，
  但使用独立的 `EgoBrowserBinding` 身份模型，不依赖 `agent-remote-device` 的任何实体。
- 为断网、用户接管、session 结束和 Bridge 崩溃定义 Bridge 控制面的 fail-closed 语义，
  并明确区分“停止受管执行”和“回滚已产生副作用”。

### 3.2 非目标

- MVP 不在远端启动或控制第二个 Chromium。
- MVP 不实现 ego lite 内部的 CDP 或 `globalThis.ego`，也不模拟原生浏览器绑定。
- MVP 不把原始 CDP 协议直接暴露给远端网络。
- MVP 不提供本机通用远程桌面、SSH shell、SOCKS、HTTP 代理或端口转发。
- MVP 不保证远端脚本只调用浏览器 helper；完整 heredoc 是本机 Node 执行权。
- MVP 不实现 Windows/Linux 本地 ego lite；远端 runtime 固定为 Linux，协议记录
  `remote_platform=linux` 和 `local_platform=macos`。
- Bridge 不主动把本机 Claude、Claude OAuth、`~/.claude`、Anthropic API Key 或其他
  secret 注入子进程或协议字段；由于 MVP 与用户同 UID 且无 sandbox，full-trust heredoc
  仍可能读取 Bridge 运行身份本来就能访问的本机资源，产品不得承诺这些资源不可达。
- MVP 不把浏览器页面数据写入控制面数据库、审计正文或普通运行日志。

## 4. 为什么采用透明 heredoc 转发

`ego-browser` 仓库中的 CLI 会把 stdin 读取为一段 JavaScript，构造异步函数并注入
`page`、`browser`、`taskSpaces`、`site`、`fetch` 和 `cdp`。真正的浏览器状态保存在
ego lite 进程中，而不是 Node 进程中。

因此最小可行路径不是在远端重新实现 `globalThis.ego`，而是：

```text
remote ego-browser wrapper
  -> send stdin script as one request
local Browser Bridge
  -> invoke real local `ego-browser`
local ego-browser runtime
  -> globalThis.ego / CDP
local ego lite
```

这样保留了 code-first 的优势：一次远程请求可以在本地组合导航、Snapshot、输入、
提取和等待，避免每个 helper 调用都经过远端网络往返。

## 5. 总体架构

```text
┌──────────────────────────────┐
│ Remote fclaude tool session  │
│ official ego-browser Skill   │
└──────────────┬───────────────┘
               │ stdin heredoc
               ▼
┌──────────────────────────────┐
│ Remote ego-browser wrapper    │
│ request framing + output      │
└──────────────┬───────────────┘
               │ authenticated relay stream
               ▼
┌──────────────────────────────┐
│ agent-remote Server relay     │
│ outer envelope auth + lease   │
│ inner payload remains opaque  │
└──────────────┬───────────────┘
               │ local Bridge outbound connection
               ▼
┌──────────────────────────────┐
│ Local ego-browser Bridge      │
│ independent Device Client     │
│ binding guard + subprocess    │
└──────────────┬───────────────┘
               │ local process / stdin
               ▼
┌──────────────────────────────┐
│ Real local ego-browser        │
│ local Task Space + helpers    │
└──────────────┬───────────────┘
               ▼
┌──────────────────────────────┐
│ ego lite Chromium             │
│ local profile and login data  │
└──────────────────────────────┘
```

### 5.1 组件职责

| 组件 | 职责 | 不应负责 |
| --- | --- | --- |
| Remote wrapper | 读取 heredoc、inner 加密、调用 Node-side broker、回传输出 | 持有长期设备密钥、决定 binding 身份、直接访问本地网络 |
| Server | EgoBrowserBinding、外层 envelope 认证、relay、lease、撤销、审计元数据 | 解密或解析脚本、保存页面内容、执行本地代码 |
| Local Browser Bridge | 本地授权校验、调用真实 ego-browser、结果封装、终止进程 | 自行实现 CDP、替远端决定授权 |
| Real ego-browser | helper 注入、CDP、Snapshot、Task Space、截图和站点学习 | 远程认证和 relay |
| ego lite | Chromium、浏览器 profile、原生 `ego` runtime | 远端 session 编排 |

## 5.2 仓库和代码所有权

### 新建 `agent-remote-ego-browser`

该仓库是本方案的唯一 ego-browser 扩展仓库，建议使用 Rust stable + Tokio：

```text
agent-remote-ego-browser/
  crates/protocol/          # canonical JSON schema、版本和测试向量
  crates/remote-wrapper/    # Linux 远端 `ego-browser` 兼容命令
  crates/local-bridge/      # macOS 本地 Bridge 和 ego-browser 子进程管理
  crates/device-client/     # 独立设备注册、候选查询、绑定和状态客户端
  installer/                # 远端 Node runtime / 本地 Bridge 安装脚本
  integration-tests/        # relay、wrapper、Bridge、artifact E2E
  docs/
```

Rust 的选择理由：

- wrapper、Bridge 和 device client 都是长连接、进程管理和有界 IO 场景，Tokio
  适合统一处理这些边界；
- `protocol` 可以在同一 workspace 中共享严格的 serde 类型和测试向量；
- 不需要在本地额外运行一个 Node 网络服务；Node 只作为官方 `ego-browser`
  子进程运行时；
- Linux 远端 wrapper 与 macOS 本地 Bridge 可以发布同一 workspace 的不同 target。

该仓库不重新实现 ego lite，不 fork 官方 `ego-browser` Skill，也不保存用户
浏览器 profile。

### 现有仓库的变更边界

| 仓库 | 变更范围 |
| --- | --- |
| `agent-remote` | 本计划、跨仓库契约、版本 pin、部署和发布门禁 |
| `agent-remote-server` | `ego_browser_bridge` channel、`EgoBrowserBinding`、授权模式、outer envelope 转发、lease/generation/审计 |
| `agent-remote-node` | 安装官方 Skill、安装 remote wrapper、为 Claude runtime 注入 wrapper PATH 和 binding context |
| `agent-remote-cli` | 默认集成：展示浏览器 binding 状态并提供控制命令；不是 Bridge 运行依赖 |
| `agent-remote-device` | 完全不参与；无需安装、无需运行、无需修改 |
| `agent-remote-ego-browser` | 独立 device client、wrapper、Bridge、协议、artifact、安装器和 ego-browser 专属 E2E |
| ego lite 官方应用 | 外部依赖，由用户安装；本项目不重新打包或修改 |

`agent-remote-ego-browser` 与 `agent-remote-device` 没有运行时依赖、安装依赖或
授权依赖。两者未来最多共享控制面通用 relay 的抽象文档，不共享设备实体、
授权流程、XPC 服务、Keychain access group、GUI Executor 或可执行代码。

### 独立性硬约束

- 本地 ego lite 不感知 `agent-remote-device`，也不需要其 SDK、App、后台服务或配置。
- `agent-remote-ego-browser` 的 Bridge、Device Client、设备密钥、授权 UI、relay
  client、协议和安装器全部由新仓库拥有。
- `agent-remote-server` 只提供通用用户、Node、tool session 和 relay hub 能力；
  ego-browser 设备和绑定使用独立表、API、授权 mode、channel 和审计事件。
- `agent-remote-cli` 默认提供状态展示、绑定诊断、暂停/恢复和结束控制；MVP 的本地
  Bridge 执行仍不依赖 CLI 进程，也不允许通过 CLI 间接拉入 `agent-remote-device`。
- 构建、安装、启动、升级、回滚和 E2E 测试必须在未检出
  `agent-remote-device` 的环境中通过。

## 5.3 Relay 方案决策

复用现有控制面的 ticket、撤销、限流和审计原语，但先把 relay hub 抽象成与旧
`device_sessions` 无关的通用 `RelayBinding`。浏览器使用独立的 binding kind、key、
route 和状态机；不能仅在旧 relay 上增加一个 channel 字符串：

```text
channel = ego_browser_bridge
protocol = ego-browser-bridge-v1
binding = EgoBrowserBinding
relay_binding_kind = ego_browser
relay_key = (relay_binding_kind, binding_id, generation)
```

通用 relay 必须支持跨 worker 的共享状态（Redis/等价 broker）或明确的 sticky routing，
并在连接建立后通过 revocation bus/共享状态处理 binding 撤销、lease 过期和 generation
切换。pair 状态不能只保存在单个进程内存中。这样可以沿用控制面的短期 ticket、撤销、
租约和审计基础设施，同时避免把 ego-browser frame 混入其他 GUI Computer Use 协议。
传输采用双层格式：Server 可见且
可验证的 authenticated outer envelope，包裹只有 wrapper/Bridge 能解密的 inner payload。

当前生产实现固定使用 PostgreSQL + Redis，不使用 sticky 或进程内降级：ticket 和设备 PoP
challenge 在 Redis 中原子单次消费；`(binding_id, generation, role)` presence 的 TTL 为 5 秒，
活跃连接持续刷新；每个 endpoint 使用独立 Pub/Sub channel 传递 opaque frame 和 close 通知，
因此 bridge 与 wrapper 可以落在不同 Server worker。重复 role、peer presence 缺失、subscriber
缺失、共享状态损坏或 Redis 错误都必须关闭连接，不能回退到单 worker 配对。生命周期事务先在
PostgreSQL 递增/终止 generation 并写 durable revocation outbox，cleanup worker 再幂等发布；
发布成功前不能把 outbox row 标为 delivered。

浏览器方案自有设备密钥和握手协议；不依赖 `agent-remote-device` 的 nested TLS、
XPC、Keychain 或设备身份。具体 E2E 加密实现必须在新仓库中单独形成 ADR，但 ADR 必须
保持以下边界：ticket 绑定的 identity 由 Server 派生，inner payload 使用 AEAD 保密和
完整性保护，Server 不获得解密密钥。

Server 读取 outer envelope 的 channel、binding kind、binding、generation、sequence、
request ID、方向和密文长度，校验 ticket、lease、重放和速率后转发 inner ciphertext；
Server 不解析
脚本、stdout、截图、artifact 或页面内容。若现有 relay 的数据模型无法承载任意长度
heredoc/双向 stdout，则在同一授权和 E2E 体系下增加专用 stream endpoint；
不得退回公网本地监听、通用 WebSocket 服务或任意 SSH reverse tunnel。

旧 `DeviceRelayBinding`、`device_session_id` exchange key、旧 `/device-sessions/*/relay`
route、旧 device/proxy role 和 device-control release evidence 不得作为
`ego_browser_bridge` 的身份或唯一键。可以共享底层 transport，但必须有独立的
`EgoBrowserRelayBinding` claims、API route、数据库/Redis key namespace 和跨 worker 测试。

Outer envelope 的 binding identity 必须来自已消费的、一次性的 Server ticket 和受信
Node broker；payload 中重复出现的 ID 只用于一致性检查，不能成为授权来源。Outer schema
由 Server 严格拒绝未知字段；inner schema 由 wrapper/Bridge 严格拒绝未知字段。

Node-side broker 是 `agent-remote-node` 中唯一可以代表远端 tool session 进入 relay 的
组件。它为每个 `tool_session_id` 签发仅存在于当前 broker 进程内存中的随机 capability
nonce，并通过 Node 的已认证控制通道兑换和短期保存 binding ticket 与 claims；ticket 只在
受保护内存中保存，退出或 generation 变化时立即清零。wrapper 通过继承 FD 或 owner-only
Unix socket 与 broker 通信，只提交 capability nonce 和待发送的 inner payload 元数据，不能
提交或选择 `binding_id`；broker 从 nonce 派生精确的 `tool_session_id`，再从最新控制面快照
唯一解析 binding，然后签发一次性
request permit。permit 至少绑定 `binding_id`、`generation`、`request_id`、单调
`sequence`、过期时间、字节额度、并发 scope 和 `allowlist_revision`；broker 原子消费
permit、负责构造 outer envelope 并提交 relay。wrapper 不能自行填写身份、发送 standalone
frame、打开 relay 连接或取得长期设备私钥。脚本、inner 明文、ticket、长期私钥和 relay
URL 不得进入环境变量、argv、workspace、持久化日志或 broker 的长期状态；broker 重启后
必须重新取得 ticket，旧 generation 的 ticket/permit 全部失效。
该 IPC 只防止普通误用和跨用户访问，不是同 UID full-trust 脚本的安全边界；若脚本能够
窃取正在运行的 wrapper/FD 或伪造其调用上下文，风险仍按本机任意代码执行处理，不能以
broker 存在为由宣称设备密钥或 relay capability 对同 UID 攻击者不可达。

远端 broker IPC 同时允许 Native Runtime 与 Docker Sandbox。root-owned runtime helper 为
Native session 分配专用非 root host UID，并为 Docker Sandbox 解析配置的固定非 root
UID/GID；`runtime_uid` 只返回给 Node worker，worker 在对外 task result 中删除该字段并拒绝
UID 0。broker 目录基础 mode 为 `0700`、socket 为 `0600`，numeric ACL 仅给该 UID 目录
`--x` 和 socket `rw-`，每次连接还必须同时通过 Linux `SO_PEERCRED` 精确 UID 与进程内 nonce
校验。Docker 路径还必须校验 root-owned trusted spec，并挂载固定版本的 wrapper、Skill 与
broker 目录。rootful Linux 证明由
`agent-remote-node/tests/linux_ego_browser_uid_acl_test.sh` 执行：UID 20001 可连接、UID 20002
先被 ACL 阻止，临时授予文件访问后仍被真实 `SO_PEERCRED` 拒绝。

## 6. 端到端生命周期

### 6.1 本地设备准备

1. 用户安装 ego lite，并完成首次登录/Chrome 数据迁移。
2. 用户可选择安装独立的 `agent-remote-ego-browser` 本地组件；不安装
   `agent-remote-device` 也不影响 ego lite 的正常使用。
3. 独立 Bridge 检查本地 `ego-browser` 命令可用，并读取支持的 runtime/skill 版本。
4. Device Client 首次运行时在本方案自有的凭据命名空间中生成 `EgoBrowserDevice` 密钥，
   并完成 proof-of-possession 注册。具备 entitlement 的构建使用本方案独立的 macOS
   Keychain access group；`community-local-trust` 使用独立 Keychain service 或 owner-only
   0600 凭据文件，文件必须由当前 UID 拥有、禁止符号链接且通过严格 JSON 校验，不能冒充
   Apple access group。
5. Bridge 和 Device Client 注册为当前用户的 `~/Library/LaunchAgents` user agent，使用
   `launchctl bootstrap gui/$UID`/`bootout` 管理；不安装 system daemon、不监听 TCP 端口，
   本地 IPC 只使用带 peer/capability 校验的 owner-only Unix socket 或进程 stdin。
6. Bridge 主动建立到控制面的 relay；launchd 重启只恢复连接和状态，不自动恢复或重放旧
   execute request。

Device Client 的设备密钥注册采用 proof-of-possession：注册、绑定激活、relay hello 和
密钥轮换都必须签署包含 `ego_browser_device_id`、当前 generation、release profile、
`credential_profile` 和控制面主机名的 challenge。轮换时先以新公钥完成 PoP 并取得新的
device generation，Server 原子标记旧公钥为 retiring；所有 live binding 收到撤销事件并
停止旧 permit 后才撤销旧公钥。撤销或重新注册必须显式由 Device Client/用户发起，不能由
远端 wrapper 代办；community 凭据文件和 Keychain service 的轮换同样要求 owner-only
权限、原子替换和旧 revision 失效。

`community_file` 的凭据文件必须位于用户预配置的 canonical 配置目录，权限为 `0600`、
所有者为当前 UID、`st_nlink=1` 的 regular file，并以 `O_NOFOLLOW`/等价方式打开；文件大小、
JSON key 集合、HTTPS server URL、token 字符集和到期时间都要有上限和严格校验。写入采用
同目录临时文件、`fsync` 后原子 rename，再重新校验 inode；旧文件和旧 token 不进入日志或
发布物。该文件只承载短期控制面 credential，不能替代设备 PoP 私钥，也不能被 wrapper
读取。

### 6.2 绑定远端 session

```text
ego-browser Device Client
  -> GET candidates
  -> 用户选择远端 fclaude session
  -> Server 原子 claim EgoBrowserBinding
  -> Bridge 建立专用 relay + E2E channel
  -> Bridge 探测本地 ego-browser
  -> Server 激活 lease
  -> remote wrapper 获得 ready 状态
```

绑定必须包含完整身份：

```text
(user_id, ego_browser_device_id, tool_session_id, binding_id,
 node_id, remote_platform, local_platform, generation)
```

任何请求都必须携带或由受信组件注入该绑定。客户端不能自行提交目标设备、用户、
Node、session 或授权对象。

Bridge hello 还必须提交经本地验证的 `release_profile`、签名证书 SHA-256、
`credential_profile`、`allowlist_revision` 和 `learning_bundle_digest`，并用
EgoBrowserDevice 私钥签署 challenge。Server 只接受与设备注册记录和 community release
manifest 一致的 hello；wrapper 不能替换这些字段或以开发 profile 冒充受控生产。

claim 时 Server 必须从已锁定的 `tool_session_id` 派生
`agent-remote:<tool_session_id>`，拒绝 Device Client 提交的不同 `task_space_label`，并在
claim/resume 响应中返回 canonical 值。Device Client 只有在响应中的 device、binding、
generation、authorization mode 和 label 均匹配后，才原子更新 owner-only active-binding
handoff；Bridge 不从环境或项目文件另选目标空间。

### 6.3 远端执行一轮 heredoc

1. Agent 按官方 Skill 生成 heredoc。
2. Remote wrapper 通过受信 Node-side broker 的继承 FD/受保护 Unix socket 提交当前
   tool session 的进程内 capability nonce；broker 从该 nonce 派生 binding 并返回一次性
   request permit。wrapper 构造严格的 inner request，并使用仅对本次
   request 有效的 sealing context 生成 AEAD ciphertext；wrapper 随即把 ciphertext 交给
   broker，由 broker 附加 authenticated outer envelope。sealing context 不能导出长期 ticket
   或设备私钥；脚本内容不出现在 outer metadata 或 broker 的持久化状态中。
3. Server 根据一次性 ticket 派生并验证 user/device/tool session/binding/node identity，
   校验 outer channel、request ID、generation、sequence、wire size、lease 和重放状态，
   然后只转发 inner ciphertext。
4. Local Bridge 验证 outer envelope 与 capability 的一致性，解密 inner request，严格
   校验 schema、脚本大小、timeout、默认 Task Space 标签、并发 scope、
   `allowlist_revision`、`learning_bundle_digest` 和当前 lease 后执行。
5. Bridge 在本地受控工作目录中启动真实 `ego-browser` 子进程，将脚本写入 stdin。
6. 本地进程执行脚本，ego lite 完成 Task Space、Tab、Snapshot 和输入操作。
7. Bridge 收集 stdout、stderr、退出码、受控 artifact 和耗时。
8. 结果以同样的 inner/outer 双层格式返回 Remote wrapper，再由 wrapper 输出给 fclaude。
9. 请求结束后 Bridge 清理临时目录、子进程和一次性资源。

lease 的默认时长为 60 秒，broker 在 binding 处于 `active` 且未撤销时每 20 秒自动续租；
续租只能延长到 binding 的绝对 TTL（8 小时），不能由脚本或 wrapper 自行改变。admission
前若剩余 lease 少于 20 秒，broker 必须先完成一次成功续租，否则直接拒绝请求；正在执行
的请求可在续租成功后继续，但单次 execute 仍不得超过 120 秒。续租连续失败时将 active
binding 的 lease health 标记为 `renewal_grace`，停止新请求并保留 10 秒宽限；宽限结束后
Bridge 从外部终止受监管执行单元并返回 `lease_expired`。撤销、停止和 generation 切换优先
于任何续租，不能被续租的竞态覆盖。

同一 binding 可以同时接受多个请求，但 scheduler 受 `max_parallel_requests` 硬上限
约束（MVP 默认 4，计入执行、artifact 收集和清理中的请求）。每个请求声明
`concurrency_mode` 和可解析的 Task Space/Tab scope；scheduler 按固定顺序先取得
Task Space 锁，再取得 Tab 锁。不同且可解析的 scope 可以并行；锁冲突立即返回
`concurrency_conflict`，不隐式排队。未声明、无法解析或声明 wildcard 的请求使用
binding 级锁，并在整个受监管执行单元完成前独占 binding。所有锁都绑定当前 generation
和 request permit；同类 scope 多于一个时按规范化 ID 的字典序取得、按逆序释放，禁止
反向嵌套。崩溃或撤销时由 supervisor 回收；full-trust 脚本可以绕过协作锁，因此
该机制只解决正常请求的竞态，不提供安全隔离。

### 6.4 结束、断线和接管

- 用户点击停止：立即关闭当前本地执行进程，废弃当前 request permit；若该操作使当前
  generation 失效则递增 generation，binding 保持暂停，恢复必须重新授权。
- 用户结束控制：撤销 EgoBrowserBinding、lease、relay 和本地 Bridge；不停止远端 Claude
  session。
- 远端 fclaude 结束：Server 撤销 binding；Bridge 关闭所有正在执行的本地命令。
- relay 断开：Bridge 停止当前 heredoc，禁止自动重放，等待新的明确激活。
- lease 过期或续租失败：本地不再接受新请求；active binding 进入 `renewal_grace` lease
  health 后经过 10 秒宽限，
  Bridge 从外部终止仍在运行的受监管执行单元，并返回 `lease_expired` 或
  `binding_revoked`。续租只允许 `active` 且未撤销 binding，且使用 generation/CAS 检查；
  revoke/stop 一旦提交就优先于 renewal。
- tool session stop、Node 撤销、用户禁用、EgoBrowserDevice 撤销和管理员 stop 都必须调用
  同一个 `revoke_ego_browser_binding` 事务，先递增 generation、写入持久化 outbox，再向
  所有 relay worker、broker 和 Bridge 广播；不能只停止旧 `device_session` 或等待 lease
  自然过期。
- ego lite 退出或 `ego-browser` 不可用：本地返回稳定错误，不重试危险动作。
- 用户在 ego lite 中手动接管 Task Space：Bridge 的独立 monitor 必须先从原生
  `listTaskSpaces()` 观察到 canonical 空间的 `ownership=agent` 后才 armed；随后变为
  `agentDelegatedToUser` 或 `user` 时，先 revoke admission 并等待受监管执行终止，再用旧
  generation 和 `task_space_takeover` 请求 Server pause。monitor 重复匹配、未知 ownership、
  runtime 故障或意外退出同样 fail closed，pause reason 为
  `task_space_monitor_unavailable`。Server pause 失败或超时不能恢复本地 admission。
  monitor 不调用或包装 `useOrCreateTaskSpace`、`claimTaskSpace`、`takeOverTaskSpace`，也不
  解析 helper error/stderr；Bridge 死亡通过 supervisor control-pipe EOF 终止 monitor。
  用户必须显式确认 resume 推进 generation，之后才能按意愿调用原生 helper 交还控制；
  原请求绝不重放。
- Device Client 是本地授权存活 peer：每 2 秒通过当前 UID、mode `0600` 的 Unix socket 发送
  固定 heartbeat；Bridge 要求初始 heartbeat，并以 5 秒无有效 heartbeat 为授权丢失。处理顺序
  固定为先 revoke supervisor 并终止受监管执行，再清除本地 active-binding handoff，最后尝试
  最多 10 秒的 generation-bound Server stop。stop 失败或超时不得恢复本地 admission。

## 7. Remote wrapper 设计

### 7.1 命令兼容表面

远端 PATH 中的 `ego-browser` wrapper 至少支持：

```text
ego-browser nodejs <<'EOF' ... EOF
ego-browser --doctor
ego-browser --reload
ego-browser --help
```

`nodejs` 是 Skill 期望的兼容入口；wrapper 不把它解释为远端 Node 子命令。

- `nodejs`：读取 stdin 并发送 execute request。
- `--doctor`：查询当前本地 Bridge、ego lite、relay 和版本状态。
- `--reload`：请求本地 Bridge 清理运行时连接；不得绕过授权或重建 binding。
- `--help`：输出远端 wrapper 和官方 Skill 的兼容说明。

当 broker 无法在 admission 窗口内完成续租时，`nodejs` 只返回
`lease_renewal_required`/`lease_expired`，不启动本地 `ego-browser`，也不重试原始 heredoc。

### 7.2 请求模型

协议使用长度前缀的 canonical JSON outer envelope；inner payload 为 canonical JSON 后
使用会话密钥 AEAD 加密。`max_wire_frame_bytes` 限制整个 outer frame，不能代替脚本、
stdout、stderr 和 artifact 各自的额度。

Server 可见的 outer envelope 只包含路由和反重放元数据：

```json
{
  "protocol": "ego-browser-bridge-v1",
  "channel": "ego_browser_bridge",
  "relay_binding_kind": "ego_browser",
  "type": "execute",
  "request_id": "opaque-request-id",
  "binding_id": "opaque-binding-id",
  "generation": 3,
  "sequence": 17,
  "direction": "request",
  "payload_bytes": 842,
  "nonce": "base64url",
  "ciphertext": "base64url",
  "auth_tag": "base64url"
}
```

`user_id`、`ego_browser_device_id`、`tool_session_id` 和 `node_id` 不由请求声明；Server
从一次性 ticket/受信 Node broker 的已认证 claims 派生，并将派生结果与 `binding_id`
做一致性检查。`request_id`、`sequence`、`generation` 和 channel 由 broker/受信 wrapper
生成或注入；模型、heredoc 和项目脚本不能修改它们，也不能直接提交 standalone frame。

解密后的 inner execute payload 只由 Bridge/兼容 wrapper 校验：

```json
{
  "protocol": "ego-browser-bridge-v1-inner",
  "type": "execute",
  "script": "const task = await useOrCreateTaskSpace(...)\\n...",
  "timeout_ms": 120000,
  "cwd_label": "workspace-default",
  "default_task_space": "agent-remote:<tool_session_id>",
  "concurrency_mode": "task_space_tab",
  "task_space_scope": "agent-remote:<tool_session_id>",
  "tab_scope": "target-id-or-wildcard",
  "allowlist_revision": 7,
  "learning_bundle_digest": "sha256:<digest>"
}
```

Server 必须拒绝未知 outer 字段、重复 outer JSON key、错误 channel、错误方向、无效
ticket、重复 request ID、非严格整数 sequence、旧 generation、超大 wire frame 或超过
lease 的 admission。Bridge/Remote wrapper 必须拒绝未知 inner 字段、重复 inner JSON key、
超大脚本、超长 timeout、超出 capability 的 cwd/Task Space 标签或 concurrency scope、
不匹配的 `allowlist_revision`/`learning_bundle_digest` 和无法验证的 AEAD。
Server 只能按密文长度限制 wire payload；inner 脚本字节数由 Bridge 在解密后强制限制。

`concurrency_mode` 只允许协议中声明的 `task_space_tab`、`task_space` 或 `binding`。
scope 必须是 broker capability 中的规范化 ID；请求省略 scope、使用 wildcard 或无法由
Bridge 解析时自动按 `binding` 处理，不得猜测或隐式排队。`allowlist_revision`、
`learning_bundle_digest` 和 capability 中的版本必须逐字匹配，任何漂移都返回
`protocol_error` 或 `bridge_unavailable`。

wrapper 读取 heredoc stdin 时必须采用有界流式读取，在超过 `max_script_bytes`（MVP 1 MiB）
的第一个字节立即停止并返回 `protocol_error`；不得先把无上限 stdin 读入内存。Bridge 对
解密后的 inner script 再做一次同样的字节数和 UTF-8/协议校验，stdout、stderr 和 artifact
也必须使用独立的流式上限。

### 7.3 响应模型

响应的业务内容位于加密 inner payload；outer envelope 只重复 request ID、generation、
sequence、方向、密文长度和完整性字段。以下是解密后的 inner response 示例，Server 不可见：

```json
{
  "protocol": "ego-browser-bridge-v1-inner",
  "type": "execute_result",
  "request_id": "opaque-request-id",
  "sequence": 17,
  "status": "completed",
  "exit_code": 0,
  "stdout": "...",
  "stderr": "",
  "artifacts": [],
  "duration_ms": 842
}
```

`status` 至少包括：

```text
completed
script_error
timeout
cancelled
bridge_unavailable
ego_runtime_unavailable
lease_expired
binding_revoked
protocol_error
artifact_error
concurrency_conflict
lease_renewal_required
unknown_result
```

`unknown_result` 表示本地进程可能已经产生副作用但结果无法确认。wrapper 不得自动
重放该 request；Agent 必须重新 Snapshot 或由用户决定下一步。outer envelope 的
`request_id`/`sequence` 仍必须进入持久化 ledger，避免重连时把同一 inner response 当成
新请求。

## 8. 本地 Browser Bridge 设计

### 8.1 执行方式

MVP 使用用户级 launchd 管理的 Bridge supervisor 和本地真实 `ego-browser` 子进程：

```text
Bridge
  -> launchd user agent / supervisor
  -> spawn configured ego-browser executable
  -> stdin: one heredoc script
  -> stdout/stderr: bounded capture
  -> exit status: returned to remote
```

Bridge 和 Device Client 的 plist 固定安装在 `~/Library/LaunchAgents`，文件权限为 owner-only；
安装/升级使用 `launchctl bootstrap gui/$UID <plist>`，卸载或停用先执行
`launchctl bootout gui/$UID/<label>` 再删除。未来可以增加图形化状态 UI，但 UI 不替代该
user agent、不会改变同 UID/无 sandbox 语义，也不负责承载长期 device credential。

默认每个 request 使用独立子进程。浏览器状态仍由 ego lite 保存；每轮脚本开始时
必须显式调用 `useOrCreateTaskSpace(nameOrId)`，符合官方 Skill 约定。supervisor 允许
最多 `max_parallel_requests=4` 个受监管子进程，实际启动前必须持有 broker 签发且尚未
过期的一次性 permit，并执行 Task Space/Tab 协作锁。permit 不能跨 request、generation
或 allowlist revision 复用。

后续可增加长生命周期 worker，但必须保持请求级 sequence、超时、取消和崩溃恢复，
不能因为复用 Node 进程而放宽权限。

### 8.2 本地执行上下文

Bridge 为每个 request 设置：

- 私有临时目录；
- 受控工作目录标签；
- 清理后的环境变量；
- 明确的超时和输出上限；
- request ID、EgoBrowserBinding ID 和 generation；
- 当前默认使用的 Task Space 标识或前缀，仅用于工作流选择和审计关联。
- request 的协作锁声明（Task Space 标识、Tab target ID 或显式 wildcard）；锁声明只用于
  正常请求调度，不改变 full-trust heredoc 的可访问能力。
- broker permit 的过期时间、`sequence`、`allowlist_revision`、`learning_bundle_digest`
  和 `concurrency_mode`；这些值只用于一致性校验，不能由脚本改写。

MVP 的全信任语义意味着脚本仍可能动态读取环境、导入 Node 模块或启动子进程。Bridge
不得声称 cwd、环境清理、Task Space 标签、artifact 目录或 owner-only IPC 已经限制了
这些能力。同一 UID 下的脚本还可能访问该 UID 可见的进程、文件和 Unix socket。若后续
需要限制，必须增加经过实测的 OS 级执行边界，或切换到新的受限协议/授权模式，而不是
静默改变 `ego_browser_script_full_trust` 的行为。

### 8.3 Task Space 工作流约定（非安全边界）

推荐将远端 tool session 映射到本地专用空间：

```text
agent-remote:<tool_session_id>
```

Server 在 claim 时从已认证并锁定的 tool session 派生该 canonical label，拒绝客户端不同
值；Device Client 校验 claim/resume 响应后将 label 写入 owner-only handoff。Node broker
从 session nonce 独立派生同一 label 并写入一次性 permit，wrapper 不信任 environment
override。Bridge 从 handoff 加载目标并拒绝 request `default_task_space` 或声明 scope
不匹配。

官方 Skill 脚本仍调用 `useOrCreateTaskSpace`；Bridge preamble 只将该调用的参数重映射为
canonical label，不在激活时或脚本前 eager-select 空间。官方 Skill 的默认脚本不得自动
claim user-owned 空间，也不得主动切换或关闭目标空间以外的 Tab。

以上规则只约束官方 Skill 和正常 wrapper 工作流。full-trust heredoc 可以直接调用
`listTaskSpaces`、`claimTaskSpace`、`takeOverTaskSpace`、Tab helper、原始 CDP 或 native
`globalThis.ego` 方法，因此 Bridge 不能以 Task Space 名称、前缀或脚本静态检查作为授权
边界。用户授权的是 Bridge 运行身份下的完整 Node/ego lite 能力，不是单一 Task Space。

Bridge 使用独立受监管 `ego-browser` runtime 只调用 `listTaskSpaces()`、读取 canonical 空间
的原生 `ownership`。它先观察到 `agent` 才 armed；随后
`agentDelegatedToUser`/`user` 才是接管。空间尚不存在或初始 user-owned 不触发误判；重复
匹配、未知状态或 monitor 失效则 fail closed。用户接管时，Bridge 先从外部 revoke admission
并等待受管执行终止，再按准确 generation 将 `EgoBrowserBinding` 置为 `paused`。原生 helper
错误只作为脚本状态，不能驱动接管判断；monitor 不调用/wrap claim、takeover 或 create helper。
恢复要求用户明确确认新 generation，可按用户决定使用仍为原生语义的 helper 交还 ownership。

### 8.4 截图和 artifact

ego-browser 的 `screenshot()` 默认返回本地文件路径，而远端无法直接读取该路径。
MVP 必须实现受控 artifact 传输：

1. Bridge 为 request 设置私有临时 artifact 目录。
2. 默认截图路径必须落在该目录内。
3. Bridge 只收集该目录内的 PNG/JPEG，应用大小、像素数和总字节上限。
4. 响应携带 `artifact_id`、媒体类型、大小和内容；不发送任意本地路径。
5. Remote wrapper 把 artifact 写入远端私有临时目录，并在输出中返回远端路径。
6. request 结束后本地和远端临时文件都清理。

Bridge 的自动 artifact 收集只接受私有临时目录内、通过媒体类型和大小校验的文件；
目录外的 screenshot 不进入 artifact 响应。`setInputFiles` 和 `download.saveAs` 只有在
目标路径经过用户配置的 canonical path allowlist 校验时才允许。allowlist 由 Device Client
保存为规范化的绝对根目录集合，并带单调递增的 `allowlist_revision`；远端脚本不能创建、
删除或修改根目录。

每次文件操作都必须：

1. 对根目录、父目录和目标执行 `realpath`/等价 canonicalize；拒绝 `..` 路径穿越、任何
   符号链接组件、父目录不存在或 canonical path 逃出已确认根目录。
2. 对输入源打开时使用 `openat`/`O_NOFOLLOW`/等价检查，并用 `fstat` 比对 canonical
   inode，确认是当前用户可读且 `st_nlink=1` 的 regular file；拒绝目录、FIFO、socket、
   设备文件、硬链接和其他非 regular file，避免检查与实际读取之间的 TOCTOU/替换。
3. 对 `download.saveAs` 先 canonicalize 已存在的父目录，再以不跟随符号链接的方式创建或
   替换目标；目标文件和临时文件都必须仍在根目录内。
4. 在单文件、单 request 总量和文件数量上限内读取/写入；超过任一上限立即返回
   `artifact_error` 或 `protocol_error`，不得部分绕过限制。

capability、inner request 和审计元数据都绑定当前 `allowlist_revision`。Device Client
修改 allowlist 必须由用户明确确认，采用 CAS 更新 revision，并使旧 permit/capability
失效或要求重新激活；Server、broker 和 Bridge 必须拒绝 revision 不一致的请求。

由于本模式是 full trust，这项规则只限制 helper 的文件输入和 Bridge 自动上传器，不能
阻止脚本使用 Node 文件 API、stdout 或网络读取和外发任意可访问数据。UI 和安全文档必须
明确区分“helper allowlist”与“本机文件安全边界”。

### 8.5 Site Learnings

远端安装 Skill 不会自动使本地运行时拥有 Site Learning。部署必须保证本地 Bridge
可读取与本地 ego-browser runtime 兼容的、只读的固定版本 bundle：

```text
skills/ego-browser/
  agent_helpers.js
  learnings/<site>/manifest.json
  learnings/<site>/notes/
  learnings/<site>/tools/
  learnings/<site>/browser-tools/
```

MVP 只采用 Bridge 安装包携带的本地 learning bundle（或同一发布物中的固定资源），
不从控制面或远端脚本同步、覆盖或执行未验证文件。manifest 至少包含 bundle 版本、
`skill_version`、`local_ego_browser_runtime_version`、协议兼容矩阵、每个文件的相对路径、
大小和 SHA-256，以及发布签名。Bridge 安装/启动前使用内置公钥验证签名、manifest 和
所有文件 hash，并计算覆盖 canonical manifest 与文件清单的 `learning_bundle_digest`；
校验失败时 binding 不得激活。验证通过的 bundle 放在 Bridge 管理的只读目录，每次
binding 激活和每次 relay 恢复都重新验证 manifest、版本、签名和 digest，并把
`learning_bundle_digest` 写入 capability/audit metadata。任何 digest 漂移都暂停 binding
并撤销旧 permit。`EGO_BROWSER_AGENT_WORKSPACE` 不能把远端路径注入本地 runtime；远端
脚本也不能覆盖 Bridge 管理的 learning workspace。

## 8.6 官方依赖和自行实现边界

### 必须使用/安装的官方组件

| 组件 | 安装位置 | 方式 |
| --- | --- | --- |
| ego lite | 本地 macOS | 用户安装官方应用；Bridge 只检测和调用，不重新打包 |
| `ego-browser` Skill | 远端 Linux Claude Native Runtime 或 Docker Sandbox | `agent-remote-node` 安装器预装固定版本，用户不需要手动 `npx skills add` |
| `ego-browser` runtime | 本地 ego lite 安装中 | 使用官方随应用提供的命令/Bundle，不从远端下载替代品 |
| Claude Code | 远端 Native Runtime 或 Docker Sandbox | 使用现有受管 Claude 安装流程 |
| Node.js | 本地 `ego-browser` 运行时/远端必要工具 | 使用 ego lite 或现有受管 runtime 的兼容版本 |

### 必须自行实现的组件

| 组件 | 所属仓库 | 推荐语言 |
| --- | --- | --- |
| remote `ego-browser` wrapper | `agent-remote-ego-browser` | Rust/Tokio |
| local Browser Bridge | `agent-remote-ego-browser` | Rust/Tokio |
| frame schema、版本、序号和错误码 | `agent-remote-ego-browser` | Rust serde 类型 + JSON Schema |
| relay channel 适配 | `agent-remote-server` / `agent-remote-ego-browser` | Python 服务端 + Rust 客户端 |
| 远端 Skill 安装和 PATH 注入 | `agent-remote-node` | Go |
| 绑定、状态和诊断命令 | `agent-remote-cli` | Rust |
| 本地用户选择和授权入口 | `agent-remote-ego-browser` | Rust/Tokio CLI + macOS user agent；不依赖 `agent-remote-device` |

### 明确不自行实现的部分

- 不重写 Chromium。
- 不模拟 `globalThis.ego`。
- 不在远端运行另一个浏览器。
- 不 fork 官方 `ego-browser` Skill；只固定版本、安装并通过 wrapper 提供命令入口。
- 不使用 Puppeteer/Playwright 代替 ego-browser 的 CDP runtime。
- 不把本地浏览器 profile、Cookies 或 Claude 登录态同步到远端。

### 远端默认安装策略

`agent-remote-node` 创建或更新 Claude Native Runtime 或 Docker Sandbox 时必须：

1. 安装固定版本的官方 `ego-browser` Skill 到受管 skill workspace。
2. 安装固定版本的 `agent-remote-ego-browser` remote wrapper。
3. 在 Claude runtime 的 PATH 中将 wrapper 注册为 `ego-browser`。
4. 写入 wrapper 所需的非秘密配置：控制面地址、协议版本和 runtime 标识。
5. 不写入本地设备 token、relay ticket 或长期私钥。
6. 在没有 active browser binding 时，wrapper 返回明确的 `bridge_unavailable`，不启动远端浏览器。
7. 远端 runtime 的 `remote_platform` 必须为 `linux`，只安装 Linux wrapper 制品；
   `local_platform` 必须为 `macos`。

Skill 与 wrapper 必须随 Node release 一起 pin 和升级；版本不一致时节点报告 capability
不兼容，Server 禁止新建 binding。

### 本地安装策略

本地安装器必须：

1. 检查本地 macOS 平台和 ego lite 官方应用是否存在。
2. 检查真实 `ego-browser` 命令、Bundle 版本和最小支持版本。
3. 根据下方 macOS build profile 安装新仓库提供的 Browser Bridge 和独立 Device Client；
   `community-local-trust` 的已验证制品可以用于受控生产，未签名或 ad-hoc
   `development_local` 制品不得被标记为生产制品。
4. 将 Bridge 注册为当前用户的 `LaunchAgents`；Device Client 负责首次注册、候选 session
   展示和明确绑定。
5. 不下载或替换 ego lite 应用，不复制浏览器 profile。
6. ego lite 缺失、版本过低、命令不可执行、learning bundle 校验失败或 profile 与
   capability 不兼容时，阻止 binding 并给出安装/升级提示。

### macOS build profile 与当前签名限制

本项目当前没有 Apple Developer ID。参照 `agent-remote-device` 的 community release
流程，默认生产 profile 是无需 Apple 账号的 `community-local-trust`；它可以在受控生产
环境启用 capability，但不等于 Apple notarization 或公共分发。各 profile 必须明确区分：

| profile | 允许的用途 | 签名/安装 | Server capability |
| --- | --- | --- | --- |
| `logic_test` | Rust 协议、状态机、fuzz 和 fake relay | 可运行未签名二进制，不访问 ego lite/TCC/真实 Keychain | 永久关闭 |
| `development_local` | 单机和受控测试机上的真实 Bridge/Device Client | 参考 community development 流程，优先 ad-hoc `codesign --sign -` 并执行 deep/strict 验证；没有 `codesign` 时只允许手工前台运行 | 关闭；仅本地开发控制面显式开启 |
| `community-local-trust` | 受控生产环境的 Bridge/Device Client | 持久项目自签证书、Hardened Runtime、嵌套签名和严格校验；安装器/验证 CLI 固定证书指纹并要求用户明确建立本地信任；不需要 Apple Developer 或 notarization | 通过下列 release evidence 后可开启 |
| `developer_id`（可选未来 profile） | Apple 生态分发或更强平台信任 | Developer ID Application、Hardened Runtime、notarization、stapling 和相应安装/更新证据 | 通过更严格门禁后可开启 |

`development_local` 的 ad-hoc/未签名制品不是 Apple 信任的应用，不得宣称 TCC、IPC、
Keychain access group 或进程隔离已被证明；真实浏览器测试应使用 disposable ego lite
profile 和测试数据。其 launchd plist 必须由用户手动 `launchctl bootstrap gui/$UID`，
并使用绝对可执行文件路径、固定版本/hash 和私有日志目录；卸载先 `bootout` 再删除。

`community-local-trust` 生产门禁至少要求：持久私钥不进入仓库或发布物；应用及嵌套
Bridge/Device Client 组件的签名、Hardened Runtime、bundle version 和证书 SHA-256/指纹
均可复核；在受保护的官方 macOS runner（或等价可审计构建器）上使用持久项目签名身份，
安装包、SBOM、源码 provenance、更新签名和 checksum 可追溯；应用层出口目标
检查和 owner-only 凭据文件权限测试通过；协议、fuzz、fail-closed、并发、租约、撤销和
兼容性测试通过；community profile 的 relay/更新出口使用应用层固定的 HTTPS/WSS 目标
allowlist，不依赖 Apple Network Extension 或系统级签名出口策略；安装器在用户确认后固定
叶证书指纹并移除相应 quarantine。发布记录必须
明确 `production_ready=true`、`profile=community-local-trust`、`apple_notarized=false`
和 `public_distribution=false`，不能把项目自签说成 Apple 信任链。证书轮换必须先发布
新指纹、验证双版本兼容窗口，再撤销旧指纹。
该出口 allowlist 只约束 Bridge 的控制面/更新连接，不限制 full-trust `ego-browser` 子进程
自身发起的网络请求；后者仍按已确认的本机 Node 全信任风险处理。

实现可以参考 `agent-remote-device` 的 community/development 流程：
`scripts/build-community-release-app.sh`、`scripts/verify-packaged-xpc.sh`、
`scripts/build-development-app.sh`、`scripts/verify-development-xpc.sh`、
`docs/release-signing.md` 和 `docs/macos-security.md`
中的 profile、版本、deep/strict 验证、community credential fallback 和“开发制品不等于
生产制品”逻辑，但不得链接、安装或运行 `agent-remote-device` 的代码。没有 Apple
Developer 时，Server 仍可在上述 community release evidence 完整且用户已建立证书信任
后开启 `ego_browser_bridge_enabled`；若证书指纹、manifest、凭据权限或任一门禁失效则
必须关闭。开发控制面即使开启 capability，也必须在审计中标为 `development_local`。

## 9. 授权和安全模型

### 9.1 新授权模式

在独立的 EgoBrowserBinding 授权枚举中新增显式模式：

```text
authorization_mode = ego_browser_script_full_trust
authorization_policy_version = 1
```

不要复用 `session_full_trust`。后者表示本机任意 GUI 应用控制；本模式表示本地
ego-browser Node 脚本全信任，两者的权限对象、UI 警告、capability 和撤销路径不同。

授权说明必须明确显示：

> 远端 fclaude 可以在本地执行 ego-browser heredoc。脚本不只能够控制浏览器，
> 还可以使用 Bridge 运行身份能够访问的文件、环境、网络、浏览器登录数据、Node 模块
> 和子进程。Task Space 不是安全隔离；脚本可能控制用户的其他 Tab 或 Task Space，并将
> 读取到的数据发送到远端。停止控制不会撤销已经产生的副作用。

### 9.2 授权前提

Server 只有在以下条件全部满足时才激活 binding：

- 用户明确选择远端 fclaude session；
- EgoBrowserDevice token 属于当前用户和当前 ego-browser 设备；
- tool session 处于 `running`、`active` 或 `detached`；
- 设备在线且 Bridge 能力版本兼容；
- 本地 ego lite 和真实 `ego-browser` 探测成功；
- release profile、证书指纹/签名证据和 `credential_profile` 与控制面策略一致；
- `allowlist_revision` 与已确认的本地 allowlist 一致，`learning_bundle_digest` 已通过
  manifest、文件 hash、版本和签名校验；
- 不存在其他 live browser binding；
- relay、TLS 1.3 和新仓库定义的 E2E 通道已建立；
- binding 为 `active/healthy`，lease 和绝对 TTL 有效，且 admission 时剩余时间不少于最小
  窗口，或已完成一次成功续租；`active/renewal_grace` 只允许 renewal/cleanup。

### 9.3 不可绕过的绑定字段

每个 relay 握手和 execute request 必须校验：

```text
user_id
ego_browser_device_id
tool_session_id
binding_id
node_id
remote_platform=linux
local_platform=macos
generation
monotonic_sequence
task_space_label=agent-remote:<tool_session_id>
```

ID 不是凭证。请求不能从模型参数、heredoc 内容、环境变量或项目仓库中取得身份字段。

### 9.4 传输安全

- 本地 Bridge 只发起出站连接。
- Server relay 只解析 authenticated outer envelope；不解密或记录 inner 脚本、stdout、
  截图、artifact 或页面内容。
- 使用独立 Bridge 的 TLS 1.3 transport、inner payload AEAD、短期 relay ticket 和
  EgoBrowserDevice proof-of-possession；凭据按 `credential_profile` 存储，community profile
  使用 owner-only 文件/独立 service，不假设 Apple access group。具体算法、密钥轮换和
  transcript binding 写入 ADR。
- 每条 execute request 使用由 ticket/broker 绑定的单调 sequence，Server 和 Bridge 都
  拒绝重放和双活；sequence 状态写入持久化 ledger，不只存在于进程内存。
- relay ticket 一次性兑换，重连必须重新签发短期材料。
- Server、Node、EgoBrowserBinding 或用户撤销后，旧 generation 的帧全部失效。
- broker 仅为 active、未撤销 binding 续租；每次续租使用 expected generation/lease 的
  CAS，撤销或 stop 与 renewal 冲突时以撤销为准。
- Server 只能依据 outer metadata 做 admission 和限额；所有 inner schema、AEAD、脚本和
  artifact 语义校验必须在 Bridge/Remote wrapper 完成。

### 9.5 本机进程安全

由于 MVP 是全信任脚本执行，Bridge 必须：

- MVP 明确与当前 macOS 登录用户同 UID 且不启用 App Sandbox；授权 UI 必须在绑定前和
  每次恢复时标注“该 session 获得当前 macOS 用户可访问的本机代码执行权”。这不是
  浏览器 sandbox，不能用于承诺文件、凭据、网络或 Task Space 隔离；若未来要提供更强
  隔离，必须另立授权模式和 profile/运行身份方案。
- 不把用户 shell 环境、SSH agent、云凭据和 Anthropic token 注入子进程；
- 清除 `PATH`、代理、云凭据和未授权 secret 环境变量；
- 将 cwd、临时目录和可上传 artifact 限制在显式路径；
- 不把脚本内容、输入内容、环境变量或命令输出写入普通日志；
- 使用有界 stdout/stderr 缓冲，防止远端脚本耗尽内存；
- 使用独立的受监管执行单元和外部 supervisor；超时、撤销和用户接管时终止整个执行单元；
- 使用进程组取消作为最低实现，并明确记录同 UID full-trust 脚本可以主动创建脱离进程组
  的 daemon；MVP 不承诺此类进程一定被清除，也不把 supervisor 当作安全边界；
- Bridge 崩溃、launchd peer 丢失或本地控制客户端退出时，由独立 supervisor 尽力清理
  仍受监管的执行单元，并报告无法确认清理的状态。

环境清理、私有目录和进程组不能把全信任变成浏览器 sandbox；它们只降低意外泄漏和
普通残留进程的概率。正式发布前仍必须实测 ego lite IPC、文件访问、同 UID Unix socket
和子进程逃逸，并将结果作为风险证据；通过这些测试不代表获得文件、凭据、Task Space
或残留进程隔离。

### 9.6 高风险浏览器动作

MVP 不实现可靠的语义动作分类器，因此不能声称自动识别“付款”“发送”“删除”等
动作。产品 UI 必须显示全信任警告；后续可以在 Agent 层增加用户确认，但不能把确认
逻辑伪装成本地 Bridge 已经阻止了任意脚本。

## 10. 状态机

### 10.1 EgoBrowserBinding

```text
pending_device
  -> connecting
  -> probing_local_browser
  -> active
  -> paused
  -> stopping
  -> stopped

pending_device / connecting / probing_local_browser / active / paused
  -> expired
  -> failed
  -> revoked
```

`active` 另有 lease health 子状态：

```text
healthy -> renewal_grace -> expired
```

`renewal_grace` 不是可执行的独立 binding 状态；它表示 binding 仍为 `active` 但暂时拒绝
新请求，等待当前 renewal CAS 在宽限期内成功。宽限结束后 binding 进入 `expired`。

状态约束：

- 只有 `active/healthy` 接受 execute request；`active/renewal_grace` 只允许当前 renewal
  CAS 和清理，不接受新请求。
- `paused` 不接受脚本，等待用户明确恢复。
- `task_space_takeover` 与 `task_space_monitor_unavailable` 都先在本地 revoke admission 和终止
  受管执行，再让 generation-bound pause 推进 generation；pause 请求无法确认也不恢复本地
  admission。
- `active/healthy` 由 broker 按续租间隔自动续租；`active/renewal_grace` 不接受新请求，
  只允许当前 broker renewal CAS 在宽限内成功，成功后回到 `healthy`，否则进入 `expired`。
- `paused` 不自动续租；恢复必须重新检查 capability、digest、allowlist revision 和 lease。
- `paused` 的明确恢复保留 Server 派生的 canonical Task Space label，重新确认 full trust 并
  创建新 generation；不自动 claim/takeover 或重放被中断脚本。
- `stopping`、`stopped`、`expired`、`failed`、`revoked` 不能恢复旧 generation。
- `pending_device` 超时后进入 `failed`，不能由远端 wrapper 自行重试 claim。
- lease health、`expired` 和 `revoked` 的 transition 与 revoke/stop 使用同一 CAS；renewal
  不能把终态或旧 generation 改回 `active`。

### 10.2 本地执行状态

```text
idle
  -> accepting
  -> running
  -> collecting_output
  -> completed

accepting / running / collecting_output
  -> cancelled
  -> timed_out
  -> binding_revoked
  -> bridge_failed
  -> unknown_result
```

`unknown_result` 是终态。任何可能已经提交浏览器动作的 timeout 或 relay 断线都不能
直接自动重新提交原始脚本。

## 11. 版本和能力协商

### 11.1 版本字段

至少协商（`remote_platform` 固定为 `linux`，`local_platform` 固定为 `macos`）：

```text
bridge_protocol_version
remote_wrapper_version
local_ego_browser_runtime_version
ego_lite_runtime_version
skill_version
release_profile
signer_certificate_sha256
credential_profile
allowlist_revision
learning_bundle_digest
max_parallel_requests
remote_platform
local_platform
```

MVP 要求远端 Linux Skill 版本和本地 macOS runtime 处于受支持兼容矩阵。版本不兼容时返回
`EGO_BROWSER_VERSION_MISMATCH`，不能静默降级到远端浏览器或原始 CDP。

### 11.2 能力

第一版能力建议：

```text
ego_browser_script_execute_v1
ego_browser_snapshot_v1
ego_browser_screenshot_artifact_v1
ego_browser_task_space_v1
ego_browser_concurrency_v1
ego_browser_file_allowlist_v1
ego_browser_site_learning_v1
```

后续可以独立增加：

```text
ego_browser_persistent_worker_v1
ego_browser_structured_ops_v1
```

`ego_browser_file_allowlist_v1` 只有在 capability 携带已确认 revision 且每个 helper 操作
通过 canonical path 检查时才可广告；`ego_browser_site_learning_v1` 只有在本地 bundle
签名、版本、文件 hash 和 digest 全部通过时才可广告。能力缺失或 profile/证据不匹配时
必须 fail closed。不能因为远端脚本调用了不存在的 helper 就自动改走桌面 GUI、远端浏览器
或通用 shell。

### 11.3 MVP 平台兼容矩阵

| 组件 | Linux remote runtime | macOS local device |
| --- | --- | --- |
| 官方 `ego-browser` Skill | 支持 | 不安装为远端 Skill |
| `ego-browser-remote` wrapper | 支持 | 不适用 |
| `ego-browser-bridge` | 不运行 | 支持 |
| 独立 Device Client | 不运行 | 支持 |
| ego lite Chromium/profile | 不运行 | 用户安装并运行 |
| Bridge release profile | 不适用 | `community-local-trust`（受控生产）或 `development_local`（仅开发） |

远端 Linux 的 CPU 架构由受管 Node runtime 决定；发布流水线至少应覆盖当前实际使用的
Linux 架构，并为每个 target 生成独立 checksum 和签名。

## 12. API 和控制面变更

### 12.1 独立 EgoBrowser 数据模型

Server 不复用其他设备控制模块的 `device_sessions` 实体。新增独立表/集合，
并仅复用通用的 `users`、`nodes` 和 `tool_sessions`：

```text
ego_browser_devices
ego_browser_bindings
```

`ego_browser_devices` 保存设备公钥、能力、版本、在线状态和撤销信息；设备注册、
心跳和撤销均由新仓库的 Device Client 发起或确认。
`ego_browser_bindings` 保存一次远端 session 到本地 Task Space 的授权绑定。

`ego_browser_bindings` 的核心字段如下：

| 字段 | 语义 |
| --- | --- |
| `user_id` | 绑定所属用户 |
| `binding_id` | 独立绑定 ID |
| `ego_browser_device_id` | 独立设备 ID |
| `tool_session_id` | 远端 fclaude tool session |
| `node_id` | 承载远端 wrapper 的 Node |
| `status` | `pending_device`/`active`/`paused`/`stopped` 等状态机状态 |
| `control_channel` | `ego_browser_bridge` |
| `relay_binding_kind` | 固定为 `ego_browser`，用于通用 relay 的独立 key/claims |
| `authorization_mode` | `ego_browser_script_full_trust` |
| `authorization_policy_version` | 固定为 `1` |
| `release_profile` | `community-local-trust`（受控生产）或 `development_local`；由设备证明，不能由 wrapper 声明 |
| `signer_certificate_sha256` | 已验证制品的签名证书摘要；用于安装和更新指纹固定 |
| `credential_profile` | `community_file`、`keychain_access_group` 等受支持凭据后端 |
| `remote_platform` | MVP 固定为 `linux` |
| `local_platform` | MVP 固定 `macos` |
| `local_runtime_version` | 最近一次本地探测版本 |
| `bridge_protocol_version` | 当前 Bridge 协议版本 |
| `task_space_label` | 脱敏后的本地空间标签，可选 |
| `allowlist_revision` | 用户确认的 canonical path allowlist 版本 |
| `learning_bundle_digest` | 已验证本地 Site Learning bundle 的摘要；未使用时为 `null` |
| `concurrency_mode` | 支持的默认并发 scope 模式 |
| `max_parallel_requests` | binding 的并发硬上限，MVP 默认 `4` |
| `lease_until` | 当前短期租约 |
| `lease_health` | `healthy`/`renewal_grace`；仅 `active/healthy` 接受 execute |
| `lease_renew_interval_seconds` | 自动续租间隔，MVP 固定 `20` |
| `lease_renew_failure_grace_seconds` | 续租失败后的宽限，MVP 固定 `10` |
| `absolute_ttl_until` | binding 不可超过的绝对截止时间（MVP 为激活后 8 小时） |
| `generation` | 连接/撤销代次 |

`task_space_label` 不得包含本地绝对路径、用户名、Cookie、页面内容或脚本内容。

claim 必须在事务中以 CAS 原子检查唯一 live binding（同一用户/设备只能有一个 active
binding，tool session 也只能指向一个 live binding），写入初始 generation、lease、
allowlist revision 和 learning digest，并投递 outbox/revocation 事件。renew、pause、stop
和 revoke 都必须携带 expected generation；任何旧 generation 或重复 claim 都失败，不能
通过不同 worker 或重试产生第二个 live binding。

### 12.2 建议 API

使用独立的 ego-browser binding API；这些接口不调用其他设备控制模块的 session API：

```text
GET  /api/v1/ego-browser/devices
POST /api/v1/ego-browser/devices/register
GET  /api/v1/ego-browser/bindings/candidates
POST /api/v1/ego-browser/bindings/claim
POST /api/v1/ego-browser/bindings/{binding_id}/connected
POST /api/v1/ego-browser/bindings/{binding_id}/relay
POST /api/v1/ego-browser/bindings/{binding_id}/renew
POST /api/v1/ego-browser/bindings/{binding_id}/stop
POST /api/v1/ego-browser/bindings/{binding_id}/revoke
GET  /api/v1/ego-browser/bindings/{binding_id}/allowlist
POST /api/v1/ego-browser/bindings/{binding_id}/allowlist/confirm
```

allowlist 查询可以由状态 UI 使用，但 `allowlist/confirm` 只接受 Device Client 的设备签名
和一次性用户确认 nonce；远端 Node、wrapper、管理员 API 或 heredoc 不能代替该确认。

远端 wrapper 使用的 relay data channel 不应暴露给普通 HTTP 客户端；它必须通过
已认证 Node/proxy 与独立 Bridge relay client 进入 `ego_browser_bridge` 通道。WebSocket
route 必须按 `relay_binding_kind=ego_browser` 和 `binding_id/generation` 查找通用
`EgoBrowserRelayBinding`，不能复用旧 `device_session_id` route；同一 binding 的两端只能
各有一个有效 endpoint，跨 worker 由共享状态或 sticky routing 保证。

`renew` 只接受 `active` 且未撤销 binding，并要求 broker/Device Client 的 proof、expected
generation、当前 digest/revision 和绝对 TTL 都匹配；成功后返回新的 `lease_until`。剩余
lease 小于 admission 窗口时，Server 不接受 execute，除非同一 CAS renewal 已先成功。
`stop`（binding-level）用于停止整个 binding，`revoke` 用于不可恢复地撤销 binding；
用户点击“停止当前请求”则只取消该 request 的 permit。binding-level stop/revoke 都幂等且
优先级更高，必须先写撤销 outbox、递增 generation，再广播到所有 worker/broker/Bridge。
renew 与 stop/revoke 的竞态以 stop/revoke 为准；恢复必须重新获得明确授权和新 generation。

### 12.3 审计事件

允许记录：

```text
ego_browser_binding.created
ego_browser_binding.activated
ego_browser_binding.paused
ego_browser_binding.renewed
ego_browser_binding.renewal_failed
ego_browser_binding.stopped
ego_browser_binding.revoked
ego_browser_bridge.connected
ego_browser_bridge.disconnected
ego_browser_execute.accepted
ego_browser_execute.completed
ego_browser_execute.failed
ego_browser_execute.timeout
ego_browser_execute.cancelled
ego_browser_artifact.returned
ego_browser_allowlist.updated
ego_browser_learning.verified
```

审计字段只包括用户、EgoBrowserDevice、EgoBrowserBinding、tool session、Node、generation、sequence、
协议版本、release profile、证书摘要、credential profile、allowlist revision、learning
bundle digest、并发模式、字节数、耗时、状态和 request ID。禁止记录：

- heredoc 内容；
- stdout/stderr 正文；
- Snapshot 和截图内容；
- URL、标题、Cookies、Token、输入值；
- 本地文件路径、环境变量和命令参数。

## 13. 跨仓库实施分工

### 13.1 `agent-remote`

- 保留本文作为跨仓库契约。
- 更新 `agent-remote-architecture.md` 的浏览器控制边界。
- 更新 `agent-remote-implementation-appendix.md` 的组件和协议索引。
- 更新 `deployment.md`、安全文档和发布说明。
- 在 `release-manifest.json` 中固定各组件兼容版本。
- 在 release manifest 中记录 `community-local-trust` profile、证书 SHA-256、
  `signing_type=project-self-signed`、`outbound_policy=application-enforced`、
  `production_ready`/`apple_notarized`/`public_distribution` 状态和 learning bundle digest；
  Server 的生产 capability 门禁只接受可复核的 manifest。
- 增加跨仓库 E2E 验收清单和回滚流程。

### 13.2 `agent-remote-server`

- 增加 `control_channel=ego_browser_bridge` 和授权模式 schema。
- 增加独立 EgoBrowserBinding claim、activation、renew、stop 的通道校验。
- claim 从 `tool_session_id` 派生 canonical Task Space label，拒绝 mismatch，并在 claim/resume
  响应中返回该值；Device pause 保留有界 takeover/monitor failure reason。
- 在 relay hub 中增加 outer envelope 的认证转发和 inner ciphertext 的 opaque forwarding。
- 实现 ticket 派生 identity、lease、generation、sequence、持久化重放 ledger 和双活检查。
- 抽象通用 `RelayBinding`，为 `ego_browser` 使用独立 key namespace、claims、route 和
  revocation propagation；保留旧 device relay 行为兼容，不把两种 binding 混用。
- 为 renewal 实现 20 秒 interval、10 秒 failure grace、admission 最小剩余窗口和
  absolute TTL/CAS；stop/revoke 必须优先于 renewal。
- 持久化 `allowlist_revision`、`learning_bundle_digest`、`credential_profile`、
  `release_profile` 和并发 capability；变更通过 outbox 广播并使旧 permit 失效。
- 将 tool session stop、用户禁用、Node/设备撤销和管理员 stop 全部接入
  `revoke_ego_browser_binding`；撤销事件必须跨 worker 幂等投递，不能依赖旧
  `device_session_id` 的联动实现。
- 增加 relay 连接数、单帧大小、总吞吐和执行超时策略。
- 保持控制面不解析脚本和页面内容。
- 增加迁移、API、审计和撤销联动测试。

### 13.3 `agent-remote-node`

- 在远端 tool session 中安装并校验官方 `ego-browser` Skill。
- 安装 `ego-browser` wrapper，并保证命令名兼容 Skill。
- 在受信 Node daemon 中实现 Node-side broker；它负责兑换/续期短期 relay ticket、保存
  binding claims、分配 sequence、签发一次性 request permit，并通过继承 FD 或受保护
  Unix socket 向 wrapper 提供最小 IPC。broker 在内存中保存 ticket，按 active/未撤销状态
  自动续租，且把 `allowlist_revision`、`learning_bundle_digest`、并发 scope 和额度绑定
  到 permit。ticket、长期私钥、inner 明文和 relay URL 不进入 Claude runtime 的环境、
  argv、workspace 或日志。
- broker 必须验证 peer UID、绑定到精确 `tool_session_id` 的进程内 nonce、协议版本和单调
  sequence；wrapper 不能提交 `binding_id`，session 可先于 claim 创建并在刷新后获得 binding；
  permit 只能消费一次，
  不能被 wrapper 复制到另一个进程或跨 generation 使用。broker 崩溃、连接断开、stop/revoke
  或 revision/digest 漂移时清零短期材料并拒绝新请求。
- 将 wrapper 和远端 fclaude session 绑定到正确的 EgoBrowserBinding relay；wrapper 只能
  通过 broker 提交 outer envelope，不能自行声明 user/device/session/Node 身份。
- 管理 wrapper 进程的 stdout/stderr、超时和退出码。
- 禁止 wrapper 直接打开本地或任意公网回连端口。
- 增加版本探测、连接恢复、permit 撤销、旧 session 清理和 broker 崩溃后的旧 generation
  失效。
- 在 Native Runtime 与 Docker Sandbox session 中注入经过校验的 wrapper、官方 Skill、broker
  socket/nonce 和专用 Task Space；使用 runtime helper 返回的非 root UID 配置最小 ACL，并以
  `SO_PEERCRED` 做最终 peer 授权。Docker 还必须绑定 root-owned trusted spec 与准确 mount；
  任一 backend 的 identity、spec、mount 或 capability 不匹配时 helper fail closed。

### 13.4 `agent-remote-cli`（默认集成）

- 增加 `agent-remote ego-browser status` 或等价诊断输出；该命令只调用独立
  ego-browser API，不进入其他设备控制流程。
- 展示本地 ego lite/Bridge 是否可用。
- 提供明确的绑定、暂停、恢复和结束控制命令。
- 保存 device/session/generation/relay 状态，不保存 connection token 和脚本。
- 保持 `fclaude` 原生参数透传，不把浏览器脚本改写到 Claude 参数中。
- 随 `agent-remote` 默认发行包安装或启用该集成；CLI 不负责启动本地 Bridge，
  也不替代新仓库的 Device Client 授权流程。

### 13.5 `agent-remote-device`（明确不参与）

本方案不修改、不安装、不启动也不链接该仓库。它不提供 ego-browser 的设备注册、
用户授权、relay、Bridge、XPC、Keychain、GUI Executor 或协议实现。任何实现、测试、
发布和回滚步骤都必须能在 `agent-remote-device` 完全缺失时完成。

### 13.6 新建 `agent-remote-ego-browser`

- 发布 `ego-browser-remote` wrapper 和 `ego-browser-bridge` 本地 Bridge。
- 发布共享的 Rust protocol crate、JSON Schema、测试向量和错误码。
- 实现 stdin heredoc framing、relay client、request guard、进程组取消和有界输出。
- 实现真实本地 `ego-browser` 探测、子进程启动、artifact 收集和临时目录清理。
- 实现 Node-side broker permit 协议、Task Space -> Tab 协作锁、`max_parallel_requests`
  限流、lease 自动续租和 revoke/stop 优先级。
- 实现 owner-only active-binding label handoff、request label/scope 精确校验，以及仅调用原生
  `listTaskSpaces()` ownership 的独立受监管 monitor；接管/monitor 故障按“revoke admission
  -> 等待执行终止 -> generation-bound pause”处理，禁止自动 claim/takeover 和 helper-error
  推断。
- 实现 canonical path allowlist、`allowlist_revision`、symlink-safe 文件操作，以及固定
  Site Learning bundle 的 manifest/签名/hash/digest 校验。
- 提供 macOS local Bridge 和 Linux remote wrapper 的 target build；MVP 不发布其他远端
  wrapper target。
- 提供独立安装器和 checksum/signature；支持 `community-local-trust` 的证书指纹固定、
  owner-only credential fallback 和可复核 release evidence；不打包 ego lite 或官方 Skill。
- 维护与 `agent-remote-server`、`agent-remote-node` 的兼容矩阵；不建立与
  `agent-remote-device` 的版本或运行时兼容关系。

### 13.7 `agent-remote-admin-web`

- 展示用户自己的 browser binding、设备、远端 session、版本和状态。
- 提供停止/撤销入口，不显示脚本、页面正文、截图或本地路径。
- 在首次绑定和状态页面展示全信任脚本执行警告。
- 管理员可以清理异常 binding，但不能读取用户脚本和页面数据。

## 14. 实施阶段

### Phase 0：本地单机 PoC

目标：不接控制面，验证“远端 wrapper -> 本地真实 ego-browser”机制。

- 创建 `agent-remote-ego-browser` Rust workspace，包含 `protocol`、`remote-wrapper` 和
  `local-bridge` 三个 crate。
- 远端 Linux wrapper 使用 fake relay，把 stdin 脚本发送给本地 Bridge。
- 本地 Bridge 调用用户已安装的官方 `ego-browser`，不引入第二个浏览器。
- 手工启动本地 Bridge。
- wrapper 发送一个 heredoc。
- 验证专用 Task Space 的正常工作流、Snapshot、导航、输入和输出回传。
- 验证截图 artifact 能安全返回。
- 验证本地 `serverFetch`、文件路径和动态 import 的全信任边界。
- 负向验证脚本能够枚举/claim 其他 Task Space、切换其他 Tab 和发送原始 CDP，并确认
  产品文案没有把专用 Task Space 描述为安全隔离。
- 验证用户接管产生的 helper 错误可被脚本捕获后继续运行，因此 Bridge 必须通过独立
  控制信号从外部终止执行，而不是依赖 heredoc 的异常传播。
- 使用 fake broker 验证一次性 permit、sequence、旧 generation 和 peer UID 检查；验证
  Task Space -> Tab 固定锁顺序、`max_parallel_requests=4` 和冲突立即失败。
- 使用 fake clock 验证 60 秒 lease、20 秒续租、10 秒 failure grace、120 秒 execute 上限
  及 stop/revoke 与 renewal 的竞态。
- 验证 canonical allowlist 的路径穿越、符号链接、非 regular file、单文件/总量/数量限制，
  以及 learning bundle 的 manifest、签名、hash 和 `learning_bundle_digest` 校验。
- 明确记录 ego lite 未安装、命令不存在、超时和进程取消行为。

验收：在 Linux 远端连续执行三轮 heredoc，浏览器状态可复用，用户自己的 Tab 在官方
Skill 正常路径下不被主动选择；同时确认 full-trust 脚本可以越过该工作流
约定。异常时 supervisor 能终止受监管执行单元；同 UID 下主动创建的逃逸进程属于已知
接受风险，必须在授权 UI、运行状态和运维文档中显示，不能伪造为已清理。

### Phase 1：远端单用户正式授权 relay 闭环

- Server 增加正式 `EgoBrowserBinding`、独立 relay channel 和原子 claim；生产配置硬拒绝
  临时 binding、自动绑定和仅凭最近 session 的绑定。
- 独立 Device Client 展示候选 session、完整 full-trust 警告和目标 session 详情；用户
  明确确认后才提交 claim。
- claim 必须校验当前用户、EgoBrowserDevice、tool session、Node、平台、能力矩阵和
  authorization policy，并由 Server 签发绑定 capability；未完成 claim 时 wrapper 只能
  返回 `bridge_unavailable`。
- 新仓库的 Local Bridge 使用设备 token 主动连接。
- 新仓库的 Remote wrapper 使用短期连接材料发送脚本。
- Node-side broker、并发锁、lease 自动续租、allowlist revision 和 learning digest 纳入
  正式 relay 闭环；不允许先用临时 binding 再补授权。
- 以 `community-local-trust` 制品完成受控生产 canary：验证持久项目自签、Hardened Runtime、
  嵌套签名、证书指纹固定、owner-only credential、应用层出口检查、SBOM/provenance 和
  `production_ready=true` 证据；明确记录 `apple_notarized=false`、`public_distribution=false`。
- Node 安装器默认安装官方 `ego-browser` Skill 和新仓库 wrapper。
- 先支持单用户、单设备、单 active binding。
- 暂不支持自动重连后的脚本重放。

验收：只有完成 Device Client 明确选择和 full-trust 确认的 binding 才能执行；远端
Linux runtime 中的 fclaude 可以完成打开网页、Snapshot、点击、填充和结果回传；控制面
不能从日志或数据库看到脚本和页面内容。任何未 claim、过期、撤销、续租失败、profile/证书
证据不匹配、allowlist revision 或 learning digest 不匹配的请求都在 Server、Bridge 和
wrapper 三端拒绝。

### Phase 2：可靠性、恢复和运维加固

- 完善 generation、lease、撤销、paused、用户接管和全局停止的跨 worker 联动。
- 增加持久化 request ledger、single-flight、Bridge 重启恢复、断线重连新 ticket 和
  `unknown_result` 运维流程；旧 request 不自动重放。
- 增加设备密钥注册、proof-of-possession、轮换、撤销和异常恢复。
- 增加兼容矩阵和升级失败语义。
- 将本地 Browser Bridge 纳入 `community-local-trust` 签名、安装、证书轮换和 release
  evidence；Developer ID/notarization 作为可选的更严格 profile，不作为 MVP 前置条件。

验收：绑定、换绑、撤销、过期、断网、Bridge 崩溃、ego lite 退出、设备密钥轮换和用户
接管均 fail closed；任何终止路径都不能创建新的未授权 binding。

### Phase 3：artifact、诊断和运维

- 完善截图 artifact、大小限制和清理。
- 增加 `--doctor`、连接诊断和版本显示。
- 增加 Server/Node/独立 Device Client 指标、审计和运维 runbook。
- 展示已验证的 `learning_bundle_digest`、`allowlist_revision` 和 release profile；不增加
  控制面或远端脚本的 learning 同步能力。

### Phase 4：可选安全收紧

如果未来不再接受本机任意 Node 执行权，必须设计新的模式，例如：

```text
authorization_mode = ego_browser_structured_ops
```

新模式只接受受限浏览器操作 schema，不得通过配置开关静默改变全信任模式的语义。

## 15. 测试计划

### 15.1 协议和单元测试

- outer/inner canonical JSON、长度前缀、重复字段、未知字段和超长 wire frame 拒绝；
  Server 只测试 outer schema，Bridge/Remote wrapper 测试 inner schema。
- outer ticket、request ID、sequence、generation 和 lease 校验，以及 inner AEAD 和
  capability transcript binding。
- 旧 generation、重复 request 和未知 binding 的拒绝。
- Node-side broker 的 peer UID、per-tool-session 进程内 nonce、无 wrapper `binding_id` 的
  唯一 binding 派生、先创建 session 后 claim、session stop 注销、一次性 permit、ticket
  不落环境/argv、sequence 原子递增、permit 重放和 broker 崩溃清零。
- 不同 worker 的 `EgoBrowserRelayBinding` 配对、共享 revocation state，以及旧
  `device_session_id` route 对浏览器 envelope 的拒绝。
- stdout/stderr、退出码、超时、取消和 unknown result 映射。
- artifact 媒体类型、像素数、大小和路径范围校验。
- `concurrency_mode`、Task Space -> Tab 锁顺序、binding 级 wildcard 锁、`max_parallel_requests`
  限额和 `concurrency_conflict` 立即返回。
- 60 秒 lease、20 秒自动续租、10 秒 failure grace、admission 最小剩余窗口、绝对 TTL，
  以及 renewal 与 stop/revoke 的 CAS 竞态。
- `allowlist_revision` 与 `learning_bundle_digest` 的 capability 绑定和漂移拒绝。
- Server canonical Task Space 派生、claim mismatch 拒绝、Device Client response/handoff 校验、
  Bridge request label/scope mismatch 拒绝。
- ownership monitor 只读 helper 表面、`agent` 后 armed、takeover/monitor-unavailable reason、
  control-pipe cleanup，以及 revoke-before-pause 顺序。
- wrapper `nodejs`、`--doctor`、`--reload` 和 `--help` 兼容行为。
- 在 rootful Linux 环境以真实文件 ACL 和 `SO_PEERCRED` 证明正确 runtime UID 可连接、其他
  UID 即使后来获得 socket 文件访问仍不能通过 broker；UID 0 与 Docker runtime 必须拒绝。

### 15.2 本地执行测试

- 脚本可以调用 `snapshot`、`click`、`fill`、`wait` 和站点工具。
- 在未安装 `agent-remote-device`、未运行 Bridge 时，ego lite 仍可按官方方式启动和使用。
- Task Space 在多个 heredoc 轮次中保持正确。
- 本地用户 Tab 不被远端默认选择。
- ego lite 退出时没有残留 Bridge 子进程。
- timeout 会杀掉进程组而不是只杀父进程。
- Bridge 崩溃、Device Client 退出和 relay 断线会停止执行。
- 被脚本捕获的 helper error 不停止请求；独立原生 ownership transition 会从外部停止该请求及
  descendant，将 Server pause 为下一 generation，明确 resume 后重新 armed。
- 验证全信任脚本能够触发动态 import 时，产品警告和审计语义仍正确。
- 并发 Task Space/Tab 请求按固定锁顺序运行，冲突不排队；锁在 artifact/清理完成后释放，
  进程崩溃时不会遗留可消费 permit。
- allowlist 的 realpath、`O_NOFOLLOW`、父目录/非 regular file、路径穿越、符号链接逃逸、
  单文件/总量/数量上限和 revision 变更均 fail closed。
- 本地 learning bundle 目录只读；激活和 relay 恢复都验证签名、manifest、版本、文件 hash
  和 digest，远端脚本无法覆盖。
- `logic_test`、`development_local` 和 `community-local-trust` profile 的 capability 门禁、
  证书指纹固定、owner-only credential 权限和 Keychain/fallback 轮换行为。
- community credential file 的 `0600`、当前 UID、regular file、`st_nlink=1`、
  `O_NOFOLLOW`、严格 JSON 和原子轮换测试；未持有 broker capability 的 wrapper/同 UID
  进程不能通过 broker IPC 取得它。

### 15.3 跨组件 E2E

- 远端 Linux fclaude 完成 wrapper -> Server relay -> local Bridge -> ego lite 的完整闭环。
- 本地浏览器已登录时无需再次登录；登录态不进入 relay 日志。
- 远端访问本地 `localhost` 页面。
- 多轮 Snapshot/locator 操作和截图回传。
- 用户选择、暂停、恢复、换绑和结束控制。
- 原生 Task Space ownership 从 `agent` 变为 `user` 时，接管先终止受管执行，再持久化
  `task_space_takeover` pause；明确确认 resume 后进入新 generation。
- session 停止、设备撤销、用户禁用和 lease 过期的即时失效。
- relay 重连获得新 ticket，但旧 request 不重放。
- lease 自动续租、续租失败宽限、绝对 TTL 和撤销/停止竞态在真实跨组件链路中符合状态机。
- 远端脚本试图访问任意本地路径、环境变量、子进程时，按已确认全信任语义执行，
  但日志仍不得泄露这些内容。

真实控制面 relay 门禁使用独立 Redis database，并运行实际 TLS/PoP Server WebSocket、Redis
ticket/pairing、Node broker、wrapper、Device Client heartbeat 与出站 Bridge；只有最终本地
`ego-browser` executable 使用 fixture：

```sh
AGENT_REMOTE_INTEGRATION_REDIS_URL=redis://127.0.0.1:6379/14 \
  bash integration-tests/real-relay-e2e.sh
```

该门禁证明三轮加密状态复用、in-flight revoke、descendant cleanup、request ledger、outbox
delivery 和 content-free metrics；它不能替代真实 ego lite canary。

### 15.4 负向和安全测试

- 篡改 user/device/tool session/binding/Node ID。
- 修改 outer `generation`、`sequence`、relay ticket、binding 或请求方向，并分别篡改 inner
  ciphertext、nonce、auth tag 和 capability。
- 将同一 binding 的两个 endpoint 分发到不同 worker，验证共享状态/sticky routing 能正确
  配对；向旧 `device_session_id` relay route 发送浏览器 envelope 必须被拒绝。
- 伪造其他设备的本地 Bridge hello。
- 发送未知协议版本、未知字段、重复 JSON key 和超长脚本。
- 尝试通过 wrapper 打开 shell、PTY、SSH forwarding 或公网监听。
- 通过 artifact 路径读取本地任意文件。
- 通过 allowlist 外的路径、符号链接、路径穿越、FIFO/socket/device 或超限文件进行上传/保存。
- 使用未签名、错误版本、错误 hash 或被覆盖的 learning bundle 激活 binding。
- 在旧 binding 已撤销后发送延迟帧。
- 在用户接管 Task Space 后重试原始请求。
- 伪造 claim Task Space label、加密 request label/scope、重复 Task Space match、未知
  ownership，以及 monitor 意外退出；均不得开放 admission 或自动 claim/takeover。

## 16. 观测、限额和隐私

建议默认限制：

```text
max_script_bytes              = 1 MiB
max_stdout_bytes              = 4 MiB
max_stderr_bytes              = 1 MiB
max_artifact_bytes            = 12 MiB per image
max_artifact_pixels           = 4,000,000
max_execute_timeout_seconds   = 120
default_lease_seconds         = 60
lease_renew_interval_seconds  = 20
lease_renew_failure_grace_seconds = 10
lease_admission_min_remaining_seconds = 20
absolute_binding_ttl_seconds  = 28,800
max_parallel_requests         = 4
max_allowlisted_file_bytes    = 64 MiB per file
max_allowlisted_total_bytes   = 256 MiB per request
max_allowlisted_file_count    = 32 per request
max_active_browser_binding    = 1 per device
```

`max_execute_timeout_seconds=120` 不会绕过 60 秒 lease：活跃请求必须由 broker 按 20 秒间隔
续租，且续租失败只能在 10 秒 grace 内继续清理；绝对 TTL 到期立即拒绝 admission。文件
allowlist 限制只适用于 helper 输入和自动 artifact，不限制 full-trust Node 通过 stdout 或
网络外发数据。这些值必须由 Server、Node、独立 Device Client 和 wrapper 共同限制，不能
只依赖远端客户端。

指标由各进程的结构化日志产生；collector 必须从受信 workload/launch-agent identity 添加
`component`，不能信任事件正文自报来源，也不能把同名 Node/Bridge 事件重复计数：

| Source | Metric | 有限 label taxonomy |
| --- | --- | --- |
| Server | `ego_browser_bridge_connections` | `metric_operation={opened,closed}`, `relay_role={bridge,wrapper}`, `relay_transport={redis,memory}`；生产只允许 `redis` |
| Server | `ego_browser_bytes_total` | `metric_direction={request,response}`, `metric_status={completed,rejected,frame_limit,transport_error}` 加上述 relay role/transport |
| Server | `ego_browser_revocations_total` | `revocation_reason={absolute_ttl,admin,policy,device_key,device,lease,node,pause,resume,tool_session,user,other}` |
| Node | `ego_browser_bindings_active` | 无动态 label |
| Node | `ego_browser_execute_total`, `ego_browser_execute_duration_seconds`, `ego_browser_bytes_total` | `status={completed,concurrency_conflict,renewal_required,lease_expired,unavailable,timeout,rejected,unknown_result}`；bytes 另有 `direction={request,response}` |
| Bridge | `ego_browser_execute_total`, `ego_browser_execute_duration_seconds`, `ego_browser_bytes_total`, `ego_browser_artifacts_total` | status 固定为 `completed,script_error,timeout,cancelled,bridge_unavailable,ego_runtime_unavailable,lease_expired,binding_revoked,protocol_error,artifact_error,concurrency_conflict,lease_renewal_required,unknown_result`；bytes 使用有限 direction，artifact 使用 `media_type={image/png,image/jpeg,other}` |
| Device Client | `ego_browser_device_service_up`, `ego_browser_device_bridge_peers`, `ego_browser_device_peer_total`, `ego_browser_device_refresh_total` | `status` 分别限定为 `{ready,stopped}`、`{connected,disconnected}`、`{rejected}` 和 `{completed,unregistered,identity_unavailable,client_unavailable,control_plane_error}` |

指标 label 不使用 user/device/session/binding/generation/request ID、URL、文件名、本地路径、
脚本、页面、输入、输出或 artifact 标识。生产巡检至少执行以下 metadata-only 查询；Redis
只能 `SCAN` key name，不能把 ticket、challenge 或 Pub/Sub payload 写入 incident log：

```sql
SELECT count(*) AS pending, min(created_at) AS oldest
FROM ego_browser_revocation_outbox
WHERE delivered_at IS NULL;

SELECT status, lease_health, count(*)
FROM ego_browser_bindings
GROUP BY status, lease_health
ORDER BY status, lease_health;
```

```sh
redis-cli --scan --pattern 'agent-remote:ego-browser:*' | sed -n '1,100p'
```

告警覆盖：超过 pair timeout + 5 秒 presence TTL 的 role 不平衡、持续
`transport_error`/`frame_limit`、超过三个 cleanup interval 且至少 30 秒的 outbox row、
active/healthy binding 无 relay、超过 20 秒 renewal interval + 10 秒 grace 的重复
renewal/lease failure、任何 `unknown_result`、本地 peer 意外丢失以及异常 policy/device_key/node
revocation。处置时先关闭新 claim，再通过正常 lifecycle stop/revoke 所有 generation，等待
outbox 和连接 gauge 收敛为零；Redis 故障时保留 pending row，禁止手工标 delivered 或删除
relay key。恢复时先验证 PostgreSQL/Redis、GETDEL/PubSub/presence/revocation subscriber，再重启
worker/Node/Bridge，要求新的显式 native-session claim 和 generation；旧 ticket、nonce、permit、
handoff、sequence lease 或 `unknown_result` request 永不恢复或重放。

## 17. 部署和升级

### 17.1 安装顺序

1. 安装或升级本地 ego lite。
2. 安装经验证的 `agent-remote-ego-browser` `community-local-trust` Bridge 和独立 Device
   Client；不安装 `agent-remote-device`。安装器显示版本、SHA-256 和叶证书指纹，要求用户
   明确确认本地信任，并在校验通过后按 community 流程处理 quarantine；不宣称 Apple
   notarization 或公共分发。
3. Bridge 探测真实 `ego-browser` 和本地 Skill workspace。
4. 校验 community release manifest（`production_ready=true`、`profile=community-local-trust`、
   `apple_notarized=false`、`public_distribution=false`）、嵌套签名、Hardened Runtime、
   证书指纹、SBOM/provenance 和应用层出口检查；失败时不开放生产 capability。
5. 升级 Server relay、`ego_browser_devices` 和 `ego_browser_bindings` schema。
6. 升级 Node 中的 remote wrapper 与官方 Skill。
7. 随默认发行包升级或启用 `agent-remote-cli` 的 ego-browser 状态和控制集成。
8. 进行单用户 canary binding。
9. 通过完整跨仓库 E2E 后开放 capability。

### 17.2 兼容策略

- 旧 Device Client 不认识 `ego_browser_script_full_trust` 时拒绝绑定。
- 旧 Node 不认识 browser relay channel 时不创建 browser session。
- 旧 wrapper 不支持 artifact 时只能使用无截图流程，或明确拒绝。
- 任何版本不匹配不得静默切换到远端浏览器、桌面 GUI 或原始 CDP。

### 17.3 回滚

1. Server 关闭 `ego_browser_bridge_enabled`，阻止新 binding 和重连。
2. 主动撤销现有 binding，等待最长 lease/grace（最多 10 秒宽限加当前执行清理），并确认
   renewal 已停止。
3. 确认 Node wrapper、broker 和本地 Bridge 无活动 request 或可消费 permit。
4. 再回滚 Server/Node/`agent-remote-ego-browser` 组件和 community 证书指纹；旧指纹在
   控制面撤销列表中保留。
5. 保留终态 EgoBrowserBinding 和审计记录，不做 destructive schema downgrade。

## 18. 已知风险和处理方式

| 风险 | 处理 |
| --- | --- |
| 远端获得本机 Node 任意代码执行权 | 这是已确认的产品能力；使用显式全信任授权、完整权限文案、短 lease、受监管执行单元和全局停止降低风险 |
| heredoc 读取或外发本地敏感数据 | 这是 full-trust 权限的一部分；E2E 只保护传输，不阻止端点外发；不记录正文并要求用户明确选择具体 session |
| 脚本访问用户 Tab 或 Task Space | Task Space 只约束正常工作流；UI 明确授权整个 ego lite 能力，用户接管触发 Bridge 外部强制停止 |
| 脚本启动残留或逃逸子进程 | 外部 supervisor 尽力终止受监管执行单元；同 UID、无 sandbox 下的主动逃逸属于接受风险，不能声称完全清理 |
| 远端动作已执行但响应丢失 | `unknown_result`，禁止自动重放，要求重新观察 |
| 本地 ego lite/Skill 版本漂移 | 激活前探测和兼容矩阵，版本不符直接拒绝 |
| 官方 Skill 正常流程误选用户 Tab | 专用 Task Space、显式 task-space 选择、回归测试；不把这些措施描述为对恶意 full-trust 脚本的隔离 |
| 公网暴露本地服务 | 本地只出站，relay ticket 和 E2E，不使用公开监听 |
| 本地 Skill Learning 被远端覆盖 | 签名/版本校验，远端脚本不能直接写 Skill workspace |
| community 自签证书被替换或过期 | 发布 manifest 固定证书指纹和 digest；安装器要求用户确认并 pin；轮换使用双版本窗口，指纹不匹配立即撤销 capability |
| community profile 没有 Apple notarization | 仅用于受控生产，不宣称 Apple 信任或公共分发；Server 只接受完整 community release evidence，未来可切换更严格 Developer ID profile |
| lease 续租与撤销竞态 | renewal 使用 active/generation/CAS，stop/revoke 先写 outbox 并递增 generation |
| allowlist 误把 full-trust 变成文件沙箱 | 明确只限制 helper 和自动 artifact；Node stdout/网络外发仍属于已授权全信任能力 |
| 透明转发被误认为浏览器沙箱 | 所有 UI、文档、审计和安全评审明确写“本机 Node 全信任” |

## 19. 验收标准

正式将 capability 标记为可用前，必须满足：

1. 远端 `fclaude` 可以在不安装远端浏览器的情况下调用本地 ego lite。
2. 官方 `ego-browser` Skill 的 heredoc 工作流无需 Agent 侧改写。
3. 本地已登录网站可直接使用，浏览器 profile 不被整体同步到控制面；授权后的脚本可以
   读取和外发其可访问的 Cookie、页面和登录态数据，产品文案对此没有相反承诺。
4. 官方 Skill 正常工作流为每个 tool session 选择专用 Task Space，且回归测试证明不会
   意外操作用户 Tab；Server/Device/broker/Bridge 对 canonical label 一致，原生 ownership
   接管会触发外部停止；安全说明同时明确 full-trust 脚本可以主动越过该工作流约定。
5. 用户可以明确看到当前绑定、暂停、结束和停止入口。
6. relay、lease 自动续租/宽限、generation、sequence、broker permit、并发锁、Task Space
   takeover pause/resume、monitor fail-closed 和撤销测试全部通过。
7. 本地 Bridge 不监听公网/局域网端口。
8. 控制面日志、审计和指标不包含脚本、页面、截图、输入和本地路径正文。
9. Bridge 自动回传的截图 artifact 只能来自受控临时目录并受大小限制；该限制不被描述为
   full-trust 脚本的文件或网络外发边界。
10. 断线、超时和结果未知时不会自动重放可能有副作用的 heredoc。
11. 所有组件版本在兼容矩阵内，未知 capability 一律拒绝。
12. 产品文案明确说明远端拥有 Bridge 运行身份下的本机 Node/heredoc 全信任、整个 ego lite
    浏览器控制和数据外发能力，而不是仅控制绑定 Task Space。
13. `community-local-trust` release manifest（含 `signing_type=project-self-signed` 和
    `outbound_policy=application-enforced`）、嵌套签名、Hardened Runtime、证书指纹、
    owner-only credential、SBOM/provenance、应用层出口检查和 `production_ready=true` 均
    可复核；文案明确 `apple_notarized=false`、`public_distribution=false`，并且没有把
    Apple Developer 账号当作 MVP 前置条件。
14. allowlist 的 canonical path、`allowlist_revision`、单文件/总量/数量限制，以及本地
    learning bundle 的签名、hash、版本和 `learning_bundle_digest` 在激活和恢复时均通过。
15. 卸载或停用 `agent-remote-ego-browser` 后，官方 ego lite 仍可独立启动和使用；
    `agent-remote-device` 从未安装也不影响该结论。
16. 首次绑定和每次恢复均明确显示“同一 macOS 用户 UID、无 sandbox、可访问该用户资源”，
    并显示 supervisor 只能保证受监管执行单元的停止，不能保证主动逃逸进程清理。

## 20. 后续 ADR 入口

以下是实现细节，不改变已经确认的 MVP 选择，且不能把未决项当成生产 capability 的默认
开启条件：

- ego lite `ego-browser` 命令的发现、可执行文件验证和版本读取方式；
- relay 是否复用控制面的通用 TLS transport；浏览器 E2E 握手始终由新仓库独立定义；
- screenshot artifact 的远端 Claude 消费格式和媒体编码；
- community 证书轮换的双版本兼容窗口，以及未来 `developer_id` profile 的切换流程；
- 是否在 MVP 之后新增独立的结构化浏览器操作授权模式；不得用它静默改变已确认的
  `ego_browser_script_full_trust` 语义。

以下事项已经确定，不再作为决策入口：本地 Bridge/Device Client 使用用户级
`~/Library/LaunchAgents`；MVP 仅支持 remote Linux + local macOS；allowlist、并发锁和本地
固定签名 learning bundle 属于 MVP；`community-local-trust` 可以在完成证据和用户信任
确认后用于受控生产，即使没有 Apple Developer 账号，但不宣称 Apple notarization 或公共
分发；`agent-remote-device` 不属于运行时依赖。
