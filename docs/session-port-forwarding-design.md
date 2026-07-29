# agent-remote Session 端口转发设计

## 1. 文档状态

本文定义 agent-remote 长期使用的远端开发端口访问方案。它是 CLI、控制面、Node、SSH gateway 与 Runtime Helper 的共同实现契约。

当前发布基线只启用 `native` backend。`docker_sandbox` 是后续兼容目标，只有在稳定、可审计的 network namespace 接口和真实隔离测试均通过后才能由 Node 显式上报 capability；在此之前控制面必须拒绝为 Docker session 创建转发，不能回退到容器端口发布、宿主代理或动态防火墙规则。

本方案保持以下既有安全边界：

- 节点不暴露动态公网端口。
- WireGuard 不为每个 dev server 动态放行端口。
- OpenSSH 的标准 TCP、X11 forwarding 和普通 shell 继续禁用。
- 用户设备不能通过隧道访问宿主机、控制面、metadata、其他 session 或任意网络目标。
- dev server 可以只监听 runtime 内的 loopback，不需要监听 `0.0.0.0`。

## 2. 背景与目标

Claude Code 经常会在远端 session 中启动 Vite、Next.js、Webpack、Storybook、Jupyter 或其他临时服务。服务通常监听 runtime 内的 `127.0.0.1:3000`、`127.0.0.1:5173` 等端口，而用户需要在本地浏览器或本地工具中访问。

Native Runtime 使用独立 network namespace，Docker Sandbox 也有独立网络边界，因此节点宿主机的同名端口不等于 runtime 端口。直接发布容器端口、开放节点防火墙或允许通用 `ssh -L` 都会扩大攻击面，并破坏 session 隔离。

### 2.1 目标

1. 用户通过本机 `localhost` 访问指定 session 中的单个 TCP 端口。
2. 完整支持 HTTP/1.1、HTTP/2、WebSocket、SSE、gRPC 和普通 TCP。
3. backend 明确上报 capability 后，Native 与 Docker 使用一致的 CLI 和权限模型；当前只承诺 Native。
4. 转发权限绑定用户、设备、SSH key、session、node 和远端端口。
5. 隧道断线可自动重连，session 停止或权限撤销后快速失效。
6. 不要求节点新增公网入口、DNS、证书或反向代理配置。
7. 不解密、不解析、不记录用户应用流量。
8. 可审计生命周期和用量，同时不记录敏感内容。

### 2.2 非目标

- 不提供通用 VPN、SOCKS 代理、HTTP 代理或任意目标转发。
- 不提供从公网或局域网访问 dev server 的分享链接。
- 不替代生产环境的 ingress、反向代理或服务发布流程。
- 不扫描 runtime 内所有监听端口。
- 首版不自动修改 Vite、Next.js 等框架配置。
- 首版不允许 UDP、Unix socket 或反向转发。

## 3. 用户体验

### 3.1 CLI 命令

```text
agent-remote forward <remote_port>
agent-remote forward <remote_port> --session <session_id>
agent-remote forward <remote_port> --local-port <local_port>
agent-remote forward <remote_port> --local-port auto --open
agent-remote forward list
agent-remote forward stop <forward_id>
agent-remote forward stop --session <session_id> --all
```

`fclaude` 可提供等价的 session 上下文命令：

```text
fclaude forward 3000
fclaude forward 5173 --local-port auto --open
fclaude forward list
fclaude forward stop <forward_id>
```

解析规则：

- `fclaude forward` 默认使用当前 attach 的 session；未 attach 时使用当前 workspace 最近的活动 session。
- `agent-remote forward` 在当前 workspace 只有一个活动 session 时可省略 `--session`，否则要求显式选择。
- `remote_port` 只接受十进制 `1..65535`。默认策略拒绝 `1..1023`，管理员可配置例外。
- `--local-port` 默认等于远端端口；被占用时不静默替换，而是提示使用 `auto` 或指定其他端口。
- `--local-port auto` 由操作系统分配空闲的高位端口。
- `--open` 仅在本地 listener 成功、首个远端探测成功后打开系统默认浏览器。
- CLI 只监听 `127.0.0.1` 和可用时的 `::1`，首版不提供 `--bind 0.0.0.0`。

成功输出示例：

```text
Forward active
  Session:      3f15c2d8
  Local:        http://127.0.0.1:5173
  Remote:       127.0.0.1:5173
  Forward ID:   pf_01K...
  Expires:      2026-07-30T07:30:00Z

Press Ctrl-C to stop. The remote dev server is not exposed publicly.
```

CLI 不应假设服务一定是 HTTP。只有使用 `--open` 时才以 `http://` 打开，后续可增加 `--scheme https`。

### 3.2 推荐的 dev server 启动方式

远端服务应监听 runtime loopback：

```sh
npm run dev
npm run dev -- --host 127.0.0.1
python -m http.server 8000 --bind 127.0.0.1
```

监听 `0.0.0.0` 的服务仍可通过 runtime 的 `127.0.0.1` 访问，但 agent-remote 不要求这样配置，也不会将该端口发布到 node。

## 4. 总体架构

```text
Local browser / local client
  -> 127.0.0.1:<local_port>
  -> agent-remote CLI TCP listener
  -> one multiplexed tunnel over restricted SSH stdio
  -> agent-remote SSH forced-command gateway
  -> node port-forward handler
  -> root runtime helper: DialSessionLoopback
  -> exact session network namespace
  -> 127.0.0.1:<remote_port>
```

控制路径：

```text
CLI
  -> control-plane API: create/reconnect/stop forward
  -> short-lived one-time connection token
  -> SSH gateway
  -> node API: redeem token and obtain renewable authorization lease
```

数据路径不经过控制面。控制面只负责授权、状态和审计；实际字节通过本地设备到 Node 的 WireGuard/SSH 链路传输。

## 5. 核心设计决策

### 5.0 方案选型

| 方案 | 暴露范围 | session 隔离 | 撤销和审计 | 结论 |
| --- | --- | --- | --- | --- |
| Node 公网端口/临时域名 | 公网或节点网络 | 需要额外代理和路由 | 链路长、应用层风险高 | 不采用 |
| WireGuard 内直接开放动态端口 | 所有获准 peer 可见 | 需要动态 NAT/ACL | 易产生残留规则 | 不采用 |
| 标准 `ssh -L` | 本机 loopback | 默认目标是 Node 网络空间 | 难绑定准确 session | 不采用 |
| runtime 内 cloudflared/ngrok | 第三方公网 | 依赖用户进程 | 难统一治理 | 不作为产品能力 |
| 受限 SSH stdio + session netns dial | 仅本机 loopback | helper 强制准确 session | 可短租约、即时禁用、完整审计 | 采用 |

选择的关键不是传输协议本身，而是把“目标地址”从客户端输入中彻底移除。客户端只能引用已授权的 `forward_id`，Node 和 root helper 最终只能连接控制面绑定的 session loopback 单端口。

### 5.1 不启用 OpenSSH 标准 TCP forwarding

`AllowTcpForwarding` 和 authorized key 的 `no-port-forwarding` 限制保持不变。CLI 不调用 `ssh -L`、`ssh -R`、`ssh -D` 或 `ssh -W`。

端口转发使用一个无 PTY 的 forced-command SSH session：

```text
ssh -T agent-remote@<node_wg_ip> \
  agent-remote-tunnel --forward <forward_id> --protocol 1
```

实际 authorized key 的 forced command 继续截获并严格解析 `SSH_ORIGINAL_COMMAND`。只允许既有 attach 命令和上述固定 tunnel 命令，不执行 shell，也不接受 host、路径或额外参数。

这样既复用 SSH 的设备认证、加密、完整性和 WireGuard 私网路径，又不会为 SSH key 授予通用网络能力。

### 5.2 一个 forward 只对应一个远端端口

每个 `forward_id` 固定：

- 一个用户；
- 一个设备和 SSH key；
- 一个 session；
- 一个 node；
- 一个 TCP remote port；
- 一个最大有效期。

本地端口不属于服务端授权边界，只保存在 CLI 本地状态和审计元数据中。需要多个远端端口时创建多个 forward。这样权限、撤销、审计和故障定位更清晰。

### 5.3 多路复用而不是每个浏览器连接启动一次 SSH

一个浏览器页面通常会产生多个 HTTP、WebSocket 和资源连接。每个 forward 使用一个 SSH 连接，并在其 stdio 上运行 HTTP/2 prior-knowledge 多路复用协议。每个 HTTP/2 CONNECT stream 对应一个本地 TCP connection。

SSH 已提供加密，隧道内部的 HTTP/2 不再叠加 TLS。协议实现必须使用成熟的 Rust 和 Go HTTP/2 库，不自行实现流控或帧解析。

### 5.4 Node 在 runtime 内拨号

Node 不监听临时 TCP 端口、不添加 DNAT、不发布 Docker port，也不向用户暴露 runtime IP。每个 CONNECT stream 到达后，Node 请求 root runtime helper 在指定 session 的 network namespace 中连接 loopback，并通过 Unix domain socket 的 `SCM_RIGHTS` 返回已连接的 socket FD。

Root helper 只接受声明式请求：

```text
DialSessionLoopback {
  request_id,
  session_id,
  address_family: "auto",
  protocol: "tcp",
  port
}
```

helper 自己从受管账本解析 runtime 和 network namespace，调用方不能传 PID、namespace path、container ID、IP 或 host。helper 先尝试 `127.0.0.1:<port>`，再按策略尝试 `[::1]:<port>`。

## 6. 信任边界与威胁模型

### 6.1 受信任组件

- 控制面负责身份、授权和撤销，是权限事实来源。
- Node worker 和 root runtime helper 属于节点可信计算基。
- CLI 二进制和当前已注册设备在未撤销期间可信。
- SSH 与 WireGuard 提供传输机密性和对端认证。

### 6.2 被防御的风险

| 风险 | 控制措施 |
| --- | --- |
| 用户访问宿主 `localhost` | helper 只在目标 session netns 中拨号 |
| 用户访问 metadata 或私网 | 目标地址不可配置，只能是 runtime loopback |
| 用户访问其他 session | grant 固定 session，helper 校验对象归属和运行态 |
| 窃取 forward ID 后连接 | ID 不是凭证；还需要设备 SSH key和一次性 token |
| token 出现在进程列表 | token 只在 SSH 加密 stdio 的握手体中传输 |
| token 重放 | Redis 原子 redeem，一次性使用，短 TTL |
| 已撤销设备维持隧道 | Node 使用短租约续期，撤销后停止续期 |
| 恶意协议帧耗尽 Node | 严格帧限制、并发限制、流控、超时和总配额 |
| dev server 意外暴露公网 | node 无动态 listen、publish、NAT 或防火墙放行 |
| 日志泄露应用内容 | 只记录元数据和字节计数，不记录 payload |
| 端口探测 | 每个 forward 固定一个显式端口，并限制创建频率 |

### 6.3 不承诺防御的风险

- 已攻陷的 node root 或宿主内核。
- 已攻陷的本地设备读取本地浏览器或 CLI 流量。
- dev server 自身的 XSS、CSRF、目录遍历或远程代码执行漏洞。
- 同一 agent-remote 用户下工具账户之间超出现有 Runtime 模型的强隔离。

本机 loopback 上的开发服务仍可能被浏览器中的恶意网页尝试访问。随机本地端口可降低偶然命中概率，但不能替代 dev server 自身的 Host、Origin 和 CSRF 校验。

## 7. 授权和连接流程

### 7.1 创建 forward

1. CLI 解析 session，并确认 WireGuard、CLI token 和设备状态。
2. CLI 先尝试绑定本地 listener，避免服务端创建无用授权。
3. CLI 调用创建 API，提交 session ID 和 remote port。
4. 控制面校验用户、设备、session 状态、node 状态、端口策略和配额。
5. 控制面创建持久化 `port_forwards` 记录。
6. 控制面生成 256 bit 随机 `connect_token`，只返回一次；Redis 只保存 token 的 keyed hash，默认 60 秒过期。
7. CLI 建立无 PTY SSH 连接，命令行只包含不可作为凭证的 `forward_id`。
8. CLI 在 SSH stdio 的二进制握手中发送 token。
9. Gateway 将 token、forward ID 和当前 SSH key/device identity 交给 Node redeem。
10. Node 通过 node API 原子兑换 token，获得 60 秒可续租 authorization lease。
11. 握手成功后启动 HTTP/2 多路复用，CLI 开始接受本地连接。

创建操作成功不代表远端端口已经监听。CLI 在 tunnel 建立后执行一次受限 connect probe，并清楚区分：

- 授权失败；
- SSH/WireGuard 失败；
- runtime 不可用；
- 远端 `connection refused`；
- 本地端口占用。

远端端口尚未启动时，forward 可以保持活动；后续本地连接可再次尝试，CLI 不因此自动销毁授权。

### 7.2 自动重连

SSH 断开后 CLI 使用指数退避重连，建议为 250 ms、500 ms、1 s、2 s、5 s，之后每 10 秒一次，并加入 jitter。

一次性 token 不可复用。每次重连前，CLI 使用 CLI token 调用 connection API 获取新的短期 token。控制面重新验证权限，但复用同一个 `forward_id`。

CLI 在重连期间继续持有本地 listener：

- 已建立连接被关闭，不承诺透明续传。
- 新连接最多等待可配置的 5 秒，然后返回连接失败。
- tunnel 恢复后浏览器、Vite HMR 或其他客户端自行重连。

### 7.3 停止和撤销

以下任一事件必须终止 forward：

- 用户按 Ctrl-C 或执行 `forward stop`；
- session 进入 `stopping`、`stopped`、`failed` 或 `interrupted`；
- 用户、设备、SSH key、工具账户或 node 被禁用或撤销；
- forward 达到绝对 TTL；
- 管理员策略变更使当前端口或配额不再允许；
- Node 无法续租且超过控制面不可用宽限期。

Node 续租默认每 20 秒一次，lease 为 60 秒。控制面不可用时已有 tunnel 最多宽限 5 分钟，随后 fail closed；新 tunnel 不允许建立。宽限期由管理员设置，允许配置为 0。

## 8. 隧道协议

### 8.1 SSH stdio 握手

协议以固定 magic 开始：

```text
ARPF\x00\x01
uint32_be payload_length
JSON payload, UTF-8
```

客户端 payload：

```json
{
  "forward_id": "pf_01K...",
  "connect_token": "base64url...",
  "client_version": "0.1.0",
  "max_streams": 128
}
```

服务端响应使用相同 envelope：

```json
{
  "ok": true,
  "protocol": 1,
  "lease_expires_at": "2026-07-29T23:31:00Z",
  "max_streams": 128,
  "max_bytes_per_second": 0
}
```

要求：

- 握手 payload 上限 8 KiB。
- JSON 拒绝未知关键安全字段、重复 key、无效 UTF-8 和尾随数据。
- token 比较必须恒定时间。
- token、完整握手体和 SSH_ORIGINAL_COMMAND 不写日志。
- 握手超时默认 10 秒。
- 错误只返回稳定 error code 和 request ID，不返回内部路径、PID 或网络信息。

握手成功后，双方立即切换为 HTTP/2 prior-knowledge。协议版本不兼容时必须失败，不允许猜测或静默降级。

### 8.2 HTTP/2 CONNECT

每个本地 TCP connection 创建一个 CONNECT stream：

```text
:method = CONNECT
:authority = session-loopback
x-agent-remote-forward-id = <forward_id>
```

remote host 和 port 不出现在 stream 请求中，Node 只使用已经兑换的 grant。返回 `:status = 200` 后，DATA frame 即为双向 TCP 字节流。

语义要求：

- 支持双向 backpressure 和 TCP half-close。
- 单 SSH 连接默认最多 128 个并发 stream。
- stream 建立超时 10 秒，runtime connect 超时 3 秒。
- header list 上限 16 KiB，拒绝无关 header 和请求方法。
- HTTP/2 connection flow-control window 必须有上限，不能按对端输入无限增长。
- CLI 和 Node 都设置 SSH keepalive；Node 还使用 lease 续期判断授权有效性。
- 不检查或修改 DATA 内容，不注入 `X-Forwarded-*` header。

### 8.3 错误码

稳定错误码至少包括：

```text
AUTH_INVALID
AUTH_EXPIRED
AUTH_REDEEMED
DEVICE_REVOKED
SESSION_NOT_RUNNING
SESSION_MISMATCH
NODE_MISMATCH
PORT_NOT_ALLOWED
POLICY_LIMIT
TUNNEL_EXPIRED
RUNTIME_UNAVAILABLE
REMOTE_CONNECTION_REFUSED
REMOTE_CONNECT_TIMEOUT
PROTOCOL_UNSUPPORTED
RATE_LIMITED
CONTROL_PLANE_UNAVAILABLE
```

CLI 将错误码映射为可操作提示；服务端原始错误、netns 路径和内部标识不直接展示。

## 9. 控制面设计

### 9.1 API

用户/CLI API：

```text
POST   /sessions/{session_id}/port-forwards
GET    /port-forwards
GET    /port-forwards/{forward_id}
POST   /port-forwards/{forward_id}/connections
DELETE /port-forwards/{forward_id}
```

创建请求：

```json
{
  "remote_port": 5173,
  "local_port": 5173,
  "client_instance_id": "ci_01K...",
  "ttl_seconds": 28800
}
```

创建响应：

```json
{
  "id": "pf_01K...",
  "session_id": "...",
  "node_id": "...",
  "node_wireguard_ip": "10.80.0.12",
  "remote_port": 5173,
  "status": "pending",
  "expires_at": "2026-07-30T07:30:00Z",
  "connection": {
    "token": "base64url...",
    "expires_at": "2026-07-29T23:31:00Z"
  }
}
```

`connection.token` 必须带 `Cache-Control: no-store`，不得进入 access log、trace attribute、错误上报或 CLI 持久化状态。CLI 只在内存中持有它。

节点 API：

```text
POST /node-api/port-forward-connections/redeem
POST /node-api/port-forwards/{forward_id}/renew
POST /node-api/port-forwards/{forward_id}/release
```

Node API 只接受节点凭证。redeem 必须同时验证当前 node、SSH key/device identity 和一次性 token，数据库状态更新与 Redis token 消费应具备原子语义。实现无法跨存储原子提交时，采用 Redis 原子 consume 后的幂等 redeem ledger，禁止失败后恢复同一个 token。

### 9.2 数据模型

新增 `port_forwards`：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | uuid/uuidv7 | 主键，对外使用带 `pf_` 编码 |
| user_id | uuid | FK users |
| device_id | uuid | FK user_devices |
| ssh_key_id | uuid, nullable | 首次成功 redeem 时绑定 forced-command 提供的实际 SSH key，之后不可变 |
| session_id | uuid | FK sessions |
| node_id | uuid | FK nodes |
| remote_port | integer | 固定目标端口 |
| requested_local_port | integer | 审计和用户体验元数据 |
| client_instance_id | text | CLI 进程实例，限制长度 |
| status | text | 状态枚举 |
| policy_snapshot | jsonb | 创建时非敏感策略摘要 |
| bytes_up | bigint | 聚合计数 |
| bytes_down | bigint | 聚合计数 |
| connection_count | bigint | 聚合计数 |
| generation_bytes_up | bigint | 当前 connection generation 已确认的上行累计值 |
| generation_bytes_down | bigint | 当前 connection generation 已确认的下行累计值 |
| generation_connection_count | bigint | 当前 generation 已确认的连接累计值 |
| last_connected_at | timestamptz | 最近连接时间 |
| lease_expires_at | timestamptz | 当前 Node lease |
| expires_at | timestamptz | 绝对 TTL |
| stopped_at | timestamptz | 可空 |
| stop_reason | text | 稳定原因码，可空 |
| created_at | timestamptz | 创建时间 |
| updated_at | timestamptz | 更新时间 |

状态机：

```text
pending -> active -> disconnected -> active
   |          |            |
   +----------+------------+-> stopped
   +----------+------------+-> expired
   +----------+------------+-> revoked
   +----------+------------+-> failed
```

终态不可恢复。重连复用非终态记录，但每次签发新的 connection token。状态更新使用行版本或条件更新，避免旧 Node connection 覆盖新 connection 状态。

Redis 只保存：

- 一次性 token keyed hash 和 60 秒 TTL；
- `forward_id -> connection_generation`；
- 当前 lease/cache；
- 创建和 redeem rate limit。

PostgreSQL 和审计日志不保存 token、token hash或应用流量。

创建 forward 时，控制面只验证设备至少存在一把有效 SSH key，不预先猜测
OpenSSH 最终选择哪一把 key。首次 redeem 必须使用 forced-command 可信上下文中的
`ssh_key_id` 完成绑定；后续 reconnect/redeem 只接受该 key。这样不会因为设备有多把
有效 key 而错误拒绝合法连接，也不会允许连接建立后切换身份。

Node 的 renew 用量字段采用 connection generation 内单调累计值，而不是增量值：

```json
{
  "generation": 3,
  "bytes_up_total": 1048576,
  "bytes_down_total": 8388608,
  "connection_count_total": 17
}
```

控制面只应用大于该 generation 已确认值的差额。重复响应、超时重试和乱序 renew
因此不会重复计费；旧 generation 的上报不能覆盖新 generation 状态。

### 9.3 管理策略

建议提供以下节点或全局配置：

```text
port_forwarding_enabled = true
port_forward_allowed_ports = 1024-65535
port_forward_denied_ports = []
port_forward_max_per_user = 10
port_forward_max_per_device = 10
port_forward_max_per_session = 5
port_forward_max_streams = 128
port_forward_default_ttl_seconds = 28800
port_forward_max_ttl_seconds = 86400
port_forward_connection_token_ttl_seconds = 60
port_forward_lease_seconds = 60
port_forward_control_plane_grace_seconds = 300
port_forward_bytes_per_second = 0
port_forward_create_rate_limit_per_minute = 30
port_forward_redeem_rate_limit_per_minute = 120
```

`0` 表示不设置带宽上限，而不是无限并发。管理员可完全禁用 capability。策略变更对新建 forward 立即生效，对已有 forward 在下一次 lease renew 时生效。

## 10. Node 与 Runtime 实现

### 10.1 SSH gateway

Gateway 必须：

1. 从受控 authorized key 上下文获得 `ssh_key_id` 和 `device_id`，不信任客户端自报。
2. 对 `SSH_ORIGINAL_COMMAND` 使用固定语法解析器，不调用 shell。
3. tunnel 模式拒绝 PTY、agent forwarding、environment、X11 和额外 channel request。
4. attach 模式和 tunnel 模式使用独立处理路径和资源限制。
5. tunnel 子进程继承最小环境，设置 wall-clock deadline，并在 SSH 断开后清理。

建议继续在 authorized_keys 使用 `no-port-forwarding,no-X11-forwarding,no-user-rc`。是否允许 agent forwarding 由既有 attach profile 决定，与 tunnel 子协议无关。

### 10.2 Node handler

Node handler 运行在非 root worker 中：

- 完成握手、token redeem、HTTP/2 multiplex、lease renew 和计数聚合。
- 每个 stream 请求 runtime helper 返回 connected FD。
- 使用 bounded buffer 双向复制，不将完整 payload 留在内存。
- 每 30 秒或连接结束时上报聚合字节数；上报失败不阻塞数据路径，但受 lease 宽限期约束。
- 同一 forward 只允许一个 active connection generation。新 generation 成功后关闭旧 generation，避免双活。

### 10.3 Native backend

Root helper 根据 session ledger 定位其持久 network namespace。进入 netns 的操作必须在线程锁定或短生命周期 helper 子进程中完成，防止 Go runtime 线程切换导致 namespace 泄漏。

安全顺序：

1. 验证 peer credentials 是受信任 Node UID。
2. 验证 session UUID、user/node 归属、backend 和运行态。
3. 验证请求 port 与 Node 已兑换 grant 一致；helper 可要求带短期 Node 内部 capability，防止 worker 任意调用。
4. 在隔离子进程中 `setns` 进入目标 netns。
5. 创建 `SOCK_STREAM|SOCK_CLOEXEC` socket，只连接 loopback 常量地址。
6. 将 connected FD 通过 `SCM_RIGHTS` 返回并退出子进程。

helper 绝不接受任意 IP、hostname、PID 或 namespace filesystem path。

### 10.4 Docker Sandbox backend

Docker backend 不使用 `docker -p`，也不修改运行中容器的 publish 配置。Root helper 从受管 session ledger 解析固定 container/runtime ID，进入其 network namespace，并复用与 Native 相同的 loopback dial 路径。

如果 Docker Sandbox 不允许稳定获取或进入 network namespace，backend capability 必须上报 `session_port_forwarding=false`，而不是降级为宿主端口发布。实现验证通过后再启用该 capability。

当前发布基线只承诺 Native backend。Docker Sandbox 必须在官方、稳定且可审计的
network namespace 接口和真实隔离测试均通过后，才可加入 capability；不能通过在
sandbox 内启动用户可替换的代理进程来伪造等价安全边界。

### 10.5 Capability 上报

Node heartbeat 增加：

```json
{
  "capabilities": {
    "session_port_forwarding": {
      "supported": true,
      "protocol_versions": [1],
      "backends": ["native"],
      "max_streams": 128
    }
  }
}
```

控制面只在 session backend 被节点明确支持时签发 forward。版本不匹配时 CLI 给出升级 Node/CLI 的明确提示。

## 11. 本地 CLI 实现

CLI 负责：

- session 解析、API 授权和本地 listener 生命周期；
- 调用系统 OpenSSH，复用 agent-remote 设备 key 和现有 SSH 配置；
- SSH host key 严格校验，不允许自动 `StrictHostKeyChecking=no`；
- stdio 握手、HTTP/2 client 和本地 TCP stream multiplex；
- SIGINT/SIGTERM、休眠唤醒、网络切换和自动重连；
- 可选打开浏览器；
- 对用户显示稳定、脱敏的诊断信息。

本地状态可以保存 `forward_id`、session ID、端口和过期时间以便展示，但不保存 connection token。CLI 异常退出后，控制面依靠 lease 将记录转为 `disconnected`；绝对 TTL 或显式 cleanup 最终进入终态。

Windows 使用系统 OpenSSH Client，listener 同样只绑定 loopback。进程控制不能依赖 Unix signal；应使用 Job Object 或等价机制确保父进程退出时回收 SSH 子进程。

## 12. 生命周期和故障语义

| 场景 | 预期行为 |
| --- | --- |
| remote port 未监听 | forward 保留；每次连接返回明确 refused |
| dev server 重启 | tunnel 不重建，后续连接自动可用 |
| SSH 短暂断线 | CLI 获取新 token 并重连；现有流断开 |
| WireGuard 重连 | 与 SSH 断线相同 |
| CLI 崩溃 | Node lease 到期，状态转 disconnected |
| Node 重启 | 流断开；Node 恢复后 CLI 可重新授权连接 |
| 控制面短暂不可用 | 已有 tunnel 在配置宽限期内工作 |
| 控制面长期不可用 | 超过宽限期 fail closed |
| session 停止 | Node 立即关闭 tunnel，控制面进入 stopped |
| session interrupted | 不自动跨 runtime 恢复；旧 forward 终止 |
| session 被迁移到其他 node | 旧 forward 终止，用户重新创建 |
| 设备撤销 | 下次 lease renew 前关闭，目标不超过 60 秒 |
| local port 被占用 | 创建前失败，不签发服务端授权 |
| local sleep/wake | 唤醒后重新检查 WG、重新签发 token 并连接 |

forward 的生命周期不绑定 tmux attach 连接。用户可以断开 Claude 终端而继续保留单独运行的 `agent-remote forward` 进程。

## 13. 审计、指标与隐私

### 13.1 审计事件

```text
port_forward.created
port_forward.connected
port_forward.disconnected
port_forward.reconnected
port_forward.stopped
port_forward.expired
port_forward.revoked
port_forward.denied
```

允许记录：用户、设备、session、node、remote port、requested local port、时间、持续时间、连接数、聚合上下行字节数、终止原因和 request ID。

禁止记录：connection token、token hash、应用 payload、URL/path/query、HTTP header、cookie、WebSocket message、DNS 内容和 dev server 响应。

### 13.2 指标

```text
agent_remote_port_forwards_active
agent_remote_port_forward_streams_active
agent_remote_port_forward_bytes_total{direction}
agent_remote_port_forward_connect_total{result}
agent_remote_port_forward_redeem_total{result}
agent_remote_port_forward_lease_renew_total{result}
agent_remote_port_forward_runtime_dial_seconds
```

指标 label 不使用 user ID、session ID、forward ID 或 port，避免高基数和隐私泄露。详细定位通过结构化日志中的脱敏 request ID 完成。

### 13.3 告警建议

- 5 分钟内 redeem 失败率超过 10% 且请求数超过 20：检查时钟、Redis、设备 key 同步和版本兼容。
- lease renew 失败持续超过 2 个周期：检查控制面可用性；接近 grace deadline 时升级为高优先级。
- runtime dial 非用户预期错误持续出现：检查 Runtime Helper、session ledger 和 netns 生命周期。
- Node 文件描述符使用率超过 80%、pending dial 或 active stream 接近策略上限：拒绝新 stream 并告警。
- cleanup backlog 中已过期记录的最老年龄超过 2 个 cleanup 周期：检查任务调度和数据库锁竞争。

告警只使用聚合维度；需要定位单次故障时通过 request ID 查询受限日志和审计记录。

## 14. 资源限制与滥用控制

- 创建 forward 按 user、device 和 session 限速。
- token redeem 按 forward、device 和 source WireGuard IP 限速。
- 单 forward 默认 128 streams，单 session 默认 256 aggregate streams。
- 每个方向使用固定上限 buffer，建议每 stream 64 KiB 到 256 KiB。
- 限制 HTTP/2 frame、header、connection window 和 pending dial 数量。
- Node 达到文件描述符或内存水位时拒绝新 stream，不中断已有 stream。
- 字节带宽限制如启用，应使用 token bucket 且对上下行分别计算。
- 禁止 remote port range、host list 或动态改端口；每个端口单独授权。
- 对连续 connection refused 不自动扫描相邻端口。

## 15. 实施范围

### 15.1 `agent-remote-server`

- 数据库 migration、模型、状态机和 cleanup job。
- `/port-forwards` 用户 API 和 `/node-api` redeem/renew/release API。
- Redis one-time token、lease、rate limit 和幂等控制。
- session/device/node 撤销联动、策略、审计和指标。

### 15.2 `agent-remote-node`

- heartbeat capability。
- SSH gateway tunnel command 分发。
- 握手和 HTTP/2 server。
- lease renew、generation fencing、配额和统计。
- Runtime Helper 的 `DialSessionLoopback` 与 FD passing。
- Native/Docker backend netns 适配、安全负向测试和对账清理。

### 15.3 `agent-remote-cli`

- `agent-remote forward` 与 `fclaude forward` 命令。
- API client、本地 listener、OpenSSH 子进程和 HTTP/2 client。
- 自动重连、跨平台进程回收、`--open` 和诊断。
- macOS、Linux、Windows 端到端测试。

### 15.4 `agent-remote-admin-web`

- 全局和 Node 端口转发开关、端口范围、TTL、并发和宽限期策略。
- 活动 forward 列表、用量、终止动作和审计查询。
- 不提供浏览器内代理或直接预览 dev server。

## 16. 分阶段交付

### 16.1 Phase 1: Native backend 最小闭环

- 单端口、单 SSH connection、HTTP/2 multiplex。
- 创建、重连、停止、TTL、lease 和审计。
- Native netns loopback dial。
- CLI 支持 macOS/Linux/Windows。
- 管理策略先使用服务端配置，不要求 Admin Web 完整 UI。

### 16.2 Phase 2: Docker 与运维能力

- Docker Sandbox netns adapter。
- Admin Web 策略和活动 tunnel 管理。
- 完整指标、容量保护、节点对账和异常清理。
- 网络切换、休眠唤醒和弱网压力测试。

### 16.3 Phase 3: 体验增强

- `--open` scheme、自定义本地端口偏好。
- attach 输出中的 localhost URL 检测后给出本地提示，但不自动授权或打开端口。
- 可选 workspace 配置声明常用端口。
- 在不扩大安全边界的前提下评估 IDE 集成。

### 16.4 升级、灰度与回滚

升级顺序固定为：

1. 先部署支持新字段但仍上报 capability false 的控制面和数据库 migration。
2. 部署 Runtime Helper 与 Node；仅测试节点上报 Native capability。
3. 部署 CLI，使用测试用户完成静态 HTTP、WebSocket/HMR、SSE、重连和安全负向测试。
4. 按 Node 灰度开启策略，再开启全局策略；观察 redeem、dial、lease、FD 和内存指标。
5. 最后上线 Admin Web 管理入口。旧 CLI 不识别该功能，但不影响 attach 和 session。

回滚时先关闭控制面的 `port_forwarding_enabled`，阻止新建和重连；等待最长 lease/grace 或由 Node 主动关闭现有 tunnel，再回滚 CLI/Node。数据库表和字段在一个兼容周期内保留，不在紧急回滚中执行 destructive downgrade。Runtime Helper 应在 Node 回滚并确认无调用后再降级。

协议兼容遵循显式版本协商：服务端可同时支持有限的相邻版本，但不得静默降级安全语义。移除旧协议前，应先确认低版本 CLI 活跃量归零或达到公开的支持期限。

### 16.5 运维 Runbook

- 用户访问失败时依次检查：本地 listener、WireGuard、SSH host key、token redeem、lease、session 状态、runtime dial 和 dev server 是否监听 loopback。
- `REMOTE_CONNECTION_REFUSED` 通常表示应用尚未启动或端口错误，不应重启 Node 或修改防火墙。
- 大面积 `AUTH_INVALID` 应先检查设备 key 同步和时钟，不应放宽 token TTL 或关闭 key 绑定。
- 控制面或 Redis 故障期间禁止手工改为公开端口；已有 tunnel 按 grace 运行，新 tunnel fail closed。
- session、设备、用户或 Node 被禁用时，控制面在同一事务将关联 forward 置为终态；Node 本地事件立即关闭 tunnel，其他撤销最迟在 lease/grace 边界生效。
- 定期验证 cleanup、终态记录保留策略、审计归档和 Redis key TTL；Redis 恢复后不得复活旧 token。

## 17. 测试计划

### 17.1 功能测试

- HTTP 静态资源、大文件上传下载。
- Vite/Next.js HMR WebSocket。
- SSE、gRPC streaming、长连接和 TCP half-close。
- 一个 forward 下 100+ 并发浏览器连接。
- remote server 启停、端口拒绝和超时恢复。
- CLI 自动端口选择、Ctrl-C、崩溃、休眠和网络切换。

### 17.2 安全负向测试

- 修改 forward ID、remote port、session ID、node ID 或 device identity。
- 重放、过期、并发兑换和跨设备使用 connect token。
- 通过协议尝试连接宿主 loopback、runtime veth IP、metadata、其他 session 和 Unix socket。
- 非法 SSH_ORIGINAL_COMMAND、shell metacharacter、额外参数、PTY 和标准 SSH forwarding。
- 超大握手、重复 JSON key、HTTP/2 frame flood、header bomb、stream flood 和慢速读写。
- session 停止、设备撤销、用户禁用和策略收紧后的撤销时延。
- helper peer credential、session ledger、namespace ownership 和 SCM_RIGHTS 校验。

### 17.3 故障注入

- 控制面、Redis、PostgreSQL、Node、Runtime Helper 和 SSH 分别重启。
- token consume 后数据库/API 返回失败。
- lease renew 响应丢失和 generation 竞争。
- Node 文件描述符、内存和 cgroup 资源接近上限。
- Native netns 消失、Docker runtime ID 变化和 session 对账清理。

## 18. 验收标准

1. 用户可在本地 `127.0.0.1:<port>` 稳定访问 Native session 中的 Vite 服务，HMR 正常。
2. 当前发布中 Docker backend 明确返回不支持；未来只有通过与 Native 等价的隔离验收后，才能开启 capability，且不得发布宿主端口。
3. Node 公网监听端口、防火墙和 WireGuard ACL 不因 forward 动态变化。
4. 标准 SSH `-L/-R/-D/-W` 仍失败，普通 shell 仍不可用。
5. 无法通过协议访问宿主、metadata、其他 session 或任意非 loopback 地址。
6. connect token 不出现在命令行、数据库、日志、trace、崩溃报告或本地磁盘。
7. 设备/session 撤销后，活动 tunnel 在配置的 lease 上限内关闭。
8. 控制面长期不可用超过宽限期后 fail closed。
9. CLI 断线重连不需要重建 forward，本地地址保持不变。
10. 100 个并发 stream 下无无界内存增长、goroutine/task 泄漏或明显数据串流。
11. 所有生命周期操作可审计，但审计和指标不包含应用层内容。
12. macOS、Linux 和 Windows CLI 均通过端到端测试。

## 19. 明确不采用的方案

### 19.1 直接开放 Node 或 WireGuard 端口

需要动态防火墙、端口冲突处理和 runtime 到宿主映射，并使服务暴露范围大于本机 CLI，不采用。

### 19.2 直接启用 `ssh -L`

OpenSSH 的 `direct-tcpip` 目标由客户端提供，动态限制到准确 session netns 的实现复杂，容易意外访问宿主或其他网络，不采用。

### 19.3 公网反向代理或临时域名

需要 DNS、TLS、WebSocket、Host/Origin、cookie 和访问认证处理，且会将开发服务引入公网暴露面。它可以作为未来独立的显式分享功能，但不是本地开发预览方案。

### 19.4 每个 TCP connection 启动一个 SSH 进程

实现简单但浏览器连接多时进程和握手开销过高，弱网体验差，不采用。

### 19.5 在 runtime 内安装 cloudflared/ngrok/localtunnel

依赖第三方公网服务，难以统一认证、撤销、审计和数据边界，只能作为用户明确知情的临时手段，不作为产品能力。
