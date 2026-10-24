# Skill 验收状态

更新：2026-10-24。本文只记录当前 Server、Node、CLI 和 Desktop 代码已经提供的 Skill 合同与可复核证据。历史版本号、旧测试目录和已删除的本机路径不属于当前验收记录。

## 当前实现

- Server 持有 Skill 配置、版本、快照、发布、冲突、保留和删除回执；请求使用 owner-scoped 上下文和不可重放的 caller key。
- Node/Helper 负责受控运行时、工作区权限、快照准备、发布和清理；无法证明终止或清理时保留 `pending`，不会伪造成功。
- CLI 负责登录上下文、同步、Skill 操作和恢复查询；未知结果只查询原始请求 key，不用新 key 重放。
- Desktop 只展示当前账户、项目、会话和操作收据，不保存凭据、原始命令或 Skill 内容。
- Mutagen 同步链已在一次性 Docker 环境通过双向传输、暂停/恢复、冲突处理、显式 resolve/reset，以及 Node 和 Mutagen 重启恢复。

## 当前质量证据

最近一次质量门禁结果：

- Server：2266 passed，127 skipped，覆盖率 91.68%；Ruff、Mypy 和 docstring 检查通过。
- CLI：1404 passed，4 skipped；静态检查、合同测试和安装器检查通过。
- Node：`go test ./...` 通过。
- Desktop：`bash scripts/check.sh` 和 workbench probe 通过。
- Docker sync-chain：真实 Linux sshd、Server、Node、worker/helper、Mutagen 和重启恢复通过。

这些结果证明代码合同和同步链边界，不等同于目标主机上的真实 Claude/SSH/tmux 会话或生产 Skill 发布证据。

## 仍需的发布证据

1. 在一次性 Server/Node/SSH/tmux/fclaude 环境完成 Skill 创建、保存、恢复、停止、删除和清理回执闭环。
2. 将真实 session、attachment 和同步证据绑定到最终发布组合。
3. 在目标主机完成 Agent TUI、IME、附件、输入反馈和长时间运行验证。

验收必须使用临时凭据、临时 home、一次性数据库、一次性工作区和临时容器。结束后删除测试用户、会话、文件、容器、镜像、socket、日志和 evidence 目录；不得使用生产凭据或真实工作区。

## 相关入口

- Skill 合同：[`skill-manager.md`](skill-manager.md)、[`skill-manager-wire-v1.md`](skill-manager-wire-v1.md)
- 备份与恢复：[`backup-restore.md`](backup-restore.md)
- 跨仓远程验收：`../agent-remote-desktop/docs/remote-interop-acceptance.md`
