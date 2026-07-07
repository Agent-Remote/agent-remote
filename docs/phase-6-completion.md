# agent-remote Phase 6 完成记录

## 状态

Phase 6：WireGuard 与 SSH 受控连接，状态为完成。

Phase 6 的目标是打通本地设备、控制面和 VPS 节点之间的受控连接链路，让 CLI 可以获取 WireGuard 配置、检查或启动本地隧道，并通过 SSH forced command 只进入已授权的远端 tmux session，而不是获得通用 shell。

本阶段完成的是源码和协议层面的连接闭环。真实跨机器连通性仍需要在部署环境中具备 WireGuard 系统权限、节点 endpoint、SSH daemon 配置和发布包内置二进制；这些属于部署验收，不再要求用户手动安装依赖。

## 已完成交付物

- [x] 设备 WireGuard peer 注册和撤销沿用设备注册流程
- [x] 节点 WireGuard 公钥、endpoint、SSH host、SSH port、SSH user 字段
- [x] `GET /api/v1/network/wireguard/config`
- [x] `POST /api/v1/sessions/{session_id}/attach`
- [x] `POST /api/v1/node-api/attach/verify`
- [x] CLI WireGuard config 渲染和写入
- [x] CLI WireGuard check/up/down 命令
- [x] CLI SSH 可用性检查
- [x] CLI attach 授权和 SSH 执行入口
- [x] 随 CLI 发布的 `agent-remote-wireguard` helper 入口
- [x] 节点端受控 `authorized_keys` 管理
- [x] 节点端 `sync_ssh_keys` 任务执行
- [x] 节点端 `agent-remote-attach` forced-command 二进制
- [x] 节点端 attach 请求回查控制面验证
- [x] 节点 Docker 镜像同时打包 `agent-remote-node` 和 `agent-remote-attach`

## 仓库提交

```text
204a64b feat: add connection control contract
```

`agent-remote-server`：

```text
f43147a feat(connection): add attach control apis
```

`agent-remote-cli`：

```text
cc949eb feat: add wireguard and attach commands
```

`agent-remote-node`：

```text
81e95da feat: add attach ssh key management
```

## 控制面能力

server 新增连接服务 `ConnectionService`，统一处理 WireGuard 配置读取、session attach 授权和节点 forced-command 回查。

WireGuard 配置读取要求：

- 当前 token 必须是设备 token
- 设备必须属于当前用户
- 设备状态必须为 `active`
- 设备必须存在 active WireGuard peer
- 节点必须具备 WireGuard IP、公钥和 endpoint

session attach 授权要求：

- 当前 token 必须是设备 token
- session 必须处于可 attach 状态
- session 所在节点不能禁用或离线
- 当前设备必须存在 active SSH key
- session 必须存在 tmux session name

授权成功后，server 会为节点创建或复用 `sync_ssh_keys` 任务，把设备 SSH public key 写入节点受控 `authorized_keys` 区块，并绑定 forced command：

```text
agent-remote-attach --session <session_id> --device <device_id>
```

节点执行 forced command 时会调用 `/api/v1/node-api/attach/verify`，由控制面再次校验节点、设备和 session 状态。设备被撤销后，即使 SSH key 还残留在节点文件中，attach 验证也会失败。

## CLI 能力

新增命令：

```sh
agent-remote wireguard config
agent-remote wireguard check
agent-remote wireguard up
agent-remote wireguard down
agent-remote ssh check
agent-remote attach --session-id <session-id>
```

`agent-remote wireguard config` 会向 server 拉取当前设备配置并写入：

```text
~/.config/agent-remote/wireguard/agent-remote.conf
```

`agent-remote-wireguard` 是 CLI 发布包内置的受控 helper 入口。当前源码实现会检查配置文件和 `wg-quick` 可用性，并在 up/down 时委托底层 WireGuard 工具执行；正式发布包需要把对应平台 WireGuard 组件或受控安装逻辑一起放入托管依赖目录，避免用户手动安装。

`agent-remote attach` 会先向 server 获取一次 attach 授权，再执行 server 返回的 SSH 命令进入 tmux session。需要只查看命令时可使用：

```sh
agent-remote attach --session-id <session-id> --print-only
```

## 节点端能力

节点端新增 `agent-remote-attach` 二进制，作为 SSH forced command 的实际入口。

执行流程：

1. SSH daemon 命中受控 `authorized_keys` 条目。
2. forced command 启动 `agent-remote-attach`。
3. `agent-remote-attach` 使用节点 token 请求控制面验证。
4. 控制面返回可 attach 的 tmux session name。
5. 节点端执行 `tmux attach-session -t <name>`。

节点端新增 `install-ssh` 命令，用于初始化受控 authorized_keys 文件：

```sh
agent-remote-node --config config.json install-ssh
```

节点端配置新增：

```json
{
  "ssh_authorized_keys_path": "/home/agent/.ssh/authorized_keys.agent-remote",
  "attach_binary_path": "/usr/local/bin/agent-remote-attach"
}
```

`sync_ssh_keys` 任务只维护以下标记区块，不覆盖用户已有的其他 SSH key：

```text
# BEGIN agent-remote managed keys
# END agent-remote managed keys
```

写入的 SSH key 默认携带：

```text
command="agent-remote-attach ...",no-agent-forwarding,no-X11-forwarding,no-port-forwarding,no-pty
```

因此 SSH 入口不能获得普通 shell，只能走控制面授权后的 attach 流程。

## 验证命令


在 `agent-remote-server` 仓库执行：

```sh
scripts/run-quality-checks.sh
```

```sh
UV_CACHE_DIR=/Users/rem/Documents/Git/agent-remote-server/.uv-cache uv run alembic heads
```

```sh
docker compose config
docker compose build server
```

server 仓库执行禁用词扫描，排除 `.git`、虚拟环境和工具缓存目录。

在 `agent-remote-cli` 仓库执行：

```sh
scripts/run-quality-checks.sh
```

```sh
cargo run --bin agent-remote-wireguard -- check --config Cargo.toml
```

在 `agent-remote-node` 仓库执行：

```sh
go test ./...
```

```sh
docker build -t agent-remote-node:phase6 .
```

## 验收结果

- server：21 个测试通过，包含 WireGuard 配置读取、attach 授权、节点 attach verify 和设备撤销失败用例。
- server：Alembic head 为 `0004_connection_fields`。
- server：Docker Compose 配置和 server 镜像构建通过。
- server：禁用词扫描通过。
- CLI：7 个 Rust 测试通过。
- CLI：`agent-remote-wireguard check` 可检查配置文件并报告底层 WireGuard 工具状态。
- node：Go 测试通过，覆盖受控 authorized_keys 写入和 `sync_ssh_keys` 任务执行。
- node：Docker 镜像构建通过。
当前未在真实 VPS 上执行跨机器 WireGuard ping 和 SSH daemon 级连接测试。该测试需要实际节点公网 endpoint、WireGuard 系统权限和 SSH daemon 引用受控 authorized_keys 文件，进入部署验收时执行。

## Phase 7 进入条件

Phase 7 可以开始，前提是：

- Phase 6 提交已推送。
- server、CLI、node 仓库保持干净。
- 部署环境后续按本阶段产出的 WireGuard 和 SSH 接口接入真实系统组件。

进入 Phase 7：Mutagen workspace 同步。

Phase 7 目标：

- 建立 workspace 创建和同步 session API。
- CLI 在新目录首次启动前询问是否同步。
- 节点端准备远端 workspace 目录。
- CLI 使用内置或托管 Mutagen binary 创建、暂停、恢复、重置同步。
- 默认冲突时阻止进入工具 session。
