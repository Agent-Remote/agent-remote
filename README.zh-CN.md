# agent-remote

[English](README.md) | 中文

agent-remote 是一套开源、自托管系统，用于在可信远程环境中运行 AI 编程 Agent，同时让本地开发工作流尽量接近原生使用体验。

项目面向希望优先使用 Claude Code、并为 Codex 等未来工具保留扩展空间的个人和小团队。本地通过 `fclaude` 等命令经由 WireGuard 连接远端节点，通过 Mutagen 保持项目文件同步，并附加到由 tmux 保持长期在线的 Agent shell。Claude 默认可在不依赖 KVM 或 Docker 的 Linux Native Runtime 中运行，同时继续兼容可选的 Docker Sandbox backend。

## 仓库

- `agent-remote`：项目级部署包、架构方案和跨仓库文档。
- `agent-remote-server`：Python 3.13 控制平面 API，负责用户、设备、节点、会话、同步、浏览器任务和审计数据。
- `agent-remote-admin-web`：React/Vite 管理控制台。
- `agent-remote-node`：部署在 VPS 主机上的 Go 节点运行时。
- `agent-remote-cli`：Rust 本地 CLI，以及 `agent-remote`、`fclaude` 等工具启动器。

## 运行模型

- WireGuard 提供本地到节点的私有网络路径。
- Mutagen 提供项目文件同步。
- 控制面把每个工具账户固定到管理员允许的 `native` 或 `docker_sandbox` backend。
- Native Runtime 使用独立 Linux 用户、systemd cgroup、Bubblewrap、network namespace 和 nftables，不依赖 KVM 或 Docker。
- 明确启用并成功上报 capability 的节点仍可使用 Docker Sandbox。
- tmux 让远端 Agent shell 在本地断开后继续保持在线。
- SSH 用于原生终端附加和节点 forced-command 访问。
- 远端临时浏览器会话使用节点侧浏览器容器和 VPS 网络身份。

## 文档

- `docs/agent-remote-architecture.md`
- `docs/agent-remote-implementation-appendix.md`
- `docs/native-runtime-design.md`
- `docs/deployment.md`
- `docs/e2e-acceptance.md`
- `docs/phase-12-completion.md`
- `docs/phase-13-completion.md`

## 发布

每个仓库都有 `prepare-release` workflow。使用版本号运行后，会更新该仓库负责的版本文件、更新 `CHANGELOG.md`、提交 `chore: release vX.Y.Z`、推送 tag，并触发 release workflow。

Release workflow 会发布部署归档、CLI/Node 二进制、GHCR 镜像和 GitHub Release notes。

## 许可证

agent-remote 使用 GPL-3.0-only 许可证。详见 `LICENSE`。

第三方依赖声明见 `THIRD_PARTY_NOTICES.md`。
