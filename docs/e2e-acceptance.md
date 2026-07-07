# 端到端验收清单

本文档用于验证 agent-remote MVP 从空白部署到可使用远端 Claude 工作流的完整路径。

## 自动 Smoke 测试

在 `agent-remote` 仓库中执行：

```sh
scripts/e2e-smoke.sh
```

默认检查内容：

- Docker Compose 部署配置。
- 所有仓库的 GitHub Release tag。
- 主仓库部署包、CLI 包和 Node 包。
- CLI 与 Node 当前一键安装脚本 URL。

常用选项：

```sh
AGENT_REMOTE_VERSION=0.0.3 scripts/e2e-smoke.sh
AGENT_REMOTE_SMOKE_NETWORK=0 scripts/e2e-smoke.sh
AGENT_REMOTE_SMOKE_IMAGES=1 scripts/e2e-smoke.sh
```

`AGENT_REMOTE_SMOKE_IMAGES=1` 会额外检查 server 和 admin-web 的 GHCR 镜像 manifest。

## 人工验收清单

使用一台空白控制面服务器、一台空白节点服务器，以及一台本地 macOS 或 Linux 机器完成验收。

### 控制面

- 从 release 部署包部署 `agent-remote`。
- 将 `deploy/compose/.env.example` 复制为 `deploy/compose/.env`。
- 配置域名、公开 Base URL、密钥、PostgreSQL 密码和 CORS origins。
- 使用 Docker Compose 启动整套服务。
- 确认公开域名下的 `/healthz` 返回成功。
- 打开管理端并创建第一个管理员。
- 使用管理员账户登录。

### 节点

- 在 VPS 节点安装 Docker、OpenSSH server、tmux、TUN 支持和 Docker Sandbox CLI。
- 安装 Node runtime：

```sh
curl -fsSL https://raw.githubusercontent.com/Agent-Remote/agent-remote-node/main/scripts/install.sh | sudo bash
```

- 在管理端创建节点注册 token。
- 使用 server URL、node ID 和 registration token 执行 `agent-remote-node register`。
- 启动节点服务。
- 确认节点显示在线，heartbeat 时间持续更新。

### 本地 CLI

- 安装 CLI runtime：

```sh
curl -fsSL https://raw.githubusercontent.com/Agent-Remote/agent-remote-cli/main/scripts/install.sh | bash
```

- 执行 `agent-remote init`。
- 使用管理员已创建的普通用户登录。
- 确认本地设备出现在管理端。
- 执行 `agent-remote status --online`。
- 确认依赖检查包含随包提供的 Mutagen binary 和 WireGuard helper。

### 网络与 SSH

- 确认 CLI 能获取或刷新 WireGuard 配置。
- 确认本地机器可以通过 WireGuard 地址访问节点。
- 确认 SSH forced-command 入口可通过节点访问。
- 在管理端撤销设备，并验证 CLI 无法继续 attach。
- 恢复或重新注册设备后，确认访问恢复。

### 项目同步

- 在本地项目目录执行 `fclaude`。
- 当项目没有已有远端 workspace 时，确认 CLI 会询问是否自动同步。
- 确认当前项目 key 只创建一个 Mutagen 项目同步 session。
- 在同一项目目录再次执行 `fclaude`。
- 确认第二个 session 复用已有远端 workspace，不重复创建项目同步。
- 本地修改文件，确认远端项目目录同步更新。
- 远端修改文件，确认本地项目目录同步更新。
- 确认 `.git` 同步遵循用户配置的开启或关闭状态。

### Claude 配置

- 在管理端绑定 Claude 工具账户。
- 确认账户具备地区、时区、locale 和节点放置策略配置。
- 执行 `fclaude`，并在需要时手动完成 Claude 登录。
- 确认 Claude 登录状态存储在账户级远端配置目录。
- 使用同一项目和同一账户启动另一个 `fclaude` session。
- 确认容器挂载共享项目 workspace 和共享 Claude 配置目录。
- 执行 Claude `resume`，确认能看到预期历史。

### Agent Session 生命周期

- 启动一个新的 `fclaude` session。
- 断开本地终端但不停止远端 shell。
- 在同一项目目录再次执行 `fclaude`。
- 确认默认恢复当前项目绑定的 tmux session。
- 显式启动一个新 session，确认它可以与已有 session 共存。
- 通过 CLI 停止 session，并确认节点状态变为 stopped。

### 远端浏览器

- 为 `https://claude.ai/` 创建临时浏览器 session。
- 未选择工具账户时，确认 region、timezone 和 locale 参数被正确接受。
- 打开浏览器 stream URL。
- 确认浏览器能渲染远端桌面并正常导航。
- 确认访问流量从 VPS 网络出口发出。
- 停止浏览器 session，并确认容器被移除。
- 对 Claude 登录所需邮箱服务重复同样流程。

### 恢复能力

- 停止节点服务，确认控制面在 heartbeat 超时后将节点标记为不健康。
- 重启节点服务，确认节点恢复在线。
- 在 `fclaude` attach 期间中断本地网络。
- 恢复网络后，确认可以重新 attach 到同一个 session。
- 停止本地 Mutagen，确认 CLI 报告同步健康问题。
- 恢复同步后，确认文件传播恢复。

## 已知限制

- Claude OAuth 和账户验证仍然需要用户手动完成。
- 真实 WireGuard 配置需要主机网络权限，不同操作系统可能有差异。
- 浏览器 session 是临时无痕用途，不设计为持久保存用户 cookie。
- 节点注册和 Claude runtime 验收需要真实 VPS 类主机，并具备 Docker、tmux、SSH 和 TUN 支持。
- Docker Sandbox CLI 和上游浏览器镜像是外部运行依赖，可能独立变化。
- Windows 不是 MVP 支持目标。

## 故障排查

- 如果 `scripts/e2e-smoke.sh` 的 release asset 检查失败，检查对应仓库的 `vX.Y.Z` release workflow 是否完成。
- 如果 Compose 校验失败，去掉 `--quiet` 执行 `docker compose --env-file deploy/compose/.env.example -f deploy/compose/docker-compose.yml config` 查看具体错误。
- 如果 `agent-remote init` 无法登录，确认控制面已经存在该用户。CLI 不负责创建用户。
- 如果 WireGuard 无法连通，检查主机 TUN 支持、防火墙规则和 peer 配置。
- 如果 Mutagen 不同步，检查项目 key、远端 workspace 路径、ignore 规则，以及该项目是否已有 sync session。
- 如果 `fclaude` 恢复了错误 shell，确认命令从预期项目路径启动。
- 如果浏览器 connect 返回 `401`，从管理端或 API 重新生成浏览器 connect URL，stream token 是临时的。
- 如果浏览器 connect 后只有桌面但没有浏览器窗口，检查浏览器容器日志，并等待 VNC 桌面进程完成启动。
