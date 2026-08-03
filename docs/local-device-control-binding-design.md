# 本地设备控制绑定与切换设计

本文将设备控制的绑定入口固定为 `Agent Remote Device.app` 主动选择远端
`fclaude` session，并定义 Server、Node、macOS App、Admin Web 和 CLI 之间的
契约。本文补充 `local-device-control-security-design.md`，不改变设备控制的
端到端加密、应用审批和本机 Claude 隔离要求。

## 1. 产品语义

这里的“绑定 Claude”指绑定一个服务端的工具运行 session，不是绑定
`ToolAccount`，也不是扫描本机的 `claude` 或 `fclaude` 进程。

```text
UserDevice -- device token --> User
ToolAccount -- remote Claude login --> Session(fclaude)
DeviceSession -- temporary control binding --> UserDevice + Session
```

`ToolAccount` 保存远端 Claude 登录态和运行时亲和关系；`Session` 保存远端
Claude 的项目、workspace、Node 和生命周期；`DeviceSession` 保存本机 GUI
控制授权、generation、lease、审批摘要和 Node 控制任务。Workspace 的
`device_id` 只表示本地目录同步来源，不授予 GUI 控制权。

Server 是绑定状态的唯一事实来源。Device APP、Admin Web 和 Node 只能持有绑定
的缓存或运行时副本，不能通过本地状态自行恢复授权。一个 live binding 的完整
身份是：

```text
(user_id, device_id, tool_session_id, device_session_id, node_id, generation)
```

其中 `device_session_id` 区分一次换绑，`generation` 区分同一设备控制会话内的
断线、停止和重新激活。任何 Node task、relay ticket、XPC 请求和 GUI action
都必须匹配完整身份；只有 `tool_session_id` 不能作为清理或撤销依据。

“正在运行的 fclaude”在本设计中表示服务端状态为 `running`、`active` 或
`detached` 的 Claude `Session`。Device APP 不执行、查找、解析或连接本机
Claude，不读取 `~/.claude`，也不能可靠判断一个本机终端进程是否仍然打开。

## 2. 目标流程

```text
Device APP 启动
  -> 连接安全 XPC broker
  -> 检查 Accessibility / Screen Recording
  -> 查询当前用户可控制的 Claude candidates
  -> 用户选择一个 session
  -> Server 原子 claim/rebind
  -> Node 激活新的 device-control generation
  -> Device APP 展示本机应用审批
  -> active lease + nested TLS relay
```

首次启动时，APP 不单独创建第二套用户登录态。安装器或 `agent-remote device`
流程把现有 `UserDevice` 的 device credential 写入 Broker 专用 Keychain/access
group；APP 只读取该设备身份。凭据缺失、过期或设备已撤销时，APP 显示重新配对
状态，不能展示候选、复用旧 binding 或自行降级为 user token。

系统权限与远端绑定是两个独立门槛：APP 可以在没有候选 session 时完成
Accessibility 和 Screen Recording 引导，但只有两项权限都有效后才能 claim。
权限在控制期间被撤销时，APP 必须先停止当前本机执行和恢复桌面，再调用同一
DeviceSession 撤销流程；不能只把界面切回权限提示。

控制结束有两个独立语义：

- `Stop current action`：中止当前动作，增加 generation，保留设备和 Claude
  session 的控制绑定，等待下一次本机审批。
- `End device control`：停止 `DeviceSession`，撤销 lease、machine lock、relay
  和 Node bridge，但不停止远端 Claude `Session`。

APP 的换绑操作可以直接从 active 状态进入候选列表，但在 Server claim 成功后，
本机必须先取消旧 relay、恢复隐藏应用和输入状态，再接受新 binding 的
`pending_device`。新 binding 必须重新进行本机审批，不能沿用旧审批摘要。

为避免 Server 已换绑而本机仍保留旧 relay，Broker 的 claim 操作顺序固定为：

1. 记住当前完整 binding 并停止本机 Executor、relay、续租和 generation 轮换；
2. 恢复隐藏应用并确认输入状态已经释放；
3. 调用 Server claim；
4. 校验返回 binding 属于当前 device，再进入新的本机审批。

第 3 步失败时旧控制仍保持已结束状态，用户可以重新选择；APP 不自动恢复旧
relay。这样失败语义是 fail closed，而不是在两个 session 之间回滚授权。

远端 Claude session 的停止仍使用工具 session 生命周期 API，不由本机控制结束
隐式触发。

## 3. Candidate API

Device APP 使用 device token 请求最小字段接口：

```http
GET /api/v1/device-sessions/candidates
Authorization: Bearer <device-token>
```

Server 从 token 取得 `user_id` 和当前 `device_id`，不得接受客户端传入的目标
设备身份。返回只包含当前用户的 Claude session，且同时满足：

- `status in (running, active, detached)`；
- `device_control_protocol_version == 1`；
- 分配 Node 仍为 `healthy` 或 `degraded`；
- Node capability 明确支持 protocol 1、`platform=macos` 和 session 的
  pinned runtime backend。

candidate 允许包含以下零内容字段：

```json
{
  "tool_session_id": "...",
  "tool_type": "claude",
  "tool_account_id": "...",
  "workspace_id": "...",
  "project_key": "opaque-project-label",
  "display_name": "...",
  "status": "running",
  "node_id": "...",
  "runtime_backend": "native",
  "current_device_id": "...",
  "current_device_name": "...",
  "device_session_id": "...",
  "controllable": true
}
```

`project_key` 只能是经过脱敏的稳定项目标签；优先使用 `Workspace.display_name`，
不得把本地路径、远端路径或包含用户名的原始 project key 返回给 Device APP。
接口不得返回窗口内容、Claude 凭据、relay 材料或应用审批内容。Candidate 列表
是提示性状态；claim 时必须再次锁定并验证目标 session，不能信任列表中的 status。

## 4. Claim/Rebind API

```http
POST /api/v1/device-sessions/claim
Authorization: Bearer <device-token>
Content-Type: application/json

{"tool_session_id":"..."}
```

Server 在一个数据库事务中完成以下步骤：

1. 按全局固定顺序锁定目标 `Session`、当前 `UserDevice` 和相关 live
   `DeviceSession` 行。涉及两个已有 binding 的交换场景也必须遵守同一排序，
   不能按请求参数顺序加锁。
2. 重新验证用户归属、Claude 类型、session 状态、协议版本、Node 状态和
   capability。
3. 如果目标 session 已被其他设备控制，将旧 DeviceSession 变为终态，原因
   为 `rebound`，清除 lease 和 lock，写入 deactivate task 和审计记录。
4. 如果当前设备控制了另一个 session，同样停止旧控制绑定。首期一台设备只
   允许一个 live DeviceSession，以匹配本机 Broker 的单 relay 状态机。
5. 创建新的 `pending_device` DeviceSession 和 activation task，最后提交事务。

Claim 必须具备幂等性：目标已经绑定当前设备且仍处于 live 状态时，返回当前
DeviceSession，不创建重复记录。两个并发 claim 不能产生双活；数据库唯一约束
和事务行锁共同保证这一点。目标在列表后结束时返回 `409`，不能创建半失效绑定。

“删除旧绑定”是撤销旧授权，不是物理删除数据库记录。旧记录保持 `stopped`，
保存 `stop_reason=rebound` 和审计关联，按既有终态 retention 清理。

旧 binding 的撤销是逻辑上的立即生效：数据库提交后，所有新握手必须失败，
当前 relay 必须关闭；延迟到达的 Node deactivate 或旧 APP 请求只能返回过期/无效，
不能影响新 binding。旧 device 不需要停止远端 Claude session。

## 5. 数据库不变量

`device_sessions.tool_session_id` 不能对终态历史记录继续使用全生命周期唯一约束，
否则旧记录停止后无法重新绑定同一个 Claude session。迁移后应使用两个 live-only
唯一约束：

```text
tool_session_id unique where status is non-terminal
device_id       unique where status is non-terminal
```

现有 `device_sessions_device_status_idx` 保留用于列表查询。终态记录不再占用
live binding 的唯一槽位，但仍受到 retention 和审计策略保护。

为避免删除已停止的 Claude `Session` 时通过外键级联删除 binding 历史，
`device_sessions` 同时保存不可变的 `tool_session_reference_id`。当前 live 关联使用
可空且 `ON DELETE SET NULL` 的 `tool_session_id` 外键；公开响应和审计使用不可变
引用；该引用在迁移回填后必须非空。这样工具 session 删除后仍能按 retention 保留旧设备绑定和 `rebound` 原因。
设备和 Node 在仍有 retained DeviceSession 引用时禁止删除，防止其他父表级联路径
绕过同一 retention 策略。

回退到旧 schema 会重新启用 `tool_session_id` 的全生命周期唯一约束，因此无法保留
同一 Claude session 的多次绑定历史。执行 `0016` downgrade 前必须导出终态历史；
迁移会为每个 `tool_session_id` 只保留最新记录，确保旧唯一索引可以恢复。

## 6. 撤销和任务顺序

数据库提交后，Server 必须按旧 generation 关闭 relay 的活跃端点；Node
`deactivate_device_control` 任务作为第二层清理，停止旧 bridge、清除 runtime
context 和本地 activation manifest。新 activation 不得在旧 context 清理前造成
双活；Node task 执行必须依赖 task ID 幂等和完整 binding 校验。

`deactivate` 到达时如果当前 context 已属于另一 `device_session_id` 或更高
generation，必须成功返回 `no-op/stale`，不能报错后重试，也不能删除新 context。
`activate` 到达时如果发现同一 tool session 的旧 context，应先以完整 binding
比较并安全替换；替换失败时新 binding 必须保持不可用并进入可观测的 failed 状态。

`DeviceRelayHub` 需要提供按 `(device_session_id, generation)` 关闭当前 pair 的
能力。数据库只在握手时校验 binding，不能作为已经建立 WebSocket 的即时撤销机制。
生产部署必须保证撤销信号能到达持有 WebSocket 的进程：要么每个 relay 只运行一个
Server worker，要么使用 Redis pub/sub 或等价的跨进程撤销通知。仅把 pair 放在
单个 worker 的 Python 内存中不满足多 worker 部署要求。
旧 App、Node bridge、GUI Executor 和 proxy 在 relay 关闭后必须 fail closed，释放
按下的鼠标、键盘和隐藏应用状态。

所有终止入口都调用同一个撤销服务：

| 入口 | DeviceSession | 远端 Claude Session | Node/relay |
| --- | --- | --- | --- |
| APP `End device control` | stopped | 保持运行 | 立即撤销并异步清理 |
| Web stop/revoke | stopped | 保持运行 | 立即撤销并异步清理 |
| lease/max TTL 到期 | expired | 保持运行 | 立即撤销并异步清理 |
| rebind | 旧 binding stopped，新 binding pending | 保持运行 | 旧 binding 立即撤销 |
| `fclaude stop`/远端进程退出 | stopped/expired | stopped/interrupted | 同步清理 |
| Device token revoke | stopped | 保持运行 | 立即撤销并异步清理 |

## 7. App、Web 和 CLI 边界

- Device APP 负责 candidate 展示、切换确认、本机权限、应用审批、停止当前动作
  和结束本机控制。
- Device APP 只使用当前设备的 device token；candidate 和 claim API 都从 token
  推导 `user_id/device_id`，请求体不得接受目标设备 ID。
- Admin Web 展示 Claude project/session、当前设备、generation、lease 和
  `rebound` 原因；结束控制调用同一个 stop service，不能实现第二套 rebind 逻辑。
- Admin Web 不创建绑定，也不绕过本机应用审批；首期只提供状态、审计和结束控制。
- CLI 保留 `fclaude` session 生命周期命令，并提供 `agent-remote device launch` 验证
  安装包和共享 device credential 后启动 APP。CLI 不调用 candidate/claim，不保存
  Claude 登录态或 relay 秘密，也不替代 APP 的本机审批。

旧的 `POST /api/v1/device-sessions`（客户端同时提交 `device_id` 和
`tool_session_id`）不再是普通用户的绑定入口。迁移期间可以保留兼容路由，但必须
默认返回明确的弃用错误，或仅允许管理员执行受审计的迁移操作。

Device credential 的安装、轮换和撤销继续复用 CLI 已有设备注册能力。APP
不得保存 user token、Claude token 或账户登录态；CLI 也不得替 APP 执行本机应用
审批。

## 8. 验收场景

至少覆盖以下场景：

1. APP 启动后没有权限时先引导权限，权限恢复后进入 candidate 列表。
2. 选择未绑定的 running Claude session，完成审批后 relay active。
3. 选择已绑定另一设备的 session，旧设备立即失去 relay，新设备重新审批。
4. 当前设备已有另一个控制 session，claim 后旧控制终止且不产生双活。
5. 两台设备同时 claim 同一个 Claude session，请求按用户级锁串行执行；后提交的
   claim 可以撤销前一个，最终只能有一个 live binding。
6. Claude session 在列表后停止，claim 返回 `409` 且无新增绑定。
7. Device APP 结束控制、Web 结束控制和 lease 到期均能清理 Node bridge、relay
   和本机 GUI 状态，但不停止远端 Claude session。
8. 终态历史记录保留，之后同一个 Claude session 可以重新绑定。
9. 远端 Claude session 停止或 Node 对账发现进程退出时，DeviceSession、relay、
   bridge 和 APP 本地隐藏状态均被清理，且不会留下 live binding。
10. 多 worker Server 中，Web stop/rebind 能关闭由另一 worker 持有的 relay pair。
11. APP 在 active、activating 和 pending approval 状态均可发起切换；旧 relay、
    Executor、隐藏应用和输入状态先清理，claim 失败也不会恢复旧控制。
12. Accessibility 或 Screen Recording 在 active 期间被撤销时立即结束控制，
    Server、Node、relay 和本机状态最终一致。
