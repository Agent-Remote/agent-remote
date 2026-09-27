# 远端用户级 Skill 管理器：方案与命令契约

## 1. 状态与已确定决策

状态：产品方案已按用户决策修订，命令及运行时能力尚未实现。本文是后续跨仓库实现的行为契约；挂载和故障恢复仍须按验收条款验证。

已确定：

1. 每个 Agent Remote 用户独立管理自己的 skill 库。A 用户只能管理 A 的记录、内容、账户规则和运行数据；B 用户完全独立。同节点部署也不改变此边界。没有公共贡献库、团队共享或跨用户发布。
2. 安装默认面向该用户的所有已接入工具。目前只有 Claude，因此当前实际只给 Claude；以后新增工具适配器后默认继承，不需要重新安装。明确的工具范围限制继续保留。
3. 安装、更新、回滚、启停、卸载和账户覆盖变更只影响新 session。已有 session 保持启动时选定的版本、规则与工作副本，attach 不重新解析。
4. 普通第三方 skill 的会话目录可写，允许其按原有路径修改自身文件、保存学习结果和生成文件。管理器承担持久化、版本迁移和冲突处理，不要求所有 skill 改为专用数据 API。
5. 首版支持账户单独覆盖，包括启用状态、固定版本与恢复继承。用户库共享安装内容，运行中产生的改动默认按工具账户隔离。

“当前用户”来自 Agent Remote 登录身份。CLI 所在目录、节点 Linux 用户名不决定用户范围。除解析本地来源相对路径外，命令在任何目录执行都管理同一用户库。

目标是让符合目标工具格式、可在远端 Linux 环境运行的第三方 skills 尽量无需改写即可使用。文件可写不能补齐缺失的系统依赖、凭据、macOS 专用程序或其他工具 API；不能承诺任意第三方代码都能在任意工具和操作系统中运行。

## 2. 核心模型：共享安装，账户继承，会话独立写入

```text
Agent Remote 用户
  ├─ 用户 skill 库：来源、不可变版本包、默认选择规则
  ├─ Claude 工具规则：覆盖用户默认
  │    ├─ 账户 A：账户覆盖 + A 的持久运行改动
  │    │    ├─ session 1：固定版本 + 独立可写副本
  │    │    └─ session 2：固定版本 + 独立可写副本
  │    └─ 账户 B：账户覆盖 + B 的持久运行改动
  └─ 后续工具：复用相同接口与继承规则
```

区分三个概念：


| 概念                | 归属与用途                                | 可变性                           |
| ----------------- | ------------------------------------ | ----------------------------- |
| 发布版本包 revision    | 用户库中安装的原始完整文件、来源 commit、摘要           | 不可变；更新生成新 revision            |
| 账户运行状态 checkpoint | 某账户在某 revision 上累积的学习、自修改、新增与删除记录    | 每个 checkpoint 不可变，当前 head 可推进 |
| session 工作副本      | 启动时基于 revision 和 checkpoint 构建，暴露给工具 | 可写；仅本 session 修改              |


旧会话“保持原版本”指管理操作和其他会话不会替换其基线或文件；该会话自身仍可以修改自己的副本。运行改动不会自动成为用户库的新发布版本，也不会自动传播给其他账户或工具。

原始包由 Server 持久化，节点保存缓存；账户 checkpoint 也保存到 Server。活动 session 的工作目录保存在节点持久磁盘，不能放入退出即清理的临时目录。

## 3. 工具和账户覆盖规则



### 3.1 按字段继承

对每项已安装 skill 分别解析启用状态与版本：

```text
enabled  = 账户显式值，否则工具显式值，否则用户默认值
revision = 账户固定版本，否则工具固定版本，否则用户库当前版本
```

账户规则必须属于当前用户，且账户的 tool_type 决定所属工具。两个字段独立继承：账户可以只固定版本，同时继续继承工具启用状态。工具与账户覆盖不能创建跨用户引用。

普通未指定范围的安装：用户默认启用，适用于所有已接入工具。`add --tool claude`：用户默认关闭，仅为 Claude 建立启用覆盖。`add --account-id ACCOUNT_ID`：安装内容仍归用户库，用户默认关闭，仅为指定账户建立启用覆盖。两种范围参数互斥。

默认范围使用“所有工具”的规则，不把当前工具列表永久展开成只有 Claude。尚未接入的工具不能通过 `--tool` 手工指定；新增适配器上线后按已保存规则继承。已明确声明不兼容的 skill 或缺失运行能力必须显示原因，不静默声称可用。

### 3.2 启停的具体语义

- 无范围的 `enable/disable` 修改用户默认值，保留已有工具和账户覆盖。
- `enable/disable --tool` 修改该工具的显式值，保留账户覆盖。
- `enable/disable --account-id` 修改指定账户的显式值。
- 因此账户显式启用可以覆盖工具或用户默认停用；输出必须列出不受本次默认变更影响的显式覆盖。
- `disable --all-scopes` 将用户默认设为关闭并清除所有工具、账户的启用覆盖，使所有账户的新会话停用；保留版本固定规则和运行数据。
- `inherit --tool/--account-id` 恢复上级继承；默认恢复启用与版本两个字段，可用 `--field enabled` 或 `--field revision` 限定。
- 用户库卸载、用户权限、工具未接入、系统保留名称和运行能力要求是前置条件，任何账户规则都不能绕过。

示例：用户默认启用 r3，Claude 工具停用，账户 A 显式启用并固定 r2。A 的新 session 使用 r2；没有覆盖的 Claude 账户 B 停用。A 执行 `inherit --field enabled` 后继承 Claude 的停用，但其 r2 固定规则仍保留。

### 3.3 版本与账户数据边界

`update` 和 `rollback` 改变用户库默认版本；固定版本的工具和账户不随之切换。`update --stage` 只登记候选版本，不切换默认。`pin` 只能选择同一用户、同一 skill 已安装且仍保留的 revision，不创建来源分叉。`unpin` 等价于对 revision 字段恢复继承。

同名不同来源首版返回冲突；账户覆盖不承担把一个 skill 替换成任意其他来源的职责。此边界保证名称、来源和版本历史可追踪。

账户运行数据以 `(user_id, tool_account_id, skill_id, installation_epoch, base_revision)` 分支保存。A 和 B 即使使用相同 r2，也不会共享可变目录或学习结果。新账户继承安装与规则，从原始版本开始；账户间运行数据复制不属于默认行为。

## 4. CLI 命令契约

入口为 `agent-remote skill`，`agent-remote skills` 为等价别名。以下名称、来源、ID 和 revision 为示例；命令尚未实现。

### 4.1 安装

```sh
# 查看仓库内容，不安装
agent-remote skill add owner/repo --list

# 默认给所有已接入工具；目前实际只有 Claude
agent-remote skill add owner/repo --skill my-skill

# 选择多个，或安装来源中的全部有效 skills
agent-remote skill add owner/repo --skill skill-a --skill skill-b
agent-remote skill add owner/repo --all

# 指定来源、子目录与上游版本
agent-remote skill add https://github.com/owner/repo.git --path skills/my-skill --ref v1.2.0

# 限定为某工具，或某个账户
agent-remote skill add ./my-skill --tool claude
agent-remote skill add ./my-skill --account-id ACCOUNT_ID

# 从现有本地目录导入或预览计划
agent-remote skill add ~/.claude/skills/my-skill
agent-remote skill add ./my-skill --dry-run
```

支持 GitHub `owner/repo` 简写、HTTPS Git URL、本地目录。Git 引用通过 `--ref`，仓库子目录通过 `--path`，不解析任意网页作为安装来源。URL 不携带访问令牌或用户名密码。

来源只有一个 skill 时自动选择；多个时交互选择，非交互调用必须提供 `--skill` 或 `--all`。`--yes` 不代替来源选择。`--list`、`--all` 和 `--skill` 的互斥组合由 CLI 校验。

识别来源根目录或子目录中的 `SKILL.md`；识别一个 skill 后不把其 references/assets 当作嵌套 skill 扫描。发现阶段排除 `.git` 和依赖缓存，展示名称、描述和相对路径。

同用户、来源、子路径、摘要重复安装为内容 no-op。已安装条目不通过重复 `add` 重置规则：若请求范围与已有规则不同，明确提示使用 enable/disable/inherit；内容不同提示 update；同名不同来源报冲突。

`--tool` 可重复指定已接入工具，不能与 `--account-id` 同用。`--all` 只表示选择来源中的全部 skills，不扩大工具或账户范围。一次 add 的所有选中项先完成验证和冲突检查，再在同一用户库事务提交；某项失败不产生部分安装。后续节点部署可以部分 pending，必须逐项展示。

名称用于交互，稳定 skill ID 用于引用。CLI 名称在用户库内唯一；相同仓库中重复名称需通过来源子路径消除歧义，否则拒绝。update 不自动跟随名称或来源子路径变化，返回 `SOURCE_LAYOUT_CHANGED` 并展示差异。绝对路径、`..`、目录分隔符、NUL 或与系统保留名冲突的名称不能作为安装目录。

### 4.2 查询和解释实际结果

```sh
agent-remote skill list
agent-remote skill list --tool claude
agent-remote skill info my-skill
agent-remote skill info my-skill --account-id ACCOUNT_ID

# 某账户下一次启动会用什么，及每个字段来自哪一级
agent-remote skill list --account-id ACCOUNT_ID --effective

# 某旧会话实际固定了什么
agent-remote skill list --session SESSION_ID --effective

# 操作进度与等待
agent-remote skill status OPERATION_ID
agent-remote skill status OPERATION_ID --wait
```

账户详情必须展示解析结果、字段来源、版本固定原因、当前 checkpoint、迁移或合并冲突、最后同步时间。普通清单展示用户库，可用 `--include-system` 增加内置项；有效集合始终包含系统项及已知账户手工项。

`--account-id` 和 `--session` 互斥。list 的账户或会话查询必须带 `--effective`；info 的账户查询用于解释单项规则。所有对象 ID 校验当前用户归属。

有效集合查询是配置与文件视图的说明，不能宣称模型已实际加载。项目 skill 的发现和同名优先级由工具原生规则决定；未检查项目时标记 `not_inspected`。

### 4.3 更新、回滚和固定版本

```sh
agent-remote skill check
agent-remote skill check my-skill
agent-remote skill update my-skill
agent-remote skill update --all
agent-remote skill update my-skill --ref v1.3.0
agent-remote skill update my-skill --from ./my-skill

# 仅登记候选版，再只让某账户试用，不改变其他账户的默认版本
agent-remote skill update my-skill --ref v2.0.0 --stage
agent-remote skill pin my-skill --revision r4 --account-id ACCOUNT_ID

agent-remote skill rollback my-skill
agent-remote skill rollback my-skill --revision r2

# 账户独立固定版本，不受用户库后续更新影响
agent-remote skill pin my-skill --revision r2 --account-id ACCOUNT_ID
agent-remote skill unpin my-skill --account-id ACCOUNT_ID

# 同样允许工具层固定版本
agent-remote skill pin my-skill --revision r2 --tool claude
agent-remote skill unpin my-skill --tool claude
```

Git 来源记录完整 commit 和跟踪引用；默认跟踪安装时的默认分支。分支允许 check/update；tag 和 commit 固定，切换必须显式提供 `--ref`。发现 tag 被移动时报告来源漂移，不静默接受。

本地来源上传完整快照，check 标记为 local source，后续更新必须提供 `--from`。本地绝对路径不作为其他设备可依赖的更新地址。revision 为用户库版本编号，与上游 tag/commit 分开显示。

rollback 恢复 Server 已保存的原始版本包，将用户级上游更新策略设为固定版本；恢复分支跟踪用 `update --ref <branch>`。回滚不清除启用规则、账户固定版本或运行状态，也不等于回滚学习数据。切换到旧 base revision 时恢复该分支已保存的 checkpoint，不把新版运行数据盲目灌回旧版。

不带 --revision 的 rollback 选择用户默认版本激活历史中，上一次不同于当前版本的 revision；不按编号减一，也不选只 stage 从未激活的版本。没有可用历史时返回明确错误。相同内容重复获取不创建新的内容 revision；新的来源观测与跟踪引用记入独立审计记录，不重写旧 revision 的 provenance。

`--stage` 仅支持单项 update，不与 --all 同用；保存候选 revision 及其来源，但不改变默认版本、默认上游跟踪策略或任何账户状态。输出新 revision ID 后可用于 pin。试用完成后显式 update 到相同来源版本可激活已登记 revision，无需重复上传相同文件。

pin/unpin 必须指定 `--tool` 或 `--account-id`，两者互斥。用户默认版本通过 update/rollback 管理。`update --all` 逐 skill 原子处理，部分失败返回非零并给出清单；不承诺跨 skill 的全局事务。

check 和 update --all 对固定 tag/commit、本地来源分别显示 pinned/local_source 并跳过，不把它们当作抓取失败；网络和来源验证失败仍返回非零。update --all 不接受 --ref、--from 或 --stage，避免把一个版本选择错误应用到不同来源。

### 4.4 启停、恢复继承与卸载

```sh
# 用户默认
agent-remote skill enable my-skill
agent-remote skill disable my-skill

# 工具覆盖
agent-remote skill disable my-skill --tool claude

# 账户覆盖，可以覆盖上级的默认停用
agent-remote skill enable my-skill --account-id ACCOUNT_ID
agent-remote skill disable my-skill --account-id ACCOUNT_ID

# 恢复账户继承；只恢复启用字段，或恢复全部规则
agent-remote skill inherit my-skill --account-id ACCOUNT_ID --field enabled
agent-remote skill inherit my-skill --account-id ACCOUNT_ID

# 停用所有范围，清除启用覆盖但保留固定版本
agent-remote skill disable my-skill --all-scopes

# 卸载用户库中的 skill；只针对新会话
agent-remote skill remove my-skill
```

`inherit` 必须选择工具或账户范围；`--field` 为 enabled/revision/all，默认 all。`--all-scopes` 只用于 disable，不能与工具或账户范围混用。账户“移除”用 disable 表达，remove 不接受范围参数。

remove 是用户级卸载，先展示受影响账户与固定版本规则；卸载后任何覆盖都不能使新会话继续使用。历史包、运行 checkpoint 和活动 session 副本保留，先逻辑删除，按引用和保留策略回收。重新安装同一来源时明确提示有保留的账户运行状态，并按新 revision 的迁移规则处理。首版不提供 remove --all。

卸载与重新安装用独立 installation epoch 区分。remove 后旧会话仍提交到被归档的 epoch，完成收尾。相同来源重新 add 时建立新 epoch，默认继承重新安装时已经发布的账户 checkpoint 与原有覆盖；旧 epoch 此后晚到的提交仅归档，不自动进入新安装。重新安装显式要求不同范围时先提示冲突，使用 enable/disable/inherit 调整，不能偷偷抹掉原账户规则。首次安装没有历史时才使用 add 的默认范围。

同名但不同来源重新安装使用新 skill ID、全新规则和状态，不复用旧来源的学习数据。已归档的同名条目通过稳定 ID 查询与导出，不能让短名称错误解析到另一来源。详情列出 epoch 和归档状态；restore 可在同用户、同账户、同 skill、同 base revision 的旧 epoch 间显式恢复，不能跨来源恢复。

### 4.5 运行改动与冲突处理

```sh
# 查看账户运行改动、checkpoint 与冲突
agent-remote skill state list my-skill --account-id ACCOUNT_ID
agent-remote skill state diff my-skill --account-id ACCOUNT_ID
agent-remote skill state info CHECKPOINT_ID
agent-remote skill state conflicts my-skill --account-id ACCOUNT_ID
agent-remote skill state diff --conflict CONFLICT_ID

# 查询或导出某份保留快照，不要求理解内部目录
agent-remote skill state export my-skill --checkpoint CHECKPOINT_ID --output ./skill-state

# 针对一个冲突路径选择保留侧，或上传人工处理后的文件
agent-remote skill state resolve CONFLICT_ID --path references/memory.md --use current
agent-remote skill state resolve CONFLICT_ID --path references/memory.md --use incoming
agent-remote skill state resolve CONFLICT_ID --path references/memory.md --file ./resolved-memory.md

# 整项 skill 的不透明数据冲突：保留完整一侧，或提供完整处理结果
agent-remote skill state resolve CONFLICT_ID --use current
agent-remote skill state resolve CONFLICT_ID --directory ./resolved-skill-state

# 将旧 revision 上晚到的运行改动迁移到新 revision 分支
agent-remote skill state migrate my-skill --account-id ACCOUNT_ID --from-revision r2 --to-revision r3

# 清除某账户当前选定 revision 的运行改动，从原始包重新开始
agent-remote skill state reset my-skill --account-id ACCOUNT_ID

# 恢复该账户保存过的运行状态，只影响新会话
agent-remote skill state restore my-skill --account-id ACCOUNT_ID --checkpoint CHECKPOINT_ID
```

state diff 默认比较账户当前 checkpoint 与该分支原始包；冲突详情包含 base/current/incoming 的明确来源与摘要。current/incoming 随冲突类型解释为账户 head/会话提交，或新上游包/旧账户改动，不能只给含糊的 ours/theirs。

resolve 只在全部冲突路径处理完成且目标 head 仍匹配时原子发布新 checkpoint；不向 SKILL.md、JSON、数据库或其他文件写冲突标记。`--file` 仅适用于普通文件内容冲突；删除、目录和类型冲突通过选择完整一侧解决。整项冲突用不带 --path 的 --use current/incoming，或 --directory 上传完整处理结果，不能逐文件拆开不透明数据组。目标变化时重新计算，不以旧解决结果覆盖新内容。

resolve 的 --use/--file/--directory 三选一；--file 必须带 --path，--directory 禁止 --path。每次选择先保存为解决计划，全部路径完成才发布；dry-run 不保存计划。除 head 外，还必须校验账户目录 head、state epoch、installation epoch 和目标 revision。reset、restore、重新安装或新的迁移取代旧计划后，旧冲突标记 superseded，不能继续发布。选择新版迁移的 incoming 完整旧树可能覆盖新版脚本，预览必须列出相对新基线的全部覆盖；输出 `base_revision + modified`，不能宣称得到未修改的新版。

state reset 创建新的干净 checkpoint，保留可恢复历史，仅影响后续会话；明确列出数据变更并确认。对于该账户该分支，reset 同时推进 state epoch；此前启动的旧会话晚到写入保存为 detached checkpoint，不能自动复活已清除的数据。用户可通过导出或 state restore 显式恢复。

state restore 可选择普通历史或 detached checkpoint，但必须属于同一用户、账户、skill 和当前选定的 base revision，且内容已完整持久化；不同 revision 先显式切换或执行迁移。restore 发布新的 head 并推进 epoch，保留被替换 head 的历史。export 可导出 Server 已保存的快照，或在来源 Node 在线时导出已停止写入、尚待上传的本地快照；无法取得内容时明确报错，不产生声称完整的空目录。

state list 列出该账户各 revision/epoch 的 published、detached、pending 和 conflicted 快照；info 给出完整引用与持久化位置；conflicts 列出冲突 ID 和阻塞原因。export 输出包含树清单和内容摘要的可验证目录，要求目标不存在或为空，写入临时目录成功后才发布目标；解包不跟随输出目录外的链接。大文件/二进制 diff 只显示摘要和大小变化，正文通过 export 查看。

根级辅助数据和完整的跨 skill 提交也必须可查询和恢复。`state list/diff/conflicts/export/reset/restore/prune` 支持 `--scope account-directory --account-id ACCOUNT_ID`，与位置参数 skill 互斥；未指定 scope 时仍使用单项 skill 语义。目录范围 export/restore 的 `--checkpoint` 指向完整目录 checkpoint；`state info CHECKPOINT_ID` 自动展示对象范围。目录 diff 默认比较当前已发布目录与其父目录 checkpoint，无父节点时与首次接管的初始目录比较。完整目录冲突的路径相对发现根，`resolve --directory ./resolved-tree` 上传该冲突范围的完整结果；info 必须明确是单项还是完整目录，不能靠目录名猜测。

目录范围 reset 恢复当前有效用户库项的原始包、当前启用账户本地项的初始快照，并清空根级辅助数据；先展示所有受影响项。目录范围 restore 要求快照属于同一用户和账户、各条目的稳定 ID/目录名/base revision 与当前有效集合一致，且来源身份仍可验证；跨 installation epoch 仅允许同来源条目的显式恢复。集合不一致返回 `STATE_SCOPE_MISMATCH` 并列出差异，不隐式修改规则、启用已停用项或把旧版文件灌入新版。reset/restore 都原子推进目录 epoch 及涉及分支的 state epoch，未暴露条目不受影响。目录 prune 不能绕过任何单项分支的保活引用。

首版不支持通过 state 命令读取其他用户的运行数据，也不把账户状态发布成公共或用户库版本。

### 4.6 公共行为

修改命令支持 `--dry-run`：可读取来源、计算摘要和计划，不上传或修改远端。明确参数加 `--yes` 支持非交互执行；交互只确认一次具体变更。`--yes` 不绕过来源、权限或冲突校验。

`--json` 返回稳定结果，说明写入 stderr。修改命令默认等待当前受影响节点和账户的部署/迁移结果 60 秒，`--no-wait` 在 Server 持久化受理后返回 operation ID；`--timeout <seconds>` 调整等待期限。超时不取消操作。跨账户部分失败明确展示，不因某账户成功就宣称全部可用。

退出码：0 为完成，或 no-wait 下成功受理；1 为业务/执行失败及已确定的冲突；2 为参数错误；3 为超时仍 pending。check 发现可更新项仍为 0，通过结构化字段表达。被更新操作取代的任务标记 superseded 并给出替代 ID。

管理入口首版在已登录的本地 CLI；不要求 SSH shell。远端 Agent 直接调用管理 API 留作后续会话授权能力，不能把本地登录 token 注入远端来实现。

默认展示的名称均可用完整 skill ID 替代。用户库和账户本地条目重名时必须用 ID；账户本地条目仅允许带该账户范围的查询、启停和状态操作，不能通过工具或用户默认命令扩展其范围。本地条目在 AccountLocalSkill 保存自己的 enabled，默认 true，inherit 恢复该默认值；不套用用户库的 tool/account 覆盖表，也不支持 pin，恢复历史内容使用 state restore。

自动重试处理临时网络错误；已结束的可重试操作可用 `agent-remote skill retry OPERATION_ID` 恢复。retry 复用原来源摘要与计划，不重新抓取上游，不重复提交成功项；被取代的操作、权限失败和未解决冲突不能靠 retry 绕过。status 输出 `retryable`、配置是否已提交、每个目标的 readiness 与操作 ID，失败退出后仍能判断哪些变更已生效。

JSON 顶层包含 `schema_version`、`operation_id`（查询时可空）、`status`、`committed`、`retryable`、`data` 与 `errors`；错误至少有稳定 `code`、`message` 和对象/目标引用。非交互缺少必要参数返回 2，不能进入提示等待。`superseded` 为原操作未完成，返回 1 并给出 replacement ID，不把替代操作的成功混成原操作成功。账户无目标节点时 `stored` 是受理目标已完成，返回 0，同时展示 `deploy_on_first_use`；节点离线仍为 pending。CLI 中断等待只停止本地等待，不能回滚已提交配置；重试幂等键和 operation ID 必须写入现有本地状态组件，使网络断开后能找回受理结果。

### 4.7 完整使用流程

```sh
agent-remote skill add owner/repo --skill my-skill
agent-remote skill list --account-id ACCOUNT_ID --effective
cd /path/to/project
fclaude new --account-id ACCOUNT_ID
```

更新或更改账户覆盖后，同样用 fclaude new 创建新会话；直接 fclaude 可能恢复原会话，因此不保证使用新配置。想继承上一会话刚产生的学习结果，应先正常结束上一会话并等待对应状态 published；不需要停止其他无关会话。

## 5. 运行时最佳方案：不可变基线与可写会话副本



### 5.1 启动流程

Server 在创建 session 时固定用户库 generation、工具与账户规则、选定 revision 和已发布 checkpoint。Node 校验所有内容齐备，构建会话独立副本，再启动工具；任何已启用 skill 缺失或存在阻止启动的迁移冲突，都给出具体错误，不能静默跳过。

精确生效边界是 Server 成功创建 SessionSkillSnapshot 的事务：先解析规则、准备缺少的账户分支，再检查 generation/head/epoch 仍匹配并一次性登记全部引用。准备期间配置变化就重新解析，不能混用新规则和旧 checkpoint。该事务之前提交的管理变更必须被新 session 看到；事务之后的变更只影响后续 session。已固定的启动重试复用同一快照，不因 Node 重试而重新选版本。失败且不会再启动的记录才释放引用。

用户默认所有工具属于期望范围；实际资格需要适配器、有效目录和声明兼容性都满足。明确不兼容项显示 excluded_incompatible，不误当可安装失败；未知语义不靠扫描正文自动排除。对已经属于有效集合的 skill，文件缺失、状态迁移冲突或节点能力不足必须阻止该次启动，而非省略后继续。有效清单同时给出 enabled、eligible 与 exclusion_reason。

副本首版使用普通完整文件复制作为语义基线；支持可靠 reflink 时可优化空间，失败回退普通复制。不能用可写硬链接，也不依赖 overlayfs 才能工作。Native 和 Docker 通过适配器将同一语义的普通可写目录映射到原生 skill 发现位置。

Claude 使用其实际 CLAUDE_CONFIG_DIR 对应位置；配置目录和 /account 中可见的等价 skill 路径必须指向同一 session 副本，防止通过路径别名写回用户包或共享账户源。不暴露宿主绝对路径软链接。其他账户和其他用户的副本不挂载进 session。

skills 根目录及普通第三方条目可写，保留脚本执行位、相对路径和文件内容。自修改 SKILL.md、重写参考文件、生成二进制数据和新增文件均可在当前会话完成。运行数据持久化捕获完整树及删除记录，不靠猜测 cache/learning 文件名筛选。

SessionSkillSnapshot 必须记录实际 materialized 的条目 ID、目录名、起始 checkpoint，以及系统排除路径。仅对当时暴露的条目计算删除；因工具范围、账户停用或版本选择没有挂载的条目不等于被会话删除。新增名称不自动冒充同名用户库条目，必须经身份和名称冲突检查。

捕获范围是整个第三方 skill 发现目录，包含根级辅助文件、空目录和无法识别为新 skill 的目录；这些保存为账户目录状态，不提升到用户库。会话同时改动多个 skill 或根级共享资源时，以 AccountSkillDirectoryState 的目录 manifest 统一提交全部变更；任一冲突保留完整提交，不能只发布其中一半。该 manifest 引用各 skill 分支 checkpoint，CAS 覆盖本次涉及的 head 与目录 head，其他未暴露条目保持原状。

运行时完整目录清单是跨条目链接的校验边界；原始安装包仍以单个选定 skill 为边界。运行 checkpoint 可以引用完整目录树摘要及子树前缀，而不是把带有跨 skill 相对链接的子树当作独立、悬空的安装包重新校验。子树视图不授予额外文件读取权限。未来新会话组合不同版本或停用链接目标时，要对最终物化清单重新验证；依赖缺席报告 `STATE_DEPENDENCY_MISSING`，不偷偷重新启用目标项，也不把链接目标复制成失去身份的重复数据。跨条目链接连通的条目构成共同合并单元；其涉及不透明运行数据时共同按完整单元处理。单项导出遇到此类链接时要求改用目录范围导出，不能生成声称自包含的残缺目录。

SessionSkillSnapshot 同时保存原始内容清单和实际准备后的权限基线。增加 owner 读写/目录搜索权限是物化步骤，不是用户改动。捕获时与实际准备基线比较：权限未变则保留原始清单权限，实际 chmod 才记为状态变化；新增文件记录清除特殊位后的实际权限。无用户改动的 session 不得仅因复制、umask 或 fsync 产生新内容 revision 或虚假迁移冲突。

### 5.2 持久化与完成边界

session 运行期间，写入立即落到其节点持久工作目录。正常结束、停止或明确进入无写入的终态后，必须等待其所有受管写入进程退出，生成完整快照并校验，再上传 Server，最后合并到账户分支 head。退出后的用户提示区分 local_durable、upload_pending、persisted、published 和 conflict。本地 finalization 必须完成文件、目录和 journal 的 fsync，再通过原子 rename 提交；仅普通写调用返回不代表已抗断电持久化。

首版不在任意时刻复制一个仍被修改的目录并声称获得应用一致快照，也不周期性把活动副本直接覆盖到账户 head。CLI 从 tmux detach 不代表 session 结束，因此不会发布新的账户 head；此时另开 session 继承上一次已完成发布的状态。需要继承最新改动时先正常结束原 session，并等待状态显示 published。persisted 只表示内容已保存，存在冲突时还不能被后续会话默认继承。

节点重启后扫描未收尾工作目录，在原进程已不存在后生成恢复快照并标记 unclean；文件可恢复不代表第三方数据库业务事务一定完整。unclean 快照上传保存，但不自动推进账户 head；先使用上次干净状态并提示可恢复数据，用户检查后通过 state restore 明确恢复。待上传、待解决冲突和有 session 引用的数据不得自动清理。正常停止流程等待快照持久化，网络异常时保留本地任务并报告未完成同步。

活动副本在节点磁盘永久丢失前尚未上传的改动无法保证恢复；这是首版实时备份边界。checkpoint 一旦 Server 持久化，换节点无需原节点在线。Node 原始包缓存可删除重建，但不能把尚未上传的 session 数据当成缓存处理。

### 5.3 同账户并发会话

每个 session 从其启动时的 checkpoint 分叉，独立读写。完成时以“启动 checkpoint / 当前账户 head / 会话最终树”做三方比较：

- 某路径仅一侧相对共同基线变化：采用该侧；双方结果相同：采用该结果。
- 不同路径的变更可自动合并，包含显式的删除记录。
- 同一路径双方不同、删除与修改、目录与文件类型冲突：保留双方完整快照和冲突清单，不采用最后写入获胜。
- 二进制文件、数据库和文本都不默认做内容级猜测合并。即使是 Markdown 或 JSON，也不插入冲突标记或自动拼接来冒充语义正确。

文件级无冲突不等于应用语义兼容。首版对于涉及二进制运行改动或已识别数据库/sidecar 的分支分歧，保守地把整项 skill 作为一个合并单元，双方都发生变化时要求选择完整一侧或提供处理后的完整状态，不能把数据库主体与另一侧 WAL/索引拼接。普通文本文件的路径级合并仍保留双方原始快照，便于恢复。

一次发布对完整 checkpoint 原子生效。存在冲突时账户 head 保持原状，会话提交完整保留；后续 session 默认从上一个已发布 head 启动并提示存在未合并改动。若用户需要这些改动，使用 state resolve 完成合并后创建新 session。

Server 使用 head CAS 和 state epoch 校验处理并发，不能因两个 Node 任务的到达顺序丢失数据。默认同账户 affinity 仍按现有调度约束执行，此协议同时防御重试和未来迁移。

合并对象是路径、文件类型、规范化权限和内容摘要；删除通过相对起始 manifest 的缺失表达，而不是把一个不完整上传当成删除。目录与文件替换、权限双方分歧、链接目标变化均参与冲突判断。多个 skill 的会话提交遵循第 5.1 节的目录级原子规则，任一项冲突时其他项标记 waiting_for_related_conflict，解决后一起发布。

原子提交与 epoch 的优先级必须一致：一次目录提交的任一改动分支因 reset/restore/remove/reinstall 失去发布资格时，完整提交保存为 detached，其他共同改动也不单独发布；纯粹未暴露或未修改的条目不算本次写入。目录范围 reset/restore 会使此前目录 epoch 的整个提交失去发布资格。只有 head 变化而 epoch 未变时，可重新三方合并并重试 CAS；不能把 epoch 失效当普通竞争重试。旧冲突计划被取代后保留完整输入快照及相关项，不因 superseded 清理未发布数据；用户可导出或按恢复条件显式恢复。

### 5.4 与 stop、delete、清理任务的衔接

现有 Native `Engine.stopSession` 会删除 SessionRoot；新工作副本和收尾 journal 必须放到独立持久 SkillStateRoot，不能只增加一个 SessionRoot 子目录。stop 先确认整个运行进程组已退出，再冻结副本、写入可恢复的本地 finalization journal，然后才能删除临时 runtime spec 和网络资源。进程停止失败时不得快照为 clean，更不能继续删除其工作目录。SIGKILL、超时强停、异常退出等即使已无写入进程，也归类 unclean；进程组为空只证明能安全复制，不证明第三方应用正常关闭。

进程生命周期与数据保存状态分开：session 可以 stopped，同时 skill finalization 为 upload_pending/conflict。正常 stop 在等待上限内尝试完成保存，超时明确返回“进程已停止，数据保存待完成”及 operation ID；后台继续重试，不能为了等网络而让进程保持运行。

自然退出、手工 stop、cleanup_resources、服务重启和启动失败均必须进入同一幂等 finalization 入口。journal 以 session ID 和 snapshot ID 去重；重复 stop 即使 runtime spec 已删除，也要查询 journal，不能直接把“spec 不存在”当作数据收尾成功。

session delete 和批量 delete 必须保留独立的 finalization/快照引用，不允许数据库级联删除未上传数据的索引。存在仅保存在本地、尚未持久化到 Server 的快照时返回 state_pending；内容完整保存为 published/conflicted/detached 后可以删除会话展示记录，无须先解决所有冲突；快照仍保留来源 session ID 与用户授权信息。账户删除继续遵守现有禁用、未绑定和无 session 历史约束，并增加状态引用检查，不能借本功能放宽原删除条件。

## 6. 更新时保留运行改动

上游原始包和账户运行改动分别保存。账户从 r2 跟随默认更新到 r3 时，按“旧原始包 r2 / r2 已发布账户树 / 新原始包 r3”比较：

- 上游改脚本、账户只新增学习文件：两者保留。
- 上游未改的文件，账户改了：保留账户改动。
- 账户未改的文件，上游改了：采用新版。
- 双方改同一路径或发生删除/类型冲突：生成迁移冲突，不覆盖任一侧。

上述自动迁移受第 5.3 节的不透明数据保护约束。涉及数据库或其他二进制运行状态时，不推断新版脚本是否兼容旧数据格式；不能证明可直接复用的双侧变更进入完整状态冲突处理。

只有迁移成功的完整树才能发布为 r3 的账户 checkpoint。用户库默认版本可以先提交为 r3，但相关账户明确标记 needs_resolution；该账户的新 session 不静默回退 r2，也不加载未经解决的混合文件。用户可以解决冲突，或用 pin 显式暂留 r2；其他无冲突账户继续使用 r3。

账户 r2 已固定时，用户库更新到 r3 不为其触发迁移。之后 unpin 跟随 r3 时才执行必要迁移。目标 revision 分支已存在时默认恢复该分支 head，不重复覆盖其运行改动；跨分支新增改动通过 state migrate 显式合入。

首次进入目标分支时不能假设前一版就是用户库的 r(n-1)。自动迁移来源为该账户该 skill 上一次成功准备并发布的有效分支，跳过该账户从未使用的中间版本；无历史则从目标原始包开始。切换到较早登记且从未使用的 revision 时，从该原始包开始并提示未迁移新版状态；需要带回数据则显式 state migrate。revision 登记顺序不宣称等于上游语义版本兼容顺序。

迁移在成功事务中记录确切 source checkpoint、target checkpoint、双方 epoch 与模式；新会话只能选择完整发布的目标。迁移失败或被新配置取代时，不能提前更新 last_effective_revision 或 last_migrated_checkpoint。state reset 可以为当前目标直接建立干净分支并取消旧迁移计划；这允许用户明确放弃迁移改动后继续启动。

更新后仍运行的 r2 session 结束，只提交到 r2 分支，不把晚到写入塞进已在运行的 r3 session 或已迁移的 r3 head。详情显示 r2 有尚未迁移的 checkpoint，可用 state migrate 将增量带到 r3。迁移记录保存 last migrated checkpoint，重复迁移以该记录为基线，不能把旧差异重复应用；仍需与当前目标 head 三方比较并经 CAS 发布。

反复切换版本时，在第 8.2 节保留期与引用规则内，每个分支保留自己的状态。卸载归档分支并保留活动工作副本；卸载期间结束的会话仍可完成数据收尾，但不会重新启用安装。state reset 后 epoch 不匹配的提交只保留，不自动合并。

## 7. 既有手工 skills 与系统 skills

账户原有手工 skills 不自动删除、覆盖或提升到用户级库。首次接入时记录来源并纳入该账户的手工条目及其可写 session 副本，后续按同一 checkpoint 机制保存。原目录作为迁移来源保留，使用可回滚清单跟踪接管状态；接管后是账户 checkpoint 为权威，不能同时把旧目录当成另一个可变主库。

首次接管需要该账户没有仍直接写旧共享 skill 目录的 legacy session。存在时报告 migration_pending，等待这些会话正常结束后再取稳定初始快照；不强停已有会话，也不一边接管一边忽略旧进程的晚到写入。此条件仅适用于首次从旧目录迁移，新模式下并发 session 走第 5 节协议。

会话内普通安装器新增的有效 skill 目录保存为该账户的本地条目，后续同账户会话可继承；不自动共享到其他账户。会话内删除或修改用户库 skill 只属于该账户分支的运行改动，不执行用户库卸载；被删条目在诊断中显示 locally_removed，state reset 可恢复。

手工条目与用户库同名时报告来源冲突，不根据时间戳覆盖。项目级 skills 保持 workspace 与工具原生发现机制；项目文件不进入用户库或账户 skill checkpoint。项目级同名优先级由适配器解释，但不改写项目。

工具插件提供的 skills 属于插件发现范围，不自动拆包接管。适配器能枚举时在有效清单标记 plugin_external 并解释同名优先级；无法枚举则标记 not_inspected。管理器的版本固定保证覆盖自己物化的目录，不能声称同时固定仍由项目同步或插件管理器维护的内容。

账户进入 managed_v1 后，旧 `account import-config` 中 skills 路径不得再直接写旧目录。Server 规划阶段若发现该账户已接管且请求包含 skills，原子拒绝本次导入并给出 `SKILL_MANAGER_OWNS_PATH`；CLI 为其提供 `account import-config --exclude-skills` 迁移其他配置，skills 使用 skill add 的账户范围导入。Node 在执行排队的旧任务时再次检查接管状态，不能让迁移前入队的任务绕过该规则。批量配置导入不允许先写其他文件再发现此冲突。

managed_v1 之前首次接管会锁定并排空旧 skills 导入任务，之后才取稳定快照。legacy → managed_v1 的目录权威切换有单一提交点，失败可重试且不重复导入。最后一个用户库 skill 被卸载也不自动退回 legacy，因为账户还有持久状态和本地条目。

`ego-browser`、`agent-remote-device` 是系统保留名称，由现有 release/capability 流程维护。其需要不可变校验的文件继续只读挂载，不能用普通第三方写入策略覆盖 wrapper、broker、nonce 或签名内容。普通用户库 add 遇到保留名称时解释已由系统提供，并指向组件管理入口。

文件包、session 副本和提交快照验证均排除系统受管路径；普通第三方的自修改不能把系统文件内容发布为账户状态。系统 skill 需要的可写数据按其既有运行时协议处理。

运行中的第三方文件可能把 SKILL.md 改成无效格式。内容安全校验与工具格式校验分开：普通可表示文件的完整快照仍持久化，记录 `invalid_skill_format`；当前会话不被管理器替换文件，后续启动若该项仍在有效集合则明确报错，用户可 disable/reset/restore。不能因格式错误丢弃自修改，也不能把已知条目降格为匿名根级数据后绕过检查。新生成但尚不构成有效 skill 的目录按根级辅助数据保存；以后成为有效 skill 时执行身份和名称冲突检查。

## 8. 存储、接口和部署状态


| 实体                          | 内容                                                                                           |
| --------------------------- | -------------------------------------------------------------------------------------------- |
| SkillInstallation           | user_id、名称、来源、默认 revision、默认 enabled、installation epoch、删除状态                                 |
| SkillRevision               | 不可变包摘要、来源 commit/ref、相对路径、元数据、来源类型与所属用户/账户                                                   |
| AccountLocalSkill           | user_id、account_id、稳定 skill ID、enabled、手工或会话安装来源、初始 revision                                 |
| SkillToolOverride           | installation_id、tool_type、enabled 三态、可空 pinned_revision                                      |
| SkillAccountOverride        | installation_id、tool_account_id、enabled 三态、可空 pinned_revision                                |
| AccountSkillState           | user/account/skill/installation epoch/base_revision、head、state epoch、last_effective_revision |
| AccountSkillDirectoryState  | account、目录 manifest head、目录 epoch、根级辅助数据、各条目与 checkpoint 引用                                  |
| SkillCheckpoint             | 完整树摘要、可选子树前缀、对象范围、父引用、来源 session、base revision、持久化状态                                         |
| SkillStateMigration         | 源/目标分支、上次迁移 checkpoint、目标 head、冲突引用                                                          |
| SkillConflict               | 类型、base/current/incoming、路径差异、解决状态、期望 head 与各 epoch                                          |
| SkillFinalization           | session/snapshot ID、节点持久 journal、完整内容引用、收尾与同步状态                                              |
| SkillOperation / Deployment | 幂等键、目标 generation、节点/账户状态、错误、替代操作                                                            |
| SessionSkillSnapshot        | session、规则 generation、解析原因、物化清单与权限基线、revision、起始 checkpoint、各 epoch、系统 release 引用、工作副本引用     |


工具与账户覆盖的 enabled 三态为 inherit/enabled/disabled；用户默认 enabled 为布尔值。pin 的空值为继承，不使用某个特殊 revision 表示 inherit。数据库约束验证账户与安装属于同一用户、账户工具与工具覆盖一致。规则更新使用 generation 前置条件；运行状态使用独立 head/epoch，不让学习数据写入触发用户库配置变更。

SkillRevision 区分 user_library 与 account_local 来源。后者的原始快照同样持久化，但通过 AccountLocalSkill 归属指定账户，不出现在用户库默认清单中；其他账户不能通过 pin 引用。手工条目和用户库条目的身份不能仅由同名路径推断。

新增账户继承实时规则；符合第 5 节删除条件的账户才清理其覆盖，运行数据先按保留策略处理，其他账户不受影响。被用户当前默认、工具或账户 pin、活动/待启动 session、账户当前有效分支 head、未解决冲突、待上传收尾任务引用的内容不能垃圾回收。包与状态可存 Server 持久化 volume，数据库保存引用，后续可换对象存储。备份恢复必须同时包含两者。

CLI 获取 Git 或本地来源，上传规范化文件包；私有 Git 复用本机已有认证，凭据不上传。Node 从 Server 下载包与 checkpoint，无需用户 Git 凭据。运行 checkpoint 可能含学习内容及工具生成数据，按当前用户私有数据存储和授权，不在普通日志中输出正文。

上传暂存与原子提交分离；完整包验证后才发布 revision。现有配置导入接口不承载新文件包，也不复用其 1/8 MiB 限额。普通发布包建议单文件 10 MiB、总计 50 MiB、5,000 文件，允许管理员配置。

运行状态配额独立于安装包限制，采用第 8.2 节可配置初始默认值并由 status 展示；不能用 10 MiB 安装文件上限截断第三方生成数据库。超额保留本地副本并报告 quota_exceeded，禁止静默丢文件或把部分快照发布成成功。用户先导出/清理数据或管理员调整配额。

部署目标为受理时受影响账户所在节点，账户覆盖操作仅影响该账户。无目标节点时显示 stored; deploy on first use。节点离线可先持久化接受，等待时明确 pending。session 启动校验其精确 revision、checkpoint 与能力齐备，不依赖后台任务“应该已完成”。

乱序任务不能回退 generation/head；重复任务幂等。由新配置取代的操作展示 superseded，新配置仍须满足版本引用和状态迁移规则。支持用户库默认已提交、某账户迁移冲突、某节点离线等分别可解释的状态。

Runtime Helper 只接收校验后的用户、账户、会话与包标识，执行声明式目录准备、权限和挂载。Git 下载和仓库脚本执行不进入特权路径。

### 8.1 API 和状态机边界

具体 URL 可在实现时按仓库既有路由约定命名，但以下操作必须独立：内容包暂存/完成校验、用户库变更、工具/账户覆盖、会话快照预约、节点部署、finalization 上传与提交、冲突计划与解决、操作查询/重试。不能用一个“写任意远端路径”接口实现这些功能。

修改请求统一携带幂等键与期望 generation 或 head/epoch；相同键且相同请求返回原结果，相同键不同请求拒绝。幂等记录与变更在同一事务提交。Server 从认证身份确定 user_id，从已授权对象确定路径和账户；不能相信请求传来的任意 user_id 或路径。

Node 上传的 checkpoint 绑定 Server 下发的 session/snapshot ID、node ID、账户、revision 和起始 head/epoch，并由 Helper 验证本地目录归属。内容摘要验证只证明完整性，不代替这些归属校验。包下载按对象所属用户或已绑定节点任务授权，知道摘要不等于有权限。


| 对象           | 主要状态                                                                           | 关键约束                                   |
| ------------ | ------------------------------------------------------------------------------ | -------------------------------------- |
| 内容上传         | staged → verified → committed，或 rejected                                       | 未 verified 不发布引用；重复完成请求幂等              |
| 配置操作         | accepted → preparing → ready / needs_resolution / failed / superseded          | needs_resolution 不是完成；配置可能已经提交         |
| finalization | local_durable → upload_pending → persisted → published / conflicted / detached | persisted 只代表内容保存；published 才能被新会话默认继承 |
| 异常退出快照       | persisted_unclean → detached                                                   | 不自动成为账户 head，显式 restore 才发布            |


配置操作是否 committed、节点是否 ready、状态是否 published 分别输出。no-wait 返回 accepted；等待调用遇到已确定 conflict/needs_resolution 返回 1，pending 超时返回 3，不用一个“installed”覆盖所有状态。冲突解决计划以多个小请求保存，最终发布是单次原子操作；不能因最后一条路径上传成功就提前宣称整个合并完成。

### 8.2 内容清单、资源上限与回收

清单固定格式版本，按规范化相对路径排序，记录条目类型、普通文件长度和 SHA-256、规范化权限、空目录及链接目标；树摘要覆盖全部这些字段。mtime、宿主 UID/GID 不参与内容身份，清除 setuid/setgid 等特殊位。记录并拒绝重复路径、规范化后碰撞、路径穿越和解包时的链接替换；实际字节数与解压后配额都需校验。

Git 下载定位到完整 commit 后打包，不执行来源 hook，不静默忽略未取得的 submodule 或 LFS 内容；缺少所选 skill 引用的资产时报 incomplete_source。读取本地来源时检测文件读取前后身份/大小变化，发现不稳定就重试或报错；用户须停止并发写入才能得到应用一致快照。先完整打包至本地暂存，再计算上传计划和确认范围。

Server 配额、Node 会话副本配额与磁盘余量分别计量。启动前预留构建副本所需空间；空间不足返回 insufficient_storage，不能启动后才发现 skill 未复制完整。运行期额度不足不截断快照、不自动删学习文件；原目录保留，停止后的 export 仍应在足够输出空间下可用。管理员配置必须有明确数值与单位，未设置时使用发布定义的默认值，不把“无限”当默认。

历史不是无限保留：发布/账户当前引用、pin、pending、conflict 和活动会话构成 GC 根；终态且超过保留期的操作、已解决冲突、旧 checkpoint 元数据先按策略退役，再计算内容可达性。退役的普通历史父关系不永久保活全部旧包，否则无法回收。已回收 revision 仍保留最小审计 tombstone，restore/rollback 明确返回 revision_expired；不能列为可恢复版本。

“当前分支”指现有安装 epoch 中该账户当前解析版本的状态；仅停用不会使它失去保护。非当前版本、无 pin、无 session/冲突/收尾引用的分支属于可按保留期退役的历史，不能因为还有一个 head 字段就永久保活。卸载 epoch 的分支也按归档规则计算；账户目录 manifest 必须同步退役这些历史引用。曾使用但状态已过期的版本再次被选中时显示 state_expired，要求显式 state reset 从原始包开始，不静默把“学习数据已回收”伪装成从未使用。

所有历史保留期与配额由发布配置定义，CLI info/status 展示保留截止时间和空间用量。GC 分两阶段标记与删除，提交新引用和删除之间必须有租约或事务校验；并发会话预约、pin 或 restore 不能拿到正在删除的对象。用户删除遵守系统已有数据删除策略，不能由 skill 外键默认 cascade 悄悄改变。

首版初始默认值如下，部署管理员可以调整；它们是可配置运行参数，不是已通过容量测试的性能结论：


| 配置项                              | 初始默认值                  | 计算与例外                                              |
| -------------------------------- | ---------------------- | -------------------------------------------------- |
| 单个账户 skill 或根级辅助状态的完整 checkpoint | 1 GiB、最多 100,000 条目    | 展开后的普通文件总大小；不设额外 10 MiB 单文件限制                      |
| 单次完整账户目录快照                       | 10 GiB、最多 100,000 条目   | 所有物化条目与根级辅助数据的总和；同时满足单项上限，完整 manifest v1 不分片绕过条目上限 |
| 单用户 Server 原始版本包存储               | 2 GiB                  | 含保留版本和候选版本，按该用户唯一内容对象计量，与运行状态额度分开                  |
| 单用户未提交上传暂存                       | 2 GiB                  | 并发上传原子预留额度；运行快照按运行状态额度预留，不额外受原始包暂存上限限制             |
| 单用户 Server 运行状态存储                | 20 GiB                 | 按该用户保留引用的唯一内容对象计量；不与其他用户合并额度                       |
| Node 启动前剩余磁盘保留                   | max(2 GiB, 文件系统容量的 5%) | 扣除准备副本的预计空间后仍须满足；不代替系统运行期磁盘管理                      |
| 未被引用的普通历史、已解决冲突和候选版本             | 30 天                   | 从最后解除有效引用或解决时计时                                    |
| 卸载归档且无保活引用的内容                    | 90 天                   | 活动旧会话、未解决冲突和待同步对象仍受保护                              |
| 未完成且无活动上传租约的暂存包                  | 24 小时                  | 不适用于 Node 本地唯一的未上传工作副本                             |


保活引用解除后才进入上述回收时钟。用户需要提前释放历史空间可用 `agent-remote skill state prune my-skill --account-id ACCOUNT_ID --dry-run` 查看候选，再去掉 --dry-run 执行；默认仅回收保留期已到的运行历史，`--all-unreferenced` 可明确提前回收非保活历史。命令展示将失去恢复能力的 checkpoint 清单并确认，不能回收当前 head、正在使用的快照、待同步内容或未解决冲突。未解决冲突先通过 resolve 明确选择保留结果，再进入历史回收。prune 不修改技能包版本和固定规则。

### 8.3 能力协商与发布顺序

Node 按 backend 报告 skill_manager 协议版本、文件清单版本、可写副本、状态收尾与恢复能力；Server 只向匹配版本下发任务。旧 Node 对操作显示 unsupported，不能伪装为 pending 无限重试。首次无管理器使用的账户保留 legacy；一旦进入 managed_v1，即使用户库暂空也不能在旧 Node 静默降级。

发布顺序是 Server schema/API 兼容升级、Node/Helper、CLI，最后允许账户切换 managed_v1。Server 可在旧 Node 存在时接受用户库内容，但明确该账户不可部署；启用模式和首次迁移需要节点能力齐备。降级不能让旧二进制读取新 ledger 并清理 SkillStateRoot；需要先停止相关会话并执行显式、可验证的数据导出/迁移流程。

## 9. 第三方兼容策略

1. 保留第三方文件内容、必要执行位、标准目录结构和相对引用，不要求额外 Agent Remote manifest。名称和 frontmatter 按目标工具实际规范验证；内部身份使用稳定 ID，不为管理方便重写 SKILL.md。
2. 来源根目录可解析本地软链接；目录内部链接可在选定来源根内保留或规范化，须保证远端仍指向同一包内资源。外部链接、环、特殊文件和越界写入不直接打包，展示缺少的资源让用户整理完整来源。
3. 捕获运行快照时，内部有效链接保留链接语义，不沿新生成的外部链接读取 session 外文件。指向适配器明确识别的受管运行时程序（例如虚拟环境的 Python 解释器）的链接保存为外部依赖引用，只记录目标，不上传目标内容；目标运行环境须重新校验能力和路径。其他外部链接报告 portability_error 并保存诊断/本地副本，不宣称可跨节点恢复。安装校验和运行数据捕获分开处理，不能把合法的运行时依赖链接一律当作安装包损坏，也不能跟随任意链接读取节点私有文件。
4. 所有普通第三方文件可写，不区分提示词、脚本与学习文件。自修改影响当前会话及该账户后续 checkpoint；用户库发布版本保持原样。
5. 依赖检查展示缺失程序、工具能力和已声明依赖。不把安装来源中的任意脚本自动当作安装 hook；需要依赖时按远端运行环境正常安装流程执行，不能把本地 macOS 的依赖目录直接视为 Linux 可运行资产。
6. 任意二进制数据库和文本的并发语义无法通用推断，因此通过独立副本、快照保留和显式冲突解决保证不丢数据；不承诺无冲突自动合并一切内容。
7. 首版适配 Claude；后续工具注册发现路径、格式约束、系统保留名称、依赖探测和运行时映射。未知工具明确报错；用户默认“所有工具”的规则仍保留。



## 10. 首版范围与实施顺序

首版必须包括：用户库、Git/本地安装、来源选择、列表与有效配置解释、更新/回滚、工具与账户覆盖、pin/unpin/inherit、可写会话副本、状态持久化、三方路径合并、版本迁移、冲突导出与解决、启停卸载和失败恢复。

首版不包含：公共贡献或共享市场、全网搜索、账户间自动共享学习、项目依赖锁文件、任意依赖自动安装、远端 Agent 自主管理 API。Web 页面可后续复用同一 API。不能把账户覆盖或可写状态延后而仍声称完成本文首版。

涉及 agent-remote-cli、agent-remote-server、agent-remote-node 及本仓库文档。实现顺序：

1. 冻结规则解析、数据实体、状态分支与命令参数契约；验证账户覆盖、恢复继承和引用保护。
2. 验证 Native/Docker 的普通可写副本、路径别名、持久目录和系统 ego-browser 挂载；普通复制为可用基线，reflink 仅作优化。
3. 打通本地安装、session 启动、正常结束发布 checkpoint、下一会话继承的完整闭环。
4. 实现并发写入、更新迁移、旧分支晚到写入、冲突处理、reset epoch、离线与重启恢复。
5. 完成 Git 来源、批量更新、JSON/状态契约、文档和跨仓库发布能力协商。



## 11. 验收标准

- A 用户管理、下载、查询和修改操作均不能访问 B 用户数据，包括同摘要包、冲突和 checkpoint；同节点不例外。
- 无 --tool 安装目前只在 Claude 生效；新增测试工具适配器后自动继承。明确限定工具或账户的安装不扩大范围。
- 覆盖按字段解析；账户启用可覆盖上级默认停用；all-scopes 停用清除启用覆盖；inherit 不删除状态；pin 阻止自动跟随更新。
- 两个账户共享原始版本但学习数据独立；同账户两个 session 写同路径不会互相改变活动文件或丢弃最终提交。
- 第三方可修改 SKILL.md、执行 scripts、写 references、保存二进制文件和新增有效 skill；正常结束持久化后，新会话继承相同内容与删除记录。
- 管理更新或其他 session 完成不会改变旧 session 的工作副本；当前 session 自身修改仍正常。
- 上游与账户修改不同路径可迁移；同路径冲突保留双方、不写冲突标记、不静默回退；pin 可显式保持旧版本。
- 老版本 session 晚到提交不污染新分支；重复迁移不重复应用；reset 之前的旧提交不会复活被重置状态。
- Node 离线、进程异常退出、系统重启、上传失败、配额不足、乱序和重复任务有准确状态；未持久化数据不被当缓存清理。
- 备份恢复覆盖版本、账户状态、规则、冲突与所有引用；新节点能恢复 Server 已持久化内容。
- 手工迁移源保留且单一权威明确；系统只读文件、broker 和 capability 校验保持有效。
- Native 与 Docker 分别验证，未通过的 backend 不发布此能力；不能以宿主目录存在代替远端工具读取和写入成功。



### 11.1 必须覆盖的状态交错用例


| 场景                               | 必须得到的结果                                                |
| -------------------------------- | ------------------------------------------------------ |
| stage r4，再只 pin 账户 A；账户 B 跟随 r3  | A 新会话用 r4，B 继续 r3，默认上游跟踪不变                             |
| 会话准备 r2 时默认切到 r3                 | 快照事务前切换则重解析；事务后切换则该会话仍用 r2                             |
| reset 推进 epoch 后旧 resolve 到达     | 旧计划 superseded，不能恢复被清除状态                               |
| remove E1 后重新 add 为 E2，旧会话此时完成   | 内容归档于 E1，不推进 E2 head                                   |
| 账户停用某项，因此会话根目录没有该项               | 收尾不记录删除，不影响其已有 checkpoint                              |
| 同一会话改两个 skill，其中一项冲突             | 两项均等待同一提交解决，不发布半份跨 skill 改动                            |
| 正常停止后网络断开，同时执行 delete/cleanup    | 进程可以 stopped，journal 与完整工作副本保留，delete 返回 state_pending |
| 上传完整但三方合并冲突                      | persisted 不等于 published，新会话仍读上一个已发布状态                  |
| SIGKILL 后重启                      | 快照标记 unclean/detached，不能自动覆盖干净 head                    |
| legacy 导入任务入队后账户切换模式             | 执行时校验模式，任务拒绝写旧 skills 路径且不部分导入                         |
| GC 标记对象后同时 pin 或创建 session       | 通过引用事务/租约保活，不能返回已删除对象                                  |
| runtime 生成 venv 的解释器链接           | 仅保存合法运行时依赖引用，不复制解释器，也不读取任意外部目标                         |
| 会话改 A/B 两项，A 被 reset 后会话才结束      | 整个提交 detached，B 不单独发布；完整内容仍可导出恢复                       |
| 目录范围 reset 后旧会话写入根级辅助文件          | 目录 epoch 拒绝旧提交自动发布，不能复活已清空的根级数据                        |
| skill A 的相对链接指向 B，随后账户停用 B       | 保留已发布完整快照；新会话报 STATE_DEPENDENCY_MISSING，不重新启用 B        |
| 原始脚本权限 0555，准备时加 owner 写权限但会话未修改 | 收尾保持原始权限身份，不生成虚假运行改动或迁移冲突                              |
| SKILL.md 在会话中被写成无效格式             | 普通文件内容完整持久化并报告格式错误；后续有效项启动被阻止且可恢复                      |
| 目录 restore 时当前有效版本或条目集合已经变化      | STATE_SCOPE_MISMATCH，不更改规则、不部分恢复、不向新版写旧状态              |
| 无绑定节点的安装，及等待时 CLI 断线             | 前者 stored/deploy_on_first_use 且退出 0；后者可凭持久化幂等键找回原受理结果  |


这些是后续实现的测试契约，本次文档审查不代表上述行为已通过实际运行测试。

## 12. 实现阶段需要验证的事项

用户范围、默认工具范围、新会话生效、第三方可写和账户覆盖均已确定，不再作为待用户选择项。

实现阶段自行解决并验证：不同 backend 的挂载顺序与路径别名、session 退出后全部写进程收尾、既定初始配额的容量测试、CLI/API 的分块上传和超时、文件树类型冲突的事务处理。若某 backend 暂不满足契约，应明确不支持并给出验证结果，不能静默改为共享可变目录或只读第三方目录。

## 13. 本轮复审结论

复审以本文规则和当前 CLI/Server/Node 实现衔接为依据。下列遗漏已补入对应章节，不改变第 1 节用户已确定的产品边界。


| 级别  | 原缺口                         | 已补约束                                                    |
| --- | --------------------------- | ------------------------------------------------------- |
| 高   | 停止、删除与资源清理可能移除唯一运行数据        | 独立 SkillStateRoot、finalization journal、停止/数据状态分离和删除检查   |
| 高   | 会话准备过程中配置与 checkpoint 可能混用  | 精确快照事务边界、固定引用与重试语义                                      |
| 高   | reset、重新安装后的旧提交或旧冲突可使历史数据复活 | installation epoch、state epoch、完整发布前置条件                 |
| 高   | 缺席条目被误判删除，根级文件或跨 skill 改动漏存 | materialized 清单、账户目录 manifest、目录级原子提交                   |
| 高   | 配置导入继续写已接管目录                | 双端模式校验、--exclude-skills 与首次迁移提交点                        |
| 中   | 账户试用新版必须先改变所有账户默认版本         | update --stage 与账户 pin                                  |
| 中   | 回滚目标、重装继承和未用过目标版本不确定        | 激活历史、归档 epoch、确定的迁移来源与初始分支规则                            |
| 中   | 冲突难查询、成功状态含义混淆              | state info/conflicts/diff、计划发布条件、persisted/published 分离 |
| 中   | 历史永久占用或与 GC 并发导致引用悬空        | 明确配额/保留期、可达性回收、prune 与引用保护                              |
| 中   | 旧 Node、插件来源和运行时链接的行为未定义     | 协议能力门槛、外部发现范围、合法运行时依赖链接                                 |
| 高   | 跨项原子发布遇到单项 epoch 失效时处理不明确   | 完整提交 detached、目录 epoch、无部分发布和完整输入保留                     |
| 高   | 跨 skill 链接与单项清单校验矛盾         | 完整目录校验、带前缀的 checkpoint 视图、链接依赖单元和缺席错误                   |
| 中   | 根级辅助数据有保存模型但没有恢复入口          | state 的 account-directory 范围及严格集合匹配恢复                   |
| 中   | 物化权限和第三方无效格式可能误判或丢失改动       | 实际权限基线、格式诊断与内容持久化分离                                     |
| 中   | JSON、无节点完成、目录总上限及暂存配额不明确    | 稳定结果字段、stored 退出语义、持久幂等键和明确总额度                          |


与现有代码衔接的直接依据：Node 的 `internal/runtimehelper/engine.go` 中 stopSession 删除 SessionRoot；Node 的 `internal/worker/worker.go` 中 import_tool_account_config 直接调用账户文件导入；Server 的 `services/sessions.py` 和 `services/tool_accounts.py` 维护现有删除条件。实现时必须同时修改这些调用路径及测试，不能只新增 skill 子命令。