# agent-remote

<p align="center"><img src="assets/agent-remote-icon.svg" alt="Agent Remote 图标" width="96" height="96"></p>

[English](README.md) | 中文

`agent-remote` 是一套开源、自托管系统，用于在可信远程环境中运行 AI 编程 Agent，同时让本地工作流保持接近原生终端体验。

## 组件

| 仓库 | 职责 |
| --- | --- |
| `agent-remote-server` | FastAPI 控制面，负责用户、设备、账户、节点、会话、同步和审计数据。 |
| `agent-remote-node` | VPS 上运行的轮询式 Go 节点运行时，不暴露公开控制 HTTP API。 |
| `agent-remote-cli` | Rust 本地 CLI 与启动器：`agent-remote`、`fclaude`、WireGuard、SSH、Mutagen 和 desktop-control 合同。 |
| `agent-remote-desktop` | 基于 Go/mygo 的原生工作台，管理本地 Codex/Claude 与远程 `fclaude` 会话。 |
| `agent-remote-admin-web` | React/Vite 管理控制台。 |
| `agent-remote-device` | Swift macOS Device 应用与受管 MCP proxy。 |
| `agent-remote-ego-browser` | macOS Bridge、Device Client、Linux wrapper 及显式全信任浏览器控制的发布工具。 |

## 运行模型

- WireGuard 提供设备到节点的私有网络路径。
- Mutagen 同步用户选定的项目工作区。
- 控制面为每个工具账户选择管理员批准的 `native` 或 `docker_sandbox` backend。
- Node 在隔离运行时中启动 Agent，并用 tmux 保持 shell 在线。
- SSH 将本地终端接入经过授权的 tmux 会话。
- desktop 共用 CLI 配置、凭据和结构化操作合同，不维护第二套凭据存储。

desktop 仍处于开发阶段。UI 重构已经实现，但正式版还需要完成其实施状态中列出的平台、broker、远程链路和性能证据。

## 文档

以下当前代码合同是事实来源：

- 产品与跨仓库计划：`docs/agent-remote-desktop-design.zh-CN.md`
- Desktop 实施与发布状态：`../agent-remote-desktop/docs/implementation-status.md`
- 部署与升级：`docs/deployment.md`、`docs/upgrade.md`
- 运行架构：`docs/agent-remote-architecture.md`、`docs/native-runtime-design.md`
- 会话端口转发：`docs/session-port-forwarding-design.md`
- Device 控制安全与运维：`docs/local-device-control-security-design.md`、`docs/device-control-operations-runbook.md`
- Ego-browser 生命周期与发布：`docs/ego-browser-humanized-lifecycle.md`、`docs/ego-browser-bridge-release-promotion.md`
- Skills：`docs/skill-manager.md`、`docs/skill-manager-wire-v1.md`、`docs/skill-acceptance-plan.md`

历史规划仅在解释当前兼容性或迁移边界时保留，不代表当前实现状态。

## 跨仓库检查

在各同级仓库运行组件检查。根仓库也提供合同和发布证据脚本，例如：

```sh
python3 -m pytest
bash scripts/run-local-device-control-e2e.sh
python3 scripts/check-device-control-release-readiness.py
```

验收时使用临时 home、测试凭据和一次性 server/node 数据，不使用生产凭据或真实用户工作区。

根仓库保留以下跨仓库和发布脚本入口：

```sh
bash scripts/run-local-device-control-e2e.sh
bash scripts/run-session-port-forwarding-e2e.sh
python3 scripts/check-device-control-release-readiness.py
scripts/prepare-release.sh <version>
scripts/update-changelog.sh <version>
```

这些脚本只操作一次性测试数据或发布元数据，不会自行发布版本。

## 发布策略

各仓库拥有独立版本和发布流程。根组合发布必须固定组件 commit、制品、schema 和兼容性证据。desktop 正式目标是 `darwin/arm64`、`windows/amd64` 和 `linux/amd64`；macOS 使用项目社区自签，Windows/Linux 不要求发行者代码签名。Apple Developer ID 和公证不属于本发布策略。

所有必需的原生、远程、安全和兼容性门禁通过并由用户审阅前，不得发布。

## 许可证

GPL-3.0-only。第三方依赖声明位于 `THIRD_PARTY_NOTICES.md`。
