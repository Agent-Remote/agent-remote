# 本机设备控制发布门禁状态

本文按 `local-device-control-security-design.md` 第 12.3 节逐项记录当前证据边界。状态为“部分完成”
只表示仓库内实现或合成测试已存在，不表示生产门禁已经满足。生产设备控制继续默认关闭。

| 条件 | 当前状态 | 已有证据 | 仍需完成 |
| --- | --- | --- | --- |
| 1. 0 个已知 Critical/High 漏洞 | 部分完成 | Server、Node、CLI、Admin 和 Device 的 CI/release 已覆盖依赖漏洞扫描；当前本地扫描均为零命中或零 High/Critical，release 报告会绑定摘要并由发布身份签名 | 在远端受保护环境运行清单所固定的各组件 release，验证其签名扫描报告和最终组合制品后，才能判定生产门禁满足 |
| 2. 安全测试、fuzz、跨租户 E2E、macOS 权限测试通过 | 部分完成 | Rust/Swift/Go/Python 测试、协议 fuzz、Server→Node→Rust→Swift 合成 E2E 和负向授权测试已实现，并有仓库级覆盖率下限。schema 9 总装精确要求 TCC 与签名安装生命周期、选择 session 授予 full trust、信任随 DeviceSession 终止、动态应用身份复核、Device 进程排除、系统保护表面拒绝、安全 launch、无 observation 全局剪贴板、剪贴板零内容日志、前台恢复、混合版本 fail closed、远端高风险最终动作确认、机器锁与崩溃释放，以及 Esc、输入释放、多屏、用户切换、睡眠和网络切换；缺项或任一 false 均拒绝 | 在真实签名且公证的安装包上执行全部 schema 9 `macos_scenarios`，生成绑定最终制品摘要和原始报告归档；仓库内单元/合同测试不能替代这些结果 |
| 3. 独立安全评审完成 | 未完成 | 总装要求独立性声明、精确组件范围、签名报告身份与摘要、签名验证、Critical/High 清零和复测完成，并绑定原始报告归档；这些字段不能把自审变成独立评审 | 由独立评审方完成审计，关闭并复测全部 Critical/High 发现，交付可验证签名报告和发布批准记录 |
| 4. 签名、公证、SBOM、更新签名和摘要可验证 | 部分完成 | 六仓库发布工作流已绑定各自不可变标签，并生成摘要、SBOM、Sigstore/GitHub provenance；根发布清单分别固定组件版本与 commit；Server、Node、macOS app 和 proxy 的 SBOM 均由各自精确 release workflow 身份独立签名，总装拒绝仅有 SPDX 结构但签名缺失或身份不匹配的 SBOM；Device 正式构建会对 App 和两个 XPC 的实际代码签名逐一验证 Developer ID Application authority、Hardened Runtime 和配置的 Team ID，证据再从最终 App 签名读取 Team ID 并与受保护环境及 Broker plist 三方核对；工作流生成绑定 app 摘要/notary submission/stapler/Gatekeeper 的签名证据，并从已打包 Broker 提取 bundle ID、policy ID、attestor mach service 和公钥摘要；总装要求这些值与外部 outbound-policy 原始证据完全一致；六项外部门禁还必须携带摘要匹配、结构安全的原始报告归档并随最终 evidence artifact 交付 | 配置真实 Apple/GitHub 受保护环境并成功运行清单认证组合；验证下载制品而非仅验证工作流契约 |
| 5. 本机出站 allowlist 已安装并激活 | 部分完成 | Network Broker 在激活 full-trust Executor 和建立 relay 前都要求固定受管 mach service 返回带随机 challenge 的 Ed25519 签名实时证明；证明精确绑定 Team ID、Broker bundle ID、策略 ID、唯一控制面主机、Network Extension 启用状态、允许探测和 unauthorized/Anthropic 阻断探测，缺失、过期、身份/目标不符、策略失效或超时均 fail closed；正式构建强制固定 attestor service、公钥和策略 ID，开发构建默认拒绝 | 由 MDM/Network Extension 部署方独立实现并安装 attestor 和按签名进程 allowlist，在签名安装包上生成绑定最终制品的原始策略与主动探测证据；仓库内接口和合成签名测试不能替代该证据 |
| 6. 不访问本地 Claude 且不连接 Anthropic | 部分完成 | 隔离证据格式和 fail-closed verifier 已实现并有契约测试；总装要求文件/网络传感器均激活、输出完整、观测进程身份已验证且 Team ID 与公证应用一致 | 在安装且已登录本地 Claude 的真实 Mac 上采集文件与网络传感器证据，持续至少 60 秒并绑定最终应用摘要 |
| 7. 撤销、全局停止和 fail-closed 演练通过 | 部分完成 | full-trust 自动激活事务、Esc、租约、撤销、断线和恢复路径有自动化测试。Executor authorization 在 generation 轮换时要求除 generation 外完全一致；relay、rotation、本机安全监控或 XPC 失败会 abort 已激活 Server binding；过期异步完成不能复活终止 generation。Stop/End 只取消精确完整 binding，输入释放、前台恢复、单调 sequence 和未知结果不重放保持不变 | 对真实签名安装包执行综合演练，覆盖按键按下期间断线、Broker/Executor 崩溃、锁屏、TCC 撤销、Node/Server 撤销、rotation、抢占和权限残留 |
| 8. 当前 Claude Code 和 MCP 兼容性验证 | 未完成 | 公开 Computer Use schema 和 MCP proxy 契约测试已实现；schema 9 总装记录强制绑定当前 Claude Code/MCP 版本和精确五个公开工具 `act`、`input_text`、`launch_application`、`observe`、`read_clipboard`，并要求真实运行明确观察到受管 MCP 配置、图片结果、长序列操作和可信 turn stop。单一 `mixed_version_fails_closed=true` 不再满足门禁：兼容性记录必须精确覆盖 new/old Server 与 Device、new/old proxy 与 Device、capability-policy mismatch 五种组合，逐行绑定 Server/Node/application/proxy 的版本、摘要和候选角色，证明 full trust 未激活且未发送未知协议，并把矩阵报告摘要绑定到原始归档 | 固定当前 Claude Code/MCP 版本，在真实远端 Claude 会话完成 full-trust、launch、全局剪贴板、高风险确认和五场景混合版本部署矩阵，上传绑定最终制品的原始回归报告；结构化 fixture 和合成合同测试不能替代真实部署结果 |

## 2026-09-03 Session full trust 本地实现状态

五仓库已完成 session 选择授权、`pending_device -> active` 自动激活、动态应用身份复核、安全
`launch_application`、无 observation 全局纯文本剪贴板、完整 capability fail closed、精简 Device UI、
Admin policy 展示和两份 managed skill 同步。新 full-trust session 不创建 approval row，不进入
`pending_user_approval`；legacy mode、旧状态和旧审批数据仅用于受控兼容，不能从空 approvals 推断授权。

release evidence 当前由 Apple 和 Community 组装器生成 schema 9；schema 8 仅作为已签发格式永久兼容。
Server 在启动、HTTP 和 relay WebSocket 运行时检查中把证据版本绑定到授权模式；schema 8 只能授权
legacy `per_application_approval`，不能用于生产 `session_full_trust`。
仓库内合同覆盖新 `macos_scenarios`、五工具 public surface 和混合版本拒绝，但真实签名/公证 macOS
E2E、真实混合版本部署矩阵、独立安全评审、精确生产组件组合签名和生产默认策略切换均未完成。

## 2026-08-05 Computer Use v2 实现状态

结构化状态优先路径已经在 Device、Node 和受管 MCP proxy 中完成代码集成：Node 广告并写入
`observation_mode_v2`、`ax_state_v2`、`adaptive_settle_v2`；proxy 通过 `--compact-tools` 仅暴露
`observe`、`act`、`input_text`、`launch_application`、`read_clipboard`；macOS Executor 实现有界 AX full/diff、绑定当前
状态/应用/窗口/显示器的元素动作、自适应等待，以及 compact/standard/region 图片 fallback。
v2 请求 schema 和 Swift/Rust 共享 fixture 已提交，v1 工具和完整 v1 协议仍作为缺少 capability 时
的 fail-closed 兼容路径。Server 只协商完整三项 v2 capability，Node 将其绑定 managed context 并拒绝
同 generation 降级；proxy 还会生成有界零内容 JSONL，Device benchmark harness 可直接比较 v1/v2
图片次数、字节、p95 时延、fallback、stale 和成功率。使用真实组件二进制的本地合成
`Server -> Node -> Rust -> Swift` harness 已升级为完整 session-full-trust capability：seed 不再直接创建
active DeviceSession，而是以 Device token 调用公开 claim API，核对 `pending_device` 后通过
`device-connected` 进入 `active`，再把动态 session ID、expiry 和 lease 传给各 peer。随后先在零
application state 下读取全局剪贴板，再按唯一名称启动应用并取得首个 AX full observation，最后执行
后续 `observe(auto)`；三步均通过真实 nested TLS relay，并验证 GUI state generation 单调前进而
screenshot generation 保持不变。

自 `v0.2.5` 起，Computer Use v2 被定义为正式默认能力，不再把可选质量报告当作运行依赖。Server 在
`DEVICE_CONTROL_V2_ENABLED=true` 时对每个新 generation 自动协商完整三项 capability；Node 部分、未知
或畸形上报完整回退 v1。管理员可把开关设为 `false`，让新 generation 使用 v1，活动
generation 不做中途降级。

Apple profile 组装器和 Community schema 9 工作流仍可生成绑定精确浏览器、指标、零错误目标、零敏感
遥测和回滚断言的专项质量证据，并验证 `report_sha256` 对应文件真实存在于受限原始证据归档。
`computer_use_v2_evidence_sha256` 继续受规范 Ed25519 签名保护；schema 9 在缺少可选专项报告时将该字段设为
`null`。缺少这份可选记录不再阻止正式 v2 能力，但不得把减少截图次数或延迟作为放宽确认策略、secure
field hand-off、stale target 拒绝或远端高风险最终动作确认的理由。

本方案的文档事实源已经固定：总体架构、Token 预算、浏览器边界、默认协商和完成定义见
`local-device-control-security-design.md` 第 6.5 节；wire contract 与唯一调用状态机见 Device 仓库
`docs/protocol.md`；采集、真实 Token 对账和 golden prompt 回归见 Device 仓库
`docs/optimization-benchmark.md`；模型日常调用规则见 Device skill 及其按需浏览器 reference。任何工具
schema、默认 observation policy 或 skill 元数据变更都必须同步通过上述 corpus，不能只更新单份提示词。

## 已实现的总装约束

`device-control-release-evidence` 工作流只能从精确根分发 `vVERSION` 标签运行。它按根发布清单分别验证 Server、Node、
macOS app 和 proxy 的摘要、签名、SBOM、provenance 与 notarization，并要求同标签、同 commit 的成功
`device-control-external-gates.yml` workflow_dispatch run 提供第 2、3、5、6、7、8 项真实证据；其他 workflow
即使上传同名 artifact 也会被拒绝。缺项即失败。受保护环境中的 Ed25519 私钥只签署与根版本
绑定的 schema 9 永久清单；所有动态外部门禁必须在签发前 30 天内采集，旧记录不能靠重新签名延长门禁记录
自身的新鲜度。该签名表示
部署方批准了精确证据，不替代上述验证，也不会修改生产 capability 配置。
Apple Developer ID 发布打包和真实签名/公证 E2E 暂不纳入当前 release 范围；仓库内 fixture、合同测试与
合成 E2E 不作为这类外部证据。

当前本机构建目录中的候选包仅供开发验证：六个组件已统一为 `0.1.0`，但 macOS app 为 ad-hoc
签名，且没有生产 SBOM、provenance、notarization 或外部门禁证据，因此不得提交给生产证据生成器。

## 2026-07-31 本地测试 release

已在 `dist/device-control-test-release` 组装可重复生成的本地测试 release，包含 macOS arm64 App 和
CLI、Linux amd64/arm64 Node 与 standalone proxy、Server/Admin OCI 镜像以及 Compose 测试配置。
包内摘要已全部复核，CLI 版本与可执行架构、两个 proxy 架构、归档结构和 App 深度签名均已完成
冒烟检查；proxy 的包内摘要可在解包目录直接验证，Node 内嵌 proxy 与对应 standalone 制品逐字节
一致；本地合成 `Server -> Node -> Rust -> Swift` v2 E2E 已通过。当前包可用于非敏感数据的功能测试，
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

本轮还收紧了三处生产门禁：Server 对启动时已验证的 schema 8 或 9 release evidence 在运行期持续检查其
永久绑定的版本/签名，不再按时间撤销；旧 schema 过期时仍拒绝新建、连接、审批、加锁、续租、重连、
relay material 和 WebSocket，同时保留 Abort/Stop 用于安全清理；release CLI 在编译时固定受保护环境
提供的 Apple Team ID，并分别验证 App 与两个
XPC 的签名身份；受保护的自托管 Mac 工作流只收集固定的 12 项外部门禁原始文件，拒绝额外文件、
符号链接、重复 JSON 字段、摘要不一致和危险归档成员。上述实现不会生成或代填任何外部门禁通过
结果，也不能替代 Developer ID、公证、TCC/MDM、Claude 隔离、兼容性和独立安全评审证据。

本轮范围内本地质量门禁已完整执行：Server 171 passed、4 skipped，行覆盖率 71.27%；Node 语句覆盖率
50.6%；Admin 53 tests、行覆盖率 86.67%；Device Swift 267 tests、行覆盖率 59.86%，Rust 93 tests、
行覆盖率 82.93%；均高于仓库门槛。Device 还覆盖了 Secure Input 交互拒绝、五种剪贴板错误码透传、
嵌套安装应用发现、Device Bundle/签名 identity 命名空间排除、launch 首次窗口绑定已验证 PID、
launch 失败前台恢复、launch 不确定结果终止 generation 和 claim 端 Device capability 拒绝。Server、
Node、proxy 和 Executor 四层均按 binding 的 authorization mode 拒绝 legacy/full-trust capability 混用；
策略切换不会放宽 pending binding，
active 同 generation 续租也不会降级。根仓库全部自带 Python release/contract tests 通过。这些结果是
本地实现证据，不替代远端受保护 workflow、真实签名制品或外部门禁。

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
