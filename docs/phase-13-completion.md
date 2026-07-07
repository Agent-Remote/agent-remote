# agent-remote Phase 13 完成记录

## 状态

Phase 13：端到端验收和 MVP 发布准备，状态为完成。

本阶段为 MVP release 增加可重复的验收路径，用于验证发布产物、部署配置、安装器和真实环境工作流。

## 完成内容

- 新增 `scripts/e2e-smoke.sh`，用于 release 与部署 smoke 验证。
- 新增 `docs/e2e-acceptance.md`，作为人工端到端验收清单。
- 文档化控制面、节点、CLI、WireGuard、SSH、Mutagen、Claude、`fclaude`、远端浏览器、设备撤销和恢复能力检查。
- 更新部署文档，使用当前 CLI 和 Node 一键安装脚本。
- 更新 release 文档，将 GitHub Actions `prepare-release` workflow 作为标准发布路径。
- 在英文和中文 README 中加入端到端验收文档入口。

## 自动验证范围

Smoke 脚本会验证：

- Docker Compose 部署配置语法。
- 主仓库、server、admin-web、CLI 和 node 仓库 release tag。
- 主仓库部署包。
- CLI 的 Linux/macOS amd64/arm64 release 包。
- Node 的 macOS amd64/arm64 和 Linux glibc/musl amd64/arm64 release 包。
- CLI 和 Node 一键安装脚本 raw URL。
- 当 `AGENT_REMOTE_SMOKE_IMAGES=1` 时，额外验证 GHCR image manifest。

## 人工验证边界

以下检查需要真实基础设施，不能只通过仓库自动化真实完成：

- 空白公开控制面部署后的第一个管理员创建。
- 真实 VPS 节点注册和 heartbeat。
- 跨公网 WireGuard 连通。
- 通过节点执行 SSH forced-command 访问。
- 对真实远端节点 workspace 运行 Mutagen 同步。
- Claude OAuth 登录和登录状态持久化。
- 临时浏览器流量从 VPS 网络出口访问。

这些检查已经写入 `docs/e2e-acceptance.md`，上线前应按清单执行。

## MVP 发布门禁

用于 MVP 测试的 release 应满足：

- 目标版本执行 `scripts/e2e-smoke.sh` 通过。
- 至少一个空白部署通过人工端到端验收清单。
- `docs/e2e-acceptance.md` 中的已知限制对目标用户可接受。
