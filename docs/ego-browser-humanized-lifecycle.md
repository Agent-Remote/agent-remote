# ego-browser / ego-lite 人性化安装与生命周期契约

本文是 `agent-remote`、`agent-remote-node`、`agent-remote-cli`、
`agent-remote-server`、`agent-remote-admin-web` 和 `agent-remote-ego-browser` 之间的用户体验
与行为契约。
它把安装、注册、连接、升级、修复和卸载拆成可验证的生命周期，并规定哪些值由系统
自动发现，哪些值只在高级诊断中显示。

> **先记住三句话（目标流程）**：Node 安装默认不会打开 ego-browser；正常 macOS
> Bridge/bootstrap 升级不需要重新注册 Device；`EXPECTED_64_HEX_DIGEST` 由受信发布 profile
> 自动提供，普通用户不填写。

本文不改变 full-trust 的安全边界：远端脚本仍以当前 macOS 用户身份执行完整
`ego-browser` heredoc。减少输入只意味着把可自动验证的内部参数收回系统管理，不能
省略用户对本机信任、具体远端 session 和 full-trust 的确认。

> **文档状态**：这是跨仓库的目标契约和实施蓝图。本文只固化方案，不宣称当前版本已经
> 提供下文所有新命令；在 P0-P3 完成前，应继续使用第 8 节列出的兼容入口，并把每个阶段
> 的验收门槛作为发布条件。高层 `setup` 可以编排固定版本的官方 ego lite 安装；底层
> Bridge release installer 只安装 Bridge/Device Client，不能自行下载、替换或修改 ego lite。

> **规范词和冲突处理**：本文中的“必须”是发布阻断条件，“应”是默认实现（偏离时必须留下
> 设计记录），“可以”是可选能力。安全边界文档中的更严格约束优先于本文；本文优先于低层
> 部署手册和旧 README 的用户流程描述。本文描述的是目标行为，命令或 API 在实现前不得被
> 当作当前版本已经存在。

> **事实源优先级**：涉及具体版本、制品摘要、证书 pin 或发布状态时，以已验证的
> `release-manifest.json`/schema 及其签名证据为准；涉及权限、数据暴露和 fail-closed 时，以
> 安全边界文档中更严格的规则为准；本契约只定义用户入口和跨仓库语义。若低层 runbook、README
> 或本文件中的示例与上述事实源不一致，应停止部署并先更新文档/发布记录，不能自行挑一个值。

> **本方案边界**：实现范围只覆盖 ego-browser/ego-lite 生命周期及其跨仓库契约；不修改、
> 不安装、也不把 `agent-remote-device` 作为运行依赖。本文本身不授权生产部署、真实设备撤销、
> 证书轮换或自动 commit/push。

相关事实源：[`release-manifest.json`](../release-manifest.json) /
[`release-manifest.schema.json`](../release-manifest.schema.json)（版本与 pin）、
[`ego-browser-bridge-security.md`](ego-browser-bridge-security.md)（安全边界）、
[`ego-browser-bridge-deployment.md`](ego-browser-bridge-deployment.md)（低层部署/恢复）、
[`upgrade.md`](upgrade.md)（跨组件升级顺序）、
[`ego-browser-bridge-acceptance.md`](ego-browser-bridge-acceptance.md)（发布验收）和
[`ego-browser-bridge-release-promotion.md`](ego-browser-bridge-release-promotion.md)（证据晋级）。

## 0. 先看结论

这三条结论直接回答最常见的安装疑问：

| 问题 | 默认答案 | 允许的例外 |
| --- | --- | --- |
| Node 安装会不会自动开启 ego-lite？ | 不会。新 Node 在没有明确意图时将 `ego_browser_enabled=false`；已有值原样保留。 | 管理员显式 `--enable-ego-browser`，或已验证的加入码明确声明 `ego_browser_enabled=true`（UI 可显示为 `enabled=true`），并且仅在 artifact、profile、证据和 enrollment policy 校验全部通过后生效。 |
| macOS bootstrap/Bridge 升级要不要重新 Device 注册？ | 不要。升级复用同一 Device ID、签名密钥、加密密钥和 `device_generation`；旧 binding 失效后只需用户确认并创建新的 binding generation。 | 显式 `device-rotate`、key 损坏/删除、Server 撤销、`forget-this-mac`，或切换用户/Server origin 时，才进入重新加入流程。 |
| `EXPECTED_64_HEX_DIGEST` 从哪里来？ | 普通用户不获取、不填写；已批准且签名的 release profile/root manifest 自动提供规范字段 `signer_certificate_sha256`。 | 自定义/自签发布的维护者从已验证 code-signature 叶证书 DER 计算 SHA-256，并通过独立证据链注入 pin。 |

### 0.1 术语边界

| 术语 | 本文中的固定含义 |
| --- | --- |
| ego lite / ego-lite | macOS 上独立安装的官方浏览器运行时；本文正文统一写作 `ego lite`，Bridge 卸载不应删除它。 |
| Bridge | macOS 本机的受管执行进程，负责本地 ego lite 调用和出站 relay。 |
| Device Client | `agent-remote-ego-browser` 提供的独立本机客户端；不指 `agent-remote-device` 产品。 |
| Device identity | Bridge 的长期本机身份：Device ID、签名/加密密钥和 `device_generation`。 |
| Device credential | Server 为 identity 签发的短期凭据；过期可刷新，不等于重新生成 identity。 |
| release profile | 由 root manifest 签名固定制品、版本、证书 pin 和 runtime 的发布记录。 |
| credential profile | 约束 credential 存储/交换方式（例如 file 或 keychain），不决定发布信任。 |
| policy / learning bundle | allowlist、能力集合及其摘要；变更必须触发新的 binding generation。 |
| Node capability | Linux Node 对 wrapper、Skill、runtime 和 ego-browser 能力的经验证明；安装文件不等于已启用。 |
| configured_enabled / effective_enabled | 前者是管理员写入的意图，后者是本地 artifact/profile/evidence 与 enrollment policy 校验后的有效 Node capability；二者都不等于 execution admission。 |
| enrollment | 允许安装、`ensure`、状态查询和 credential 刷新。 |
| execution admission | 允许 claim、relay hello 和 execute 的独立闸门；本文默认指 Server execution admission，现有 `EGO_BROWSER_BRIDGE_ENABLED` 映射到此语义。Bridge 另有独立的 local admission。 |
| enabled | 对外兼容的状态投影：Node 映射为 `effective_enabled`；Bridge 映射为本机功能和 release 已启用。它永远不表示已经可以 execute。 |
| available | “可以开始尝试连接”的资格，而不是执行许可；要求组件、identity、版本、policy 和 Server `execution admission` 均通过，Bridge 的 `local_admission` 仍可在 claim 前保持关闭。 |
| binding admission | 针对某个 `binding_generation` 的 claim、lease 和撤销状态；只有它与 Server/local admission 都通过时才允许 execute。它不计入未连接时的 `available`。 |
| binding generation | 一次远端连接授权的代次；与本机 `device_generation` 完全独立。 |

本文中“官方 installer”只指 ego lite 上游运行时的固定安装包；Bridge/Device Client 的
`community-local-trust` profile 是项目自签、非 Apple notarized、非公开分发 profile。普通用户
仍不需要手工处理其证书 pin，但不能把“已批准”误解为 Apple 或第三方独立背书。

### 0.2 普通用户只需做什么

| 场景 | 用户动作 | 系统自动完成 |
| --- | --- | --- |
| 首次 macOS 使用 | 登录、同意安装/信任、授予 macOS 权限 | 探测版本、校验 release、安装组件、`ensure`、启动服务 |
| 连接远端 session | 从候选列表选一个并确认 full-trust | 取得候选、生成 PoP、claim、保存 handoff、建立 lease |
| 日常恢复 | 执行 `status` 或 `repair` | 分类诊断、刷新短期 credential、修复当前 release/launchd |
| 升级 | 明确执行 `upgrade` 并确认新 release | drain、撤销旧 `binding_generation`、原子切换、保留 Device identity |
| 忘记本机 | 明确执行 `forget-this-mac` | 在线撤销 Device，联网失败时排队，成功后清理本机身份 |

开始前只需满足三个前置条件：当前版本的 `agent-remote` CLI、控制面账号（以及一个 active
Server profile）、可运行 GUI 的 macOS 用户会话；若要执行 `connect`，再准备至少一个已上线且
通过兼容性校验的远端 Node/session。
具体系统版本、网络和权限要求仍以 [`deployment.md`](deployment.md) 与发布 profile 为准；这些
前置条件不应转化为要求用户手工填写的 token、UUID 或 digest。

请区分两次可能出现的确认：`setup` 只确认本机 release/profile 和 macOS 权限；`connect`/`resume`
才确认具体远端 session 的 full-trust 执行风险。前者不会暗示后者已经授权。

推荐阅读路径：普通使用者读第 0、1、5、6 节；实现者再读第 2、3、4、7、8、9 节；发布和
验收人员以第 10、11 节为门槛。第 9 节是对前文的强制收敛，不是可选实现建议。

### 0.3 一页执行卡（目标入口）

> 这是发布后的目标入口示例，不代表当前二进制已经支持。执行前先看对应版本的
> `--help`；未完成 P0-P3 时按第 8 节的兼容入口操作。

普通用户的成功路径不需要手工取得任何 UUID、token、Server URL 或 digest：

```sh
# 一次性前置条件（已登录时跳过）
agent-remote login

# 准备本机；可安全重复执行
agent-remote ego-browser setup

# 连接时只选择候选 session，并确认 full-trust
agent-remote ego-browser connect
```

这里的“不需要 Server URL”是指 `setup` 和后续生命周期命令不再重复询问。首次
`agent-remote login` 若本机还没有组织预置的 Server profile，仍可能需要用户输入一次由
管理员提供的 HTTPS 地址；登录成功后由 credential store 保存并复用，不能让 `setup` 再次要求
用户复制或校验该地址。尚未登录时返回 `login_required`；已有账号但没有 active profile 时返回
`server_profile_required`，并给出明确的登录下一步，而不是猜测默认 Server。

`login` 只建立控制面账号会话和 Server profile；它不替 ego-browser 创建、轮换或撤销 Device
identity。ego-browser 的 Device identity 只由 `setup`/`ensure`（或明确的 rotate/forget 流程）管理，
因此登录凭据变化不应被误认为需要重新注册 Bridge。

日常操作按以下规则选择：

| 目的 | 命令 | 用户唯一决策 |
| --- | --- | --- |
| 查看状态 | `agent-remote ego-browser status` | 无 |
| 修复当前安装 | `agent-remote ego-browser repair` | 需要重新信任/登录时确认一次 |
| 暂停并稍后恢复 | `agent-remote ego-browser pause`，之后 `agent-remote ego-browser resume` | 恢复时再次确认 full-trust |
| 结束当前连接 | `agent-remote ego-browser stop` | 确认结束；之后只能重新 `connect` |
| 升级组件 | `agent-remote ego-browser upgrade` | 是否接受新 release/profile |
| 删除 Bridge 但保留身份 | `agent-remote ego-browser remove` | 有活动连接时确认停止 |
| 撤销并忘记本机 | `agent-remote ego-browser forget-this-mac` | 二次确认不可恢复的身份删除 |

`setup` 失败时只需要按 `error_code` 执行 `next_action`；不要自行补填底层参数。只有
自定义制品、隔离测试或无人值守运维才使用 `--advanced` 入口。

`forget-this-mac` 只有在 Server 返回 revoke 确认后才报告完成；无网络时明确显示
`pending_revocation`，本机保持关闭并暂留 key 以完成后续撤销。

### 0.4 当前版本与目标契约

本文同时作为行为契约和迁移说明。2026-09-12 快照已经落地普通 macOS
生命周期命令（`setup`、`connect`、`repair`、`upgrade`、`remove`、
`forget-this-mac`、`re-enroll`、`device-rotate`、`switch-server`），以及 Server
`ensure`、Node 加入码和 Device Client 的幂等恢复；低层入口仍按兼容规则保留。命令入口
已经存在不等于 P0-P3 已验收：`setup`/`repair` 依赖当前用户已有受签名 Bridge release，
`upgrade` 必须由受管发布流程提供签名归档，缺少这些前置条件时应明确失败而不能静默跳过。
发布包、受管安装器和跨仓库验收证据的具体版本仍以各仓库的帮助文本与签名证据为准。

1. `setup`、`connect`、`ensure`、加入码和自动 digest 发现都视为目标入口；当前版本是否支持，
   以对应仓库发布包的 `--help`、版本兼容表和低层部署手册为准。当前快照中的普通 CLI
   已支持这些生命周期语义；旧版本或未更新的发布包不得仅凭本文假定已支持。
2. 低层 `ego-browser-device`、`scripts/install.sh` 和现有 `EGO_BROWSER_BRIDGE_ENABLED` 仍按
   [`ego-browser-bridge-deployment.md`](ego-browser-bridge-deployment.md) 的参数和顺序执行；本
   文档不会通过改 README 改变旧二进制语义。
3. 兼容入口继续保留一个完整 release 周期，并在输出或发布说明中标明
   `deprecated_entrypoint`；自动化脚本应优先使用新入口，并固定显式的 profile、确认和
   generation 参数。

判断“是否已完成”只能看发布版本、schema、迁移和第 10 节验收证据，不能以本文件中出现了
某条命令为依据。

当前代码与目标入口的差异（2026-09-14 快照）如下；版本升级后应重新以各仓库的
`--help`、schema 和发布记录核对，不要把快照当成永久接口：

| 范围 | 当前兼容行为 | 目标行为 | 迁移要求 |
| --- | --- | --- | --- |
| Node `ego_browser_enabled` | 安装器只有显式 `--enable-ego-browser`/`--disable-ego-browser`，`configure-ego-browser` 只有显式 `--enable`/`--disable` 才改变已有值；缺省值按旧配置逻辑处理，因此不会因组件存在自动开启 | 新 Node 明确落盘 `false`，加入码显式授权才可写入 `true` | 先保留旧配置，再通过受管迁移补齐缺省 `false`；不得把安装器升级误当成启用 |
| Node 受管传输 | `agent-remote node install` 验证 Node archive/checksum/Sigstore，经独立 SSH stdin 安装 release，再通过第二条 SSH stdin 发送 join code；CLI 固定的 Node `0.2.22` 已发布 | 受管 release 仍须由根清单认证，不允许绕过验证或把加入码放入 argv | 部署以已签名根组合为准；未完成认证时继续使用该组合中的稳定 installer，不得把单独发布的组件当作已部署 |
| Device 注册 API | `register` 仍被旧脚本调用 | `POST /api/v1/ego-browser/devices/ensure` 为主，`register` 是同语义兼容别名 | 两条路由共享幂等收敛；新客户端显式发送 enrollment mode |
| digest / token | 兼容 CLI/installer 可能要求 `--signer-certificate-sha256`、Server URL 或 token | 普通 `setup` 从已登录凭据和受保护 stdin/FD 取得 token；release/profile 使用已验证证据 | 旧入口仅限 advanced；profile 或签名变化时仍需重新确认 |
| binding 操作 | 兼容命令可显式传 binding ID 和旧 `generation` | 普通 `pause`/`stop`/`resume` 优先使用本机 active handoff，再用唯一候选或交互选择；内部使用 `binding_generation` 并在动作前复查 Server | 旧参数继续兼容；无 TTY、多候选、代次变化均 fail closed |
| macOS bootstrap | 兼容 bootstrap 可以在同一次运行中登记，甚至按参数 claim 指定 session | `setup` 只准备本机；`connect` 单独列候选并确认 full-trust | 旧 bootstrap 保留一个 release 周期并显式标注 advanced |
| Server 开关 | 旧 `EGO_BROWSER_BRIDGE_ENABLED` 可能同时影响登记和执行 | enrollment 与 execution admission 分离；安装/ensure 不被 execution 开关阻断 | Server、客户端和部署配置继续保持两道独立闸门 |

## 1. 分平台安装与启用规则

### Node 节点

安装 ego-browser 组件和启用 ego-browser 能力是两个不同动作：

```text
安装组件 = wrapper、Skill、broker 和配置文件就绪
启用能力 = 节点开始向新的 Claude session 广告 ego-browser capability
```

Node 只安装远端 wrapper/Skill/broker，不安装 macOS 上的 `ego lite`；真正的浏览器运行时和
Device identity 位于用户自己的 Mac Bridge。因而 Node 安装完成不代表本机 Bridge 已注册，也
不代表已有 session 可以执行。

通用安装器默认只安装并校验组件，不隐式打开能力。新配置没有旧值时，
`ego_browser_enabled` 明确写为 `false`；已有配置则原样保留。这样可以先完成升级和回滚，
再由管理员在确认发布证据后启用。受管的 Node 加入记录可以在管理员明确选择后携带
`ego_browser_enabled=true`；签名 profile 只能约束允许的能力和版本，不能单独把一个关闭的
Node 改成开启。安装器绝不能根据“文件存在”或 profile 可用就自行推断管理员意图。
该字段只接受布尔值；缺失按 `false` 处理，格式错误或与 profile 冲突时返回
`configuration_invalid` 并保持 capability 关闭，不能把非空字符串当成启用。

必须区分两个值：

```text
configured_enabled = 新节点的加入码/显式开关，或已有配置中的原值
effective_enabled  = configured_enabled AND artifact_verified AND profile_match AND release_evidence_verified AND enrollment_policy_allows
node_execution_allowed = effective_enabled AND server_execution_admission
```

`effective_enabled` 表示本地制品和 capability 已经验证；heartbeat 可以报告它，但只有
`node_execution_allowed` 才能向新的 Claude session 广告“可执行”的 ego-browser capability。
`node_execution_allowed` 只是 Node 侧准入，仍需 Device、binding、lease 和 Bridge local admission
才能允许 claim/relay/execute。Server execution admission 关闭时，节点仍可完成 enrollment
和状态上报，但不得广告可执行 capability 或执行远端脚本。加入码的
`ego_browser_enabled=true` 只允许在首次 enrollment，或服务端明确授权的状态变更中写入；普通重装/升级
不能借此把已有节点从关闭改为开启。需要关闭时使用显式 `--disable-ego-browser` 或管理台的
禁用动作，并记录审计事件。

显式 `--enable-ego-browser` 也是事务操作：任何 artifact/profile/evidence 校验失败都只返回
`release_verification_failed`，保留原配置，不写入半启用状态。

因此：

- 只执行普通 Node 安装，新节点默认关闭，旧节点保持原值，不会被意外打开；
- 首次加入码若声明启用，安装器在完成 artifact、profile、证据和 enrollment policy 校验后才设置为启用；
- 升级 wrapper 或 Skill 不改变原有启用状态；
- 启用、禁用或 capability 变更只对新的 Claude session/capability revision 生效；已有 session 不在运行中原地降级；
- 任何 capability、签名 profile 或证据不匹配都 fail closed。

显式禁用仍必须立即阻止新 claim，并按 stop/revoke 流程排空或撤销现有 binding；“不原地降级”
不等于让旧 `binding_generation` 无限期继续执行。

### macOS Bridge

普通用户在完成登录后只需要使用两条生命周期命令：

```sh
agent-remote ego-browser setup
```

`setup` 是幂等的“准备本机”动作：它确保本机组件和本机 Device 身份存在；它不自动升级、
连接或 claim 会话。若未登录，命令只返回 `login_required` 和 `agent-remote login`，
不得要求用户粘贴 token。
需要连接时再执行一个单独、明确的动作：

```sh
agent-remote ego-browser connect
```

用户从带有项目名、工作区、运行状态和后端的候选列表中选择数字，并确认 full-trust。
用户不需要复制 UUID、Server URL、registration token、证书摘要、binding ID 或
generation。

脚本化和旧版本入口继续可用，但只属于 advanced/compatibility API：

```sh
agent-remote ego-browser register [--server-url URL] [--signer-certificate-sha256 HEX]
ego-browser-device register --server URL --token-stdin --signer-certificate-sha256 HEX
agent-remote ego-browser claim TOOL_SESSION_ID [--yes]
```

高层 CLI 的 token 由已登录 credential store 自动取得并通过 stdin/FD 传给 Device Client；
低层示例明确使用 `--token-stdin`。旧版本若没有该能力，必须由兼容 shim 提供受保护的
stdin/FD 通道；不得为了兼容而把 token 放回 argv、环境变量、URL 或日志。新文档和 UI 不把
这些入口作为首选流程。

## 2. 三个生命周期对象

| 对象 | 创建时机 | 升级时行为 | 结束/撤销 |
| --- | --- | --- | --- |
| 组件（Bridge、Device Client、wrapper、Skill） | 安装或升级 | 原子切换 release，保留旧 release | `remove` 删除组件，ego lite 不受影响 |
| 本机身份（Device key + Device ID + `device_generation`） | 本机首次 `ensure` | 在未明确 rotate/revoke 前复用，不因版本变化重建 | 只有 `forget-this-mac`（本机）或 `device-revoke`（Server/Admin）明确撤销 |
| 远端连接（Binding + `binding_generation`） | 用户选择 session 并确认 | 暂停旧 `binding_generation`，健康检查后由用户恢复新代次 | stop/pause/revoke；不回滚已经产生的副作用 |

这三个对象不能混为一个“注册”按钮。尤其是“升级组件”绝不等价于“新建 Device”。
`device_generation` 只表示本机密钥代次；Binding 的 `generation` 只表示一次远端连接
授权代次，两者不能互相替代。

协议命名也必须保持这个区分：注册请求中的旧字段 `generation` 语义等同于
`device_generation`；Binding 的 claim/renew/pause/resume 请求中的 `generation` 语义等同于
`binding_generation`。新 schema 应使用显式字段名，兼容旧 schema 时必须按 endpoint 上下文
解释，不能把两种代次混存或互换。

| 请求上下文 | 旧字段 | 目标字段 | 分配者 |
| --- | --- | --- | --- |
| Device `register`/`ensure` | `generation` | `device_generation` | Device identity rotation（客户端提出，Server 校验） |
| Binding claim/connect/renew/pause/resume/stop | `generation` | `binding_generation` | Server binding lifecycle |

兼容层可以继续接收旧字段，但进入内部模型后必须立即转换为目标字段，并在响应、日志和
持久化中保持分开；不能仅靠一个通用 `generation` 字段跨对象传递。

身份变更的结果固定如下：

| 动作 | Device ID | key | `device_generation` | 现有 binding/credential |
| --- | --- | --- | --- | --- |
| `setup` / 普通升级 / `repair` | 不变 | 不变 | 不变 | 按需刷新 credential；旧 binding 不自动恢复 |
| `device-rotate` | 不变 | 新 key | 递增 1 | 全部 live binding 和旧 credential 失效 |
| `forget-this-mac` 后重新加入 | 新 ID | 新 key | 从 1 开始 | 旧 Device 已撤销，不得迁移 |
| `switch-server` 或切换用户 | 不跨 origin/用户复用 | 新 origin/用户独立 identity | 新 identity 的代次 | 旧 origin 先撤销；最多保留加密、不可执行的回滚元数据 |

“重新注册”在本文中只表示后三类需要用户明确同意的恢复流程；credential 刷新或新的
binding generation 都不算重新注册 Device。

## 3. 参数所有权

普通运行期只保留三个授权决策：

1. 是否接受本机 project-self-signed/full-trust 风险；
2. 要连接哪个明确的远端 Claude session；
3. 是否确认这次 full-trust claim/resume。

下面的交互边界是固定的：

| 操作 | 必须询问 | 不得询问 |
| --- | --- | --- |
| `setup` | 首次安装 ego lite、首次 release/profile 信任、macOS 权限 | Server URL、Device ID、证书摘要、control-plane/Node token |
| `connect` / `resume` | 具体 session/binding 和 full-trust 确认 | binding ID、`binding_generation`、PoP challenge |
| `repair` / credential refresh | 仅在需要时重新登录或重新信任 | 重新生成 Device key |
| `upgrade` | 目标 release 及证书/profile 变化的信任确认 | 重新注册 Device |
| `remove` | 是否停止当前执行（有活动 binding 时） | 是否删除 ego lite（默认不删除） |
| `forget-this-mac` | 明确确认“撤销并删除本机身份” | 在未确认时清理 key |

首次使用仍可能需要一次登录、安装 ego lite 的确认和 macOS 权限授予；这些是安装前置条件，
不属于每次连接都要重新填写的内部参数。证书或 release profile 变化时必须重新显示本机信任
确认，不能沿用旧确认静默通过。

以下值由发布物、已登录 CLI 或本机状态自动提供：

| 内部值 | 自动来源 | 普通用户界面 |
| --- | --- | --- |
| Server URL | `agent-remote` 登录配置 | 不要求输入 |
| control-plane login credential | CLI credential store，通过受保护 stdin/FD 传递 | 不显示、不进 argv |
| Node token | Server 在 join-code exchange 后签发/绑定，或已有 Node 状态 | 不显示、不进 argv |
| Device credential | `ensure` 响应中的短期 credential，按 profile 存入 Keychain/加密文件 | 不显示、不要求复制 |
| Device ID 和私钥 | owner-only 本机状态 | 不要求输入 |
| wrapper/Skill/runtime 版本 | signed release profile | 只显示兼容/不兼容 |
| `signer_certificate_sha256`（旧示例名 `EXPECTED_64_HEX_DIGEST`） | signed manifest 或内置 trust root | 不要求输入 |
| binding ID、`binding_generation`、sequence | 控制面和本机 handoff | 普通输出显示短状态，不显示原始值 |
| ego-browser 可执行路径 | PATH、ego lite app bundle、受管默认路径 | 自动探测 |

Server origin 进入本机状态前必须规范化为唯一 HTTPS origin（无隐式路径、重定向或备用主机）；
显式 `--server-url` 只能用于 advanced 校验，且必须与登录配置/profile 允许的 origin 完全一致。
仅 `development_local`/`logic_test` profile 可以显式允许 loopback HTTP，且不得与 production
credential 或 release 混用。
若 credential store 中存在多个账号或 Server profile，`login` 负责选定一个 active profile；
`setup` 只能使用该 active profile，发现歧义时要求一次明确选择，不能把同一 Device identity
跨账号复用。

`--advanced`、`--json` 和诊断日志可以按权限显示完整或脱敏后的标识，但不能显示 token、私钥、
脚本正文、页面内容、Cookie 或 relay ciphertext。

`agent-remote login` 的刷新凭据继续由现有 CLI credential store 管理；`setup`/`ensure` 只在
内存或受保护 FD 中短暂使用用户凭据，并在 Device credential 交换完成后立即释放。任何本机
状态文件、join code、URL、systemd/launchd 参数和崩溃转储都不得包含该凭据。

## 4. Device ensure 契约

### 4.1 命令语义

Device Client 的普通注册入口采用 `ensure` 语义；`register` 保留为兼容别名。服务端的
规范接口为 `POST /api/v1/ego-browser/devices/ensure`，现有
`POST /api/v1/ego-browser/devices/register` 委托到同一实现并继续兼容旧客户端：

两条 endpoint 必须接受现有注册 payload（公钥、加密公钥、`device_generation`、release/profile、
runtime、policy、capabilities 和 Device PoP 字段），只新增幂等语义，不得通过删除字段制造“新协议”。客户端
为一次 identity enrollment 生成一个不可预测的 `Idempotency-Key`，把它写入 pending 状态，
并在重试时原样复用；它与用于日志追踪的 `x-request-id` 不是同一个值，也不能用 Device ID
代替。Server 应按 `(user, logical_operation=device.ensure, Idempotency-Key)` 原子记录请求指纹和结果，
因此 canonical `ensure` 与兼容 `register` 共享同一幂等空间：相同 key 与
相同 payload 重试必须收敛到同一 Device，key 与 payload 不同则返回冲突。credential 的原始
值只在受保护的短期交换记录中可恢复，不能写入日志或普通业务表。
幂等 key 只是重复提交控制，不是授权凭据；每次请求仍必须通过用户认证、TLS、Device PoP 和
origin/profile 校验，Server 只保存 key 的 hash 或受保护引用。
pending 清理完成后的普通 `ensure` 可以生成新的幂等 key；无论 key 是否变化，都必须先按
Device ID/公钥/`device_generation` 做 identity 收敛，不能把“新 key”解释成“新设备”。显式
`device-rotate` 使用独立的 `logical_operation=device.rotate` 和独立幂等 key，绝不能复用
`device.ensure` 的 pending 或响应缓存。
交换记录的保留期不得短于客户端允许保留 pending 的时间。即使交换记录已过期，Server 也必须
先按 Device ID、公钥和 `device_generation` 查找并收敛到已有 identity，再单独签发新的 credential；
不能因为幂等记录过期就创建第二个 Device。
若实现不保存可恢复的原始 credential，则必须提供同一 identity PoP 保护的 recovery/refresh
分支来完成收敛；返回“已存在”而不提供可行动恢复也不算完成 ensure 契约。

最小字段的所有权固定如下；具体编码可以沿用旧 schema，但不能改变字段语义：

| 字段/头 | 请求 | 响应 | 负责方与约束 |
| --- | --- | --- | --- |
| `device_id` | 必填 | 必返 | Device 首次生成；Server 校验归属且全局唯一 |
| `device_generation` | 必填 | 必返 | Device identity 代次；仅显式 rotate 递增 |
| `signing_public_key` / `encryption_public_key` | 必填 | 必返 | 私钥只在本机；响应必须与请求一致 |
| `release_profile` / `policy_digest` / `capability_digest` | 必填 | 必返 | 来自已验证 profile；Server 不接受用户临时拼装 |
| `Device-PoP` | 必填 | 不回显 | 绑定一次性 challenge、origin 和完整 canonical payload |
| `Idempotency-Key` | 必填 HTTP header（至少 128 bit 随机） | 可返回 hash/引用 | 仅控制重复提交，不是授权凭据；不得用 Device ID 代替 |
| `server_origin` / `status` | 可选（按旧协议） | 必返 | Server 返回规范化 origin 和 `active`/错误状态 |
| `credential` | 不发送明文旧值 | 成功时必返 | 只含短期值、`credential_revision`、`credential_expires_at`、`credential_scope` |

请求和响应都必须带可脱敏的 `request_id` 供追踪；它与 `Idempotency-Key`、Device ID 和
`device_generation` 永远不是同一个字段。

```text
ensure:
  有合法本机 identity -> 复用相同 Device ID、签名密钥、加密密钥和 device_generation
  没有 identity       -> 首次生成并持久化一个 identity
  credential 过期     -> 使用已认证用户凭据刷新 credential，不生成新 Device
  key 损坏/Device revoked -> 返回可行动错误，要求显式 recovery 或 forget-this-mac

  binding generation -> 只由 claim/resume 的服务端生命周期分配；ensure 不创建或恢复 binding
```

首次 identity 必须在本机生成随机 Device ID（UUIDv4 或等价格式，至少 120 bit CSPRNG entropy，
不可从用户名、主机名或路径推导）、
Ed25519 签名 key 和 X25519 加密 key；私钥永不上传，Server 只保存公钥和必要 metadata。
`device_generation` 初始为 `1`，只在显式同设备轮换时递增；普通 credential refresh 不改变它。

首次 enrollment 和已有 identity 的 refresh 都使用已登录用户会话与一次性 Device PoP
challenge；challenge 过期时只重新申请 challenge，不重新生成 identity。ensure 的成功响应
至少必须包含 `device_id`、`device_generation`、两把公钥、`status=active`、release/profile、
policy/capability 摘要和短期 credential（含明确命名的 `credential_revision`、
`credential_expires_at` 和 `credential_scope`）。响应不得再使用无上下文的 `generation` 字段；
若旧客户端必须接收该字段，兼容层只能把它解释为 `device_generation`，并在内部立即改名。

| 结果 | 固定处理 |
| --- | --- |
| 成功（新建或复用） | 严格校验响应，原子保存 credential，清理 pending；两种情况都返回同一 Device identity。 |
| 网络超时/响应丢失 | 保留 pending，使用同一 identity、同一 `Idempotency-Key` 重试；不得生成第二把 key。 |
| `login_required` / PoP 失败 | 仅提示重新登录或重试 challenge；不删除 key，不自动 rotate。 |
| `device_conflict` / `device_generation_conflict` | 关闭 local admission，显示冲突对象和 `switch-server`/`forget-this-mac` 下一步。 |
| profile/policy 不兼容 | 返回 `compatibility_mismatch`，只允许 `repair`/`upgrade` 或显式重新信任。 |
| Server 暂不可用 | 返回 `server_unreachable`，保留全部 pending 状态，稍后可安全重试。 |

网络重试使用有上限的指数退避（例如 1、2、4、8 秒后停止本次命令），只重试 idempotent 的
`ensure`/状态交换；不得自动重试 claim、resume、脚本执行或任何结果未知的高风险动作。

`ensure` 必须在本机注册锁和服务端的 `(user_id, device_id)` 互斥锁下执行。Device 尚未
存在时不能只依赖行锁；实现应使用用户行锁、数据库 advisory lock 或等价的原子
insert-conflict/reload 方案。网络超时后重试同一个 identity 和同一个幂等请求，不能因为
没有收到响应就重新生成随机 Device ID。所有“读状态、生成/恢复 pending、交换 credential、
清理 pending”的步骤都在同一份本机锁保护下完成；拿不到锁时返回 `local_lock_busy`，不能
绕过锁并行注册。Device ID 在 Server 侧必须全局唯一；已属于其他用户或 origin 时返回
`device_conflict`，不能通过覆盖公钥“接管”该记录。

首次生成 identity 时，必须先把 `device_id`、`device_generation`、key 文件校验值、Server
origin、release profile 和一个幂等请求标识写入 owner-only 的 pending-registration 状态，
再发起网络请求。只有完整响应校验通过、credential 原子落盘后，才能清除 pending 状态。
这样即使进程在服务端成功后崩溃，下一次 `ensure` 仍能重试同一个 Device。

本地 credential 仍在有效期且距离过期超过可配置的 refresh skew（默认 5 分钟）时，
`ensure` 不得无谓地轮换 credential；缺失、即将过期或已过期时才使用已登录用户凭据刷新。

普通 `ensure` 要求本地 profile 与 Server 记录完全一致。签名 profile 的升级迁移是唯一例外：
只能由显式 `upgrade` 携带 `replaces_profile`、双 pin/信任证明和新的 policy，先使旧 binding
`binding_generation` 失效，再在保留同一 Device identity 的前提下更新 Server metadata。
任意手工修改 profile 都必须返回 `compatibility_mismatch`。

服务端两个入口都必须接受同一 Device ID 的幂等请求；客户端必须提交并校验服务端返回的
相同公钥、profile、policy、`device_generation` 和 Server origin。响应只在 credential
revision 前进且字段完全匹配时落盘。用户、Server origin、Device ID 或 profile 不匹配时
必须返回可行动错误，不能把它当作首次注册。

### 4.2 本地状态

本机状态目录仍为 owner-only：

```text
~/.config/agent-remote-ego-browser/
  ego-browser-device-key.bin       # Device ID、私钥和 device generation
  ego-browser-pending-registration.json # 首次注册或崩溃恢复的幂等状态
  ego-browser-pending-rotation.bin # device-rotate 的下一代 key（未提交前保留）
  ego-browser-pending-revocation.json # 卸载或断网时待提交的撤销操作
  ego-browser-credential.json      # 短期 relay credential
  ego-browser-policy.json          # allowlist / learning policy
  ego-browser-active-binding.json  # 最近一次明确 claim 的 handoff
  ego-browser-trust.json            # 本机 profile/pin 信任确认记录
  .ego-browser-registration.lock   # 跨进程 ensure 锁
```

上面是逻辑状态名，不要求用户手工创建或迁移文件。`credential` 在 macOS 优先存入当前用户
Keychain；`community_file` 等 profile 若必须使用文件，则使用 profile 规定的加密/权限方案和
`0600` owner-only 文件。路径、文件名和存储后端都由安装器决定，不能成为普通安装参数。

所有文件和父目录必须由当前 macOS 用户拥有，文件权限默认 `0600`、目录默认 `0700`，并拒绝
符号链接和非普通文件。`ego-browser-pending-registration.json` 至少持久化 schema version、
Device ID、key 引用/校验值、Server origin、release profile、`device_generation`、
`idempotency_key`（发送时映射为 `Idempotency-Key`）、创建时间和最近错误码；不得保存用户
token、脚本或页面内容。key 文件格式
或相邻的 owner-only identity metadata 必须持久化 Device ID、Server origin、release profile
和 `device_generation`；不能只靠短期 credential 反推出本机身份。
`pending_revocation` 至少保存撤销范围 `scope`（`binding` 或 `device`）、Device ID、
`device_generation`、撤销原因、操作 ID、目标 `binding_generation`、重试次数和下一次重试时间；
`scope=binding` 用于 `remove`/停止活动连接并保留 Device，`scope=device` 用于
`forget-this-mac`/`switch-server`。它同样不得保存原始 token 或脚本内容。
`pending-rotation` 必须保存下一代 key 的完整加密材料或安全引用、目标 `device_generation`、
操作幂等 key、旧 identity 校验值和轮换前的 `previous_credential_revision`；只有新代次成功提交后
才能删除旧 key/handoff。若恢复时只剩 rotation metadata，当前 credential revision 必须严格大于
该源 revision 才能完成清理；旧 credential 不得被误判为轮换结果。

升级不得删除上述状态。状态缺失时才允许首次生成；状态不一致时必须停止并给出修复
建议，不能静默“自愈”为另一个 Device。pending-registration、key、credential 和服务端
记录必须按第 9 节的恢复矩阵处理。pending-registration 的重试窗口默认 24 小时（可配置）；
过期只会变成 `pending_expired` 并要求用户确认下一步，不得自动删除 key 或新建第二个 Device。
`pending_revocation`（落盘文件为 `ego-browser-pending-revocation.json`）直到 Server 确认前都必须保留，
并使用有界退避重试。

## 5. 推荐流程

四条主路径的入口和终点固定如下：

| 路径 | 入口 | 关键步骤 | 成功终点 |
| --- | --- | --- | --- |
| 首次 Node 部署 | `agent-remote node install --node NODE_REFERENCE` | 传输脚本与 join code、校验 artifact/profile、写入配置、启动服务 | Node `installed`，并按显式意图成为 `enabled` 或保持关闭 |
| 首次 macOS 部署 | `agent-remote ego-browser setup` | 检测/安装 ego lite、信任确认、安装 Bridge、`ensure`、启动服务 | Bridge `installed + registered`，Server/local admission 仍由策略决定 |
| 连接 | `agent-remote ego-browser connect` | 列候选、用户选择、显示 full-trust、PoP claim、健康检查 | 一个明确的 `connected` binding |
| 升级/修复 | `upgrade` 或 `repair` | 预检、drain/修复、原子切换、状态校验 | 当前 identity 保留；需要连接时由用户显式 `resume` |

实现时只允许以下主状态转移；错误分支回到安全状态，不得跨步“自愈”：

```text
setup:   absent -> preflight -> profile_verified -> installed -> ensuring -> registered -> ready
connect: ready -> candidates -> selected -> trust_confirmed -> claiming -> connected
pause:   connected -> pausing -> paused
resume:  paused -> trust_confirmed -> resuming -> connected (new binding_generation)
stop:    connected/paused -> stopping -> stopped (terminal; connect again)
remove:  any local state -> stop/revoke live binding -> admission_closed -> pending_revocation(binding)/revoked -> removed (identity retained)
forget:  any local state -> admission_closed -> pending_revocation(device)/revoked -> identity_deleted
rotate:  registered (no active binding) -> pending_rotation -> rotated (same Device ID, next device_generation)
switch:  registered/ready/paused/stopped -> admission_closed -> pending_revocation(device)/old_revoked -> new_origin_identity (old identity never migrated)
```

`pause` 是可恢复状态：它保留 Device identity 和 binding 记录，但暂停旧 `binding_generation`；
`resume` 必须创建新的 `binding_generation`。`stop` 是当前 binding 的终态，旧 `binding_generation`
不得恢复，后续必须重新执行 `connect`。升级在 drain 成功时可以把连接置为 `paused`，
但升级命令本身绝不自动 `resume`；drain 或结果确认失败时进入 `stopped`/`admission_closed`，
只能重新连接。

`pending_revocation` 不是成功状态：它表示本机已关闭 local admission，但 Server 尚未确认撤销。
必须同时显示撤销范围（`binding` 或 `device`）。在该状态下禁止 `connect`、`resume` 或创建
新 identity；只有收到 Server 的 `revoked` 确认后，`remove` 才能报告完成（identity 保留），
`forget-this-mac`/`switch-server` 才能进入下一步。进程重启后继续同一撤销操作，不得另起一条
并行撤销。
如果 `remove` 时没有 live binding，只需关闭 local admission 并清理 Bridge/短期 credential，
可以跳过 `scope=binding` 的网络撤销；`forget-this-mac` 和 `switch-server` 的
`scope=device` 撤销仍必须得到 Server 确认。

任何 `unknown_result`、校验失败或用户取消都只能进入 `admission_closed`、`paused` 或
`pending_revocation` 等可审计状态；不能自动跳到 `connected` 或重新执行原脚本。重复提交同一
生命周期动作必须返回当前终态或安全的进行中状态，不能重复产生 key、binding 或 Node token。

### 5.1 首次 Node 部署

管理员在控制面生成一次性、短期的 Node 加入码。加入码绑定 Server、Node、版本 profile
和是否启用 ego-browser 能力（不等于是否下载 ego lite runtime）。普通入口由已登录管理员 CLI
在控制工作站发起：CLI 解析 Node 引用，
自动调用受保护的 issue 接口取得加入码，并通过已有 SSH/受管传输把安装脚本和加入码分别送到
目标 Linux Node；用户不需要在 Mac 和 Node 之间手工复制 token。直接在 Node 上执行安装器，
或从管理台复制 code 再手工传入，都属于 advanced 入口。加入码不得放进 URL、环境变量、
shell history 或进程参数。目标接口如下：

CLI/管理台生成加入码时默认选择当前批准的 release profile、Node 的现有运行后端和
`ego_browser_enabled=false`；只有管理员主动打开“启用 ego-browser”后才写入 `true`。版本、
artifact digest、Server URL 和长期 Node token 均由 profile/Server 自动填充，界面不要求逐项
输入。普通 CLI 不接受 `--join-code`、`--token` 或 `--digest` 参数；这些只存在于 advanced
兼容入口。

```sh
agent-remote node install --node NODE_REFERENCE
```

交互式终端可以省略 `--node`，由 CLI 列出候选并让管理员选择；非 TTY 或自动化调用必须提供
管理台名称或唯一短 ID。多个匹配时必须让管理员选择，不能凭列表顺序猜测。SSH/受管传输凭据
沿用现有 agent-remote 配置，加入码不作为命令行参数。

该命令在内部使用独立的脚本通道和 stdin/FD 加入码通道；若必须使用底层安装器，
目标 Node 只接受 `agent-remote-node install --join-code-stdin`，加入码由控制工作站
通过受保护的 SSH stdin 传入。加入码的字段、生命周期和重放规则见第 9 节。若 issue 或
传输中断，CLI 必须用同一个 `exchange_id` 恢复，不得要求用户重新复制 code。

安装器自动完成依赖、wrapper、Skill、systemd、heartbeat 和 capability 配置；安装/升级受管
runtime 后可自动运行 `configure-ego-browser`，但该同步动作必须保留现有
`ego_browser_enabled`。加入码从独立的
stdin/FD 读取，不进入 shell history 或进程参数。没有加入码时保留现有显式 `--enable-ego-browser`
兼容入口。

| 安装输入 | 配置结果 | capability 结果 |
| --- | --- | --- |
| 新 Node，无 `--enable`、无加入码 | 写入 `ego_browser_enabled=false` | 不广告 ego-browser |
| 已有 Node，无显式状态变更 | 保留原 `ego_browser_enabled` | 仅在 artifact/profile/evidence 全部匹配时广告 |
| 新 Node，加入码 `ego_browser_enabled=true` | 写入 `true` | 校验通过后广告；Server execution admission 仍可单独关闭 |
| 任意 Node，显式 `--disable` | 写入 `false` | 阻止新的 capability/session，并按策略结束现有 binding |

同一 Node 的重跑安装/升级应复用已有 Node token、配置和 capability revision；已消费的 join
code 不能再次换发 token。若安装中断，先按 `exchange_id` 恢复原交换结果，再继续安装，不要
重新生成 Node 或覆盖现有配置。

### 5.2 首次 macOS 部署

```sh
agent-remote login
agent-remote ego-browser setup
agent-remote ego-browser connect
```

`setup` 的顺序固定为：

1. 预检 Server 是否支持目标 `ensure`、enrollment 和 execution admission 语义；Server 明确
   返回不支持时返回 `server_capability_unavailable`，不创建 identity；仅网络超时时仍可完成
   已缓存且已验证 profile 对应的本地制品安装，并把 `ensure` 留在 pending 状态；没有可验证
   的缓存时不得绕过 profile 校验下载或安装；
2. 获取并验证 signed release profile/root manifest、来源、版本、artifact 摘要、证书 pin 和
   ego-lite installer 的 commit/SHA-256；未通过验证时返回 `release_verification_failed`，
   不运行任何下载脚本；
3. 检测 ego lite；缺失时在用户明确同意后运行 profile 固定且已验证的官方 installer，
   不能执行未经验证的 `curl | sh`，也不能追踪浮动的 `main` 或 `latest`；
4. 等待 GUI onboarding，并明确提示用户完成 macOS 权限授予；
5. 验证本地 runtime 版本，原子安装 Bridge/Device Client 和 launchd agent；
6. 执行幂等 `ensure`；
7. 输出组件、身份和服务状态，但不自动 claim session，也不在已有已验证版本时隐式升级。

`setup` 的返回阶段必须可区分：

| 结果 | 本地组件 | Device identity | 用户下一步 |
| --- | --- | --- | --- |
| `ready` | 已验证并启动 | 已注册或可刷新 | 若 `available=true` 才执行 `connect`；否则先处理 admission/error |
| `installed_pending_registration` | 已验证并启动 | pending，尚未得到 credential | 稍后重试 `setup`，不删除 key |
| `trust_confirmation_required` | 未越过信任门槛 | 不创建/不上传 | 在本机确认 profile 后重试 |
| `server_capability_unavailable` | 可保留已验证安装 | 不创建 identity | 升级 Server/客户端组合 |

ego lite 探测顺序固定为：受管安装路径、已知官方 app bundle、最后才是 `PATH`。找到多个
兼容实例时优先受管路径；仍有歧义就列出版本和路径让用户选择，不能静默选“最新”。只有
没有兼容实例时才建议安装；已有实例版本过低或来源不可信时进入显式 `upgrade`/重新信任，
不能被 `repair` 强行覆盖。

Bridge release 使用不可变目录和原子指针：`releases/<version>/` 只读保存已验证制品，
`current` 一次性切换到新目录，并保留至少一个可回滚的旧目录。任何覆盖当前目录、先删后装或
在未完成验证时重启 launchd 都视为安装失败。

任一步骤被用户取消、校验失败或网络超时，都必须保留可恢复的安装状态并关闭本机
local admission；重复执行 `setup` 从上一次安全边界继续，不得清理 key、猜测 session 或回退到
未签名制品。runtime、release profile 或本机信任尚未通过前，不创建或上传 Device identity；
只有进入 `ensure` 阶段后才写入 pending identity，且该 pending 必须按第 4 节规则恢复。
检测到未完成的 `pending_revocation` 时，`setup` 只能显示撤销进度并等待确认，不能重新启用
或创建新的 binding。

`connect` 才会查询候选 session、让用户选择并显示 full-trust 警告。没有候选、候选
过期或 Server 返回未知状态时，命令失败并保持本机 local admission 关闭。若目标已是当前
active binding，`connect` 只返回已连接状态；若本机已有另一个 active binding，必须返回
`binding_conflict` 并要求先 `pause`/`stop`，不能静默切换。Server execution admission 关闭
时必须返回 `admission_disabled`，不能伪装成空候选列表。

候选列表每项至少显示脱敏短 ID、项目名、工作区、后端、session 运行状态、最近心跳和能力
兼容结果；完整 UUID 仅在 `--advanced --json` 中显示。用户选择的索引必须在 claim 前重新向
Server 校验，候选已过期、状态改变或 capability 不匹配都返回 `candidate_stale`，不能把索引
对应到另一条 session。

claim/resume 前的 full-trust 确认必须明确显示四点：代码以当前 macOS 用户身份运行；可访问
ego lite 的全部 tabs/Task Spaces、登录态与 cookies、用户可读文件、网络和子进程；停止操作
不能撤销已经产生的浏览器/文件/网络副作用；恶意或脱离 supervisor 的同 UID 进程可能无法被
清理。用户取消时返回 `confirmation_required`，不得以默认同意或超时继续。

### 5.3 日常状态和修复

```sh
agent-remote ego-browser status
agent-remote ego-browser repair
agent-remote ego-browser pause
agent-remote ego-browser resume
agent-remote ego-browser stop
agent-remote ego-browser remove
agent-remote ego-browser forget-this-mac
```

普通状态的默认摘要仍使用三行；详情页和 `--json` 再展示五个机器状态及其错误原因：

```text
本机运行时：正常
本机身份：已注册
远端连接：项目名 / 工作区 · 已连接
```

机器接口保留 `installed`、`enabled`、`registered`、`available`、`connected` 五个正交状态；
其中 `enabled` 是平台相关的兼容投影，`available` 只表示“可以开始尝试连接”。普通 UI
将它们合并成以下可理解的阶段，避免把“已安装”误报为“可执行”：

Server 不可达时，`status` 可以展示本地最近状态，但必须标记为 `unknown/server_unreachable`，
不能把缓存的 `connected` 当作当前可执行，也不能在离线状态自动 claim、resume 或 rotate。

| 用户看到的阶段 | 机器状态摘要 | 下一步 |
| --- | --- | --- |
| 未安装 | `installed=false` | 执行 `setup` |
| 已安装，待登记 | `installed=true`、`registered=false` | 登录后重试 `setup`/`ensure` |
| 已登记，未启用 | `registered=true`、`enabled=false` | Node 由管理员显式启用 capability；Bridge 检查本机 release/profile |
| 已启用但不可用 | `enabled=true`、`available=false` | 查看稳定 `error_code`，执行 `repair` 或等待对应 admission |
| 已启用，待连接 | `enabled=true`、`available=true`、`connected=false` | 执行 `connect` |
| 已连接 | `connected=true` 且 lease 健康 | 正常使用或执行 `pause/stop` |
| 状态未知 | Server 不可达或本机状态未完成校验 | 先恢复网络并执行 `status`；禁止执行高风险动作 |

“已登记，未启用”主要用于 Node capability；macOS Bridge 若组件已安装但尚未通过本机
profile/trust 校验，应显示为“已安装但不可用”并给出 `trust_confirmation_required` 或
`compatibility_mismatch`，不要把 Bridge 的安装状态伪装成 Node 的开关状态。

缺失组件、过期 credential、Bridge 未启动、版本不兼容和 policy drift 由 `repair` 分类
处理；repair 默认修复当前已选 release、重新取得同一 signed profile、刷新 credential 或重建
launchd 状态，不改变版本。它不能静默替换 signed profile、改变 allowlist 或降低 policy；若
profile/digest/policy 发生变化，必须转入显式
`upgrade`/重新信任流程。显式 `upgrade` 才选择新 release。repair 不得自动 claim/takeover，
也不得删除 Device key。

## 6. 升级、回滚和重新注册

### 6.1 正常升级

正常升级包括 Bridge、Device Client、Node wrapper/Skill 和 ego lite runtime 的兼容升级；
`setup` 不负责隐式升级，runtime 的版本变化只能由显式 `upgrade` 触发并再次取得必要确认。
这里的 bootstrap 只是下载/安装编排器，不是 Device identity。bootstrap 可以安全重跑以修复
缺失文件，但不应被当作日常升级命令，也不得因为重跑就重新生成 identity。
行为必须是：

1. 暂停新请求并 drain 当前受管执行；drain 成功时把 binding 标记为 `paused`，否则进入
   `stopped`/`admission_closed`；
2. 使旧 ticket、permit 和旧 `binding_generation` 不可用；
3. 校验签名 profile 后安装新 release 并原子切换 `current`；
4. 保留本机 Device ID、私钥、Server origin 和 policy；
5. 健康检查通过后显示“可恢复上次连接”；这只是提示，不是自动恢复；
6. 用户选择 `resume` 时由服务端签发新的 `binding_generation`；若旧 binding 已进入
   `stopped`，则必须重新执行 `connect`；
7. 不创建新 Device，不要求重新 Device 注册。

| 升级对象 | 推荐入口 | 是否重新 Device 注册 | 是否需要新的 binding generation |
| --- | --- | --- | --- |
| Bridge / Device Client | `agent-remote ego-browser upgrade` | 否 | 是（恢复连接时） |
| ego lite runtime | `upgrade` 编排的官方固定版本 installer（仅高层入口；底层 Bridge installer 不触碰它） | 否 | 是（runtime/profile 变化时） |
| Node wrapper / Skill | Node 的显式 release upgrade | 否 | 现有 binding 按策略 drain/revoke；新 session/capability revision 使用新能力 |
| 证书/profile | 双 pin + 显式信任确认 | 通常否 | 是；旧 `binding_generation` 先失效 |
| allowlist / learning policy | 签名 policy 的显式更新 | 否 | 是；旧 `binding_generation` 不得继续执行 |

因此，直接升级 installer 和 `agent-remote ego-browser upgrade` 都不需要重新注册 Device。
这个结论的前提是升级保留 owner-only 的 Device key、origin metadata 和 `device_generation`；
如果运维脚本删除了这些状态，或用户主动执行了 `forget-this-mac`，那已经不是“普通升级”，
必须按第 6.2 节的显式恢复流程处理。
升级失败时保留原 `current` release、identity 和 policy；只有新 release 完成签名、版本和健康
检查后才能切换。升级后的“可恢复上次连接”只是提示，不是自动 resume。
旧版 bootstrap 若仍调用 `register`，其内部也必须遵守 `ensure` 语义，不能产生重复 Device。

### 6.2 需要新 key 或显式重新加入的情况

只有以下情况允许创建新密钥或新的 Device 记录：

- 用户明确执行 `device-rotate`（服务端保留同一 Device ID，并递增 `device_generation`）；
- 本机私钥损坏或被删除，且用户完成显式遗忘/撤销后重新加入；
- 服务端明确将 Device 标记为 revoked，且用户完成显式遗忘/重新加入；
- 用户执行 `forget-this-mac` 后重新加入；
- 用户明确执行 `switch-server` 或切换登录用户（新 origin/用户必须使用独立 Device identity）。

release profile/证书轮换通常只要求一次性重新信任、双 pin 窗口和新的 binding generation，
不应因此自动创建新 Device；只有发布策略明确要求 key rotation 时才适用上面的新密钥流程。

证书轮换不应通过覆盖环境变量静默完成，必须走双 pin 窗口、安装确认和新的 `binding_generation`。

`device-rotate` 的固定顺序是：取得本机锁并验证旧 key 的 PoP，生成同一 Device ID 的下一代
key，先写 owner-only pending-rotation，再向 Server 提交新公钥/`device_generation`，确认旧
binding/credential 已失效后原子切换本机 identity，最后清理 pending 和旧 handoff。任一步骤
崩溃都必须沿用 pending 中的同一新 key 重试；`device_generation` 不能回退，也不能在未确认旧
key 权限的情况下自动 rotate。pending metadata 必须固定轮换前的 credential revision；即使目标
key 已安装且 pending key 已清理，credential revision 未严格推进时也必须返回冲突并保留恢复状态。

私钥损坏或 Device revoked 时，`device-rotate` 不得假设旧 key 仍可用于 PoP；恢复流程应先
通过已登录用户凭据撤销/遗忘旧记录，再生成新的 pending identity。Server origin 或登录用户
发生变化时也必须停止并要求显式 `switch-server`/`forget-this-mac`，不能把旧 Device 迁移给
另一个用户。`switch-server` 的默认顺序是：关闭当前 local admission，停止并撤销旧 origin
的 live binding/credential，等待旧 Device 撤销确认，再为新 origin/用户建立独立 identity。
旧 origin 只能保留为加密、不可执行的回滚元数据；不得保留可用 credential、active binding
或可被新 origin 上传的旧 key。旧 Server 不可达时停在 `pending_revocation(scope=device)`，不创建新 identity；
可由旧 Server 的管理员先完成 revoke，再回到本机重试 `switch-server`。不提供“先建立新身份、
以后再撤销旧身份”的普通或 advanced 旁路。

## 7. digest 和 trust root

`EXPECTED_64_HEX_DIGEST` 是文档示例中的占位符；实际字段名为
`signer_certificate_sha256`。它是发布签名证书的 SHA-256 指纹，不是用户设备、Bridge
归档或 learning bundle 的摘要。证书摘要的规范算法是：从已验证的 code signature 提取
叶证书的 DER 原始字节，对该文件执行 SHA-256，输出 64 个小写十六进制字符（256 bit），且不带冒号或
`sha256:` 前缀。归档摘要和 learning bundle 摘要必须使用各自独立的字段，不能互换。

名称只在边界处做映射，内部统一使用 `signer_certificate_sha256`：

| 位置 | 规范名称/来源 | 谁负责填写 |
| --- | --- | --- |
| 旧文档/示例 | `EXPECTED_64_HEX_DIGEST` | 仅作迁移提示，不作为 schema 字段 |
| Bridge release manifest | `signer_certificate_sha256` | 发布流水线从已验证签名得到 |
| Bridge 构建环境 | `SIGNER_CERTIFICATE_SHA256` | 发布维护者注入并与 manifest 比对 |
| CI release variable | `COMMUNITY_SIGNER_CERTIFICATE_SHA256` | 受保护的发布环境提供；不向终端用户暴露 |
| 兼容 CLI 参数 | `--signer-certificate-sha256`（旧 installer 也可能叫 `--certificate-sha256`） | 仅 advanced/custom release |
| Bridge 运行时环境 | `EGO_BROWSER_SIGNER_CERTIFICATE_SHA256` | 由已验证 profile 渲染，已批准 profile 拒绝用户覆盖 |
| Server 运行配置 | `EGO_BROWSER_EXPECTED_SIGNER_CERTIFICATE_SHA256` | 从已批准 root manifest/profile 渲染 |
| 本机安装后的 pin | `TRUSTED_CERTIFICATE_SHA256` | 安装器验证完成后原子写入 |

查值时优先读取已批准的 root distribution manifest 中
`components.agent-remote-ego-browser.signer_certificate_sha256`（或 Bridge 包内经验证的
`SIGNING-EVIDENCE.json`）；这两个来源必须相互一致。不要从未验证的 GitHub Release 页面、
当前机器上任意二进制或用户提供的字符串直接复制 pin。

维护者只需从已验证的仓库根 manifest 读取规范字段即可（命令输出应再通过 schema 校验）：

以下命令在 `agent-remote` 仓库根目录执行；部署机没有仓库副本时，应由发布流水线把同一
已验证字段注入 profile，而不是让部署人员从本机二进制反推。

```sh
jq -er '
  .components["agent-remote-ego-browser"].signer_certificate_sha256
  | select(type == "string" and test("^[0-9a-f]{64}$"))
' release-manifest.json
```

`-e` 和 `select(...)` 会让缺字段、`null` 或格式错误直接返回非零；这说明发布证据不完整，
不要用本机旧安装的 pin 填补。

维护者在 macOS 上计算 digest 的可复现步骤（普通用户不执行）：

```sh
set -eu
SIGNED_BINARY="/path/to/verified/ego-browser-bridge"
CERT_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ego-browser-cert.XXXXXX")"
trap 'rm -f -- "$CERT_DIR"/cert-*; rmdir "$CERT_DIR"' EXIT
CERT_PREFIX="$CERT_DIR/cert-"
codesign --verify --strict "$SIGNED_BINARY"
codesign --display --extract-certificates="$CERT_PREFIX" "$SIGNED_BINARY"
DIGEST="$(shasum -a 256 "${CERT_PREFIX}0" | awk '{print tolower($1)}')"
printf '%s\n' "$DIGEST" | grep -Eq '^[0-9a-f]{64}$'
printf '%s\n' "$DIGEST"
```

输出必须经过小写化和 64 字符校验；`0` 文件必须是 leaf certificate。临时目录由 `trap`
在命令结束时清理，避免证书文件遗留。Bridge、Device Client
和 learning-bundle verifier 的签名证书应逐一验证并得到同一 pin。若需要验证发布物本身，
另行对归档执行 `shasum -a 256`，不得把归档结果填入证书 pin。任何手工计算结果都必须回到
root manifest、Sigstore evidence 和发布审计记录中，不能只改环境变量。`development_local`
或 `logic_test` 可以在完全隔离的合成数据测试中使用 `development` sentinel；
`community-local-trust`、`developer_id` 及任何生产 profile 必须使用 64 个小写十六进制字符，
不得把 sentinel 晋级到生产。

受管 release 的首次信任必须遵循固定链路：

1. bootstrap 或 root distribution manifest 通过内置 root trust 验证；
2. root manifest 固定 Bridge release manifest、版本、归档摘要和
   `signer_certificate_sha256`；
3. Bridge release manifest、Sigstore evidence、归档和嵌套签名全部验证；
4. 安装成功后才把已验证的 pin 写入 `TRUSTED_CERTIFICATE_SHA256`。

下载到的 Bridge manifest 不能单独成为自己的 trust root；不能先读取其中的 pin，再用该
pin 验证同一份 manifest。

当前 community profile 的 pin 由 root release manifest 和 bootstrap trust root 维护；
受管安装路径不得要求用户设置 `SIGNER_CERTIFICATE_SHA256`、
`EGO_BROWSER_EXPECTED_SIGNER_CERTIFICATE_SHA256` 或 `TRUSTED_CERTIFICATE_SHA256`，也不要求
用户通过 `openssl`、`codesign` 或 GitHub 页面自行计算。自定义仓库/自签发布属于 advanced
流程，必须显式指定 pin、提供独立的发布证据并接受首次本地信任确认。

### 7.1 signed release profile 的最小内容

`release_profile` 不是一个可以自由填写的字符串，而是由 root manifest 选定的不可变 profile
记录。实现至少要能从它得到以下字段：

```text
profile_id, profile_version, bridge_version, bridge_protocol_version,
ego_lite_runtime_version, wrapper_version, skill_version,
artifact_url, artifact_sha256, bridge_manifest_sha256,
signer_certificate_sha256, learning_bundle_digest,
ego_lite_installer_url, ego_lite_installer_commit, ego_lite_installer_sha256,
valid_platforms, allowed_server_origins, admission_policy_ref,
issued_at, replaces_profile
```

profile 本身必须带有 root 可验证的签名；下载地址、版本、归档摘要和证书 pin 任一变化都要
生成新的 profile/version，并重新触发本机信任确认。客户端只接受与本地平台、Server origin、
运行时和 policy 完全匹配的 profile；不能让用户在命令行逐项拼装这些字段，也不能把 profile
中的任意 URL 当作新的 trust root。

## 8. 兼容性和迁移

| 旧入口 | 兼容行为 | 新入口 |
| --- | --- | --- |
| `scripts/install.sh --server --token` | 继续工作；升级后的兼容层把 token 转入受保护 stdin/FD，旧二进制按其既有参数规则运行且标记为 advanced | `agent-remote ego-browser setup` |
| `installer/install-macos.sh` / 旧 bootstrap | 可以作为低层修复入口重跑，但必须保留 Device key、credential 目录和 origin metadata；不得把重跑当成重新注册 | `setup`（准备）或 `upgrade`（换版本） |
| `ego-browser-device register` | 作为 `ensure` 别名；已有 key 必须复用；返回同一 identity | `ego-browser-device ensure` |
| `--signer-certificate-sha256` | 接受但不再必需；已批准 profile 自动填充 | 无需输入 |
| `--session-id ID --confirm-full-trust` | 继续支持脚本化 claim | `agent-remote ego-browser connect` |
| `configure-ego-browser --enable/--disable` | 保留管理员显式开关并记录审计 | 加入码 profile 的 `ego_browser_enabled` 字段（仅首次 enrollment 或授权状态变更） |

迁移期间必须明确区分“当前兼容入口”和“目标入口”：旧版直接 installer/register 可能仍要求
显式证书 pin、Server URL 或 token；只有 `setup`/`connect` 及对应版本的 Device Client/CLI
发布后，受管流程才可以省略这些参数。不能仅更新 README 的命令示例，就宣称旧二进制已经
支持新语义。旧二进制若只能从 argv 读取 token，不得作为生产默认路径；必须先由兼容 shim
改为 stdin/FD，或明确限制在隔离的人工维护环境。

迁移顺序：先发布服务端兼容 `ensure` 的 API，再发布 Device Client/CLI，再更新 bootstrap，
最后在管理台启用加入码和候选选择器。每一步都必须能与上一个版本互通；不能先删除旧
注册接口或先改变默认 capability。迁移完成后，旧入口至少保留一个完整 release 周期，并在
弃用时返回明确的 `deprecated_entrypoint` 指引；不得把旧 `register` 直接改成“每次生成新 key”。

过渡期的开关行为也要固定：旧 Server 只有单一 `EGO_BROWSER_BRIDGE_ENABLED` 时，旧客户端
继续遵循旧语义；新 Server 拆分后，该开关只控制 execution admission，`ensure` 在
`enrollment enabled` 时仍可成功。新客户端遇到旧 Server 的“功能未发布”响应时应返回
`server_capability_unavailable` 并指向兼容版本，不能自行把开关改为 `true` 或降级为未验证
的执行路径。

## 9. 实施附录：不可变决策

> 普通用户可以跳过本节。它把前文的产品意图收敛为实现时不得自行改变的决定；若底层安全
> 文档有更严格的约束，采用更严格者；除此之外，所有仓库都按本节实现。

### 9.1 统一状态定义

| 状态 | 判定条件 | 主要来源 | 是否允许 execute |
| --- | --- | --- | --- |
| `installed` | 本地 release、manifest、签名和文件权限验证通过，`current` 指向该 release | 本机安装器 | 否，单独安装不代表可用 |
| `enabled` | Node: `configured_enabled=true` 且 artifact、profile、版本和证据校验通过；Bridge: 本机功能和当前 release 已启用；两者都不把 Server 全局开关混入此状态 | Node 配置/Bridge 本机状态 + signed profile | 否，仍需 execution admission |
| `registered` | 本机 identity 存在，Server Device 为 active；credential 即使过期也必须可通过登录凭据刷新 | Device Client + Server | 否 |
| `available` | `installed`、`enabled`、runtime/profile/policy 兼容、服务健康、Device active，且 Server execution admission 允许；Bridge 的 supervisor 已就绪，但 `local_admission` 在 claim 前仍保持关闭 | Bridge、Node、Server | 否，必须先建立 `connected` binding |
| `connected` | 存在用户明确确认的 live binding，`binding_generation` 和 lease 均有效且健康，local/server admission 仍允许执行 | Binding + relay | 是 |

为避免不同组件各自实现出不同结果，统一判定式为：

```text
available = installed
  AND enabled
  AND registered
  AND runtime/profile/policy healthy
  AND server_execution_admission
  AND local_admission_ready

connected = available
  AND binding_admission
  AND active binding
  AND healthy lease
  AND local_admission
```

这里的 `local_admission_ready` 是“claim 成功后可以打开本机闸门”，而不是已经打开；Node
没有独立 Bridge 时由 Node broker/service health 等价提供，`local_admission` 则指同一 broker
在 binding 建立后的执行闸门。`ready` 只是 `setup` 的一次命令
结果，表示本机已准备好继续检查 `available`，不是第五个持久机器状态。

有效能力必须同时满足：

```text
Node capability = verified artifact AND explicit enabled intent AND compatible server profile AND release evidence AND enrollment policy
Bridge execute = connected
```

因此 `available` 的判定使用 `local_admission_ready`，而 `execute` 的判定才使用
`local_admission`；把两者都命名成 `available=true` 或把 local admission 在 claim 前提前打开，
都属于状态实现错误。对 Node 没有本机 Bridge 时，`local_admission_ready` 由 Node broker/service
health 等价表示。

公式中的布尔值必须按同一口径计算：

| 值 | 判定 |
| --- | --- |
| `artifact_verified` | 归档摘要、文件 inventory、嵌套签名和权限全部通过；缺任一项即为 false。 |
| `profile_match` | 本地平台、Bridge/Skill/runtime 版本、protocol、policy digest 和 Server origin 均与 signed profile 相符。 |
| `release_evidence_verified` | root manifest、Sigstore/provenance、证书 pin 和必要 canary 证据均通过。 |
| `enrollment_policy_allows` | 当前用户、Node、Server origin 和 capability 均被 enrollment policy 允许；不等于 execution admission。 |
| `server_execution_admission` | Server 全局开关和用户/Node/Device 策略均允许执行。 |
| `binding_admission` | 当前 `binding_generation` 已由用户确认并处于可执行状态，lease、sequence 和 revoke 检查均通过。 |
| `local_admission_ready` | Bridge supervisor、runtime 和本机 trust 已就绪，可以在 claim 成功后打开 local admission；它不等于已经打开。 |
| `local_admission` | 已存在经过确认的 binding、有效 lease 和 runtime health，Bridge 当前允许执行。 |

join profile 不能绕过 Server 的全局 release evidence、enrollment/execution admission gate 或用户权限。组件已安装、
Device 已注册和 capability 已启用必须在 CLI、Admin 和 API 中分别展示。`configured_enabled`、
`enabled`、`available` 和 `connected` 不能用一个布尔字段互相代替。

### 9.2 命令行为和默认选择

| 命令 | 普通行为 | 不得隐式做的事 |
| --- | --- | --- |
| `setup` | 缺少组件时安装；校验现有组件；执行 `ensure`；启动本机服务；可安全重复执行 | 不自动升级、不 claim、不 takeover、不重建 identity |
| `connect` | 列出候选、用户选定一个、显示 full-trust 警告并确认后 claim | 不选第一项/最近项；已有 active binding 时不静默切换 |
| `status` | 只读展示五种统一状态和可行动错误 | 不刷新策略、不创建 Device、不改变 binding |
| `repair` | 修复当前 release、launchd、credential 和 policy drift | 不改变版本、不 claim、不删除 key |
| `upgrade` | 选择并验证新 release，原子切换 `current`，保留 identity | 不重新注册 Device、不复用旧 ticket/`binding_generation` |
| `pause` | 作用于当前 active handoff；暂停当前 `binding_generation`，保留可恢复记录 | 不执行脚本、不自动 resume |
| `stop` | 作用于当前 active handoff；终止并撤销当前 `binding_generation` | 不把 stopped binding 当作可 resume；不凭历史记录猜测目标 |
| `resume` | 作用于明确的 paused binding，重新显示 full-trust 警告并签发新的 `binding_generation` | 不用旧 `binding_generation` 直接恢复 |
| `remove` | 停止本机 agent，停止/撤销 live binding，删除 Bridge 组件和短期 credential；默认保留 Device key、policy、trust 和 origin metadata 以便重装复用 | 不删除 ego lite，不保留可执行的 active binding，不撤销可复用的 Device identity |
| `forget-this-mac` | 先在线撤销 Server Device，再删除 key、credential、policy 和 handoff | Server 不可达时不先删除本地 key |
| `re-enroll`（恢复模式） | 在 key 完整且用户确认时，用原 identity 重新建立缺失的 Server Device | 不得在 key 损坏、Device revoked 或 origin 不匹配时自动执行 |
| `device-rotate` | 在没有 active binding 且旧 identity 仍可证明时显式轮换 key，保留 Device ID 并递增 `device_generation` | 不得在 key 损坏或 Device revoked 时伪装成普通修复；有 active binding 时先 `stop` |
| `switch-server` | 显式确认后关闭当前 local admission，先停止/撤销旧 origin，再为新 origin/用户建立独立 identity；旧状态最多保留为加密、不可执行的回滚元数据 | 不得把旧 Device、key、credential 或 active binding 自动迁移给另一用户 |

`pause`、`stop`、`resume` 的默认目标解析顺序固定为：本机 active handoff；仅一个可操作候选；
交互式候选选择。多个候选且没有用户选择时必须失败；没有 active/paused binding 时返回
`no_active_binding`，不能拿历史记录猜测目标。`resume` 只接受 `paused` binding，`stop` 成功
后该 binding 永久不可 resume。`--binding`、`--generation` 和完整 ID 只属于 advanced/脚本化入口。
对仍有活动执行的 `stop`，交互式 CLI 必须先显示影响并要求一次确认；没有活动 binding 时保持
幂等且不要求确认。`pause` 不终止已产生的副作用，`resume` 则始终重新显示 full-trust 确认。
新接口应分别使用 `--device-generation`（ensure/rotate）和 `--binding-generation`
（claim/pause/resume/stop）；旧 `--generation` 只在 endpoint 上下文明确时兼容解析，不能在
同一请求或日志字段中混用。

`device-rotate`、`switch-server` 和 `forget-this-mac` 都是破坏性 identity 操作，默认必须
二次确认并显示影响范围；`--yes` 只允许 advanced 调用。`switch-server` 若保留旧 origin 的
回滚信息，必须加密且标记为 disabled，不保留可用 credential 或 active binding，并提供显式
清理动作。旧 origin 撤销尚未确认时，`switch-server` 必须返回 `pending_revocation`，不能
悄悄在新 origin 建立第二个可执行身份。

检测到非 TTY 时，普通命令不得隐式选择候选或等待不可见的确认；应返回
`confirmation_required`/`binding_conflict`，并给出可复制但已脱敏的下一步。只有 advanced
调用同时提供精确 ID、`--yes` 和已验证的当前 profile 时，才允许无交互执行。

`remove` 与 `forget-this-mac` 必须是两个不同动作。`forget` 只能作为
`forget-this-mac` 的无歧义短别名，不能指代 `remove`。若卸载时 Server 暂时不可达，本机应立即
关闭 local admission，按撤销范围写入 owner-only 的 pending revocation，禁止重新 claim，待联网后完成撤销；
不能留下一个 Server 认为 active 而本机已失去监管的 binding。撤销请求必须带当前
`device_generation`/expected `binding_generation`，重复提交可安全收敛。离线时命令返回
`pending_revocation`（而不是成功），并显示 `scope=binding` 或 `scope=device`。`scope=binding`
（`remove`）可以在撤销请求已持久化后删除 Bridge 组件和短期 credential，但必须保留 Device key、
policy、trust/origin metadata 以及完成重试所需的最小 pending 记录；`scope=device`
（`forget-this-mac`/`switch-server`）则必须保留完成撤销所需的 key/credential，直到 Server 确认
`revoked`，随后才删除 identity、credential、policy 和 handoff。进程重启或再次执行
`forget-this-mac` 必须继续同一 pending 操作。
`remove --remove-releases` 只能额外删除 Bridge 的旧 release 目录，仍不得触碰 ego lite、
Device identity 或浏览器 profile；该选项属于 advanced 维护入口。Server 已返回 revoked 但本地
清理尚未完成时，重复执行只做幂等清理，不重新发送 enrollment 或生成新 key。

用户可用这张最小对照表判断影响范围：

| 动作 | Bridge/ego-browser 组件 | Device identity | 远端 binding |
| --- | --- | --- | --- |
| `pause` | 保留 | 保留 | 暂停当前 `binding_generation`，可显式 `resume` |
| `stop` | 保留 | 保留 | 终止当前 `binding_generation`；需重新 `connect`，不能用旧代次 `resume` |
| `remove` | 删除 Bridge 组件，可选清理 release | 保留 | 停止/撤销，不可执行 |
| `forget-this-mac` | 可同时删除 Bridge 组件 | Server 撤销后删除 | 全部撤销，不可恢复 |

`forget-this-mac` 删除的是本机可用 identity 和 credential，不等于物理删除 Server 审计/历史
记录；后者仍按 Server retention 和管理员的独立清理策略处理。

所有命令的失败输出必须同时给出稳定的 `error_code`、当前状态和一个下一步动作；JSON 输出
使用同样的字段结构并只包含脱敏 ID。网络暂时不可达、需要用户确认、信任不匹配和 identity
损坏必须能被 CLI 与 Admin 区分，不能统一显示为“注册失败”。

公共 CLI/API 至少固定以下错误码（内部 HTTP/数据库错误必须映射到这些稳定码）：

错误响应的最小结构为：

```json
{
  "error_code": "admission_disabled",
  "state": {"installed": true, "enabled": true, "registered": true, "available": false, "connected": false},
  "capability": {"configured_enabled": true, "effective_enabled": true, "node_execution_allowed": false},
  "admission": {"enrollment": "allowed", "server_execution": "denied", "binding": "not_established", "local": "ready", "reason": "server"},
  "stale": false,
  "checked_at": "2026-09-12T00:00:00Z",
  "next_action": "request_execution_admission",
  "next_command": null,
  "request_id": "req_..."
}
```

`request_id` 只用于追踪；`state` 中的 ID 必须短化或省略，响应不得包含 token、key、脚本或页面
内容。`admission.reason` 使用有限集合（`release`、`profile`、`policy`、`server`、`local`、
`binding`、`login`），不能把内部异常或 URL 原文透传。`stale=true` 时只表示展示的是最近
缓存状态，不能据此允许 claim/execute。`next_action` 是稳定的机器枚举，`next_command` 仅在
确实安全且不含秘密时提供命令提示；CLI 再按语言把它渲染成可读文本。CLI 文本输出应表达同样的
error、当前状态和下一步三项信息，不能只打印底层异常字符串。

| `error_code` | 是否可自动重试 | 用户下一步 |
| --- | --- | --- |
| `login_required` | 否 | 执行 `agent-remote login` |
| `server_profile_required` | 否 | 执行一次 `agent-remote login`，按提示提供管理员的 HTTPS 地址；登录后不再重复输入 |
| `trust_confirmation_required` | 否 | 查看并确认当前 profile/pin |
| `ego_lite_missing` | 否 | 在 `setup` 中同意安装官方 runtime |
| `release_verification_failed` | 否 | 使用受信 release，不能强制继续 |
| `configuration_invalid` | 否 | 执行 `repair` 或请管理员修正受管配置；不要手工把字符串改成布尔值 |
| `server_unreachable` | 是（退避） | 保留 pending，稍后重试 `status`/`setup` |
| `pending_revocation` | 是（联网后） | 保持本机关闭，等待撤销确认；不要重新 claim |
| `local_lock_busy` | 是（短暂退避） | 等待另一份本机操作完成，不要并行运行 `ensure` |
| `pending_expired` | 否 | 重新确认 re-enroll 或执行 `forget-this-mac` |
| `admission_disabled` | 否 | 查看是 Server 还是 local admission，等待管理员放行或执行 `repair`/`resume` |
| `server_capability_unavailable` | 否 | 升级到支持 enrollment/execution 分离的 Server/客户端组合 |
| `device_not_found` | 否 | 选择显式 re-enroll 或 `forget-this-mac` |
| `device_conflict` | 否 | 校验登录用户、Server origin 和现有 key；必要时执行 `switch-server`/forget |
| `device_generation_conflict` | 否 | 检查是否有并发 rotate；恢复 pending-rotation 或显式 forget/rejoin |
| `device_revoked` | 否 | 执行显式 forget/rejoin |
| `identity_corrupt` | 否 | 停止执行，备份诊断后显式 forget/rejoin |
| `identity_origin_conflict` | 否 | 执行 `switch-server` 或 forget，不能迁移 key |
| `compatibility_mismatch` | 否 | 执行 `repair`/`upgrade` 或重新信任 |
| `no_session_candidate` | 否 | 启动/授权一个可用远端 session 后重试 |
| `no_active_binding` | 否 | 先执行 `connect`；`resume` 需要存在 `paused` binding |
| `candidate_stale` | 否 | 重新获取候选列表并重新选择 |
| `binding_conflict` / `binding_generation_stale` | 否 | 查看当前 binding，明确选择 pause/stop/resume |
| `confirmation_required` | 否 | 在本机确认具体 session 和 full-trust |
| `node_not_found` | 否 | 检查 Node 是否在线或选择正确的 Node |
| `node_ambiguous` | 否 | 从候选列表明确选择一个 Node，再重试 |
| `join_code_issue_denied` | 否 | 检查管理员权限、Server origin 和 release policy |
| `transport_unavailable` | 是（退避） | 修复 SSH/受管传输后重试同一 `exchange_id` |
| `join_code_expired` / `join_code_replayed` | 否 | 生成新的加入码 |
| `unknown_result` | 否 | 先查询状态；禁止自动重放脚本或 claim |

`trust_confirmation_required` 只用于首次或变更 release/profile 的本机信任；
`confirmation_required` 用于具体 binding 的 full-trust、resume 或破坏性 identity 操作。
两者都必须在非 TTY 环境直接失败并返回 `next_action`，不能退化为等待输入或默认同意。
旧客户端返回的 `generation_stale` 只允许在 binding endpoint 上映射为
`binding_generation_stale`；Device endpoint 的代次冲突必须映射为
`device_generation_conflict`。

### 9.3 本机授权和管理台边界

| 动作 | 本机 CLI/Device Client | Admin Web |
| --- | --- | --- |
| 安装、检测 ego lite、修复 launchd | 必须由本机执行 | 只能展示状态或提供本机命令/deep link |
| `ensure`、`device-rotate`、`forget-this-mac` | 必须由本机 key 和本地用户确认 | 不能代签 |
| `connect`、`resume` | 必须由本机 Device Client 发起 PoP，并显示 full-trust 确认 | 可创建待处理请求或显示结果，不能绕过本机确认 |
| 查看设备和 binding | 可读 | 可读，按用户/管理员权限过滤 |
| 生成、撤销 Node join code | 可选 | 管理员操作并审计 |
| 停止或撤销 Server binding | 可执行 | 管理员可执行，必须携带 expected `binding_generation`；不能代替本机清理或 full-trust 确认 |

例行 `ensure`/credential refresh 在同一已信任 profile、同一本机用户和同一 origin 下不重复弹窗；
只有首次信任、profile/pin 变化或显式的 rotate/forget/switch 等破坏性动作才需要再次确认。
`connect` 与 `resume` 的远端 full-trust 确认不适用该复用规则，每次新建 binding 都必须显示。

本机信任确认按 `(release_profile, signer_certificate_sha256)` 绑定保存；同一 profile/pin 的
后续 setup 可以复用该确认。证书、profile 或本机用户变化时确认失效。每次新建 binding 和
resume 都必须重新确认 full-trust；`--yes` 只允许用于 advanced 脚本化调用，并且必须同时
提供精确、已校验的 session/binding 标识，不能让脚本用“最近一个”作为目标。

### 9.4 ensure 的崩溃恢复矩阵

| 本机状态 | Server 状态 | 固定处理 |
| --- | --- | --- |
| 无 key、无 pending、无 credential | 无 Device | 在锁内生成 identity，先写 pending，再发起首次 ensure |
| 有 pending identity | 未知或有同 Device | 使用 pending 中的同一 Device ID、key 和幂等请求重试；成功后再清理 pending |
| 有 key、有效 credential | active Device | 直接使用；超过 refresh skew 才刷新 |
| 有 key、credential 缺失/即将过期/已过期 | active Device | 要求已登录用户凭据，调用 ensure 刷新 credential，不生成新 key |
| 有 key、credential 缺失 | Device 不存在但 pending 存在 | 先恢复 pending，不生成第二个 Device |
| 有 key、credential 缺失且无 pending | Device 记录不存在 | 返回 `device_not_found`；默认使用原 identity 显式 re-enroll，或由用户选择 forget 后生成新 identity |
| key 或 pending 损坏 | 任意 | 返回 `identity_corrupt`，关闭 local admission；要求显式 forget/rejoin，不静默自愈 |
| key 有效 | Device revoked | 返回 `device_revoked`；只能显式 forget/rejoin，不能自动 rotate |
| key/credential 对应其他用户或 Server origin | 任意 | 返回 `identity_origin_conflict`，要求显式 switch/forget |
| profile、digest、runtime 或 policy 不匹配 | Device active | 返回 `compatibility_mismatch`，只允许 repair/upgrade，不创建新 Device |

ensure 的固定顺序是：获取本机锁，读取并校验状态，准备或恢复 pending identity，调用
幂等 Server endpoint，严格校验响应，原子写入 credential，最后清理 pending。Server 对
`(user_id, device_id)` 使用可锁定的父行/用户行、advisory lock 或等价机制；单纯锁一个不存在
的 Device 行不算完成。相同幂等请求可以安全重试，不同 key、用户、origin 或 profile 的请求必须
冲突失败。若本地已保存 credential 但 pending 文件仍在，先验证 credential revision 和
identity 完整匹配，再清理 pending；若验证失败则回到 `identity_corrupt`，不得覆盖现有 key。

`re-enroll` 是 `setup` 在 `device_not_found` 分支中提供的恢复模式，默认先展示“保留本机
key 并重新建立 Server 记录”的影响，再要求确认；它不是普通 `ensure` 的隐式 fallback。
若用户选择生成新身份，必须先完成 `forget-this-mac`（或等价的 Server revoke）并得到确认。
若本机 key 已损坏而无法完成 PoP，`forget-this-mac` 必须转为已登录用户/管理员授权的
Server-side revoke：先让用户从其设备列表确认目标，再清理本机文件；不能凭本机路径或模糊
名称猜测要撤销的 Device。

### 9.5 Node join code 协议

规范实现采用“至少 128 bit 随机的一次性 code + Server 端 enrollment record”，不把长期 Node
token 或完整配置直接放入 code。code 只作为短期交换凭据；enrollment record 至少包含：

```text
code_id, node_id, server_origin, release_profile,
wrapper_version, skill_version, runtime_version,
artifact_digest, profile_digest, ego_browser_enabled,
issued_at, expires_at, consumed_at, issuer_user_id, exchange_id
```

release profile、artifact 和 digest 仍由独立签名发布链验证；join code 的 Server 记录只表达
这次 Node enrollment 的目标和授权范围，不能替代发布签名。记录中的
`ego_browser_enabled` 是 `configured_enabled` 的管理员意图字段，不是对“当前可执行”的
承诺；`effective_enabled` 必须由 Node 在本地重新计算并上报。
管理台/API 的简化字段 `enabled` 只映射到该 intent；落盘和 heartbeat 继续使用明确的
`ego_browser_enabled`/`effective_enabled` 字段，避免把用户界面状态与执行准入混为一谈。

规则固定为：

1. 管理员在控制面生成 code；默认有效期 15 分钟，最长不得超过 30 分钟；Server 只保存 code
   的 hash 和元数据，并记录生成、消费、过期和撤销审计事件。界面只显示一次 code，不能在
   列表、日志或审计详情中回显原文。用户丢失 code 时只能撤销并重新签发，不能查询原文。
   过期判断以 Server 时间为准，客户端时钟不能延长有效期。
2. 推荐入口是在已登录控制工作站运行 `agent-remote node install --node NODE_REFERENCE`；
   CLI 解析 Node 引用，先为这次交换生成并持久化 `exchange_id`，再通过既有 SSH/受管传输
   分别发送安装脚本和 code。`exchange_id` 只保存在控制工作站的 owner-only 临时状态中，
   交换完成或撤销后清理。目标 Node 的底层入口为 `agent-remote-node install --join-code-stdin`。
3. 脚本内容和 code 必须使用不同的 stdin/FD 或文件通道；code 不得进入 URL、argv、环境变量、
   shell history 或日志。
4. Server 以 CAS 原子消费 code；客户端为一次交换生成并持久化不可预测的 `exchange_id`，
   网络响应丢失时，同一 `exchange_id` 可以取回同一交换结果，其他 exchange 或第二次消费
   一律拒绝。`exchange_id` 不等同于日志用的 `x-request-id`。
5. code 中的 `ego_browser_enabled=true` 只能表达管理员意图，仍须通过 artifact、signed
   profile、Node capability 和 Server enrollment policy 校验后才生效；execution admission
   仍独立控制是否可以执行。对已有 Node，普通 install
   只保留原配置；只有带有明确状态变更授权且通过审计的 code 才能改变该值。
6. 旧 registration token 继续兼容，但新 UI 不再要求用户手工复制；join code 不能替代
   Server 的 Node token、TLS 或现有权限检查。它只在交换阶段替代人工传递：Server 验证 code
   后签发/绑定现有长期 Node token，Node 随后按原协议保存并使用该 token；join code 本身不得
   被当作长期凭据。

普通 `agent-remote node install` 的可观察流程只有“选择 Node、确认安装、等待结果”：CLI 在
控制工作站生成 `exchange_id`，向 Server 申请 code，立即通过受保护通道完成一次交换，并在
成功或明确失败后清理本地临时状态。code 原文默认不回显给用户；只有 advanced/manual 模式
才允许显示一次并要求操作者自行把它写入 `--join-code-stdin`。这样既保留离线/分权运维能力，
又不会让普通用户承担 code、token 或 digest 的复制责任。

### 9.6 enrollment 与 execution admission

安装和身份登记必须能在 Server execution admission 关闭时完成，否则无法安全地先安装、再验收、
最后启用。现有 `EGO_BROWSER_BRIDGE_ENABLED` 语义映射为 Server execution admission；不要用它阻断
本机 setup/ensure。Server 至少要区分两个语义：

```text
enrollment enabled  -> 允许 ensure、状态查询和 credential 刷新
server execution admission -> 允许 claim、relay hello 和 execute
binding admission -> 某个 binding_generation 的 claim/lease/revoke 检查通过
local admission -> Bridge 本机 supervisor 是否允许启动/继续受管执行
```

Node/Bridge 安装器不得自行写入或翻转 `EGO_BROWSER_BRIDGE_ENABLED`；该开关只由 Server 管理员
按发布门禁控制。它也不等价于 Node 的 `ego_browser_enabled`，更不等价于某个 binding 已连接。

`server_execution_admission` 是全局/主体级闸门，不包含某个 binding 的 lease；
`binding_admission` 只在 claim 成功后建立，并在 pause、stop、lease 超时或 revoke 时关闭。
因此 `available=true` 可以表示“允许开始 claim”，而 `connected=true` 才表示“当前 binding
可以执行”。

接口与闸门的对应关系固定为：

| 操作 | 需要 enrollment | 需要 execution admission | 需要本机用户确认/PoP |
| --- | --- | --- | --- |
| 安装、artifact/profile 校验 | 否（可离线） | 否 | 首次信任时需要 |
| `ensure`、credential refresh | 是 | 否 | 已登录用户凭据 + Device PoP |
| 状态查询、候选列表 | 是（或等价的只读登录权限） | 否 | 否；不改变状态 |
| claim/connect、resume | 是 | 是 | 是；本机 PoP + full-trust |
| relay hello、execute、lease renew | 是 | 是 | Device PoP/有效 binding |
| revoke/forget | 控制面可达即可（不依赖 execution admission） | 否（撤销优先于执行） | 本机 key 或管理员权限；有 binding 时带 expected `binding_generation`，设备撤销带 `device_generation` |

本机 `status` 在没有 enrollment 或网络时仍可返回本地安装、信任和服务信息，但必须把远端
字段标记为 `unknown`/`stale`；候选列表、Device active 状态和 credential refresh 需要
enrollment 及相应的只读登录权限。这样“能查看本机状态”不会被误解为“可以执行”。

release evidence、用户权限、Node capability、Device 状态或本机 runtime 任一不满足时，
该 Device/binding 的 Server execution admission 和 local admission 都保持关闭；关闭任一 admission
不应删除已存在的 Device identity。全局 Server 开关只由管理员按发布门禁控制。所有 API、
CLI 和 Admin 状态都必须返回五个机器状态，并映射到第 5.3 节的用户阶段；至少要能区分
“未安装”“已安装待登记”“已登记未启用”“已启用但不可用”“已启用待连接”和“已连接”。

### 9.7 默认值与可配置边界

下面的值是普通流程的固定默认值；实现可以在 signed profile 或 Server policy 中提高安全性，
但不能在 CLI 中让用户临时降低它们。任何调整都必须带 schema/profile 版本和验收证据。

| 项目 | 默认值/上限 | 普通用户是否可改 |
| --- | --- | --- |
| Node join code 有效期 | 15 分钟，绝不超过 30 分钟 | 否；管理员只能在上限内由策略缩短 |
| `ensure` pending 保留窗口 | 24 小时 | 否；运维策略可缩短但不得静默删除 |
| credential refresh skew | 到期前 5 分钟开始刷新 | 否；由 profile/policy 统一下发 |
| `ensure` 重试退避 | 1、2、4、8 秒后结束本次命令 | 否；后台重试也必须有界 |
| Bridge release 回滚 | 至少保留一个已验证旧 release | 否；清理属于 advanced `--remove-releases` |
| 无 TTY 的确认 | 直接返回 `confirmation_required`，不默认同意 | 否 |
| 连接并发 | 本机同一时刻最多一个 active binding | 否；多 binding 需显式产品决策和新协议 |

credential TTL、lease TTL、并发数等底层运行参数继续由已批准 release profile 管理；它们不应
暴露成要求普通用户填写的安装变量，也不能因本地环境变量被静默放宽。

下列细节由对应仓库在 schema/profile 中固定，不由普通用户决定；在实现前必须写入发布记录并
补充跨仓库测试，不能以“实现自行选择”作为长期状态：

| 实现细节 | 负责方 | 约束 |
| --- | --- | --- |
| HTTP 状态码、序列化和 API 版本 | Server + Device Client | 错误语义必须映射到本文稳定 `error_code` |
| join code 编码和显示分组 | Server + CLI/Admin | 至少 128 bit 随机；普通路径不回显、不进 argv |
| 本机目录、launchd label 和 IPC socket 名称 | Device Client/Bridge | 由安装器生成，owner-only，不能成为用户输入 |
| credential/lease TTL 与 refresh skew | signed release profile + Server policy | 只能收紧，变更必须触发 profile/version 和验收 |
| artifact URL、installer commit 和回滚目录布局 | 发布流水线 + Bridge installer | 必须由 root manifest 固定，不能追踪浮动地址 |

### 9.8 跨仓库归属

| 仓库 | 必须交付 |
| --- | --- |
| `agent-remote-server` | ensure/register 兼容 API、幂等锁、join code record、enrollment/admission gate、状态和审计 |
| `agent-remote-ego-browser` | pending identity、Device ensure、凭据刷新、安装器分层、trust chain、本机授权和协议测试 |
| `agent-remote-cli` | setup/connect/status/repair/upgrade/pause/resume/stop/remove/forget UX、候选选择和脱敏输出 |
| `agent-remote-node` | 默认 capability 保持、join code 接收、profile 验证和升级状态保留 |
| `agent-remote-admin-web` | join code 管理、机器状态及用户阶段展示、只执行允许的 Server 生命周期动作、本机动作提示 |
| `agent-remote` | 跨仓库契约、发布 pin、迁移/回滚文档和 E2E 门槛 |
| `agent-remote-device` | 不修改、不安装、不作为运行依赖 |

## 10. 验收门槛（发布人员）

以下场景必须在 CI 或跨仓库集成测试中固定：

- 同一机器连续运行两次 `setup`，服务端只有一个 ego-browser Device；
- 两个并发 `setup` 只能得到同一个 Device ID，且不会丢失私钥；
- 新 Node 无旧值时明确写入 `ego_browser_enabled=false`；显式 enable 校验失败时原值不变；
- Bridge 升级前后 Device ID 和 key bytes 不变；
- 普通 Node 安装不改变原有 `ego_browser_enabled`；加入码显式启用才改变它；
- 省略 digest、Server URL 和 token 的受管 setup 能使用已登录凭据完成；
- 旧 credential 过期时刷新 credential，不创建新 Device；
- `ensure` 与兼容 `register` 使用同一 logical idempotency key，响应丢失重试不会签发第二个 Device；
- `device-rotate` 在各个崩溃点都复用同一 pending 新 key，旧 `device_generation`/credential 不会复活；
- Server 不支持 enrollment/execution 分离时，setup 在创建 identity 前返回 `server_capability_unavailable`；
- revoked/corrupt identity 不会静默生成新身份；
- 服务端注册成功但客户端在提交 credential 前崩溃时，下一次 `ensure` 复用 pending identity；
- 首次并发注册在 Device 尚不存在时仍只创建一个记录，第二个请求得到同一 identity 的结果；
- setup 不会自动 claim 任意 session；connect 必须显示候选并要求确认；
- pause/stop/resume 在没有 binding 参数时能按 active handoff/唯一候选/交互选择解析目标，多个候选不会猜测；
- `remove` 会关闭本机 local admission 并处理 pending revocation，`forget-this-mac` 才删除 Device key；
- Server 不可达时 `forget-this-mac` 返回 `pending_revocation`；收到撤销确认后才清理 key/credential/policy；
- join code 过期、重放、不同 exchange 或 profile 不匹配时拒绝；同一 `exchange_id` 重试不会
  产生第二个 Node token；
- Admin Web 不能代替本机 Device Client 完成 ensure、connect、resume 或 full-trust 确认；
- execution admission 关闭时仍可安装、ensure 和刷新状态，但不能 claim、relay hello 或 execute；
- 证书 digest 按已验证 code-signature leaf DER 的规范算法计算，manifest 自身不能充当 trust root；
- setup 对已验证的当前 release 不会隐式升级，repair 默认也不改变版本；
- remove 默认保留可复用的 Device key 与 policy，forget-this-mac 才会清除并撤销它们；
- Server origin、登录用户或 release profile 变化会触发显式切换/遗忘，而不是自动迁移；
- `switch-server` 不会上传旧 key/credential；旧 origin 回滚信息不可直接执行；
- 同一 profile/pin 的本机信任确认可以复用，pin 或 profile 变化会重新要求确认；
- 多候选/无 TTY 时不会猜测目标；候选索引在 claim 前失效会返回 `candidate_stale`；
- 任何签名、profile、policy 或 runtime 不匹配都保持 Server/local admission 关闭；
- 生产 profile 拒绝 `development` sentinel；digest 只能来自已验证 leaf DER，且命令行映射字段一致；
- 所有破坏性 identity 操作默认二次确认，非 TTY 不会隐式继续；
- `--json` 输出不含 token、私钥、脚本、页面、Cookie、URL 正文或 relay ciphertext。

## 11. 实施顺序（维护者）

1. **P0 正确性**：Device Client `ensure`、pending identity、本地注册锁、服务端幂等锁、
   enrollment/admission 分离、bootstrap 重跑幂等和升级不换 Device。
2. **P1 入口简化**：CLI `setup/connect/upgrade/repair/status/pause/resume/stop/remove/forget`、
   候选选择、默认目标解析和 full-trust 确认。
3. **P2 参数收敛**：signed release profile、Node 加入码、digest 自动发现、信任链和统一
   状态模型。
4. **P3 管理台**：生成/撤销加入码、展示机器状态和用户阶段、提供受权限限制的 Server
   生命周期操作，以及本机动作提示；不代替本机授权。

阶段不得跳过前置门槛：

| 阶段 | 完成判据 |
| --- | --- |
| P0 | ensure 重跑/并发/崩溃恢复测试通过；升级前后 identity 不变；enrollment 关闭与 execution admission 关闭均有独立测试。 |
| P1 | 普通用户只需 `setup`、`connect`；所有无 TTY 和多候选场景 fail closed；错误码和脱敏输出固定。 |
| P2 | signed profile、join code、digest/trust chain 和五状态模型有 schema、迁移和跨仓库 E2E 证据。 |
| P3 | Admin 的 join code/状态/撤销操作有权限和审计测试，并证明不能代替本机 PoP/full-trust。 |

每一阶段完成后先发布兼容版本并保留回滚路径，再进入下一阶段；没有对应验收证据时只能继续
使用旧兼容入口，不能通过文档或 feature flag 宣称已完成。

在 P0 完成前，不应把“重新执行完整 bootstrap”宣传为安全的升级路径；可使用底层
`installer/install-macos.sh` 升级，但必须保留本机 credential 目录。
