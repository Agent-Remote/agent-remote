# 本机设备控制运维运行手册

本文覆盖 macOS 本机设备控制的数据保留、事件响应、安装与回滚、撤销和密钥轮换。它是
`local-device-control-security-design.md` Phase 2 的操作基线，不是生产就绪声明。任何发布门禁证据
缺失时，`DEVICE_CONTROL_ENABLED` 必须保持 `false`。

绑定选择、切换和结束控制的产品与 API 契约见 `local-device-control-binding-design.md`。运维人员应把
`rebound` 视为一次旧授权撤销和新授权建立，而不是删除审计历史。

## 1. 角色与不变量

- 发布负责人管理协调版本、受保护发布环境和发布证据签名键。
- 控制面负责人管理 Server 配置、设备清单、会话终止和审计元数据。
- macOS 负责人管理签名安装包、TCC 和测试 Mac；Apple Developer ID profile 还要求管理 MDM、
  Network Extension 和策略证明服务。
- 事件负责人决定影响范围、证据保全、密钥轮换和恢复时间。
- 数据负责人在生产启用前书面批准审计元数据与备份的保留期限和删除方式。

截图、zoom 图片、输入文本、剪贴板、窗口标题、页面内容、坐标、输入长度和图片 hash 不得进入
控制面数据库、日志、工单或事件附件。运维证据只记录 user/device/session 标识、时间、状态、结果码、
请求 ID、制品摘要和外部传感器的有界结论。

## 2. 数据保留

### 2.1 数据清单

| 数据 | 当前行为 | 运维要求 |
| --- | --- | --- |
| GUI 内容和输入 | 仅在当前调用的内存窗口中存在 | 禁止持久化；禁止为排障开启 body/header dump 或 core dump |
| relay 票据和每代连接材料 | 由 Server TTL 和一次性兑换约束 | 不备份、不归档；到期后不得重放 |
| 设备控制 session 元数据 | PostgreSQL 持久化 | 只允许设计文档第 9 节列出的零内容字段 |
| 授权与动作审计元数据 | PostgreSQL 持久化 | 只允许授权 mode/policy version、动作类型、结果和关联 ID；不得记录应用或剪贴板内容 |
| 发布门禁清单 | 当前 schema 9 与根版本制品绑定，永久有效 | 仅在版本、制品、签名键或部署授权被替换/撤销时重新发布；已签发 schema 8 仍永久兼容，旧 schema 1-7 仍按原 30 天迁移规则处理 |
| Actions 总装 artifact | 当前 workflow 保留 30 天 | 需要更长审计期时转存到受控、不可变且访问留痕的证据库 |
| PostgreSQL 备份 | 由部署方管理 | 保留期不得长于已批准的数据策略；过期副本和恢复测试副本同样删除 |

### 2.2 保留策略记录

生产负责人必须在部署记录中固定以下内容：数据所有者、法务依据、各类审计元数据的保留期限、备份
期限、legal hold 例外、删除执行人、复核人、执行频率和删除证明位置。策略变更必须经过数据负责人和
安全负责人共同批准。

Server 提供两个由部署方显式选择的保留期：`DEVICE_SESSION_RETENTION_DAYS` 清理截止时间前的终态
`device_sessions` 及其历史兼容审批摘要，`DEVICE_SESSION_AUDIT_RETENTION_DAYS` 只清理
`target_type=device_session` 的审计元数据。审计期不得短于 session 期；两者默认都是 `0`，表示不自动
清理。生产环境启用设备控制时任一值为 `0` 都会拒绝启动，因此生产负责人必须先批准并配置实际天数。

后台任务按有界批次执行，不删除 active session 或通用身份审计。不得用未经评审的原始 SQL、级联
删除或日志截断绕过保留服务。legal hold 期间先关闭 capability，再把两个值设为 `0` 并重启；解除后
恢复已批准期限。检查结构化日志中的删除计数并把周期性删除证明纳入部署记录，日志不得包含行内容。

每次备份和恢复演练按 `backup-restore.md` 执行，并验证恢复副本没有出现 GUI 内容字段。legal hold
结束后，恢复副本也必须重新进入正常删除周期。

## 3. 激活、安装与升级

### 3.1 激活前检查

1. 根发布清单为六个仓库分别固定独立版本、不可变 tag 和允许的干净提交：

   ```sh
   python3 scripts/check-device-control-release-readiness.py \
     --manifest release-manifest.json --require-clean --require-tag --require-origin
   ```

2. 选择并验证一种发布配置：无 Apple 账号时按 `community-local-trust-release.md` 验证 Server、Node、
   App 和 proxy 的摘要、SBOM、来源证明、自签名身份、官方 runner CI 与风险接受记录；Developer ID
   配置则按 `device-control-release-evidence.md` 验证 Apple 签名/公证和六项原始外部门禁证据。
3. 从同一个根版本部署包读取 schema 9 发布证据，确认其 `distribution_version` 与正在部署的
   `VERSION` 一致且不存在 `expires_at`，再把证据和对应 Ed25519 公钥作为只读部署输入设置到
   `DEVICE_CONTROL_RELEASE_EVIDENCE_PATH` 和 `DEVICE_CONTROL_RELEASE_PUBLIC_KEY`。禁止跨版本复制证据。
4. 设置数据负责人批准的 `DEVICE_SESSION_RETENTION_DAYS` 和
   `DEVICE_SESSION_AUDIT_RETENTION_DAYS`；后者不得短于前者，生产中都不得为 `0`。
5. Developer ID 配置由 MDM 负责人确认 Network Extension 已启用、策略证明服务可用，并在签名测试
   Mac 上重新执行允许、非授权和 Anthropic 目的地主动探测。community 配置改为在受控目标 Mac 上
   验证 Broker 的应用级目的地限制，并确认部署方已接受它不等价于系统级网络过滤。
6. 最后才把 `DEVICE_CONTROL_ENABLED=true` 部署到生产。Server 启动失败、策略页仍为 disabled 或任一
   实时证明失败时停止变更，不得绕过验证器。

### 3.2 本机安装和升级

只使用生产组合清单选中并已验证摘要的发布 app，不接受项目仓库或 API 返回的下载地址：

```sh
agent-remote device install --source "/path/to/agent-remote-device-macos-VERSION.zip"
agent-remote device diagnose
agent-remote device status
agent-remote device launch
```

升级前结束设备控制 session，保存零内容 session ID 和停止结果，然后安装新版本。安装命令允许同版本
重装和升级，拒绝降级。升级后重新验证签名、两个 XPC service、TCC 状态、Esc 停止和一次完整的
session 选择、自动激活、launch、无 observation clipboard 与停止流程。Developer ID 配置还要验证 Gatekeeper 和出站策略实时证明；community 配置要验证固定自签名
证书、手动信任状态和 Broker 应用级目的地限制。任一适用检查失败时保持 capability 关闭并进入回滚。

### 3.3 Computer Use v2 自动协商

`DEVICE_CONTROL_V2_ENABLED` 默认是 `true`。每个新 generation 都检查 Node 是否同时广告
`ax_state_v2`、`observation_mode_v2`、`adaptive_settle_v2`；三项完整时自动使用 v2，缺少、畸形或未知
时使用完整 v1，禁止部分启用。混合版本可以滚动升级，不需要设备分桶、验收窗口或额外的 v2 发布证据。
活动 generation 固定其 capability 集合，中途不升级也不降级。

升级后创建一个新的无副作用 session，确认 context task 携带完整三项 capability，并验证 AX-first、
状态绑定、stale 拒绝、adaptive settle、图片 fallback 和停止恢复。schema 9 中的专项报告仍可用于长期质量
审计，但缺失不影响已经正式支持的 v2。记录不得包含 AX 文本、URL、标题、截图、输入、坐标或剪贴板
内容。

`session_full_trust` 不能沿用上述三项基础 capability 的宽松回退。新模式至少同时要求
`observation_mode_v2`、`ax_state_v2`、`adaptive_settle_v2`、`clipboard_payload_v2`、
`session_full_trust_v1`、`application_launch_v1` 和 `global_clipboard_v1`。缺少任意一项、
policy version 不匹配或组件版本不受发布清单支持时，candidate 必须不可控并显示升级错误；不得
静默退回逐应用审批、隐藏 launch 或恢复 application-bound clipboard。

## 4. 正常停用、撤销与卸载

正常停用必须按以下顺序执行：

1. 在 Admin Web 的 Device control sessions 中停止活动 session，确认状态进入终态且本机应用恢复。
2. 在对应 Mac 上撤销远端设备身份：

   ```sh
   agent-remote device revoke --device DEVICE_ID --yes
   ```

3. 在 Admin Web 确认设备为 revoked，旧设备令牌不能再访问控制面，并确认没有活动设备 session。
4. 退出 `Agent Remote Device.app`，再删除本机安装：

   ```sh
   agent-remote device uninstall --yes
   ```

5. 运行 `agent-remote device status`，并检查 TCC、共享 Broker 凭据、应用沙盒数据和隐藏应用恢复日志
   均无残留。

### 4.1 绑定切换

用户在 Device APP 选择另一个远端 Claude session 时，Server 会停止当前设备的旧控制绑定，并在目标
session 已被其他设备使用时停止该设备上的旧绑定。旧 relay 必须先关闭，随后由 Node deactivate task
清除 runtime context；新绑定必须重新进入 `pending_device`，并由这次本机 session 选择建立新的
`session_full_trust` authorization。不能复用旧 DeviceSession 的 generation 或 authorization；同一
DeviceSession 的重连/轮换只能复制完全相同的 policy version 和 scope。

切换故障排查只记录 user/device/tool-session/device-session ID、generation、task ID、request ID、状态
和时间。不得收集截图、输入、Claude 配置或 relay payload。若数据库已显示旧绑定为终态但旧 Mac 仍能
发送动作，立即停止相关 Node bridge、关闭 Server relay hub pair，并撤销设备 token；不能只等待 lease
自然到期。

`uninstall` 不会撤销远端注册。不得颠倒 `revoke` 和 `uninstall`；若本机丢失或无法执行 CLI，控制面
管理员必须先在 Admin Web 撤销设备，再按事件流程处理本机残留。

### 4.2 结束控制的语义

| 操作 | 设备控制授权 | 远端 `fclaude` session | 备注 |
| --- | --- | --- | --- |
| APP `Stop current action` | 保留相同 session authorization，进入 paused | 保持运行 | 只停止当前 turn |
| APP `End device control` | 终止 | 保持运行 | 清理 relay、Node bridge 和本机 GUI 状态 |
| Admin Web `Stop` | 终止 | 保持运行 | 远端 APP 必须 fail closed 并恢复桌面 |
| `fclaude stop` | 终止 | 终止或进入 interrupted | 由 Server 统一清理 DeviceSession |
| lease/max TTL 到期 | 终止 | 保持运行 | 不允许依赖自然断线完成清理 |

Admin Web 和 APP 都只能调用同一个 Server revoke/stop service。旧的客户端指定
`device_id + tool_session_id` 创建接口不是普通用户入口；上线后应返回弃用错误，
避免 Web 绕过本机 session 选择授权。

### 4.3 多 worker 部署

设备 relay 的撤销通知必须能到达持有 WebSocket pair 的 Server 进程。生产 Server
通过共享 Redis pub/sub 广播 `(device_session_id, generation)`；每个 worker 在提交后
先关闭本地 pair，再发布撤销事件，订阅 worker 只关闭本地 pair 而不重新广播。
Redis 不可用或订阅持续重连时不得开启设备控制 capability。数据库状态变为终态
本身不能关闭已经建立的 WebSocket。

## 5. 事件响应

以下任一事件进入本流程：设备或签名身份丢失、异常授权、未授权目的地连接、Claude 数据目录访问、
策略证明失败、重放/乱序告警、按键未释放、TCC/隐藏应用残留、发布签名键或证明键疑似泄露。

### 5.1 遏制

1. 从 Admin Web 强制停止所有受影响的设备 session，并记录 session ID、generation、停止时间和结果。
2. 撤销受影响设备；范围不明时撤销同一用户或部署范围内的全部可疑设备。
3. 若问题涉及共享组件、策略或密钥，把 `DEVICE_CONTROL_ENABLED=false` 重新部署并重启 Server，阻止
   新 session；同时由 MDM 负责人停用对应出站策略或证明服务。
4. 确认 lease 到期、relay 关闭、本机 UI 恢复、鼠标按键/修饰键释放。不要自动重放未确认动作。

### 5.2 证据保全与分析

保全发布摘要、签名/公证记录、外部 Endpoint Security 和 Network Extension 原始导出、零内容审计
记录、请求 ID、设备/session 标识、策略 ID、Team ID 和时间线。不要采集截图、输入、剪贴板、窗口
标题、token 或完整 HTTP/WebSocket payload。记录传感器丢事件计数和时钟来源；存在采集缺口时不得
把结论标为通过。

事件负责人确定最早暴露时间、受影响制品/策略/设备和需要轮换的凭据。Critical/High 事件必须完成
独立复核与复测后，才能重新签发发布证据。

### 5.3 恢复

先完成下节所需轮换，再构建新的协调 release，重新运行全部外部门禁和签名/公证验证。不得沿用受影响
版本的自报 JSON 或仅修改证据摘要。按第 3 节从 capability 关闭状态重新激活，并在恢复后提高零内容
审计和外部传感器监控频率。

## 6. 密钥与凭据轮换

### 6.1 设备令牌

定期轮换或单设备令牌疑似暴露时，先停止该设备的所有控制 session，然后在设备 Mac 上执行：

```sh
agent-remote device rotate-token --yes
agent-remote device diagnose
```

该命令使用本地 user token 调用控制面轮换端点，不打印新设备令牌，并把新令牌写入平台凭据存储和
共享 Network Broker Keychain 项。服务端会立即撤销旧设备令牌。若本机写入失败，按输出视为“远端
已轮换、本机清理/写入未完成”，不要恢复 session；重新登录或直接撤销设备。不得从 Admin Web 把
明文令牌复制到工单、终端历史或配置文件。

### 6.2 发布证据签名键

`DEVICE_CONTROL_RELEASE_PRIVATE_KEY_PEM` 只存在于受保护的
`production-device-release-evidence` 环境；Server 只持有对应公钥。常规轮换步骤为：

1. 保持 capability 关闭，离线生成新的 Ed25519 PKCS#8 私钥并建立双人审批和恢复记录。
2. 更新受保护环境私钥，使用当前协调 release 的全新原始证据生成新清单。
3. 在同一次 Server 部署中原子更新清单和 `DEVICE_CONTROL_RELEASE_PUBLIC_KEY`，再重启验证。
4. 验证旧公钥不能接受新清单、新公钥不能接受旧清单，并销毁可恢复副本之外的旧私钥。

疑似泄露时先关闭 capability、撤销受影响设备和当前部署清单，再执行轮换。schema 9 没有到期续签：
只有旧键未泄露、旧版本制品仍受支持且组合未被撤销时，才允许同时回滚旧公钥和旧清单；不得只回滚
其中一项。更换签名键或证据组合必须随新的根版本部署。

### 6.3 出站策略证明键

证明私钥归独立 MDM/Network Extension 策略服务所有；签名 Network Broker 只固定 32 字节公钥、
mach service 和策略 ID。改变其中任何一项都要求新的签名、公证 App 和新的协调 release，不能只改
服务器 JSON。

轮换时先关闭 capability 并结束 session，发布绑定新公钥的 App，更新策略服务私钥和 MDM 配置，
重新安装 App，然后收集新的 challenge-bound 主动探测和隔离证据。新旧设备不得共用一份声称代表两套
策略的 `outbound-policy` 记录。旧证明键疑似泄露时不得回滚；保持关闭直到新 App、策略和证据全部
通过。

## 7. 回滚与演练

应用不支持降级安装。回滚必须结束 session、关闭 capability、撤销受影响设备，重新安装仍受支持且
具有匹配 schema 8 或 9 发布证据和签名公钥的版本；若该版本的密钥、策略或制品受事件影响，则不能回滚，只能前向修复。恢复
后重新注册/轮换设备凭据并执行第 3 节验证。

Computer Use v2 出现部分 capability、错误目标、敏感遥测、stale/坐标 fallback 激增、成功率回退、
延迟超阈值时，先把 `DEVICE_CONTROL_V2_ENABLED` 设为 `false`，阻止
新 generation 进入 v2；随后终止受影响的活动 device session，确认本机释放输入并恢复隐藏应用，再由
用户重新选择 session 并建立受支持的新 generation。full-trust 模式不得回退为不完整 v1；禁止原地
降级活动 generation，也禁止自动重放执行状态未知的动作。
若问题涉及签名、密钥、隔离或出站策略，继续把 `DEVICE_CONTROL_ENABLED` 设为 `false` 并执行事件响应，
不能只回退 v2 百分比。

每季度以及每次安全相关发布前演练：Server/设备撤销、Esc、Executor 崩溃、lease 到期、relay 断开、
锁屏、设备令牌轮换、两类 Ed25519 键轮换、升级失败、TCC 残留和隐藏应用恢复。演练报告必须绑定精确
制品摘要并保持零内容；失败项进入发布阻塞清单，不能用本运行手册的存在替代实际证据。

每次相关发布还应演练：`true -> false` 的新 generation 选择、活动 v2 session 终止、重新选择后的
受支持工具面、Node 缺失任一 full-trust capability，以及回滚期间没有动作自动重放。该演练可纳入 schema 9 中的可选质量
证据，但不是运行时依赖。
