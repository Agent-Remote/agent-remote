# Skill 跨仓库契约

本文件保留实现必须遵守的边界。日常操作见[使用与运维](skill-manager.md)，
实测范围见[验收状态](skill-acceptance-plan.md)。字段、路由及迁移以各仓库 schema、实现和契约测试为准；
修改协议必须同步受影响的 Server、Node、CLI 与跨语言测试。

## 责任与权限

| 组件 | 责任 | 禁止越界 |
| --- | --- | --- |
| CLI | 获取来源、私有快照、预览确认、原请求 journal、查询与校验导出 | 不保存凭据到 journal，不执行来源脚本，不静默重定基线 |
| Server | 用户库、规则、不可变版本、快照、任务租约、发布/冲突、配额与保留 | 摘要不是权限，不接收任意远端路径写入 |
| Node Worker | 主动轮询、严格验证原身份、传输、回执恢复与能力转发 | 无特权目录写权限，不加入 Docker 组 |
| Node Helper | 私有存储、账号围栏、准备/启动、停写证明、冻结、恢复与回收 | 仅可信根和认证 socket；不能凭 Worker 历史结果删除数据 |

用户库及 state 操作用当前有效用户 token。Node 内容操作必须绑定原 user/account/node、
snapshot/task UUID、当前 lease attempt 与完整输入摘要；device/session token 仅限明确授权的进度接口。
Node 导出绑定原用户 token、设备、SSH key 和快照，原 Node 在线重验并只续接仍有效的 grant。
私密内容、凭据和任意响应体不得进入日志、审计、心跳或普通任务结果。

## 内容与版本

- Manifest v1 条目按 UTF-8 路径字节排序，字段固定为
  `path, kind, mode, size, sha256, target, content_kind, dependency`；拒绝未知字段、非法数值和显式 null。
  路径是 NFC 相对 POSIX 路径，所有父目录必须显式存在；不得逃逸、成环或穿越非目录。
- `kind` 为 file / directory / symlink / runtime_link；普通链接必须在完整树内解析。
  runtime_link 还必须匹配 Helper 独立探测的适配器依赖，不能由任务指定解释器或主机路径。
  包不能携带 runtime_link。权限保留普通位，不携带特殊所有权位。
- 树摘要为 SHA-256：`agent-remote-skill-tree-v1` 加 NUL，再按上述字段次序逐项编码，每字段以 NUL 结尾。
  mode/size 使用规范十进制；不得用默认 JSON 序列化作树身份。文件另按 SHA-256 寻址并核验长度/内容类型。
- 安装包不可变；会话用独立可写副本。记录源权限与实际物化权限，未被用户修改的权限正规化不能伪造成学习。
  Node 使用 descriptor-relative no-follow 访问、私有 staging、fsync 与原子发布；不跟随替换路径或链接。
- enabled / revision 分别按账号、工具、用户继承。安装纪元与状态纪元不同，删除重装不能接受旧纪元写入。
  账号本地来源与用户库身份分离；已创建会话固定原始选择和系统制品 pin。
- 运行态捕获覆盖完整账号发现目录并排除受管系统条目；跨技能链接以完整目录为单位校验和合并。
  禁用依赖返回 `STATE_DEPENDENCY_MISSING`，不得隐式启用。Device / Ego Browser 系统 Skill 保持只读且与发布制品匹配。

## 准入、执行与保存

1. Server / Node 默认开启；显式 false 保留。Helper 实测通过后才报告 Native protocol、manifest、deployment v1
   及 writable copies / finalization / recovery。缺失、损坏或撤回报告均不能伪造 ready。
   Docker Sandbox 不声明 Skill 支持，且不在当前验收计划；通用版本协商和拒绝不支持后端仍必需。
2. 首次接管先关闭持久账号围栏、排空旧导入与写入者、保留原字节，再发布管理权。
   受管/迁移中账号的 legacy 启动、绑定、后端迁移和技能导入都被围栏拒绝，关闭 feature flag 不能绕过。
3. 配置提交保存不可变目标计划和 plan digest。全局/工具变更按前后启用选择挑选受影响账号；
   显式账号请求及未完尝试保留，disable/remove 原启用内容仍需清理部署。
   配置 committed、部署 prepared、会话 ready 和模型实际 loaded 是独立事实。
4. 部署仅凭原 attempt、task record 和未过期租约准备；成功通过专用回执确认。
   失败终止依次保存 Server 撤权、Helper 持久 drain、Server 终态。superseded/expired 不是已排空。
   重试仅作用于原操作中已结束且可重试的失败目标，不重放成功目标。
5. managed 启动不能落回 legacy 解码或结果缓存。启动意图先于执行持久化，原 spec/boot/unit/UID/invocation
   与当前租约必须一致。恢复只确认已提交的原回执；历史 ready 不能重新授权进程或 broker。
6. 冻结前证明原进程与整个 cgroup 停写。正常零退出、被迫终止和未知结果不可混淆。
   无关的 runtime inventory 不能终止 managed 会话；Node 终止证据、完整捕获、Server persisted、发布分别记账。
   捕获失败保留原数据并报告 `capture_pending`；unclean 输入只能 detached，不能自动成为当前 head。
7. finalization 独立于过期启动租约。先保存原捕获，再上传并取得完整持久化回执，最后原子发布完整目录。
   检查 generation、目录/分支 epoch 与 head；旧纪元整体 detached，同纪元 head 移动可重新合并。
   同路径冲突、二进制/数据库不透明单元和链接单元不得部分发布。未解冲突保留所有比较输入。
8. reset/restore/migrate/resolve 使用原始比较输入、精确 owner/source/revision/epoch 和确认的结果。
   metadata-only 预览不上传、建 journal 或产生发布权限。状态查询不会推进 head 或保留时钟。

## 恢复、导出与删除

- CLI 在提交前保存 Server/user 分区的原请求、generation、随机幂等键；未知提交先按原键查询，
  仅在明确不存在时重放完全相同请求。超时、中断、5xx 或错误成功体不证明拒绝或回滚。
  preparation 可取消；提交后的回执和最终原子发布必须如实报告。批量更新是逐项事务。
- Node 原身份 journal 区分启动、部署、捕获、persisted、publication、cleanup 和 reclamation。
  丢失响应用精确回执恢复；Worker journal 不授予 Helper 权限，关闭新准入也不能停止既有保存恢复。
- 跨重启恢复必须验证原私有绑定与当前 boot/unit/cgroup/mount/invocation；不同 boot 下先证明当前资源不存在，
  不得停止新进程、重建 broker nonce 或把缺失 spec 当作删除授权。
- 冻结导出持有 manifest inode 的共享 flock，读取覆盖整个上传/导出生命周期；删除须独占锁。
  仅当冻结目录确实不存在时允许独立 stopped-work 恢复；损坏捕获不能降级为工作树导出。
  原停写证明和全树前后检查必需，不另造 durable capture，不更新 head，也不删除原数据。
- manifest v1 上限保持 100000 条目；`recovery_version:1` 协商独立的完整恢复流支持超限停写树。
  恢复不以运行态 10 GiB 配额截断原数据，但保留整数、帧、内存、授权与超时限制。
  进度正常且持续授权的导出可超过 15 分钟；初/末扫描各有 15 分钟界限，续权不能复活过期授权。
  CLI 完整验证后原子发布 bundle，失败不产出貌似成功的部分导出。
- Server 保留分析覆盖 active/pinned/disabled、旧快照、待保存、冲突、迁移、上传和跨分类共享内容。
  新表/引用先纳入保护图；未知状态或超限分析整体失败。保留期从最后解除保护引用的事务开始，重新引用清时钟。
  prune 要完整签名预览与原确认；先整理目录/解除引用，再事务提交 deleting 与配额变化，最后执行可重试物理删除。
- Node 本地回收另需最新 Server 完整内容证明（60 秒单调预算）、原终态 publication/cleanup 回执、
  无 writer/reader/mount/reference 及完整未变树。只删意图指定的原 work/objects；冲突、未知或替换内容保留。
  删除意图和完成回执独立持久化；已有意图可精确续作，不能扩大删除范围。

## 后端权限迁移恢复

该边界保护账号原数据，与 Docker 是否参与验收无关。管理员使用原 logical task ID 与独立 request UUID；
新恢复任务保留原失败任务/结果。默认 v1 只验证已完成目标；`--verify-source` v2 只验证已完成源回滚；
`--repair-source` v3 才允许恢复源权限，后二者互斥，request UUID 的 action 不可改。
默认/verify 不启动 copy、chmod 或 rollback；未知/不完整证据继续阻止准入。

Helper 的 whole-migration、copy、writer 和 repair 版本域独立。恢复必须验证原 backup、内容/拓扑、
权限基线、失败 attestation、原账号 inode、共享父目录及全部写入者退出；先写 repair 意图再改权限，
不覆盖外部 ACL/属主变更。完成前重复核验、syncfs、稳定 boot 与无 writer；跨 boot 还需当前 unit/cgroup 不存在。
Server 持有同一 user/account 锁核验原 source/target 绑定，成功也保留原账号 disable 状态。
恢复错误与 status 保留原 request/action；失败查询不能推断提交不存在。

## 实现入口

- [Server](https://github.com/Agent-Remote/agent-remote-server/blob/main/docs/skill-manager.md)：schema、存储、保留、服务与迁移。
- [Node](https://github.com/Agent-Remote/agent-remote-node/blob/main/docs/skill-manager.md)：Worker / Helper、私有记录与运行态测试。
- [CLI 参数](https://github.com/Agent-Remote/agent-remote-cli/tree/main/src/cli/skills)、
  [CLI 编排](https://github.com/Agent-Remote/agent-remote-cli/tree/main/src/skill_commands)、
  [CLI 来源](https://github.com/Agent-Remote/agent-remote-cli/tree/main/src/skills)。
- 精确发布组合维护在 `release-manifest.json`；组件依赖、生成的制品策略和 golden vectors 必须同步校验。

历史逐次实现/测试日志保留在 Git 历史；新增行为更新本契约、对应组件说明和测试，避免新增阶段性 Markdown。
