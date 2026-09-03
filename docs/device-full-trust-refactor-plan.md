# Device 会话级全信任重构设计与实施计划

## 1. 文档状态

本文记录已经确认的 Device 控制目标设计，并作为跨仓库实施和外部发布验收的执行清单。

- 产品决策状态：已确认。
- 代码实施状态：阶段 A-E 及阶段 F 的本地质量、full-trust 合成跨仓 E2E、release evidence schema 9、
  装配脚本、合同测试和运维文档已完成；真实签名 macOS、真实混合版本部署、独立安全评审和生产组合
  签名/策略切换未完成。
- 适用平台：macOS。
- 涉及仓库：`agent-remote`、`agent-remote-device`、`agent-remote-server`、
  `agent-remote-node`、`agent-remote-admin-web`。
- 本文描述当前已实现的 full-trust 行为及尚未完成的外部发布条件。生产 capability 继续默认关闭，
  不得把仓库内实现或合成测试视为生产发布批准。

本文有意改变 `local-device-control-security-design.md`、
`local-device-control-binding-design.md` 和 Device 仓库安全规则中“激活前必须逐应用审批”的旧决策。
实施已同步更新这些架构和安全文档、协议、执行层和 SwiftUI 产品路径；legacy Server 状态、API 和
approval 数据只为混合版本及历史记录兼容保留，不是新 session 的授权来源。

## 2. 已确认的产品决策

1. 用户在 Device APP 中选择一个远端 Claude session，即表示为该 DeviceSession 授予会话级全功能信任。
2. 选择普通未绑定 session 后不再展示应用待批准界面，直接进入激活过程，成功后显示“等待 Claude 控制”。
3. Claude 可以查看和 Full Control 当前或之后运行的任意合格 GUI 应用，不再选择应用或控制等级。
4. Claude 可以通过新工具启动任意已安装且通过本机校验的 GUI `.app`。
5. 启动工具只接受 Bundle ID 或应用名称，不接受路径、URL、文件、命令行参数或环境变量。
6. Claude 在 active 会话中可以不依赖应用和 observation，直接读取当前 macOS 全局剪贴板。
7. 剪贴板仍只支持纯文本，UTF-8 上限为 64 KiB，不记录或持久化内容。
8. 保留远端会话侧对购买、删除、发送、发布、授权、协议接受、凭据提交等高风险最终动作的确认策略。
   Device 不新增逐动作弹窗。
9. session 已绑定另一设备时保留抢占确认。确认后旧设备立即失去控制权，但远端 Claude session 不停止。
10. 信任只属于当前 DeviceSession。turn 切换、短暂断线、续租和 generation 轮换可以延续；会话结束、
    主动切换、被抢占、设备撤销、TCC 权限撤销或绝对 TTL 到期后立即失效。
11. 不提供设备级“永久自动连接任意远端 session”。每次新的 session 绑定都必须来自一次本机选择。
12. `Agent Remote Device.app` 自身及其 XPC 服务禁止被启动或控制。
13. macOS 登录窗口、锁屏、Secure Input、TCC 授权窗口和其他操作系统保护表面继续拒绝。

## 3. 目标与非目标

### 3.1 目标

- 用一次明确的 session 选择替代逐应用、控制等级和剪贴板审批。
- 允许会话期间动态出现、启动或新安装的应用，无需重建静态应用清单。
- 保持现有用户、设备、tool session、DeviceSession、Node、generation、lease 和动作状态绑定。
- 保持端到端加密、单调序号、状态新鲜度、机器锁、全局停止、前台恢复和即时撤销。
- 使用明确的授权类型表达“会话级全信任”，避免用空数组、特殊 digest 或伪造应用记录表达通配授权。
- 为混合版本部署提供明确拒绝或受控兼容，不允许静默得到残缺的“全信任”能力。

### 3.2 非目标

- 不增加任意文件 API、任意进程 API、AppleScript API、shell API、URL 导航 API 或通用本机网络入口。
- `launch_application` 不直接执行二进制、脚本或命令。Claude 可以启动 Terminal 后通过 GUI Full Control 输入命令。
- 不绕过 macOS TCC、代码签名、Secure Input、锁屏或系统完整性保护。
- 不允许 Claude 或项目输入 endpoint、PID、bundle path、授权对象、device identity 或 session identity。
- 不删除远端 Claude/产品层已有的高风险动作确认规则。
- 不把“所有应用可授权”解释成“每次截图都可无差别采集整个桌面”。

## 4. 目标用户流程

```text
APP 启动
  -> 检查 Accessibility 和 Screen Recording
  -> 缺少权限：permission_required
  -> 权限完整：selecting_session
  -> 用户选择一个 Claude session
  -> 目标由另一设备控制：显示抢占确认
  -> claiming_session
  -> Server 创建 pending_device binding
  -> Device 建立 XPC、relay 和 nested TLS
  -> Device 按 session_full_trust 自动激活 Executor
  -> Server 设置 active lease 并更新 Node runtime context
  -> waiting_for_claude
  -> Claude observe / launch / read_clipboard / act
```

目标 APP 状态至少包括：

```text
ready
selecting_session
claiming_session
permission_required
activating
active
paused
pausing
ending_session
reconnecting
stopped
failed
```

删除 `awaiting_approval` 和 `denied` 的正常产品路径。历史 Server 记录可以继续包含
`pending_user_approval` 和 `denied`，直到兼容数据清理阶段完成。

### 4.1 UI 要求

- 选择后必须立即显示所选 session 和“正在准备安全连接”，不能闪回 session 列表或 `ready`。
- Server、Node、relay 和 Executor 全部激活后显示“等待 Claude 控制”。
- active 页面保留当前 session、连接状态、停止当前动作、结束控制和切换 session。
- 全局 Escape、睡眠、锁屏、用户切换、断网、权限撤销和故障状态仍必须可见且可恢复。
- 删除应用列表、应用勾选、控制等级控件、剪贴板勾选、Allow、Deny 和相关说明文案。
- 英文与简体中文本地化必须同步更新。

## 5. 授权数据模型

### 5.1 本机授权类型

在 Device 的 App、Broker 和 Executor 之间引入窄且显式的授权类型。建议模型：

```text
SessionAuthorization
  mode: session_full_trust
  policy_version: 1
  application_scope: all_user_gui_applications
  control_level: full_control
  clipboard_scope: global_plain_text
  application_launch: allowed
  excluded_bundle_identifiers:
    - dev.agentremote.device
  generation: <current generation>
```

实际 IPC 编码可以使用更紧凑的枚举，但必须满足：

- 未知 mode、scope 或 policy version 一律 fail closed。
- authorization 必须绑定完整 `DeviceSessionBinding` 和当前 generation。
- generation 轮换只能复制完全相同的 authorization，不能扩大范围或 TTL。
- 不允许远端动作、MCP 参数或项目配置提交或修改 authorization。
- `approvals: [LocalApproval]` 不得继续作为新模式的权威授权表示。

### 5.2 Server 持久化

为 `device_sessions` 增加：

| 字段 | 建议类型 | 语义 |
| --- | --- | --- |
| `authorization_mode` | `String(32)` | `per_application_approval` 或 `session_full_trust` |
| `authorization_policy_version` | `Integer` | 首版固定为 `1` |
| `authorized_at` | timezone datetime nullable | 本机选择产生授权的时间 |

迁移要求：

- 所有历史记录回填为 `per_application_approval`。
- 新策略启用后创建的记录写入 `session_full_trust` 和 policy version 1。
- 首个兼容版本保留 `device_session_approvals` 表、旧状态枚举和旧 API，避免破坏历史记录和旧客户端。
- 不在 approvals 表中插入 `*`、全零 digest、Device APP digest 或其他哨兵值。
- 后续删除旧审批表必须作为独立迁移完成，并先验证所有受支持客户端已经退出旧模式。

### 5.3 授权归属

session 选择是授权事件。Server 应记录不含敏感内容的审计事件，例如：

```text
device_session.full_trust_authorized
  device_session_id
  device_id
  tool_session_reference_id
  authorization_policy_version
  authorized_at
```

Server 不得记录应用名称、Bundle ID、窗口标题、剪贴板内容、AX 内容、截图、输入或启动参数。
应用动作仍在端到端加密数据路径内，控制面只观察生命周期和密文 relay。

## 6. Server 状态机和 API

### 6.1 新状态机

新模式主路径：

```text
pending_device
  -> active
  -> stopping
  -> stopped

pending_device / active
  -> expired
  -> failed
```

`pending_device -> active` 只能在以下条件全部成立后发生：

1. binding 仍匹配 user、device、tool session、DeviceSession、Node 和 generation。
2. Device 已通过认证并确认本机 XPC/Executor 基础设施可用。
3. Node/proxy 支持新模式所需完整 capability 集合。
4. session 未过期、未停止、未被抢占，远端 Claude session 仍可控。
5. Server 成功设置 lease，并成功排入 generation-bound runtime context 更新。

### 6.2 API 目标

- `POST /api/v1/device-sessions/claim` 仍是唯一普通用户绑定入口。
- claim 的 `device_capabilities` 由新 APP 固定为 `session_full_trust_v1`；full-trust 策略下缺失、
  重复、未知或不完整集合返回 `DEVICE_CONTROL_DEVICE_UPGRADE_REQUIRED`，且不创建或复用 binding。
- Server 端部署策略决定新 binding 的 `authorization_mode`，客户端不能任意请求更高权限模式。
- 管理员 legacy create API 在 full-trust 策略下返回 `DEVICE_CONTROL_CLAIM_REQUIRED`；它不能代替
  Device APP 的本机选择或写入 `authorized_at`。
- claim 响应公开授权 mode 和 policy version，使新 APP 可以严格核对预期策略。
- `POST /{id}/device-connected` 对 `session_full_trust` 直接执行激活事务；对兼容旧记录才进入
  `pending_user_approval`。
- `POST /{id}/approve` 对 full-trust session 必须返回明确状态冲突，不能覆盖授权模式。
- `/device-control/policy` 用结构化字段替代固定的 `local_approval_required: true`：

```json
{
  "authorization_mode": "session_full_trust",
  "authorization_policy_version": 1,
  "application_scope": "all_user_gui_applications",
  "control_level": "full_control",
  "clipboard_scope": "global_plain_text",
  "application_launch": true
}
```

- inbox、用户列表和管理员列表不得返回应用或剪贴板内容。
- claim、rebind、stop、expire、abort 和 reconnect 继续使用同一个撤销服务和完整 binding 比较。

### 6.3 原子性和失败语义

- 不能在 Server 已显示 active、但 Executor 尚未安装 authorization 时接受动作。
- 推荐沿用 Broker 现有激活事务顺序：建立 pending activation，配置 Executor，建立 relay，核对 Server active；
  任一步失败都停止 Executor、关闭 relay、恢复前台状态并进入可重试失败状态。
- 如果 `device-connected` 已在 Server 提交 active，但本机后续激活失败，Broker 必须调用已认证的 stop/abort，
  不得遗留可续租的空 active session。
- 超时重试必须先通过 inbox 对账，不能重复生成 binding 或重复扩大授权。

## 7. 动态应用控制

### 7.1 通配授权不等于跳过身份校验

新模式允许所有合格用户 GUI 应用，但每次操作仍必须解析并绑定具体目标：

- 运行中的真实 PID；
- Bundle ID；
- 代码签名 identifier 和有效性；
- application digest；
- window ID 和 display fingerprint；
- DeviceSession generation；
- monotonic sequence；
- 当前 model-visible state 或 screenshot generation。

状态句柄仍以具体 application digest 为作用域。应用 B 的状态不能操作应用 A；应用重启、窗口变化、
display 变化、turn 边界和 generation 变化仍使旧状态失效。

### 7.2 应用解析

- `observe(application:)` 优先按完整 Bundle ID 匹配，其次按精确、大小写不敏感的展示名称或既有受控别名匹配。
- 多个应用匹配时返回 `ambiguous_application` 和不含敏感路径的候选标识；不得选择第一个结果。
- 未运行但已安装的应用，`observe` 返回 `application_not_running`，提示使用 `launch_application`。
- 会话期间新启动或新安装的应用可以动态解析，无需更新 authorization。
- 每次解析后重新验证代码身份，不能仅信任缓存的名称、PID 或 bundle path。
- Device APP、Network Broker、GUI Executor 及其辅助进程必须按 Bundle ID、签名 identity 和进程关系排除。

### 7.3 捕获边界

- 无 application 参数的 `observe` 只选择当前前台的合格 GUI 应用。
- 有 application 参数时只捕获该精确签名应用的目标窗口。
- Device 状态窗口和排除进程始终不得出现在返回图像中。
- 不因为授权范围变成 all applications 就把窗口捕获改成任意桌面截图。
- 其他应用偶然遮挡、窗口消失或身份变化时继续返回明确 stale/capture 错误，不猜测或扩大捕获范围。

## 8. `launch_application` 协议

### 8.1 MCP 表面

新增工具：

```text
launch_application(application: string)
```

工具说明必须明确 `application` 是 Bundle ID 或已安装应用名称，不是路径、URL 或命令。
模型应优先使用 Bundle ID；名称不确定时先报告而不是试探多个应用。

### 8.2 Device 协议

在 v2 action schema、Swift 严格解码器和 Rust 严格解码器中增加：

```json
{
  "type": "launch_application",
  "application": "com.apple.TextEdit"
}
```

参数要求：

- 去除首尾空白后必须非空；
- 最大 255 个字符，并限制 UTF-8 总长度；
- 禁止控制字符和 NUL；
- 禁止 `/`、`~`、文件 URL、网络 URL、shell 片段、参数数组和环境变量；
- 解码器严格拒绝未知字段。

### 8.3 本机执行

1. 使用 LaunchServices/`NSWorkspace` 从 Bundle ID 或无歧义名称解析已注册 `.app`。
2. 拒绝 Device 自身、辅助服务、无 GUI 应用、身份无效应用和系统保护目标。
3. 在启动前记录当前前台应用。
4. 使用系统 API 启动，不拼接 shell 命令，不调用 `/usr/bin/open`。
5. 等待有界的进程启动和首个可操作窗口；超时返回 `application_launch_timeout`。
6. 验证实际运行进程与解析到的代码身份一致。
7. 产生该应用的首次完整 observation，绑定新的 state ID。
8. 如果启动过程改变前台且用户未自行切换，按既有规则恢复原前台应用。
9. 一旦已向 macOS 提交启动请求，首窗超时或结果身份不可验证必须终止当前 generation；proxy 必须
   丢弃对应 transport，不能在未确认 sequence 上继续执行。

启动动作必须是不可自动重放的交互动作。连接状态不明时返回 unknown result，调用方重新 observe，
不得跨 generation 再次启动。

### 8.4 Capability

新增 `application_launch_v1`。只有 Server 下发的 runtime context、Node 广告、proxy 和 Device
均支持时才能暴露或执行启动工具。缺少 capability 时返回明确 `unsupported_capability`，不能回退到
键盘快捷键、Spotlight、shell、AppleScript 或 URL scheme。

## 9. 全局剪贴板

### 9.1 新语义

- active full-trust session 可随时调用 `read_clipboard`。
- 不要求 application 参数、approval、最新 capture、state ID、window ID 或先行 observation。
- 请求仍携带不可由模型修改的完整 context，并消费准确的下一 monotonic sequence。
- 成功读取不推进 application state generation 或 screenshot generation，也不使已有应用元素句柄失效。
- 返回值只允许纯文本 UTF-8，最大 64 KiB。

### 9.2 错误与隐私

至少定义：

```text
clipboard_empty
clipboard_non_text
clipboard_too_large
clipboard_unavailable
clipboard_access_denied
```

`clipboard_access_denied` 只用于 authorization、lease、generation 或 macOS 权限不允许的情况，不再表示
“当前应用未勾选剪贴板”。剪贴板内容不得进入日志、数据库、审计、指标 label、崩溃报告或错误消息。

### 9.3 Capability

新增 `global_clipboard_v1`。新 proxy 在该 capability 下直接发送无应用状态依赖的 v2 clipboard action。
旧 `clipboard_payload_v2` 继续表示响应载荷格式和 64 KiB 上限；两者语义不同，不得复用同一个 capability。

## 10. 必须保留的安全不变量

本次变更有意移除应用审批和三档控制等级，但不得削弱以下不变量：

- 完整 binding：user、device、tool session、DeviceSession、Node、platform、generation 全部匹配。
- 短 lease、绝对 TTL、即时撤销和 generation 轮换。
- 单 session 机器锁和 live-only 唯一约束。
- nested TLS、peer pinning、exporter confirmation 和控制面只中继密文。
- 严格单调 sequence、请求 ID、状态代次和重放保护。
- 元素、坐标、窗口和应用身份的新鲜度校验。
- 动作未知结果不自动重放。
- 全局 Escape、停止动作、结束控制、睡眠、锁屏、切换用户、断网和 XPC peer loss 的输入释放。
- 远端临时激活应用后恢复用户原前台应用。
- Screen Recording 或 Accessibility 被撤销时立即结束控制。
- 不发现、不启动、不配置、不读取本机 Claude Code 或 Claude Desktop 的登录态与凭据。
- 远端高风险最终动作确认策略继续生效。

## 11. 跨仓库实施范围

### 11.1 `agent-remote-device`

重点文件和模块：

- `macos/AppCore/DeviceAppModel.swift`：删除审批状态和 selection 数据，重写 claim 到 activation 的状态转换。
- `macos/App/DeviceStatusView.swift`：删除 ApprovalView，增加 preparing/waiting UI。
- `macos/App/AgentRemoteDeviceApp.swift`：同步 pending binding 后自动激活，不再发现本机应用清单。
- `macos/App/LocalApplicationDiscovery.swift`：删除或改造成动态目标解析模块；不要保留启动时最多 32 个应用的快照。
- `macos/AppCore/ApprovalModels.swift`：由 `SessionAuthorization` 取代新路径中的 Approval 模型。
- `macos/App/DeviceBrokerClient.swift`：claim 后保持激活状态，提供 full-trust activation IPC。
- `macos/Shared/DeviceIPC/ExecutorMessages.swift`：版本化 authorization、launch 和全局 clipboard 契约。
- `macos/DeviceServices/NetworkBrokerDiscovery.swift`：自动激活、对账、轮换时保持相同 authorization。
- `macos/DeviceServices/NetworkBrokerService.swift`：用 activation request 取代新路径的 approval decision。
- `macos/DeviceServices/GUIExecutorSessionController.swift`：动态应用解析、launch、无 capture clipboard 路径。
- `macos/DeviceServices/GUIActionRuntime.swift`、`macos/GUIExecutor/*`：LaunchServices、窗口捕获、身份复核和错误映射。
- `macos/Shared/DeviceProtocol/*`：v2 action、严格 JSON 和 response 状态。
- `protocol/schema/*`、`protocol/test-vectors/*`：机器可读契约和跨语言向量。
- `proxy/src/protocol_v2.rs`、`proxy/src/mcp.rs`：Rust action、MCP 工具和 clipboard 调度。
- `skills/agent-remote-device/`：移除“approved application”前置条件，保留状态绑定和高风险确认规则。
- `docs/protocol.md`、`docs/macos-security.md`、`docs/rules/10-macos-security.md`：先更新冲突规则。

### 11.2 `agent-remote-server`

- 新增 Alembic migration 和模型字段。
- 更新 device-session schemas、policy schema、API 和 service 状态机。
- claim/connected/approve/reconnect/abort/stop/expire 全路径按 authorization mode 分支并严格校验。
- capability 选择必须要求 full-trust 完整集合。
- 更新 API、并发、迁移、retention、relay 和审计测试。
- 保留旧模式兼容时，必须以显式 `authorization_mode` 区分，不能从 approvals 是否为空推断。

### 11.3 `agent-remote-node`

- 广告并传播 `session_full_trust_v1`、`application_launch_v1` 和 `global_clipboard_v1`。
- 更新 managed context 的 capability 严格验证和测试。
- 同步 Node 内置 managed skill。
- 不增加 Node 对本机应用、剪贴板或明文动作的可见性。

### 11.4 `agent-remote-admin-web`

- policy 类型从 `local_approval_required: true` 改为结构化 authorization mode。
- “强制本机审批”改为“选择会话后授予会话级全功能信任”。
- 不显示虚假的应用审批数量。
- 历史 `pending_user_approval` 和 `denied` 状态仍需安全渲染。
- 中英文文案、类型、组件测试和 API fixtures 同步更新。

### 11.5 根仓库

- 更新 `local-device-control-security-design.md`、`local-device-control-binding-design.md`、
  `agent-remote-architecture.md`、operations runbook、README 和发布说明。
- 更新跨仓库 E2E，使其覆盖自动激活、launch 和无 observation clipboard。
- 更新生产 release evidence schema、外部门禁、装配脚本和合同测试。
- 新发布证据不得继续声明逐应用审批、三档控制等级或剪贴板审批已经存在。

## 12. 兼容和发布策略

### 12.1 Capability 集合

新模式至少要求：

```text
observation_mode_v2
ax_state_v2
adaptive_settle_v2
clipboard_payload_v2
session_full_trust_v1
application_launch_v1
global_clipboard_v1
```

前三项继续构成 v2 observation 基础；后四项构成目标 full-trust 产品能力。任何一项缺失时，Server
不得把新模式 candidate 标记为完整可控，也不得静默隐藏 launch 或退回应用绑定 clipboard。

### 12.2 推荐上线顺序

1. **文档与契约**：更新安全事实源、ADR/协议、JSON Schema、测试向量和 capability 名称。
2. **Server 双模式**：上线数据库字段、policy、旧模式兼容和 full-trust 状态机，但生产策略仍关闭。
3. **Node/proxy**：上线能力广告、managed context、MCP launch 和 global clipboard 支持。
4. **Device APP**：上线新 IPC、Executor、自动激活和精简 UI。
5. **Admin Web**：上线新 policy 和状态显示。
6. **跨仓库验证**：固定精确组件 commit，跑真实 macOS、混合版本和故障注入测试。
7. **发布证据**：生成并审核与新安全声明匹配的证据 schema。
8. **生产切换**：只有完整签名组合通过 release gate 后，才把默认模式切换为 `session_full_trust`。
9. **遗留清理**：至少经过一个明确兼容窗口后，单独删除 Approval UI、旧 approve API 和 approvals 表的剩余兼容代码。

不得以修改 skill、环境变量或单个组件的方式提前启用。Server 默认策略、Node capability、Device 行为和
签名 release evidence 必须作为一个经过认证的组合上线。

### 12.3 混合版本行为

- 新 Server + 旧 Device：legacy 策略允许省略 `device_capabilities`；full-trust 策略以
  `DEVICE_CONTROL_DEVICE_UPGRADE_REQUIRED` 拒绝，且不得向旧 Device 发送未知配置。
- 旧 Server + 新 Device：新 Device 明确显示服务版本不支持，不能恢复已经删除的隐式审批 UI。
- 新 proxy + 旧 Device：Server 不协商新 capability；launch/global clipboard 返回 unsupported，不发送未知 frame。
- 旧 proxy + 新 Device：candidate 不满足完整能力集合，不进入 full-trust active。
- capability 或 policy version 不匹配：fail closed，用户回到 session 列表并看到可操作的升级错误。

## 13. 测试计划

### 13.1 Device 单元测试

- 普通 claim：`selecting -> claiming -> activating -> active`，不经过 awaiting approval。
- claim 失败、activation 失败、binding 改变和 XPC 重连不出现错误的 active 状态。
- session switch、end、rebind、TTL、permission revoke 清除 authorization。
- generation 轮换只复制相同 policy version 和 scope。
- 动态解析运行中、新启动和新安装应用。
- 名称歧义、身份变化、自身进程、无 GUI app 和保护表面全部拒绝。
- `launch_application` 参数严格验证、超时、未知结果、终止性 transport 处理和前台恢复。
- 无 observation clipboard 成功；空、非文本、超限和不可用错误正确。
- clipboard 不推进 state/screenshot generation，不破坏已有 per-app AX state。
- turn、Escape、睡眠、锁屏、用户切换和 XPC loss 释放输入并恢复状态。

### 13.2 Rust/protocol 测试

- Swift/Rust 对 launch valid/invalid test vector 得到一致结果。
- 未知字段、路径、URL、控制字符、超长名称和未协商 capability 被拒绝。
- MCP 只在完整 capability 下发送 launch/global clipboard。
- clipboard payload 严格执行 UTF-8 和 64 KiB 上限。
- unknown action result 不跨 generation 重放。
- fuzz corpus 覆盖新增 action。

### 13.3 Server 测试

- migration upgrade/downgrade、历史回填和约束。
- full-trust claim 后 `pending_device -> active`，无 approval row。
- full-trust session 调用 approve 返回冲突。
- 旧模式仍可完成 `pending_user_approval -> active`。
- 并发 claim、rebind、machine lock、multi-worker relay revoke 和过期处理。
- policy/capability 不完整时 candidate 不可控。
- 审计只记录授权元数据，不包含应用和剪贴板内容。

### 13.4 真实 macOS 和跨仓库 E2E

至少覆盖：

1. 选择未绑定 session 后无审批页面并进入等待控制。
2. 抢占确认后旧设备 relay 立即关闭，新设备自动激活。
3. 控制 Safari、Chrome、Firefox、Finder、Terminal、System Settings、原生应用和 AX 不完整 Electron 应用。
4. 通过 Bundle ID 和唯一名称启动应用，并得到首次 observation。
5. 路径、URL、脚本、Device 自身、登录窗口和保护表面启动失败。
6. session 开始后安装或首次启动的应用可以动态控制。
7. 未 observe 任何应用时读取全局剪贴板。
8. clipboard 内容不会出现在 Server、Node、Device、proxy 日志和测试制品中。
9. active 期间撤销 Accessibility 或 Screen Recording，控制立即结束。
10. Escape 不传给目标应用；输入状态释放，前台应用恢复。
11. 网络中断、Broker/Executor 崩溃、Server 重启和 generation 轮换不产生双活或重放。
12. 远端高风险最终动作仍触发 Claude/会话侧确认策略。

## 14. 发布证据变更

旧 release gate 中以下声明必须删除或替换：

- `application_control_levels`
- `clipboard_permission`
- `per_session_application_approval`
- `approval_preserves_foreground_application`
- 以“未批准应用”为前提的捕获断言

新证据至少增加：

```text
session_selection_grants_full_trust
full_trust_expires_with_device_session
dynamic_application_identity_verified
device_processes_excluded
protected_system_surfaces_rejected
application_launch_bundle_id
application_launch_name_ambiguity_rejected
application_launch_paths_urls_arguments_rejected
global_clipboard_without_observation
global_clipboard_content_not_logged
foreground_restored_after_launch_and_action
mixed_version_fails_closed
remote_consequential_action_confirmation_preserved
```

外部安全评审范围必须明确说明：产品现在有意允许 Terminal、Finder、System Settings、密码管理器和其他
用户 GUI 应用的 Full Control。这是信任模型变化，不得继续引用旧的“对齐 Anthropic 三档应用审批”结论。

## 15. 分阶段执行清单

### 阶段 A：事实源和协议

- [x] 更新根安全设计、绑定设计和架构文档。
- [x] 更新 Device security rules，解除“激活前必须精确审批应用”的旧强制规则。
- [x] 定义 `SessionAuthorization`、policy schema 和 capability 常量。
- [x] 更新 v2 JSON Schema、Swift/Rust 模型和 test vectors。
- [x] 评审旧 v1 fallback 与新 full-trust capability 的边界。

### 阶段 B：Server 和数据迁移

- [x] 新增 authorization 字段和 Alembic migration。
- [x] 实现 Server-owned policy 和双模式状态机。
- [x] 更新 candidates、claim、connected、approve、reconnect 和审计。
- [x] 完成并发、迁移、retention 和 API 测试。

### 阶段 C：Device 安全执行层

- [x] 用 session authorization 替代 Executor 新路径中的 approvals。
- [x] 实现动态应用身份解析和排除策略。
- [x] 实现 `launch_application` 和首次 observation。
- [x] 实现无 application state 依赖的全局 clipboard。
- [x] 验证 stop、rotation、foreground restore 和 fail-closed 清理。

### 阶段 D：Device APP 和 Broker

- [x] 删除待批准 UI 和相关状态、模型、discovery 快照及本地化。
- [x] claim 后保持 activating，不闪回 ready。
- [x] Broker 自动激活并完成超时对账。
- [x] 完成 waiting、paused、switch、end 和 failure UI。

### 阶段 E：Node、proxy、skill 和 Admin Web

- [x] Node 广告和传播新 capability。
- [x] proxy 暴露 launch，并修改 clipboard 调度。
- [x] 更新两处 managed skill，保留远端高风险动作确认。
- [x] Admin Web 更新 policy、状态和中英文文案。

### 阶段 F：功能集成（发布验证延期）

- [x] 各仓库本地完整质量门禁通过。
- [x] 跨语言协议与 full-trust 合成跨仓库 E2E 已通过，并覆盖实际 API claim 流程、`pending_device -> active`
  和动态 binding 配置传播。
- [ ] 真实签名/公证 macOS E2E 因当前无 Developer ID 暂不运行，也不纳入本轮 release 范围。
- [x] 混合版本 fail-closed 单元/合同已覆盖。
- [ ] 五场景真实混合版本部署矩阵延后到后续 community 版本升级时运行；当前仅有 fail-closed
  单元、合同与合成覆盖。
- [x] 更新 release evidence schema、装配脚本、合同测试和运维手册。
- [ ] 独立安全评审接受新的全信任边界。
- [ ] 精确组件组合签名并切换生产默认策略。

## 16. 完成标准

只有以下条件全部满足，任务才可以声明完成：

1. 产品路径中不存在应用待批准页面、逐应用勾选、控制等级选择或剪贴板勾选。
2. 选择 session 后直接进入连接/等待控制界面，抢占场景仍有确认。
3. Server 新模式不创建 approval rows，也不经过 `pending_user_approval`。
4. Executor 对所有合格应用提供 Full Control，同时保持具体应用、窗口和状态绑定。
5. `launch_application` 可以安全启动已安装 GUI 应用，且无法接受路径、URL、参数、脚本或 Device 自身。
6. `read_clipboard` 无需 observation，仍受完整 binding、lease、sequence、64 KiB 和隐私约束。
7. 所有停止、撤销、崩溃、断线、权限撤销和 generation 轮换场景 fail closed。
8. 高风险最终动作的远端确认策略仍存在并有回归测试。
9. 所有相关文档、规则、API、schema、skill、管理 UI 和发布证据与新事实一致。
10. 各组件质量门禁、跨语言合同和本地合成跨组件 E2E 全部通过。

真实 Developer ID 签名/公证 macOS E2E、五场景真实新旧制品部署矩阵、独立安全评审和生产默认
策略切换属于后续发布验证，不阻塞本轮功能实现收口，也不得由 fixture、合同测试或合成 E2E 代替。

## 17. 后续 Agent 执行约束

- 开始实施前先读取每个 sibling 仓库的 `AGENTS.md` 和相应 `docs/rules/*`。
- 先提交或至少先形成文档与协议变更，再改安全边界代码。
- 跨协议修改必须同时更新 schema、test vectors、Swift、Rust、Server/Node capability 和 focused tests。
- 不得通过删除校验、填充虚假 approvals 或硬编码万能 application identity 快速实现。
- 不得修改日志以输出应用目标、剪贴板、窗口、AX、截图、输入或 URL 来辅助调试。
- 每一阶段完成后运行该仓库完整质量门禁；最终运行根仓库跨组件 E2E 和 release contract tests。
- 若实际 macOS API 无法同时满足动态应用控制、XPC 隔离、签名校验和前台恢复，停止实现并更新设计评审，
  不得静默合并权限边界或改用 shell/AppleScript 绕过。
