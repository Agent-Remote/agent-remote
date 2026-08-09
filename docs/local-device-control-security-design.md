# agent-remote macOS 本地设备控制安全设计

## 1. 文档状态

本文定义远端 Claude Code 通过 agent-remote 控制用户本机 macOS 图形应用的长期架构、安全边界和实施门禁。首期仅实现 macOS；协议使用平台无关的数据类型，为后续平台保留扩展点，但不承诺其他平台兼容性。

本文基于 2026-07-30 可查的 Anthropic 官方 Computer Use 文档。官方未公开的应用分类明细、内部提示、分类器和实现细节不作推测。任何声称“与官方一致”的行为，仅指本文第 5 节列出的公开可观察行为；官方行为变化后必须通过单独的兼容性评审更新，不能静默改变产品权限。

设备主动选择远端 Claude session、claim/rebind、live-only 绑定唯一性和 App/Web 停止语义见
`local-device-control-binding-design.md`。本文件中的设备控制授权、generation、relay、应用审批和
本机 Claude 隔离要求同样适用于主动 claim 流程。

绝对“0 漏洞”无法被设计、测试或形式化检查完全证明。本项目的可验证发布目标是：

- 0 个已知 Critical 或 High 安全漏洞；
- 0 条已知可绕过用户审批、跨租户边界、本地 Claude 隔离或设备会话绑定的路径；
- 默认拒绝未知协议、越权动作和失去上下文的 GUI 状态；
- 所有安全声明都有自动化测试、人工验证或明确记录的外部假设。

## 2. 已确认的产品决策

1. 本地设备控制首期只支持 macOS，协议预留平台字段。
2. 远端 Claude Code 是唯一参与任务推理的 Claude 进程。本机可以安装 Claude Code 或 Claude Desktop，但 agent-remote 不发现、不启动、不登录、不配置也不调用它们。
3. 本机 agent-remote 组件不得向 Anthropic 服务发送请求，也不得持有 Anthropic API key、Claude OAuth token 或 Claude 登录态。
4. 首版使用远端 Claude Code 的受管 MCP 工具直接完成截图与动作循环，不引入独立的 Anthropic Computer Use API agent loop。
5. 本机应用审批、控制等级、警告、全局停止、单会话锁和窗口隐藏行为对齐 Anthropic 已公开的 Computer Use 行为，不自行增加应用类别判断。
6. GUI 状态异常、目标应用变化、系统权限弹窗、动作上下文不一致或协议校验失败时立即停止，不自动尝试绕过。
7. 系统面向多用户部署；普通用户、远端 Claude 输出和屏幕内容均不可信。
8. 控制面管理员、Node root、用户本机操作系统和本机用户属于可信计算基。本文不防御这些主体主动读取内存、替换二进制或伪造运行状态。
9. 控制面可参与授权和中继，但不保存截图、输入内容、剪贴板内容或窗口图像。设备数据使用端到端加密，降低日志、备份和误配置造成的暴露。
10. 正式启用设备控制前，本机应用必须完成签名、公证、权限检查和出站网络策略检查。
11. 设备控制绑定的唯一事实来源是 Server；任何运行时副本必须匹配完整的
    `user_id`、`device_id`、`tool_session_id`、`device_session_id`、`node_id` 和
    `generation`，不能只按 `tool_session_id` 清理或恢复授权。



## 3. 目标与非目标



### 3.1 目标

1. 远端 Claude Code 可以在用户明确批准后查看和操作本机应用。
2. 每个请求绑定准确的用户、设备、远端 session、设备 session、应用和授权代次。
3. 多个用户、设备和 session 之间不能复用授权、密钥、截图或动作通道。
4. 用户可以从 macOS 全局立即中止当前动作，并能明确看到何时正在被控制。
5. 本地 Claude 安装、配置、登录态、MCP、插件、Keychain 项和历史数据与本功能完全隔离。
6. 本机网络策略能够证明设备组件只连接获准的 agent-remote 目标。
7. 审计记录足以调查授权和生命周期问题，但不记录 GUI 内容和用户输入。



### 3.2 非目标

- 不在本机运行 Claude 推理或 Anthropic Computer Use API agent loop。
- 不复用 Claude Code 内置的保留 MCP server `computer-use`。
- 不提供通用反向端口转发、SOCKS、HTTP 代理或任意目标访问。
- 不向远端暴露本机 shell、AppleScript、任意文件 API、任意进程 API 或任意 URL 导航能力。
- 不承诺与 Anthropic 未公开的应用分类、提示、注入分类器或内部实现逐字节一致。
- 不防御已取得用户 macOS 会话控制权的恶意软件、恶意本机管理员、恶意 Node root 或恶意控制面管理员。
- 不保证 GUI 自动化永远正确；不确定状态必须停止并交还用户。



## 4. 总体架构

```text
Remote Native Runtime
  -> managed Claude Code
  -> managed plugin and stdio MCP proxy: agent-remote-device
  -> authenticated device-session channel
  -> control-plane relay (ciphertext only in the data path)
  -> local Agent Remote Device.app outbound connection
       -> network broker
       -> local IPC
       -> GUI executor and approval UI
       -> macOS Screen Recording / Accessibility
       -> approved applications
```

控制面负责身份、授权状态、一次性连接材料、短期租约、撤销和审计。控制面中继只处理有大小、速率和生命周期边界的加密帧，不解析截图或输入内容。

本机始终主动建立出站连接，不监听公网或局域网端口。远端 MCP proxy 同样主动连接控制面，不获得本机地址、任意目标或通用网络转发能力。

### 4.1 本机组件

`Agent Remote Device.app` 是独立签名和公证的 macOS 应用，使用独立 bundle identifier、数据目录和 Keychain access group。应用至少分离以下职责：


| 组件             | 权限                               | 禁止持有的能力                               |
| -------------- | -------------------------------- | ------------------------------------- |
| Approval UI    | 展示 session、应用、控制等级和警告；接收允许、拒绝和停止 | Claude 凭据、远端命令执行                      |
| Network broker | 设备认证、出站连接、协议帧、租约和端到端密钥           | Screen Recording、Accessibility、任意 URL |
| GUI executor   | 截图、鼠标、键盘、窗口隐藏和恢复                 | Anthropic 凭据、设备长期凭据、任意网络目标            |


Network broker 与 GUI executor 只通过版本化 XPC 或 owner-only 本地 IPC 通信。正式实现前必须用签名安装包验证 App Sandbox、TCC、ScreenCaptureKit、Accessibility 和进程拆分能够同时满足要求；验证失败时不得把两个权限集合无条件合并，而应重新评审边界。

### 4.2 远端组件

受管插件提供：

- stdio MCP proxy；
- session start、turn stop、session end 等生命周期通知；
- 与当前 agent-remote session 绑定的设备工具；
- 图片结果和动作结果到 Claude Code 的转换。

MCP server 名称使用 `agent-remote-device`，不得使用 Claude Code 保留名称 `computer-use`。MCP proxy 不接受来自项目仓库的可执行文件、动态插件或 endpoint 覆盖。

### 4.3 控制面实体

新增 `device_sessions`：


| 字段                          | 说明                     |
| --------------------------- | ---------------------- |
| `id`                        | 不可枚举的设备 session ID     |
| `user_id`                   | 所属用户                   |
| `device_id`                 | 被控制设备                  |
| `tool_session_id`           | 绑定的远端 Claude session |
| `node_id`                   | 远端 Node                |
| `platform`                  | 首期固定为 `macos`          |
| `status`                    | 状态机当前状态                |
| `generation`                | 重连和撤销代次，使用正的有符号 64 位范围 |
| `lease_until`               | 当前短期授权租约               |
| `created_at` / `expires_at` | 生命周期边界                 |


应用审批和额外权限属于设备本地状态。控制面只保存应用稳定标识的摘要、控制等级、审批结果、时间和审计关联 ID，不保存窗口标题、屏幕内容或输入内容。

### 4.4 实现语言与 macOS 技术栈

`Agent Remote Device.app` 使用原生 Swift 6 实现，不使用 Electron、WebView、Tauri 或内嵌本地 Claude。选择原生 Swift 的原因是本功能直接依赖 macOS TCC、代码签名、App Sandbox、Screen Recording、Accessibility 和 XPC；原生实现能够减少额外运行时、跨语言 FFI 和供应链攻击面。

本机组件采用：

| 领域 | 技术 | 用途 |
| --- | --- | --- |
| 应用和审批 UI | SwiftUI | 状态窗口、应用审批、设置和停止入口 |
| 原生窗口集成 | AppKit | 窗口管理、应用隐藏与恢复、macOS 生命周期 |
| 屏幕和窗口捕获 | ScreenCaptureKit | 捕获获准应用，并排除状态窗口和未批准应用 |
| 应用与窗口识别 | Accessibility API / `AXUIElement` | 校验应用、窗口、前台状态和控制上下文 |
| 鼠标和键盘 | CoreGraphics `CGEvent` | 执行经过授权和坐标校验的输入动作 |
| 本机通知 | UserNotifications | 控制开始、完成、失败和停止提示 |
| 权限进程隔离 | XPC | 隔离 Approval UI、Network broker 和 GUI executor |
| 设备密钥 | Keychain Services | 保存独立于 Claude 的设备密钥和引用 |
| 网络 | Network.framework 或 URLSession | 连接固定的 agent-remote endpoint |

界面遵循 macOS Human Interface Guidelines，使用系统组件和标准权限说明。功能界面以审批、状态和立即停止为中心，不提供浏览器式工作台、内嵌终端或通用自动化编辑器。

远端 MCP proxy 使用 Rust stable 和 Tokio 实现，与现有 `agent-remote-cli` 的运行时和异步网络技术保持一致。它作为受管 Linux 二进制运行在远端 session 中。Swift 应用与 Rust proxy 不通过 FFI 共享可执行代码，只共享版本化协议 schema、固定枚举和跨语言测试向量。

端到端加密库在第 6.4 节要求的 ADR 中单独选择。在 ADR 完成前，不因为 Swift 或 Rust 已提供某个密码 API 就自行组合密码协议。

### 4.5 仓库与所有权边界

新增独立仓库 `agent-remote-device`，负责 macOS 应用、XPC 服务、远端 MCP proxy、设备协议 schema、签名、公证和安装产物。不得把 `Agent Remote Device.app` 放入 `agent-remote-cli`：两者使用不同的构建系统、权限、签名身份、发布门禁和更新生命周期。

建议目录结构：

```text
agent-remote-device/
  README.md
  docs/
    protocol.md
    macos-security.md
    release-signing.md
  protocol/
    schema/
    test-vectors/
  macos/
    AgentRemoteDevice.xcodeproj
    App/
    ApprovalUI/
    NetworkBroker/
    GUIExecutor/
    Shared/
    Tests/
    Entitlements/
  proxy/
    Cargo.toml
    src/
  packaging/
    notarization/
    mdm/
    network-policy/
  scripts/
```

跨仓库所有权固定为：

| 能力 | 所属仓库 |
| --- | --- |
| 总体安全设计、跨仓库契约和发布顺序 | `agent-remote` |
| macOS 应用、XPC 服务、远端 MCP proxy、设备协议和制品 | `agent-remote-device` |
| `device_sessions`、用户授权、短租约、relay API 和审计 | `agent-remote-server` |
| Node capability、设备数据通道和远端 runtime 集成 | `agent-remote-node` |
| `agent-remote device ...` 安装、状态、诊断和撤销命令 | `agent-remote-cli` |
| 设备、session、策略和审计管理页面 | `agent-remote-admin-web` |

`agent-remote-device` 使用一个仓库容纳 Swift 本机端和 Rust 远端 proxy，是因为二者共同拥有设备协议并必须作为兼容版本对发布。未来 Windows 实现可以在同一仓库增加独立平台目录，但首期构建、测试和 capability 只允许 `platform=macos`。

## 5. Anthropic 公开行为兼容配置



### 5.1 权限和资格

本功能不使用本机 Claude 的 Pro/Max 资格，也不要求本机登录 claude.ai。远端 Claude Code 的资格和登录继续由现有远端账户模型负责。

macOS 首次启用时，`Agent Remote Device.app` 请求：

- Accessibility：点击、输入和滚动；
- Screen Recording：查看屏幕。

缺少任一权限时，控制动作失败并引导用户进入对应系统设置。Screen Recording 权限变更后如系统要求重启进程，应明确提示并停止当前设备 session。

### 5.2 每 session 应用审批

首次请求某个应用时，本机必须展示：

- Claude 请求控制的应用；
- 该应用的控制等级；
- 额外权限，例如剪贴板；
- 控制期间将隐藏的其他应用数量；
- `Allow for this session` 和 `Deny`。

授权只对当前设备 session 有效。可以一次审批多个应用。授权不得跨 session、设备、用户、重连代次或本机注销复用。

### 5.3 应用控制等级

严格采用 Anthropic 公开的三档行为：


| 等级           | 能力                | 官方公开类别       |
| ------------ | ----------------- | ------------ |
| View only    | 只在截图中查看           | 浏览器、交易平台     |
| Click only   | 点击和滚动，不允许输入或键盘快捷键 | Terminal、IDE |
| Full control | 点击、输入、拖拽和键盘快捷键    | 其他应用         |


官方文档没有公开完整 bundle identifier 和类别映射。因此首版只能对官方明确举例的应用建立版本化测试映射；任何希望声称“官方一致”但无法从官方资料确定类别的新应用，必须进入兼容性待确认状态，不能由开发者凭主观判断分类。产品界面应说明“等待确认应用类别”，由用户决定是否继续当前 session，但该决定不得被记录为官方分类。

公开的额外警告保持一致：


| 警告                         | 官方示例                                         |
| -------------------------- | -------------------------------------------- |
| Equivalent to shell access | Terminal、iTerm、VS Code、Warp 和其他 Terminal/IDE |
| Can read or write any file | Finder                                       |
| Can change system settings | System Settings                              |


这些应用不是因为警告被自动禁止；用户仍按公开控制等级和 session 审批决定是否允许。

### 5.4 单 session 锁

第一次设备动作成功后获取机器级控制锁。其他 Claude session 的设备控制请求失败，并显示持锁 session。锁保持到远端 Claude session 退出或被确认失效；完成单次任务不释放锁。

远端进程异常退出、租约过期或设备通道无法续租时，恢复隐藏应用、停止执行动作并释放锁。控制面短暂不可用不能无限延长授权。

### 5.5 窗口可见性

控制开始后隐藏未批准的可见应用，只向截图暴露批准应用。由于 Claude terminal 位于远端，本机没有可保留的 Claude terminal；本机 `Agent Remote Device.app` 状态窗口承担官方终端的观察和停止作用，并从截图中排除。

turn 结束后自动恢复隐藏应用。受管插件必须通过可信生命周期事件发出 turn stop；缺失该事件或连接异常时，本机按失败路径恢复应用并停止动作。

### 5.6 截图和坐标

截图发送前按官方公开行为自动缩小并保持宽高比。兼容配置不提供用户可调的目标尺寸。具体缩放结果以受支持 Claude Code 版本的兼容性测试为准，不能把官方示例中的单台 16 英寸 MacBook Pro 数值当作所有设备的固定协议值。

坐标始终相对于传给模型的图像。GUI executor 在执行前将坐标映射回原窗口或显示空间，并验证：

- 截图代次仍为最新；
- 显示布局和缩放未变化；
- 目标应用和窗口仍存在；
- 前台应用与动作授权一致；
- 坐标位于获准捕获区域。

任一检查失败立即停止，不执行猜测性点击。

### 5.7 全局停止

获得控制锁后显示 macOS 通知，说明 Claude 正在使用本机并可按 `Esc` 停止。`Esc` 在全局范围中止当前动作、恢复隐藏应用并把控制权交还用户，按键本身不得传给目标应用。

与官方公开行为一致，中止当前动作后设备 session 仍持有机器级锁，直到远端 Claude session 退出。用户可以在状态窗口执行 `End session`，立即撤销租约并释放锁。

## 6. 工具与协议



### 6.1 MCP 工具

首版工具输入对齐公开的 Computer Use 动作集合，但通过自定义 MCP 暴露：

- `screenshot`
- `left_click`
- `type`
- `key`
- `mouse_move`
- `scroll`
- `left_click_drag`
- `right_click`
- `middle_click`
- `double_click`
- `triple_click`
- `left_mouse_down`
- `left_mouse_up`
- `hold_key`
- `wait`
- 在受支持模型和兼容配置下的 `zoom`

远端 MCP proxy 可以额外暴露 `input_text` 这类组合 helper 以减少模型往返和图片 Token。
该 helper 只能按固定顺序展开为现有已批准动作，必须在同一 operation guard 内逐步执行；每一步
仍独立校验完整 binding、单调 sequence、截图 generation、应用/窗口身份和控制等级。中间截图
不得返回模型，仅返回最后一次成功动作的截图；任一步失败即停止，并明确报告已完成的前缀，
禁止把组合 helper 编码成绕过设备协议的新动作。

动作是否可用必须同时满足工具版本、远端模型能力、应用控制等级和当前本地审批。不能因为模型请求了某个动作就自动提权。

每个调用由 MCP proxy 注入以下不可由 Claude 或项目修改的上下文：

```text
user_id
device_id
tool_session_id
device_session_id
generation
monotonic_sequence
current_screenshot_generation
```

`generation` 的跨组件有效范围为 `1...9223372036854775807`，与 Server 的 PostgreSQL
`BIGINT` 持久化边界一致。非终态最多使用 `9223372036854775806`；最大值只保留给最终停止和
撤销。重连或中止动作在没有非终态代次空间时，必须在修改状态、审计或 Node 任务前失败；最终停止
仍可使用保留值完成全局撤销。Node、proxy 和 macOS Broker 必须在各自信任边界独立验证该范围。

Claude 只能提供动作类型及该动作公开参数，不能提供 endpoint、设备身份、用户身份、PID、bundle path、任意文件路径或授权对象。

### 6.2 状态机

```text
pending_device
  -> pending_user_approval
  -> active
  -> stopping
  -> stopped

pending_* / active
  -> denied
  -> expired
  -> failed
```

只有本机 Approval UI 能完成应用审批。控制面管理员、Node、远端 Claude、MCP proxy 和项目配置都不能代替用户批准。

换绑会创建新的 `device_session_id`，即使新记录的初始 generation 仍为 `1`，也
不能复用旧 binding 的 relay、审批摘要、runtime context 或 GUI executor 状态。
旧任务如果观察到当前 binding 已经变化，必须安全地返回 stale/no-op。

### 6.3 顺序、重放和重连

- 每代连接使用一次性连接材料和短期可续租授权；
- 每个动作使用严格递增序号；
- GUI executor 只接受当前代次和下一个准确序号；
- 动作结果绑定请求 ID、序号和截图代次；
- 重复、乱序、跨代和过期消息全部拒绝；
- 重连生成新代次，不自动重放未确认动作；
- 连接断开时立即停止进行中的输入和拖拽，恢复所有按下状态。



### 6.4 加密

控制通道至少使用 TLS 1.3。截图、输入和动作 payload 在本机 broker 与远端 MCP proxy 之间额外使用会话级端到端加密，使控制面中继、日志和备份不出现明文。

不得自行设计密码算法或帧加密。`agent-remote-device/docs/adr/0001-session-e2e-encryption.md`
已固定内外两层 TLS 1.3、Network.framework、rustls 0.23、临时 P-256 身份、SPKI pin、TLS
exporter 确认、重放窗口和代次轮换方式，并由真实 Swift/Rust 互通测试覆盖。独立安全评审完成前，
设备控制仍只能用于不含真实数据的开发环境；仓库内互通测试不能替代密码学评审。

### 6.5 Token 与交互性能优化架构

本节定义并记录截图型 Computer Use 向结构化状态优先模式演进的完整架构。v2 请求 schema、
Swift/Rust 严格解码、AX full/diff、状态绑定元素动作、adaptive settle、图片分级、紧凑 MCP 面和
Node capability 传播已经实现；v1 仍是缺少能力或版本不匹配时的完整兼容路径。这里的“已实现”
自 `v0.2.5` 起表示正式默认能力：升级后的新 generation 在完整 capability 集合下直接协商 v2，
通用生产发布证据仍按第 12 节验证。真实 macOS/浏览器回归和指标证据继续作为发布质量审计，
不再构成运行时启用条件。

#### 6.5.1 当前基线与优化目标

当前 v1 在每个普通输入动作后重新捕获窗口、编码 PNG 并通过端到端加密通道返回。MCP proxy
可以丢弃组合 helper 的中间图片，从而减少模型可见图片和模型往返，但这不会消除本机截图、编码、
传输与 proxy 图片校验成本。继续增加组合动作只能取得递减收益，长期主路径必须改为：

```text
observe(auto)
  -> bounded AX full state or AX diff
  -> act with generation-bound element handle
  -> adaptive settle
  -> AX diff
  -> screenshot only when AX is insufficient or visual judgment is required
```

优化必须同时满足：

- 不降低应用审批、控制等级、机器锁、全局停止、代次和重放保护；
- 不因为省 Token 而复用旧坐标、旧元素或失去基准的 diff；
- 不把浏览器 DOM、cookie、profile、调试端口或通用 URL API 暴露给远端；
- 不记录 AX 文本、URL、窗口标题、截图、输入、坐标或剪贴板内容；
- AX 不完整、状态不一致或等待超时时可回退到显式截图，但不得静默猜测目标。

#### 6.5.2 可选观察结果与状态代次

已实现的 v2 请求为每个动作增加由 MCP proxy 选择、但受本机上限约束的观察策略：

```text
mode: none | ax_diff | ax_full | screenshot | both | auto
max_nodes
max_depth
max_text_per_node
max_total_text_bytes
max_visible_rows_per_container
settle: none | auto | fixed
settle_timeout_ms
image_profile: none | compact | standard | region
region
```

`none` 只省略返回内容，不能省略执行前后的应用、窗口、显示器、审批和 generation 校验。本机应把
窗口身份/几何校验与图片像素捕获、PNG/JPEG 编码拆开；无需图片时只更新受保护的状态上下文，不能
先生成完整图片再在 proxy 丢弃。

v2 必须拆分以下概念，不能继续由 `current_screenshot_generation` 一项同时表达：

- `state_generation`：任何成功观察或动作后的当前 GUI 状态代次；
- `screenshot_generation`：最后一张真正返回给模型且可用于坐标的图片代次；
- `state_id`：本机生成、绑定完整 session/application/window/display 上下文的不可预测状态标识；
- `base_state_id`：AX diff 所依赖的模型已见基准状态。

所有请求仍消耗严格递增的 `monotonic_sequence`。turn stop/resume、窗口或应用变化、显示布局变化、
generation 轮换和 diff 基准丢失必须使旧状态、旧坐标和旧元素句柄同时失效。

#### 6.5.3 有界 Accessibility 状态

AX snapshot 只能由拥有 Accessibility 权限且无任意网络能力的 GUI executor 生成。默认输出仅包含
完成 GUI 决策所需的规范化字段，例如 role、title、label、value、placeholder、URL、可见 frame、
settable 标记和已公开的 AX actions。首版预算建议为：

```text
max_nodes: 800
max_depth: 20
max_text_per_node: 160 characters
max_total_text: 16 KiB
max_visible_rows_per_container: 20
```

本机可以把请求的预算收紧，但不得接受超过编译时安全上限的值。密码/secure text field 的 value、
不可见敏感内容、无界 WebArea 子树和重复包装节点必须省略或脱敏。AX URL 仅作为已批准浏览器窗口
状态的一部分返回，不得变成绕过用户操作和应用审批的通用导航接口。

初次观察返回 full state；同一 application/window/display 上下文的后续观察默认返回 added、changed、
removed diff。当变化比例、节点数量或编码大小超过阈值，或 proxy 不能证明模型仍持有
`base_state_id` 时，必须返回 bounded full state 并标记 reset，不能发送无法独立解释的 diff。

#### 6.5.4 状态绑定的元素动作

元素动作不得只接受裸 `element_index`。句柄至少绑定：

```text
state_id
state_generation
application_digest
window_id
display_fingerprint
element_index
```

GUI executor 在执行 `press`、`set_value`、`select_text`、`scroll` 或 secondary action 前，必须验证该
句柄来自当前状态、AX 元素仍存在、目标应用和窗口未变化、元素实际公开对应 action，且本地审批的
控制等级足够。任一条件不满足返回具体 stale/not-actionable 错误；禁止自动改用相邻元素、同名元素
或坐标点击。

`set_value` 和文字选择属于 full-control 输入。secure text field、密码、认证凭据和受 Computer Use
确认策略要求 hand-off 的字段不得通过 AX 直接设置。坐标动作继续作为 AX 不完整应用的 fallback，
且必须绑定最后一张模型已见图片的 `screenshot_generation`。

#### 6.5.5 自适应等待与图片策略

固定 `wait_after_ms` 只保留为兼容和诊断能力，浏览器与动态应用默认使用 bounded adaptive settle：

1. 验证前台 application/window/display 上下文未变化；
2. 观察 WebArea URL/title、AX busy/loading 状态和 bounded tree hash；
3. 在最短 debounce 后连续两次得到稳定状态才返回 settled；
4. 总等待不得超过 5 秒，并受剩余 lease 和调用 deadline 的更小值约束；
5. 超时返回 `settle_status=timeout` 和最新安全状态，不得伪装为成功稳定。

图片按用途分级：AX 足够时不返回图片；普通视觉确认使用 compact image；坐标定位或 OCR 使用
standard image；细节检查使用 region image。任何缩放或压缩后的宽高必须写入截图上下文并用于坐标
映射。JPEG 可以降低带宽但不能被宣称必然降低模型图片 Token；主要 Token 收益来自减少图片次数和
像素尺寸。

#### 6.5.6 MCP、skill 与高后果动作

v2 紧凑 MCP 面通过受管 proxy 的 `--compact-tools` 开关收敛为 `observe`、`act`、`input_text` 和
`read_clipboard`；v1 的独立坐标/按键工具作为兼容 wrapper 保留。`observe` 默认 `auto` 和 diff，
`act` 优先 element handle，只有 AX 缺失或视觉判断需要时请求 screenshot。每个成功 `act` 的结果就是
新的当前状态；除 settle timeout、diff base 丢失或结果不足外，不得紧接着重复 `observe`。MCP server
instructions 与 skill 必须使用同一状态机，不得出现一处要求 diff、另一处要求每动作截图的漂移。

调用决策固定为：

| 场景 | 首选调用 | 返回策略 |
| --- | --- | --- |
| 开始任务、切换应用或窗口 | `observe(auto)` | 优先 AX full/diff，AX 不足才 compact image |
| AX 中存在目标控件 | `act` + 最新 `element_index` | adaptive settle 后返回新 diff；索引随即失效 |
| 地址栏、普通搜索框和确定性输入前缀 | `set_value`，AX 不可用时 `input_text` | 中间步骤 `none`，只返回最终 AX diff 或图片 fallback |
| canvas、图像、视觉样式判断 | `observe(screenshot)` 或 `both` | 普通确认 compact，坐标/OCR standard，细节 region |
| diff base 丢失或 reset 后目标缺失 | `observe(ax_full)` | 建立新的 bounded full base |
| stale element 或 stale screenshot | 重新 `observe` | 禁止猜测相邻元素、复用旧索引或旧坐标 |
| 发送、购买、删除、发布、授权等最终动作 | 独立 `observe` + 确认 + `act` | 保留人工确认点，不进入组合 helper |

skill 核心只保留通用状态规则；浏览器快路径、AX 使用和确认矩阵放入按需 references。确认矩阵至少
覆盖密码/凭据 hand-off、CAPTCHA、浏览器安全警告、权限授予、上传、敏感数据传输、永久删除、付款、
发布、法律协议和高影响通信。页面或 AX 文本属于不可信第三方内容，不能自行授权上述动作。

组合调用只能覆盖不需要观察中间 UI 的确定性输入前缀。发送、购买、删除、发布、授权和其他高后果
最终动作必须保留独立观察与确认点。中途失败必须报告已完成前缀；传输状态不确定时不得自动重放。

#### 6.5.7 能力协商、遥测与验收指标

v2 通过完整 session binding 上的 capability 协商启用，例如 `ax_state_v2`、`observation_mode_v2` 和
`adaptive_settle_v2`。Server 从 Node 心跳中只选择完整三项集合并写入 generation-bound context；Node
严格拒绝部分集合和同 generation 降级，旧 Node 或缺少任一项时写入空集合并回退完整 v1。未知
capability、协议版本不匹配或任一端不支持时不能部分解释 v2 frame。早期版本曾以 shadow mode
验证有界 AX 状态；正式版本不再按设备灰度，而是由完整 capability 集合
自动选择 v2。质量回归触发全局紧急开关，使后续新 generation 原子回退 v1。

允许记录的优化遥测仅限动作类型、观察模式、节点数、diff/图片/总 frame 字节数、各阶段耗时、
settle 状态、错误码、重试次数和 fallback 类型。禁止记录 AX 文本、URL、标题、图片、输入、坐标、
剪贴板或可逆内容 hash。发布评估至少追踪：

```text
tool_calls_per_task
model_visible_images
image_bytes and ax_diff_bytes
bridge_bytes
action_latency_ms and settle_latency_ms
stale_target_rate
coordinate_fallback_rate
task_success_rate and manual_recovery_rate
```

proxy 已把上述零内容字段实现为有界枚举/计数事件，写入 Node 固定的 owner-only JSONL 路径；文件达到
16 MiB、路径不安全或写入失败后停止采集，不影响动作结果。Device 仓库的
`docs/optimization-benchmark.md` 固定真实任务语料、v1/v2 采集方式和 baseline/candidate 对比命令；
`docs/adr/0002-ax-first-computer-use.md` 固定结构化状态优先的架构决策和拒绝的替代方案；生产评估
必须使用真实签名构建产生的 trace，不能用合成单元测试数据代替。

固定无敏感数据基准至少覆盖：浏览器打开 URL、搜索与自动补全、多标签切换、表单填写但不提交、
普通提交、滚动分页、动态加载、浏览器权限弹窗、安全警告、secure text field、AX 不完整的 Electron
应用、窗口移动/缩放/跨显示器，以及 turn stop/resume 后旧句柄失效。每项同时记录 v1 screenshot
baseline、组合 helper baseline 和 v2 AX 路径，不能只比较优化后的不同参数。

建议发布目标为：典型浏览器任务模型可见截图减少至少 70%，AX diff p50 小于 400 模型 tokens，
普通 AX 动作 p95 小于 1 秒，bounded settle p95 小于 5 秒，坐标 fallback 低于 20%；任何成本目标都
不能覆盖错误目标率、确认策略或 fail-closed 门禁。错误应用、错误窗口或错误元素动作必须为零；
否则不论 Token 和延迟改善多少都不得默认启用 v2 capability。

#### 6.5.8 全链路职责与单一决策源

优化不能只靠 skill 提示词约束。每层只拥有自己能够可靠执行的决策，避免多处重复判断或出现
“skill 要求 AX、proxy 仍默认截图”的漂移：

| 层 | 固定职责 | 不得承担 |
| --- | --- | --- |
| skill/reference | 判断何时使用结构化状态、图片、坐标和人工确认；保持调用序列简短 | 注入可信 binding、绕过 MCP schema 或自行声明 capability |
| MCP proxy | 暴露紧凑工具面、注入受管 context、维护模型已见 AX/image base、选择 observation policy | 信任模型提供的 session/state 标识或缓存 GUI 明文内容 |
| Node/Runtime Helper | 探测并广告完整 capability、生成 owner-only managed context、固定遥测路径 | 部分启用 v2、在同 generation 静默降级或读取 AX 内容 |
| Server | 只协商 Node 与产品策略的完整 capability 交集 | 看见设备内容、把未知 capability 当作已支持 |
| Broker/DeviceServices | 校验租约、序号、应用/窗口/显示器和本地审批，转发严格 v1/v2 frame | 解析、记录或 diff AX 文本和图片 |
| GUI Executor | 捕获有界 AX/image、维护短期元素映射、执行动作、settle、生成新状态 | 任意联网、跨应用复用元素、把 AX URL 变成导航 API |

MCP schema、server instructions、skill 和 benchmark 的调用状态机以
`agent-remote-device/docs/protocol.md` 为协议事实源；安全与发布边界以本文为事实源；具体浏览器操作以
`agent-remote-device/skills/agent-remote-device/references/browser.md` 为按需参考。修改任一处时必须用
同一 golden prompt/task corpus 回归其余三处。

#### 6.5.9 Token 预算与上下文管理

Token 优化分为三层，指标必须分别记录，不能用 bridge bytes 冒充模型 Token：

1. **工具发现成本**：skill description 只保留触发范围，`SKILL.md` 只保留通用状态机，浏览器和确认
   细节按需加载 reference；MCP 默认只广告四个 v2 工具，v1 wrapper 仅在兼容路径公开。
2. **每步观察成本**：优先 AX diff，设置节点、深度、单字段和总文本硬预算；不重复描述未变化节点，
   不在动作成功后立即重复 `observe`，确定性前缀使用 `none` 中间结果。
3. **视觉成本**：先减少图片次数，再缩小必要图片的尺寸/区域；只有视觉判断或坐标定位才升级
   `compact -> standard -> region`，禁止为了“保险”同时固定返回 AX 和全图。

每个任务需要同时汇总模型运行时报告的 input/image/output tokens、MCP tool-call 数、模型可见图片数，
以及零内容设备遥测中的 AX/image/bridge bytes。若运行时不能提供精确图片 Token，只报告图片次数、
尺寸和字节数，不推算或宣称 Token 节省比例。发布结论至少按浏览器、原生应用、Electron/AX 不完整
应用分桶，不能用浏览器优势掩盖其他应用退化。

#### 6.5.10 浏览器快路径与公开参考边界

浏览器是 v2 默认优化对象，但仍通过 macOS 公开 Accessibility 和用户可见 UI 操作：

- 地址栏、搜索框、普通表单优先最新 AX 元素的 `set_value`，导航键或提交作为独立动作；
- 链接、按钮、标签页、菜单和可滚动容器优先元素动作，每次结果直接成为下一状态；
- 自动补全、权限弹窗、下载、文件选择器、验证错误和提交前状态必须单独观察；
- WebArea 只遍历可见且有界的子树，稳定元素尽量保留 index；不可见、窗口外、secure 和重复包装内容
  不进入可执行映射；
- canvas、远程桌面、视频、复杂编辑器或 AX 语义缺失时按需回退图片/坐标，不反复尝试错误 AX 动作；
- Chromium/Electron 的 enhanced accessibility 只能作为公开 API 可用时的本机 best-effort 兼容项，
  必须有应用白名单、超时、恢复和真实版本矩阵；未完成专项验证前不得作为生产依赖；
- 不启用 CDP、远程调试端口、DOM 注入、cookie/profile 读取或浏览器内部私有 API。即使 OpenAI
  公开产品为其内置浏览器提供经审批的 Developer mode，本项目当前威胁模型仍选择更窄的 AX/UI 边界。

官方 OpenAI Computer Use 文档公开确认的可采用原则仅包括：GUI 不足以由 CLI/结构化连接器完成时
使用 Computer Use、优先专用 connector/MCP、任务保持小范围、应用权限独立审批、敏感动作额外确认、
网页内容视为不可信。官方公开文档没有给出内部 AX renderer、截图调度、Token 预算或私有调用算法，
因此本文不声称复刻“Codex 原本逻辑”。第三方 `open-codex-computer-use` 只用于比较 bounded AX tree、
element index 和常用应用操作体验，其实现不能越过本项目安全边界。

#### 6.5.11 自动协商、回滚与完成定义

Computer Use v2 是正式默认能力。Server 在 `DEVICE_CONTROL_V2_ENABLED=true` 时只对 Node 广告的完整
三项 capability 集合启用 v2；部分、未知或畸形集合完整回退 v1。混合版本部署由这一能力协商自然兼容，
不使用设备百分比分桶或临时验收窗口。活动 generation 固定其 capability 集合，不做中途协议切换。
部分 capability、错误目标、敏感遥测、stale/fallback 激增、成功率回退或 p95 超阈值时，管理员把开关
设为 `false`，终止受影响 session，并让重新审批的新 generation 使用 v1。回滚不删除审计证据，也不
自动重放状态未知的动作。

签名 release-evidence manifest 继续证明协调版本、供应链身份和通用生产门禁。Computer Use v2 专项
证据是可选质量记录，不是运行时授权。该证据可以绑定精确 application/proxy/Node/Server 摘要，并证明：签名安装、
Safari/Chrome/Firefox、AX 不完整 Electron fallback、golden prompt replay、零敏感内容遥测审计、错误
目标数为零、成功率无回退、模型可见图片减少至少 70%、普通动作 p95 不高于 1 秒、settle p95 不高于
5 秒、坐标 fallback 低于 20%，以及新 generation 回到 v1 的回滚演练。若选择生成 schema 4，专项
对象的 `report_sha256` 还必须对应
`security-tests.evidence.tar.gz` 内真实存在的普通报告文件，不能只提交布尔结论。该签名绑定现已由发布组装器和 Server 运行时
验证器共同验证：Apple profile 组装器将已验证的 `security-tests` 记录摘要写入
`computer_use_v2_evidence_sha256`；Community schema 2/3 固定为 `null`，schema 4 则要求受保护的
Community v2 记录、原始报告归档、同版本四组件摘要和明确风险接受。Server 在启动和运行期验证通用
发布清单，但不以该可选摘要决定 v2 capability。

“正式支持”要求跨语言协议 fixture、负向和预算测试、能力协商、完整 v1 fallback 与通用签名发布
门禁，这些从 `v0.2.5` 起作为默认部署路径。三浏览器与 AX 不完整应用真实回归、签名构建 benchmark、
零内容遥测审计、Claude Code/MCP 当前版本兼容报告和回滚演练仍用于持续质量验收；缺少单次可选报告
不关闭已经正式支持的 v2 能力。

## 7. 本地 Claude 硬隔离

本机设备组件必须满足以下不变量：

1. 不执行、查找、解析或探测 `claude`、Claude Desktop 或其版本。
2. 不读取或写入 `~/.claude`、Claude Desktop 数据目录、Claude MCP 配置、插件、历史记录或 session。
3. 使用独立 bundle identifier、容器目录、Keychain access group、日志目录和更新通道。
4. 不读取名称或 access group 属于 Claude/Anthropic 的 Keychain 项。
5. 不设置、读取或转发 `ANTHROPIC_API_KEY`、`CLAUDE_CODE_OAUTH_TOKEN` 及其他 Anthropic 凭据环境变量。
6. 不向本机 Claude 注入 MCP、hook、plugin、环境变量、证书或代理。
7. 不把本机 Claude、Terminal 或 IDE 作为自身控制面 UI。
8. 本机 Claude 的安装、卸载、登录、退出和升级不能改变设备桥状态。

构建和测试中应使用一台已安装且已登录个人 Claude 的测试 Mac，证明设备功能既不访问其文件，也不产生发往 Anthropic 的本机网络连接。测试不得读取真实凭据内容，只验证访问事件和网络目的地。

## 8. 本机网络约束

仅依靠代码约定不足以支持“本机绝不向 Anthropic 发送请求”的声明。正式启用要求：

1. 应用签名和 Apple notarization 校验成功；
2. 应用使用 Hardened Runtime，并尽可能启用 App Sandbox；
3. Network broker 的 endpoint 由已登录的 agent-remote 配置和控制面响应确定，Claude/MCP/项目不能覆盖；
4. MDM、系统网络过滤器或企业防火墙按签名进程实施出站 allowlist，只允许指定 agent-remote 控制面和节点；
5. 激活流程主动探测策略是否存在和生效，失败时拒绝启用设备控制；
6. CI 和发布测试通过受控 DNS、TLS 代理及连接审计确认不存在 Anthropic 目的地。

策略采用允许列表而不是仅阻止已知 Anthropic 域名，因为禁止列表无法证明没有遗漏的新域名。安装文档必须区分产品内检查和由管理员部署的系统级强制策略。

产品内激活检查通过固定在签名 Network Broker 中的受管 mach service、策略 ID 和 Ed25519 公钥完成。
Broker 在允许审批和建立 relay 前分别发送新的随机 challenge；受管服务必须返回绑定当前 Team ID、Broker
bundle ID、唯一控制面主机、Network Extension 启用状态和允许/拒绝主动探测结果的短时签名证明。
缺少服务、证明超过 30 秒、有效期超过 60 秒、字段或签名不匹配以及 5 秒内无响应均拒绝激活。该接口
不能读取发布证据 JSON 代替当前机器状态，具体 Network Extension/MDM 规则仍由部署方实现并提供原始证据。

## 9. 数据分类与留存


| 数据                         | 分类       | 控制面持久化   | 日志   |
| -------------------------- | -------- | -------- | ---- |
| 截图和 zoom 图像                | 高敏感内容    | 禁止       | 禁止   |
| 输入文本、快捷键、剪贴板               | 高敏感内容    | 禁止       | 禁止   |
| 窗口标题、页面内容                  | 高敏感内容    | 禁止       | 禁止   |
| 应用 bundle ID               | 敏感元数据    | 仅摘要或受限字段 | 默认摘要 |
| 动作类型                       | 审计元数据    | 允许       | 允许   |
| 坐标、输入长度、图片 hash            | 可形成行为侧信道 | 默认禁止     | 默认禁止 |
| session、device、user、时间、结果码 | 审计元数据    | 允许       | 允许   |


本机和远端只在完成当前工具调用所需的内存窗口内保留图片。崩溃转储必须关闭或确保敏感缓冲区不进入转储。临时文件不得用于图片、输入和剪贴板；无法避免时必须使用加密临时存储并在同一调用结束时清除，且在发布前单独评审。

终态设备 session 元数据和 `target_type=device_session` 审计元数据使用两个由数据负责人批准的独立
保留期。Server 只按停止时间删除终态 session 及其审批摘要，不删除 active session；审计期不得短于
session 期，且不会清理通用身份审计。两个期限默认关闭，生产启用设备控制时必须显式配置非零值，
后台任务按有界批次执行。legal hold、备份到期和删除证明按
`device-control-operations-runbook.md` 管理，不得使用未经评审的原始 SQL 绕过。

## 10. 威胁模型



### 10.1 受信任主体

- 用户本人和其当前 macOS 登录会话；
- 签名、公证且通过发布门禁的 agent-remote 本机组件；
- agent-remote 控制面管理员和服务端运行环境；
- agent-remote Node root、内核和受管远端 runtime；
- Apple 的代码签名、TCC 和系统安全机制；
- 用于模型请求的 Anthropic 服务身份。



### 10.2 不可信输入和主体

- 其他普通用户和租户；
- 项目仓库及其中的配置、MCP、hook、脚本和依赖；
- 远端 Claude 生成的动作；
- 截图、网页、文档和应用 UI 中的指令；
- 网络攻击者和重放者；
- 过期、被撤销或丢失的设备凭据；
- 未签名、被替换或版本不兼容的客户端。



### 10.3 主要攻击与控制


| 攻击                  | 必需控制                                                             |
| ------------------- | ---------------------------------------------------------------- |
| 跨租户控制设备             | 全链路 user/device/session 绑定；服务端对象归属检查；并发隔离测试                      |
| 窃取 ID 后连接           | ID 不作为凭证；一次性连接材料；设备身份；短租约                                        |
| 重放点击或输入             | generation、严格序号、请求 ID、截图代次                                       |
| 屏幕 prompt injection | 使用官方 Computer Use 能力时保留其分类器；自定义 MCP 路径不得声称继承分类器；高后果操作按官方建议要求人工确认 |
| 点击陈旧坐标              | 截图代次、窗口、前台应用、显示布局和坐标范围校验                                         |
| 项目注入设备 endpoint     | endpoint 不可由项目、Claude 或 MCP 参数提供                                 |
| 本地 Claude 数据串用      | 独立目录、Keychain、bundle ID、网络和访问监控测试                                |
| 控制面日志泄露 GUI 内容      | E2E payload、结构化日志 allowlist、禁止 body/header dump                  |
| daemon 断线时按键卡住      | fail closed；释放鼠标按键和修饰键；恢复应用                                      |
| 供应链替换客户端            | 签名、公证、更新签名、制品摘要、SBOM 和来源证明                                       |


自定义 MCP 路径不会自动获得 Anthropic Computer Use API 文档所述的截图 prompt-injection classifier。若该分类器是上线必需条件，必须改为在远端部署官方 Computer Use API agent loop，并把该变化作为独立架构评审；本机仍只运行设备桥，不向 Anthropic 连接。

## 11. 失败策略

以下情况立即停止当前动作、恢复隐藏应用并通知用户，不自动重试 GUI 操作：

- 目标应用、窗口或控制等级不匹配；
- 出现未批准应用或系统权限弹窗；
- 截图代次、显示布局或坐标映射变化；
- 消息重复、乱序、过期或跨代；
- 租约失效、设备被撤销或 session 状态不可确认；
- 网络断开、MCP proxy 退出或本机 executor 异常；
- 用户按 Esc、点击停止或 macOS 开始锁屏/切换用户；
- 动作超出公开 Computer Use schema 或当前应用控制等级。

传输层可在获得新连接材料后自动重连，但不重放未确认动作。恢复后必须先获取新截图，再由远端 Claude 重新决定下一步。

## 12. 安全验证与发布门禁



### 12.1 自动化验证

- 协议 parser fuzzing 和 property tests；
- generation、序号、租约和状态机模型测试；
- 跨用户、跨设备、跨 session、跨 Node 授权负向测试；
- MCP 参数注入、超大图片、压缩炸弹、畸形图片和资源耗尽测试；
- AX snapshot 节点/深度/文本预算、secure field 脱敏、diff reset 和超大 WebArea 测试；
- state-bound element handle 的跨窗口、跨应用、跨代次、过期和错误 action 负向测试；
- `none`/AX/image 观察模式、adaptive settle 超时和 v1/v2 capability 回退测试；
- 日志扫描，确保截图、输入、窗口标题、token 和明文 payload 不出现；
- 遥测扫描，确保 AX 文本、URL、坐标和可逆内容 hash 不出现；
- 文件访问监控，确保不访问 Claude 数据目录；
- 网络目的地测试，确保本机进程只访问 allowlist；
- 依赖漏洞、许可证、SBOM、制品签名和可复现来源检查；
- 安装、升级、降级、撤销和卸载后的权限残留测试。



### 12.2 macOS 端到端验证

- Accessibility 和 Screen Recording 首次授权、拒绝、撤销和进程重启；
- 官方三档应用控制等级；
- 每 session 审批和额外剪贴板权限；
- 单 session 机器锁和崩溃释放；
- 隐藏、排除和恢复未批准应用；
- Esc 全局停止及按键不传递；
- Retina、多显示器、缩放、窗口移动和显示器热插拔；
- 锁屏、快速用户切换、睡眠、唤醒和网络切换；
- 鼠标按下、拖拽或修饰键按下期间断线；
- Safari、Chrome 和 Firefox 的 AX full/diff、元素动作、动态加载和坐标 fallback；
- AX 不完整的 Electron 应用、secure text field 和浏览器权限/安全警告；
- 自适应等待的 settled/timeout、图片分级和 turn resume 后旧句柄失效；
- 本机同时安装并登录个人 Claude 时的隔离验证。



### 12.3 发布条件

Apple Developer ID profile 的任何一项不满足均不得启用对应生产 capability：

1. 0 个已知 Critical/High 漏洞；
2. 安全测试、协议 fuzz、跨租户 E2E 和 macOS 权限测试全部通过；
3. 独立安全评审完成，Critical/High 发现全部关闭并复测；
4. 签名、公证、SBOM、更新签名和制品摘要可验证；
5. 本机出站 allowlist 已安装并由激活检查确认；
6. 不访问本地 Claude 数据和不连接 Anthropic 的测试证据通过；
7. 撤销、全局停止和 fail-closed 演练通过；
8. 当前 Claude Code 和 MCP 版本完成兼容性验证。

无法取得 Apple Developer Program 身份的自托管部署可以改用
`community-local-trust` profile。该 profile 的生产含义、替代门禁和必须公开的剩余风险由
`community-local-trust-release.md` 定义；不得把自签名状态记录成 Developer ID 或 notarization 成功。

生产控制面不得只依靠 capability 布尔开关声明上述条件已满足。启用时必须验证由部署方固定
Ed25519 公钥签名、有效期不超过 30 天且绑定当前服务端版本的发布证据清单；清单至少固定 Server、
Node、macOS 应用、MCP proxy、SBOM、来源证明及上述第 2 至 8 项证据的 SHA-256 摘要。该签名门禁
只证明部署方批准了这些精确证据，不替代系统级出站策略、实际隔离采集、Apple 公证或独立安全评审。



## 13. 分阶段实施



### Phase 0：协议和验证原型

- 冻结设备 session 状态机、MCP schema 和审计字段；
- 使用无敏感数据的测试应用验证 MCP 图片结果和连续 GUI 操作；
- 验证 macOS TCC、进程拆分、全局 Esc 和窗口排除；
- 完成端到端加密 ADR 和本机网络策略原型。

该阶段不得控制真实用户应用或处理真实数据。

### Phase 1：单设备受控试用

- 签名、公证的 macOS 应用；
- 单用户单设备 session；
- 官方公开权限等级、警告、隐藏和机器锁；
- 控制面 relay、短租约、撤销和零内容日志；
- 完整停止、断线和升级恢复。



### Phase 2：多用户生产隔离

- 多租户授权和配额；
- 全套跨租户负向测试；
- 管理员策略、设备清单和远程撤销；
- 外部安全评审和发布门禁；
- 数据保留、事件响应和密钥轮换运行手册，见 `device-control-operations-runbook.md`。



### Phase 3：效果评估

- 测量自定义 MCP 路径的任务完成率、动作次数、错误停止率、延迟和图片成本；
- 建立浏览器、原生应用和 Electron 应用的固定无敏感数据基准任务；
- 以 shadow mode 采集节点数、diff/图片字节数、延迟、fallback 和错误码，不记录 GUI 内容；
- 只有在证据表明现有远端 Claude Code 路径不足时，评估远端 Computer Use API 子 Agent；
- API 子 Agent 不改变本机隔离：本机仍不登录 Claude、不持有 Anthropic 凭据、不向 Anthropic 发请求。

### Phase 4：结构化状态与成本优化

- P0（已实现，待生产证据）：确认矩阵、浏览器 skill/reference、固定基准任务、golden prompt corpus、
  零内容遥测、对比 harness 和独立 v2 ADR 已固化；真实签名构建 trace 仍需补齐；
- P1（已实现）：observation mode 使无需图片的动作跳过像素捕获和编码；
- P2（已实现）：bounded AX full/diff、state-bound element handle 和元素动作；
- P3（已实现，待真实应用验收）：adaptive settle、compact/standard/region 图片和浏览器调用策略；
- P4（已实现）：capability 协商、紧凑 MCP 工具面、默认 v2 选择和完整 v1 回退已实现；签名安装包
  benchmark 与回退演练作为持续发布质量证据维护，不作为运行时授权条件。

每个子阶段必须独立通过第 12 节门禁。不得先把 skill 切换到 AX 主路径，再补本机 freshness、
secure field、diff reset 或 fallback 测试。



## 14. 未决但不得猜测的事项

以下内容必须通过原型、官方资料或 ADR 确认：

- Claude Code 对自定义 MCP 图片结果进行长序列 GUI 操作的实际可靠性；
- Anthropic 未公开应用的官方类别映射；
- 自定义 MCP 是否能获得任何官方 Computer Use 专用提示或注入防御；默认答案为不能证明；
- App Sandbox、XPC、ScreenCaptureKit 和 Accessibility 的最终可行进程组合；
- 系统级按签名进程出站 allowlist 的具体 MDM/网络过滤实现；
- 多显示器坐标和截图缩放的最终兼容协议；
- 当前受管 Claude Code 版本的插件生命周期事件能否可靠标记 turn stop。

任何未决事项不得通过放宽权限、启用通用 shell、取消本地审批或记录敏感 payload 规避。

## 15. 官方依据

- [OpenAI Computer Use](https://learn.chatgpt.com/docs/computer-use.md)
- [OpenAI Browser](https://learn.chatgpt.com/docs/browser.md)
- [OpenAI Build skills](https://developers.openai.com/plugins/build/skills)
- [OpenAI Optimize Metadata](https://developers.openai.com/plugins/guides/optimize-metadata)
- [Claude Code CLI Computer Use](https://code.claude.com/docs/en/computer-use)
- [Claude Code MCP](https://code.claude.com/docs/en/mcp)
- [Anthropic Computer Use Tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Anthropic Computer Use reference implementation](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo)
- [Computer Use safety guide](https://support.claude.com/en/articles/14128542)

## 16. 非官方工程参考

- [open-codex-computer-use](https://github.com/iFurySt/open-codex-computer-use)：用于研究 AX tree、
  element index、set value、bounded snapshot 和常用应用操作体验。该项目不是 Anthropic 或 OpenAI
  的安全规范，不构成行为兼容、私有 API 可用性或生产安全证明；agent-remote 只采用经过本项目
  信任边界、协议和发布门禁重新验证的公开实现思路。
