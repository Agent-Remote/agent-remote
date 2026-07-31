# agent-remote macOS 本地设备控制安全设计

## 1. 文档状态

本文定义远端 Claude Code 通过 agent-remote 控制用户本机 macOS 图形应用的长期架构、安全边界和实施门禁。首期仅实现 macOS；协议使用平台无关的数据类型，为后续平台保留扩展点，但不承诺其他平台兼容性。

本文基于 2026-07-30 可查的 Anthropic 官方 Computer Use 文档。官方未公开的应用分类明细、内部提示、分类器和实现细节不作推测。任何声称“与官方一致”的行为，仅指本文第 5 节列出的公开可观察行为；官方行为变化后必须通过单独的兼容性评审更新，不能静默改变产品权限。

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
| `tool_session_id`           | 唯一绑定的远端 Claude session |
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
- 日志扫描，确保截图、输入、窗口标题、token 和明文 payload 不出现；
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
- 只有在证据表明现有远端 Claude Code 路径不足时，评估远端 Computer Use API 子 Agent；
- API 子 Agent 不改变本机隔离：本机仍不登录 Claude、不持有 Anthropic 凭据、不向 Anthropic 发请求。



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

- [Claude Code CLI Computer Use](https://code.claude.com/docs/en/computer-use)
- [Claude Code MCP](https://code.claude.com/docs/en/mcp)
- [Anthropic Computer Use Tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool)
- [Anthropic Computer Use reference implementation](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo)
- [Computer Use safety guide](https://support.claude.com/en/articles/14128542)
