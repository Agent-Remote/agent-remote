# agent-remote Native Runtime 设计与实现

## 实现状态

0.0.4 已完成本文所述的跨仓库基础实现：控制面 backend policy、账户 backend 固定与迁移、session 中性 runtime 标识与 interrupted 恢复、管理端 runtime policy、CLI replacement 流程、node root helper、Native isolation、受管 Claude runtime 和一键安装器。Docker Sandbox 继续作为显式兼容 backend，浏览器容器 capability 与 Claude Native Runtime 相互独立。

生产启用前仍应按 `docs/e2e-acceptance.md` 在目标发行版和网络环境中验证账户登录、真实 Claude session、资源上限与出口策略；单元测试和 capability probe 不替代业务级验收。

## 1. 背景与目标

现有 Claude 账户绑定和工具 session 依赖 Docker Sandboxes。该运行时在部分环境中依赖 KVM 或嵌套虚拟化，不适合没有 KVM 能力的 VPS。

本设计在保留 Docker Sandbox 兼容性的同时，为 `agent-remote-node` 增加一套直接运行 Claude Code 的 Native Runtime。Native Runtime 只依赖现代 Linux 的 systemd、cgroup v2、namespace、Bubblewrap 和 nftables，不依赖 KVM，也不依赖 Docker daemon。

最终运行链路为：

```text
local fclaude
  -> WireGuard / SSH forced command
  -> per-session tmux
  -> selected runtime backend
       -> docker sandbox exec -> claude
       -> native isolation runner -> claude
```

普通用户和 `fclaude` 不选择 backend。管理员配置 node 允许的 backend 和默认 backend，控制面在账户绑定时固定有效 backend。

## 2. 已确认的设计决策

1. 项目面向个人和可信小团队，防御误操作、资源失控、普通目录越界和横向访问，不承诺抵御宿主内核漏洞或恶意本地提权。
2. node 可同时支持 `docker_sandbox` 和 `native`，但不允许在失败时静默降级。
3. 每个 agent-remote 用户对应独立的宿主 Linux UID/GID；同一用户下的工具账户不构成强安全边界。
4. Native Runtime 首版要求 Linux kernel 5.15 以上、systemd 249 以上、cgroup v2、namespace、nftables 和 root 管理 helper。
5. 首批支持 Debian 12、Ubuntu 22.04 和 Ubuntu 24.04。
6. Claude runtime 由 node 托管并固定版本，不调用宿主环境中任意可见的 `claude`。
7. 默认只允许公网访问，宿主 localhost、私网、metadata 和 WireGuard 管理网段必须由管理员显式放行。
8. workspace、账户配置和明确绑定的开发凭据持久化；HOME、XDG cache 和临时目录按 session 隔离并在停止后清理。
9. 首版不转发个人 SSH agent，只支持专用 token、Deploy Key 或隔离 SSH agent。
10. node worker 保持非特权；新增 root runtime helper，通过 root-owned Unix socket 接收声明式请求。
11. 资源配额由管理员统一配置，session 和 Claude 参数不能自行提额。
12. 工具账户固定一个 backend；切换 backend 必须无活跃 session、显式迁移且支持回滚。
13. Docker 浏览器是独立可选 capability，不是 Native Claude 的依赖。
14. 宿主保持 UTC，session 内呈现账户时区和 locale。
15. VPS 重启后 session 标记为 `interrupted`，不自动重放 Claude 命令。
16. Bubblewrap 是 Native Runtime 的必需依赖。

## 3. 安全边界

### 3.1 进程身份

root runtime helper 根据控制面 user UUID 创建稳定的无登录系统用户。用户名从完整 UUID 的安全摘要生成，并在创建和复用时校验映射关系。

```text
agent-remote-node       非特权控制面 worker
agent-remote-runtime    root runtime helper
ar-u-<digest>           某个 agent-remote 用户的运行 UID/GID
```

node worker 不加入 Docker 组。Docker backend 所需的特权操作也通过 runtime helper 完成。

### 3.2 文件系统视图

Bubblewrap 为每个 Native session 创建独立的 mount、PID、IPC 和 UTS namespace。Claude 仅能看到：

| 路径类别 | 权限 | 生命周期 |
| --- | --- | --- |
| 当前 workspace | 读写 | 持久 |
| 当前工具账户 `.claude/`、`.claude.json` | 读写 | 持久 |
| 绑定的 developer credential profile | 按策略读写 | 持久 |
| 固定版本 Claude runtime | 只读 | node 管理 |
| CA、zoneinfo、locale、必要系统库 | 只读 | 宿主管理 |
| HOME、XDG cache、TMPDIR | 读写 | session 临时 |

其他用户、其他账户、node token、runtime helper 状态、Docker socket、宿主 `/home` 和无关 `/var` 路径不可见。

### 3.3 网络

每个 session 使用独立 network namespace 和 veth。nftables 默认策略：

- 允许受控 DNS 和公网出口。
- 拒绝 loopback 目标、RFC1918、CGNAT、link-local、multicast、云 metadata 和 WireGuard 管理网段。
- 管理员可配置明确的 CIDR allowlist。
- IPv4 和 IPv6 分别做地区一致性探测；IPv6 不一致时禁用该 session 的 IPv6。
- 不使用透明代理伪造地区，流量从目标 VPS 的真实出口发出。

### 3.4 systemd 与 cgroup

每个 session 对应一个 transient service，至少启用：

- `NoNewPrivileges=yes`
- capability bounding set 为空
- `PrivateDevices=yes`
- `ProtectKernelTunables=yes`
- `ProtectKernelModules=yes`
- `ProtectControlGroups=yes`
- `ProtectClock=yes`
- `RestrictSUIDSGID=yes`
- `LockPersonality=yes`
- `MemoryDenyWriteExecute=yes`，仅在 Claude runtime 兼容性验证通过时启用
- `MemoryHigh`、`MemoryMax`、`CPUQuota`、`TasksMax` 和 `LimitNOFILE`
- `KillMode=control-group`

默认资源策略为宿主保留至少 512 MiB 或总内存的 20%，单 session 默认 CPUQuota 不超过 200%，`TasksMax=512`，`LimitNOFILE=8192`，临时目录上限 1 GiB。具体值由管理员 policy 覆盖。

## 4. Runtime Backend 抽象

node 内部提供统一接口：

```go
type Backend interface {
    Name() string
    Capabilities(context.Context) Capabilities
    PrepareAccount(context.Context, AccountSpec) (AccountRuntime, error)
    VerifyAccount(context.Context, AccountSpec) (VerifyResult, error)
    StartSession(context.Context, SessionSpec) (SessionRuntime, error)
    StopSession(context.Context, SessionRuntime) error
    Inspect(context.Context) ([]RuntimeResource, error)
}
```

实现包括：

- `DockerSandboxBackend`：承接现有 Docker Sandbox 行为。
- `NativeBackend`：调用本地 root runtime helper。

worker 只负责 task decode、backend 选择、幂等账本和结果回写，不再拼接 Docker、Bubblewrap、systemd 或 shell 命令。

## 5. Root Runtime Helper

新增 `agent-remote-runtime` 二进制和 root systemd socket/service。Unix socket 默认位于 `/run/agent-remote/runtime.sock`。

helper 只接受版本化的声明式协议：

```text
ProbeCapabilities
EnsureUser
PrepareAccount
StartSession
StopSession
InspectSession
ListSessions
MigrateAccount
CleanupSession
```

请求只携带 UUID、枚举、版本和资源策略。真实路径、systemd unit、tmux socket、netns 和 nftables object 名称由 helper 从受控 root 派生。helper 必须校验 Unix peer credentials、对象归属、路径 containment 和重复请求幂等性。

## 6. 控制面数据与协议

### 6.1 Node

新增字段：

- `allowed_runtime_backends`: `docker_sandbox`、`native` 的允许列表。
- `default_runtime_backend`: 管理员选择的默认 backend。
- `runtime_policy`: 资源、网络和版本策略。

心跳新增：

- `runtime_capabilities.backends`
- `runtime_capabilities.native`
- `runtime_capabilities.docker_sandbox`
- `runtime_capabilities.browser_docker`
- `runtime_capabilities.dependencies`
- `runtime_capabilities.probe_errors`

控制面只能从“管理员允许、node 本地启用、实时探测成功”的交集中调度 backend。

### 6.2 Tool account

新增 `runtime_backend`。账户绑定时按 node policy 固定 backend。已绑定账户不会因 node 默认值变化而自动切换。

迁移要求：

1. 无活跃 session。
2. 备份账户目录和权限 manifest。
3. 检查目标 backend capability。
4. 转换 ownership 和 runtime metadata。
5. 在目标 backend 中执行 verifier。
6. 成功后提交 backend；失败恢复备份和原 backend。

### 6.3 Session

新增：

- `runtime_backend`
- `runtime_resource_id`
- `replaces_session_id`
- `interrupted` 状态

`container_id` 在兼容期保留，但新代码使用中性的 `runtime_resource_id`。创建、停止、attach、task result 和 reconcile 都必须携带或验证 backend。

## 7. 地区一致性

宿主保持 UTC。Native session：

- 只读映射目标 zoneinfo 为 `/etc/localtime`。
- 生成 session 专用 `/etc/timezone`。
- 设置 `TZ`、`LANG`、`LC_ALL`、`LANGUAGE`。
- 启动前验证 locale 已生成。
- 校验工具账户地区与 node 地区、出口地址族和账户 affinity 一致。

该方案提供与目标 VPS 地区高度一致的 CLI 环境，但不承诺绕过第三方服务的所有风控或设备检测。

## 8. 生命周期与恢复

1. 账户绑定和普通 session 使用相同 backend abstraction。
2. tmux socket 按 session 隔离，SSH forced command 验证控制面授权后切换到目标 UID attach。
   账户绑定使用 `agent-remote-attach --binding <tool-account-id>`，且 Native 绑定必须由设备令牌发起；控制面同步该设备的 forced-command SSH key，每次 attach 重新校验设备状态、账户归属、affinity node 和绑定状态。
3. SSH 断开不会停止 tmux、Claude 或 systemd unit。
4. stop 按顺序终止 systemd cgroup、tmux、network namespace、nftables 规则和临时目录。
5. node 启动后对账 backend 资源；不存在的活跃 session 上报为 `interrupted`。
6. `fclaude` 遇到 `interrupted` session 时创建 `replaces_session_id` 指向旧 session的新 session，不自动重放原命令。
7. `cleanup_resources` 只接受显式的 `runtime_backend=native` 和最多 100 个 `session_ids`，逐个幂等停止；未知 task type 必须失败，不允许以 noop 成功。

## 9. 安装与 capability

Native backend 安装器检查：

- 支持的发行版、kernel 和 systemd 版本。
- cgroup v2。
- Bubblewrap 自检。
- mount/PID/IPC/UTS/network namespace。
- nftables、iproute2、tmux、locale、TUN 和磁盘水位。
- root runtime socket/service。
- 固定版本 Claude runtime 和 checksum。

Docker、Docker Sandboxes 和 KVM 不再是 node systemd unit 的强依赖。浏览器、Docker Sandbox 和 Native Runtime 分别上报 capability。

## 10. 实施顺序

1. 更新架构文档、server schema、migration 和 API contract。
2. 扩展 node heartbeat、admin node policy 和 scheduler backend 过滤。
3. 建立 node backend interface，将现有 Docker 逻辑迁入兼容实现。
4. 实现 root runtime helper、协议、用户映射和 capability probe。
5. 实现 Native session 的 systemd、Bubblewrap、tmux、netns 和 nftables 生命周期。
6. 实现账户绑定、验证、停止、对账和 backend 迁移。
7. 更新 installer、systemd、release manifest、CLI 和 admin-web。
8. 完成单元、集成、安全负向、故障恢复和无 KVM VPS E2E。

其中 systemd transient unit、mount propagation、netns/veth/nftables/NAT、Bubblewrap 执行和 Mutagen bootstrap 必须在 Linux VPS 上验收；macOS 上的单元测试只验证协议、参数构造和状态机，不能替代该 E2E。

## 11. 验收标准

- 同一个 node 可同时报告并运行 Docker Sandbox 和 Native backend。
- 完全没有 Docker/KVM 的合格 VPS 可以绑定 Claude 账户、启动、attach、停止和恢复 Native session。
- backend 失败不会裸跑或静默切换。
- 不同控制面用户不能读取彼此 workspace、账户配置、进程、tmux socket或临时目录。
- Claude 不能访问 node token、Docker socket、metadata、宿主 localhost 和未放行私网。
- CPU、内存、PID 和临时空间限制可被实际触发并由 node 正确上报。
- session 内 timezone/locale 与账户一致，宿主仍为 UTC。
- SSH 断开后 session 保持；VPS 重启后状态变为 `interrupted` 且不会自动重放。
- 账户 backend 迁移支持成功提交和失败回滚。
- 现有 Docker Sandbox 账户和 session 行为保持兼容。
- server、node、CLI、admin-web 的完整质量门禁通过。
