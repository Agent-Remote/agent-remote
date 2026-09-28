# Skill 使用与运维

Skill 管理默认开启，统一管理用户技能库、账号规则和会话学习状态。当前运行验收范围为 Native；
实际 Claude 调用及学习闭环的范围与结果见[验收状态](skill-acceptance-plan.md)。
开发约束见[跨仓库契约](skill-manager-wire-v1.md)，本页只保留日常操作。

## 配置与升级

Server 推荐默认值：

```dotenv
SKILL_MANAGER_ENABLED=true
SKILL_STORAGE_POLICY={}
SKILL_DELETION_INTERVAL_SECONDS=30
SKILL_DELETION_BATCH_SIZE=100
```

| 配置 | 含义 |
| --- | --- |
| `SKILL_MANAGER_ENABLED` | 开启 Skill API 与新会话准入；显式 `false` 关闭 |
| `SKILL_STORAGE_POLICY` | JSON 配额与保留策略；`{}` 使用内置默认值 |
| `SKILL_DELETION_INTERVAL_SECONDS` | 已提交删除任务的轮询间隔（秒） |
| `SKILL_DELETION_BATCH_SIZE` | 每批处理的删除任务数；不是历史保留数量 |

默认包限制为单文件 10 MiB、单包 50 MiB / 5000 条目；运行态单项 1 GiB、完整目录
10 GiB / 100000 条目。用户包、暂存、运行态配额分别为 2 / 2 / 20 GiB。
普通无引用历史保留 30 天，卸载归档 90 天，无活动租约暂存 24 小时。
精确字段及校验以 [Server 策略模型](https://github.com/Agent-Remote/agent-remote-server/blob/main/src/agent_remote_server/skill_manager/storage/policy.py) 为准。
轮询清理不等于自动清空历史，仍受引用、保留期和已提交删除计划约束。

Node 配置 `skill_manager_enabled` 在新安装或缺字段时为 `true`；显式 `false` 会跨升级保留。
旧安装器写入的 `false` 需要管理员确认意图后改为 `true`。Server 开关和 Node 开关彼此独立。
Node 必须通过 Helper 的实际依赖、运行程序及私有存储探测，才会在新心跳报告
`skill_manager.native` 和 `skill_manager_checks`；开关开启不等于运行环境可用。

使用主仓库发布组合升级，版本以 `release-manifest.json` 为准，不在文档重复固定版本号。
同时核对 CLI / Node 的 `release-dependencies.json`：CLI 安装 Node 使用自己的内嵌版本，
Node 的 Device / Ego Browser 制品及 Server 的系统 Skill 策略也必须匹配。
部署顺序和备份见[部署指南](deployment.md)与[备份恢复](backup-restore.md)。
更新 Node 时一起更新 Worker / Helper，避开活跃会话和未完成任务后重启并核对新心跳。

Server 必须持久挂载 `/var/lib/agent-remote/skill-storage`（发行 Compose 的 `skill-content` 卷）；
其私有 `content` 子目录存放真实字节。拉取新镜像不会自动更新旧 Compose 挂载。
Node 的 `/var/lib/agent-remote-skill-state` 要与账号数据一并备份。只备份 SQL 不足以恢复 Skill。

## 安装、更新与规则

先完成 `agent-remote login`。以下 `ACCOUNT_UUID` 等占位符须替换为真实完整 UUID。
每条子命令的完整参数以安装版本的 `--help` 为准。

```sh
agent-remote skill add ./skills --list
agent-remote skill add ./my-skill --account-id ACCOUNT_UUID --dry-run
agent-remote skill add ./my-skill --account-id ACCOUNT_UUID --yes
agent-remote skill add owner/repo --ref main --skill my-skill --yes
agent-remote skill list
agent-remote skill info my-skill
agent-remote skill list --account-id ACCOUNT_UUID --effective
agent-remote skill list --session SESSION_UUID --effective
agent-remote skill check my-skill
agent-remote skill update my-skill --from ./my-skill --dry-run
agent-remote skill update my-skill --from ./my-skill --yes
agent-remote skill update --all --yes
```

- 多候选需明确 `--skill`、`--all` 或交互选择；`--yes` 只确认方案，不自动选全部。
- Git 支持 GitHub `owner/repo` 或无凭据 HTTPS URL，需要本机 Git；私库使用本机 credential helper。
  分支可跟踪更新，tag / commit 固定版本；原始 Git 对象不执行 hooks / filters，未展开的 LFS / submodule 会拒绝。
- `update --stage` 只登记版本，不激活；`update --all` 逐项处理，部分失败不会回滚已成功项。
- 生效字段各自按 **账号 > 工具 > 用户默认** 继承；启用状态与版本 pin 独立。
  不带 scope 的安装影响用户默认；用隔离测试账号时应显式指定 `--account-id`。

```sh
agent-remote skill disable my-skill --account-id ACCOUNT_UUID --yes
agent-remote skill enable my-skill --account-id ACCOUNT_UUID --yes
agent-remote skill pin my-skill --revision r2 --account-id ACCOUNT_UUID --yes
agent-remote skill unpin my-skill --account-id ACCOUNT_UUID --yes
agent-remote skill inherit my-skill --account-id ACCOUNT_UUID --field enabled --yes
agent-remote skill rollback my-skill --revision r1 --yes
agent-remote skill remove my-skill --yes
agent-remote skill status --last
agent-remote skill status OPERATION_UUID --wait --timeout 60
agent-remote skill status --storage
```

规则变更只影响后续会话，已有会话使用原快照。账号本地来源只能在原账号管理启用状态，
不支持包版本 pin / rollback / remove；历史恢复使用 state 命令。同名来源用完整 Skill UUID 消歧。
受管账号导入其他配置须使用 `account import-config --exclude-skills`，不能覆盖受管技能目录。

## 学习状态、导出与恢复

```sh
agent-remote skill state list my-skill --account-id ACCOUNT_UUID
agent-remote skill state info CHECKPOINT_UUID
agent-remote skill state diff my-skill --account-id ACCOUNT_UUID
agent-remote skill state export my-skill --checkpoint CHECKPOINT_UUID --output ./skill-state
agent-remote skill state reset my-skill --account-id ACCOUNT_UUID --dry-run
agent-remote skill state restore my-skill --account-id ACCOUNT_UUID --checkpoint CHECKPOINT_UUID --dry-run
agent-remote skill state migrate my-skill --account-id ACCOUNT_UUID --from-revision r1 --to-revision r2 --dry-run
agent-remote skill state conflicts my-skill --account-id ACCOUNT_UUID
agent-remote skill state diff --conflict CONFLICT_UUID
agent-remote skill state resolve CONFLICT_UUID --use incoming --dry-run
agent-remote skill state prune my-skill --account-id ACCOUNT_UUID --dry-run
```

先审阅 `--dry-run`，确认后用 `--yes` 提交。reset / restore 保留历史并推进状态纪元；
旧会话的迟到写入不能复活已清除状态。迁移、冲突解决使用保存的原始比较输入，不随实时 head 偷换。
`prune --all-unreferenced` 仍不能删除受保护内容；启用、pin、禁用但保留、待保存和冲突数据都受引用规则保护。

导出目标须不存在或为空，父目录须存在；完整验证后才原子发布。
检查点导出含 `checkpoint.json`、`manifest.json`、`objects/<sha256>`，链接保存在清单中，
不会在本机直接还原链接或执行文件。跨 Skill 链接须导出完整 `account-directory`。
该包是恢复证据，不能直接当作 `resolve --directory` 的解包目录。

```sh
fclaude stop SESSION_UUID
fclaude stop-status SNAPSHOT_UUID --wait --timeout 60
agent-remote skill state export --scope account-directory --account-id ACCOUNT_UUID --snapshot SNAPSHOT_UUID --output ./recovered-state
```

快照导出从原在线 Node 经受限 SSH 读取冻结内容，或读取经过停写证明的原工作树；
需要有效用户登录、已注册设备与 SSH key。停止工作树恢复可协商超出 100000 条目的独立恢复流，
不把它冒充 manifest v1 检查点。失败不发布半成品，也不删除 Node 原数据。

## 状态与故障定位

| 观察 | 能证明什么 / 下一步 |
| --- | --- |
| `stored`、`deploy_on_first_use=true` | 内容与配置已保存，未绑定账号等待首次部署；不能证明模型加载 |
| 配置 `committed=true` | 原请求已提交；仍须看每个部署目标结果 |
| `stopped` / `capture_pending` | 进程已停；后者尚未冻结成功，保留 Node 数据，修复配额/磁盘/可移植性后查询原操作 |
| `persisted` | 完整内容已在 Server 持久化；不等于已发布到当前账号 |
| `published` / `conflicted` / `detached` | 分别为已发布、待解冲突、保留但不更新当前状态；均不等于 Claude 已调用 |
| `CONTENT_STORAGE_UNAVAILABLE` | 检查 Server 持久卷及权限，修复后恢复原上传 |
| `SKILL_MANAGER_UNSUPPORTED` | 检查两端开关、匹配版本、实际 Native 探测及新心跳 |
| `STATE_PENDING` | 保存未完成，不能删除会话或直接清理目录 |

超时或断网后先查 `skill status --last` / 原 operation，再用相同参数恢复原请求；
不要换幂等键、重做 rollback 或强制 SQL 清理。默认等待 60 秒，`--no-wait` 只跳过等待。
Skill 命令常用退出码：0 成功、1 失败/冲突、2 参数/确认错误、3 等待超时、130 中断；
超时和中断不代表远端回滚。`agent-remote --json skill ...` 输出一个版本化 JSON 信封。
