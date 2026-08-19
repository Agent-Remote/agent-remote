# 本机设备控制发布门禁状态

本文按 `local-device-control-security-design.md` 第 12.3 节逐项记录当前证据边界。状态为“部分完成”
只表示仓库内实现或合成测试已存在，不表示生产门禁已经满足。生产设备控制继续默认关闭。

| 条件 | 当前状态 | 已有证据 | 仍需完成 |
| --- | --- | --- | --- |
| 1. 0 个已知 Critical/High 漏洞 | 部分完成 | Server、Node、CLI、Admin 和 Device 的 CI/release 已覆盖依赖漏洞扫描；当前本地扫描均为零命中或零 High/Critical，release 报告会绑定摘要并由发布身份签名 | 在远端受保护环境运行清单所固定的各组件 release，验证其签名扫描报告和最终组合制品后，才能判定生产门禁满足 |
| 2. 安全测试、fuzz、跨租户 E2E、macOS 权限测试通过 | 部分完成 | Rust/Swift/Go/Python 测试、60 秒协议 fuzz 工作流、真实 Server→Node→Rust→Swift 合成 E2E 和负向授权测试已实现；CI 对 Server、Node、CLI、Admin、Device Rust 和 Device Swift 均设置会阻止回归的覆盖率下限，而不是只上传报告；MCP 图片边界会拒绝畸形、错标、超像素及高压缩图片，图片解码移出异步 worker 且每代 proxy 只允许一个进行中的工具操作；Server 密文 relay 对单帧、每方向每秒速率、等待配对时间和单次连接寿命分别设置硬上限，任一超限会关闭双方；Node 对控制面、helper、本地 bridge 和持久化激活清单 JSON 拒绝重复及未知字段，完整保留 64 位 generation，并对 helper 响应和本地帧先限长后解码；Swift XPC envelope、审批、租约与生命周期 payload 递归拒绝重复字段，并按解码前后结构拒绝任意层级未知字段；Node 激活清单、Rust 受管 context 与 Swift 可见性恢复日志均使用 `O_NOFOLLOW` 单次打开、同一描述符 metadata 校验和限长读取，阻止路径替换及文件增长绕过上限；跨显示器窗口按最大交叠面积和稳定 display ID 确定主显示器，截图与动作校验使用相同选择规则；App、XPC、proxy、Node 和受管 runtime 显式禁用 core dump；总装 evidence schema 强制逐项报告 TCC、签名安装生命周期、三档控制等级、每 session 应用/剪贴板审批、机器锁和崩溃释放、未批准应用隐藏/截图排除/恢复、Esc 不传递、输入按下期间断线释放、Retina、多屏、用户切换、睡眠和网络切换，缺项或任一 false 均拒绝；还要求专用 macOS 测试机、应用签名与 stapled notarization ticket 均已验证，运行时 Team ID 必须与公证记录一致 | 在签名安装包上真实执行全部 `macos_scenarios`，并生成绑定制品摘要和原始报告归档；仓库内合成测试不能替代这些结果 |
| 3. 独立安全评审完成 | 未完成 | 总装要求独立性声明、精确组件范围、签名报告身份与摘要、签名验证、Critical/High 清零和复测完成，并绑定原始报告归档；这些字段不能把自审变成独立评审 | 由独立评审方完成审计，关闭并复测全部 Critical/High 发现，交付可验证签名报告和发布批准记录 |
| 4. 签名、公证、SBOM、更新签名和摘要可验证 | 部分完成 | 六仓库发布工作流已绑定各自不可变标签，并生成摘要、SBOM、Sigstore/GitHub provenance；根发布清单分别固定组件版本与 commit；Server、Node、macOS app 和 proxy 的 SBOM 均由各自精确 release workflow 身份独立签名，总装拒绝仅有 SPDX 结构但签名缺失或身份不匹配的 SBOM；Device 正式构建会对 App 和两个 XPC 的实际代码签名逐一验证 Developer ID Application authority、Hardened Runtime 和配置的 Team ID，证据再从最终 App 签名读取 Team ID 并与受保护环境及 Broker plist 三方核对；工作流生成绑定 app 摘要/notary submission/stapler/Gatekeeper 的签名证据，并从已打包 Broker 提取 bundle ID、policy ID、attestor mach service 和公钥摘要；总装要求这些值与外部 outbound-policy 原始证据完全一致；六项外部门禁还必须携带摘要匹配、结构安全的原始报告归档并随最终 evidence artifact 交付 | 配置真实 Apple/GitHub 受保护环境并成功运行清单认证组合；验证下载制品而非仅验证工作流契约 |
| 5. 本机出站 allowlist 已安装并激活 | 部分完成 | Network Broker 在允许审批和建立 relay 前都要求固定受管 mach service 返回带随机 challenge 的 Ed25519 签名实时证明；证明精确绑定 Team ID、Broker bundle ID、策略 ID、唯一控制面主机、Network Extension 启用状态、允许探测和 unauthorized/Anthropic 阻断探测，缺失、超过 30 秒、有效期超过 60 秒、身份/目标不符、策略失效或 5 秒超时均 fail closed；正式构建强制固定 attestor service、公钥和策略 ID，开发构建默认拒绝 | 由 MDM/Network Extension 部署方独立实现并安装 attestor 和按签名进程 allowlist，在签名安装包上生成绑定最终制品的原始策略与主动探测证据；仓库内接口和合成签名测试不能替代该证据 |
| 6. 不访问本地 Claude 且不连接 Anthropic | 部分完成 | 隔离证据格式和 fail-closed verifier 已实现并有契约测试；总装要求文件/网络传感器均激活、输出完整、观测进程身份已验证且 Team ID 与公证应用一致 | 在安装且已登录本地 Claude 的真实 Mac 上采集文件与网络传感器证据，持续至少 60 秒并绑定最终应用摘要 |
| 7. 撤销、全局停止和 fail-closed 演练通过 | 部分完成 | 协议状态机、Esc、租约、撤销、断线和恢复路径有自动化测试；本机批准后先隐藏未批准应用并启动 Esc、锁屏、用户切换、睡眠和网络丢失监控，再允许 Broker 激活 relay，激活期间的本机或远端终态都不能被完成回调覆盖；审批展示只接受活动 generation 范围；存在当前 relay 或待激活状态时，Broker 的 Stop/End Session 只取消精确完整 binding，跨 generation 请求不能取消当前会话，Executor 也独立要求请求精确匹配其当前 binding；Broker 使用待激活令牌绑定异步 relay 建立，本地结束、XPC 断连或建立失败会清除令牌，延迟返回的 relay 不能复活已结束 generation；可信 turn stop 的确认会等待 Executor 释放输入和 UI 恢复应用，同一 session 的下一次动作会先重新隐藏应用、恢复监控和 Executor，并强制先获取新截图，机器锁保持不变；Approval UI 或 Executor XPC 失联会立即取消 relay，所有安全关键 XPC 调用也有 15 秒本机回复期限和取消处理，进程在线但静默不回复同样会中止 relay；relay 失败、身份轮换或 Executor 失联会同步结束当前 UI generation 并恢复应用，清理失败进入明确 failed 状态但不能阻止控制面撤销；待审批展示按完整 session binding 去重，因此同一 session ID 的新 generation 必须重新审批；用户 Stop/End Session 使用相同撤销语义；proxy 握手与动作受剩余租约/30 秒上限约束，生命周期确认限时 15 秒，致命错误会关闭并毒化当前代次连接；generation 在 Server/Node/Rust/Swift 统一为可持久化的有符号 64 位范围，非终态耗尽在任何写入前失败并保留最终停止代次；动作序号和截图代次耗尽时在动作前失败且绝不环绕或饱和复用 | 对签名安装包执行人工/自动化综合演练，覆盖按键按下期间断线、崩溃、锁屏、Node/Server 撤销和权限残留 |
| 8. 当前 Claude Code 和 MCP 兼容性验证 | 未完成 | 公开 Computer Use schema 和 MCP proxy 契约测试已实现；总装记录会强制绑定当前 Claude Code/MCP 版本和精确 16 个动作，并要求真实运行明确观察到受管 MCP 配置、图片结果、长序列操作和可信 turn stop | 固定当前 Claude Code/MCP 版本，在真实远端 Claude 会话完成这些行为和兼容性矩阵，上传绑定最终制品的原始回归报告 |

## 2026-08-05 Computer Use v2 实现状态

结构化状态优先路径已经在 Device、Node 和受管 MCP proxy 中完成代码集成：Node 广告并写入
`observation_mode_v2`、`ax_state_v2`、`adaptive_settle_v2`；proxy 通过 `--compact-tools` 仅暴露
`observe`、`act`、`input_text`、`read_clipboard`；macOS Executor 实现有界 AX full/diff、绑定当前
状态/应用/窗口/显示器的元素动作、自适应等待，以及 compact/standard/region 图片 fallback。
v2 请求 schema 和 Swift/Rust 共享 fixture 已提交，v1 工具和完整 v1 协议仍作为缺少 capability 时
的 fail-closed 兼容路径。Server 只协商完整三项 v2 capability，Node 将其绑定 managed context 并拒绝
同 generation 降级；proxy 还会生成有界零内容 JSONL，Device benchmark harness 可直接比较 v1/v2
图片次数、字节、p95 时延、fallback、stale 和成功率。真实临时
`Server -> Node -> Rust -> Swift` harness 也已升级为完整 v2 capability 下的 `observe(auto)`，并验证
AX full 返回时 state generation 前进而 screenshot generation 保持不变。

自 `v0.2.5` 起，Computer Use v2 被定义为正式默认能力，不再把可选质量报告当作运行依赖。Server 在
`DEVICE_CONTROL_V2_ENABLED=true` 时对每个新 generation 自动协商完整三项 capability；Node 部分、未知
或畸形上报完整回退 v1。管理员可把开关设为 `false`，让重新审批的新 generation 使用 v1，活动
generation 不做中途降级。

Apple profile 组装器和 Community schema 4 工作流仍可生成绑定精确浏览器、指标、零错误目标、零敏感
遥测和回滚断言的专项质量证据，并验证 `report_sha256` 对应文件真实存在于受限原始证据归档。
`computer_use_v2_evidence_sha256` 继续受规范 Ed25519 签名保护；Community schema 2/3 固定该字段为
`null`。缺少这份可选记录不再阻止正式 v2 能力，但不得把减少截图次数或延迟作为放宽确认策略、secure
field hand-off、stale target 拒绝或应用审批的理由。

本方案的文档事实源已经固定：总体架构、Token 预算、浏览器边界、默认协商和完成定义见
`local-device-control-security-design.md` 第 6.5 节；wire contract 与唯一调用状态机见 Device 仓库
`docs/protocol.md`；采集、真实 Token 对账和 golden prompt 回归见 Device 仓库
`docs/optimization-benchmark.md`；模型日常调用规则见 Device skill 及其按需浏览器 reference。任何工具
schema、默认 observation policy 或 skill 元数据变更都必须同步通过上述 corpus，不能只更新单份提示词。

## 已实现的总装约束

`device-control-release-evidence` 工作流只能从精确根分发 `vVERSION` 标签运行。它按根发布清单分别验证 Server、Node、
macOS app 和 proxy 的摘要、签名、SBOM、provenance 与 notarization，并要求同标签、同 commit 的成功
CI run 提供第 2、3、5、6、7、8 项真实证据。缺项即失败。受保护环境中的 Ed25519 私钥只签署短期
清单；所有动态外部门禁必须在签发前 30 天内采集，旧记录不能靠重新签名延长有效期。该签名表示
部署方批准了精确证据，不替代上述验证，也不会修改生产 capability 配置。

当前本机构建目录中的候选包仅供开发验证：六个组件已统一为 `0.1.0`，但 macOS app 为 ad-hoc
签名，且没有生产 SBOM、provenance、notarization 或外部门禁证据，因此不得提交给生产证据生成器。

## 2026-07-31 本地测试 release

已在 `dist/device-control-test-release` 组装可重复生成的本地测试 release，包含 macOS arm64 App 和
CLI、Linux amd64/arm64 Node 与 standalone proxy、Server/Admin OCI 镜像以及 Compose 测试配置。
包内摘要已全部复核，CLI 版本与可执行架构、两个 proxy 架构、归档结构和 App 深度签名均已完成
冒烟检查；proxy 的包内摘要可在解包目录直接验证，Node 内嵌 proxy 与对应 standalone 制品逐字节
一致；真实 `Server -> Node -> Rust -> Swift` v2 E2E 已通过。当前包可用于非敏感数据的功能测试，
六个组件及 App/XPC bundle 均为 `0.1.0`。它仍是 ad-hoc 签名且未公证，因此
`production_ready=false`。六仓库均已形成 clean、可审计的 `0.1.0` 源码快照，协调 readiness 的
clean、tag 和 origin 严格检查已通过，本地统一 `v0.1.0` 标签已创建但尚未推送；在远端发布并完成
真实外部门禁前，不得启用生产 capability。

六仓库源码快照均已推送到 `main`：Root `9c1baf2c`、Server `7f9c4e0c`、Node `5d3a0d1a`、CLI
`f6695a27`、Admin `fc6c64da`、Device `9168fe62`。对应 GitHub Actions 已有真实成功记录：Root CI
`30612564176`、Server CI `30611243723`、Node CI `30611714895`、CLI CI `30611235824`、CLI
install-smoke `30611235810`、Admin CI `30611228121`、Device CI `30612553250`。这些记录只证明
仓库内自动化门禁成功，不代替 Apple 公证、真实 TCC/MDM、Claude 隔离与兼容性、独立安全评审或
受保护生产环境证据；本地 `v0.1.0` 标签仍未推送。

本轮还收紧了三处生产门禁：Server 对启动时已验证的 release evidence 在运行期持续检查有效期，
过期后拒绝新建、连接、审批、加锁、续租、重连、relay material 和 WebSocket，同时保留 Abort/Stop
用于安全清理；release CLI 在编译时固定受保护环境提供的 Apple Team ID，并分别验证 App 与两个
XPC 的签名身份；受保护的自托管 Mac 工作流只收集固定的 12 项外部门禁原始文件，拒绝额外文件、
符号链接、重复 JSON 字段、摘要不一致和危险归档成员。上述实现不会生成或代填任何外部门禁通过
结果，也不能替代 Developer ID、公证、TCC/MDM、Claude 隔离、兼容性和独立安全评审证据。

六仓库本地质量门禁已再次完整执行：Server 覆盖率 72.03%，Node 语句覆盖率 50.2%，CLI 行覆盖率
48.46%，Admin 行/分支覆盖率分别为 86.44%/67.45%，Device Rust/Swift 行覆盖率分别为
82.91%/62.70%，均高于对应 CI 下限。Server pip-audit、Node govulncheck、CLI/Device cargo-audit
和 Admin npm audit 当前均无已知漏洞或可达 finding。Device CI 已改为从 Cargo metadata 解析 proxy
版本，不再把 `0.1.0` 写死；proxy `SHA256SUMS` 只记录包内文件名，避免 CI 和用户解包后因构建机
路径而无法验证，并已有行为回归测试。

## Phase 2 运维准备

`device-control-operations-runbook.md` 已定义零内容数据清单、事件遏制/恢复、撤销先于卸载、升级与
fail-closed 回滚，以及设备令牌、发布证据签名键和出站策略证明键的轮换流程。CLI 的
`agent-remote device rotate-token` 会使用 user token 完成服务端轮换并直接覆盖本机平台凭据和 Broker
共享 Keychain 项，不打印新 token。

Server 已提供两个默认关闭、由部署方选择期限的有界后台清理：只删除过期终态 `device_sessions` 及
审批摘要，并以独立且不短于 session 的期限删除 `target_type=device_session` 审计；active session 和
通用身份审计不会被删除。生产启用时任一期限为零会拒绝启动。

该项仍为部分完成：部署方尚未批准实际保留期限，周期性删除证明、真实轮换演练和外部证据也未完成。
不得用未经评审的 SQL 清理或仅凭运行手册/实现存在把 Phase 2 标为 ready。
