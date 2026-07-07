# agent-remote

[English](README.md) | 中文

agent-remote 是一套开源、自部署的远程 AI Agent 运行系统，用于把 Claude Code 等工具运行在可信 VPS 环境中，同时尽量保持本地原生命令行体验。

项目面向个人和小团队。当前优先支持 Claude Code，后续可扩展到 Codex 等工具。本地通过 `fclaude` 这类命令进入远端节点：WireGuard 负责本地到节点的私有网络，Mutagen 负责项目文件同步，Docker 负责远端运行隔离，tmux 保证 agent shell 长期在线。

## 仓库

- `agent-remote`：项目主仓库，包含部署包、架构方案和跨仓库文档。
- `agent-remote-protocol`：OpenAPI、JSON Schema、节点任务协议和统一术语。
- `agent-remote-server`：Python 3.13 控制平面 API，负责用户、设备、节点、会话、同步、浏览器任务和审计数据。
- `agent-remote-admin-web`：React/Vite 管理端前端。
- `agent-remote-node`：部署在 VPS 节点上的 Go 运行时。
- `agent-remote-cli`：Rust 本地 CLI 和 `fclaude` 等工具启动器。

## 运行模型

- WireGuard 提供本地到节点的私有网络链路。
- Mutagen 提供项目文件同步。
- Docker 在节点上隔离工具运行环境。
- tmux 让远端 agent shell 在本地断开后继续存在。
- SSH 用于原生终端连接和节点 forced-command 访问。
- 临时远程浏览器会话运行在节点侧浏览器容器中，使用 VPS 网络身份。

## 文档

- `docs/agent-remote-architecture.md`
- `docs/agent-remote-implementation-appendix.md`
- `docs/deployment.md`
- `docs/phase-12-completion.md`

## 发布

每个仓库都提供 `prepare-release` workflow。输入版本号后会更新版本文件和 `CHANGELOG.md`，提交 `chore: release vX.Y.Z`，推送 tag，并触发正式 release workflow。

release workflow 会发布部署包、CLI/Node 二进制、协议包、GHCR 镜像和 GitHub Release notes。

## 许可证

agent-remote 使用 GPL-3.0-only 许可证。详见 `LICENSE`。

第三方依赖声明见 `THIRD_PARTY_NOTICES.md`。
