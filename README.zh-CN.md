# agent-remote

<p align="center"><img src="assets/agent-remote-icon.svg" alt="Agent Remote 图标" width="96" height="96"></p>

[English](README.md) | 中文

agent-remote 是一套开源、自托管系统，用于在可信远程环境中运行 AI 编程 Agent，同时让本地开发工作流尽量接近原生使用体验。

项目面向希望优先使用 Claude Code、并为 Codex 等未来工具保留扩展空间的个人和小团队。本地通过 `fclaude` 等命令经由 WireGuard 连接远端节点，通过 Mutagen 保持项目文件同步，并附加到由 tmux 保持长期在线的 Agent shell。Claude 默认可在不依赖 KVM 或 Docker 的 Linux Native Runtime 中运行，同时继续兼容可选的 Docker Sandbox backend。

## 仓库

- `agent-remote`：项目级部署包、架构方案和跨仓库文档。
- `agent-remote-server`：Python 3.13 控制平面 API，负责用户、设备、节点、会话、同步、浏览器任务和审计数据。
- `agent-remote-admin-web`：React/Vite 管理控制台。
- `agent-remote-node`：部署在 VPS 主机上的 Go 节点运行时。
- `agent-remote-cli`：Rust 本地 CLI，以及 `agent-remote`、`fclaude` 等工具启动器。
- `agent-remote-device`：Swift macOS 设备应用和 Rust 受管 MCP proxy。

## 运行模型

- WireGuard 提供本地到节点的私有网络路径。
- Mutagen 提供项目文件同步。
- 控制面把每个工具账户固定到管理员允许的 `native` 或 `docker_sandbox` backend。
- Native Runtime 使用独立 Linux 用户、systemd cgroup、Bubblewrap、network namespace 和 nftables，不依赖 KVM 或 Docker。
- 明确启用并成功上报 capability 的节点仍可使用 Docker Sandbox。
- tmux 让远端 Agent shell 在本地断开后继续保持在线。
- SSH 用于原生终端附加和节点 forced-command 访问。
- 远端临时浏览器会话使用节点侧浏览器容器和 VPS 网络身份。
- `Agent Remote Device.app` 使用 device credential 列出并 claim 当前 running 的远端
  Claude session；换绑会撤销旧设备控制，但不会停止远端 Claude。

## 文档

- `docs/agent-remote-architecture.md`
- `docs/agent-remote-implementation-appendix.md`
- `docs/native-runtime-design.md`
- `docs/session-port-forwarding-design.md`
- `docs/local-device-control-security-design.md`
- `docs/local-device-control-binding-design.md`
- `docs/local-device-control-release-gate-status.md`
- `docs/device-control-operations-runbook.md`
- `docs/deployment.md`

## 跨仓库测试

将 server、node 和 device 仓库放在同一父目录后，可运行真实设备控制数据链路，覆盖
FastAPI/WebSocket、Go Node bridge、Rust nested TLS 和 Swift Network.framework peer：

```sh
scripts/run-local-device-control-e2e.sh
```

该测试夹具仅在 loopback 上使用临时 `http/ws` 控制面；生产设备凭据和 relay 客户端仍严格要求
`https/wss`。

## 发布

每个组件仓库都有独立的发布版本和节奏。其 `prepare-release` workflow 只更新本仓库负责的版本文件与
`CHANGELOG.md`，提交并标记不可变源码，然后触发该组件自己的 release workflow。

Release workflow 会发布部署归档、CLI/Node 二进制、GHCR 镜像和 GitHub Release notes。
设备控制的生产证据使用独立的受保护装配流程，详见
`docs/device-control-release-evidence.md`。根仓库的 `release-manifest.json` 认证一组使用独立版本的
精确生产组合，包括每个组件的制品签名 workflow 身份。根发布会验证清单固定的 tag、commit、制品和兼容门禁，把已签名的多架构 Community
证据内置到部署包，并按 digest 固定部署镜像；该流程不会自动启用 capability。

## 许可证

agent-remote 使用 GPL-3.0-only 许可证。详见 `LICENSE`。

第三方依赖声明见 `THIRD_PARTY_NOTICES.md`。
