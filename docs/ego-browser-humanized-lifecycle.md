# Ego-browser Bridge 生命周期合同

本文记录当前 Bridge 的用户可见生命周期和安全语义。实现细节以 `agent-remote-ego-browser` 仓库代码、协议和 release manifest 为准；验收证据以 [`ego-browser-bridge-acceptance.md`](ego-browser-bridge-acceptance.md) 为准。

## 生命周期

1. 用户明确选择远端 `fclaude`、本机 browser binding 和 release profile。
2. Server、Node、Device Client、CLI 和 Bridge 共同校验 user、device、tool session、binding、generation、role、版本和 capability。
3. claim/connect 成功后才取得短租约和一次性 permit；Bridge 仅接受该 binding 的请求。
4. pause 关闭新的执行 admission 但保留 binding；resume 必须显式确认并使用新的 generation。
5. stop/revoke 终止当前 generation，清理本地 supervisor、socket、artifact 和 lease；历史结果不可重新授权执行。
6. 断线、超时、版本/摘要不匹配、监控或权限证明失败均进入 fail-closed 或 pending，恢复时查询原 binding 身份。

## 用户可见保证

- 页面和工具明确说明本机 runtime 与用户同 UID、full-trust 不提供 sandbox、脚本可能读取本机可访问数据，Bridge 不会把这种能力描述成隔离浏览器。
- 操作状态区分 `pending`、`connected`、`paused`、`stopping`、`revoked`、`unknown` 和 `failed`。连接成功不代表请求完成；停止或撤销成功不代表历史页面内容已保存。
- stop、revoke、Task Space takeover、文件上传和截图等动作都绑定精确目标和用户确认。结果未知时只提供 query/reconcile，不自动提交第二次动作。
- 页面内容、凭据、private key、relay ticket 和原始 heredoc 不进入普通日志、指标或 root UI；受控 artifact 只在明确 allowlist、类型和大小限制内收集并在完成后清理。

## 当前实现证据

当前自动化和分布式 relay 证据覆盖 binding generation、permit、lease、sequence、并发锁、撤销、断线、恢复、Task Space 复用、artifact 清理、owner-only IPC 和卸载隔离。开发 runtime canary 已验证导航、Snapshot、输入、点击和截图，但仍需用最终发布组合完成登录站点 canary。

详见：

- [`ego-browser-bridge-acceptance.md`](ego-browser-bridge-acceptance.md)
- [`ego-browser-bridge-deployment.md`](ego-browser-bridge-deployment.md)
- [`ego-browser-bridge-security.md`](ego-browser-bridge-security.md)
- `../agent-remote-ego-browser/docs/`

## 发布门禁

正式启用前必须用最终 release manifest 复验版本/摘要/签名、登录站点真实 runtime、显式 full-trust bypass、断线与清理，并将原始报告摘要绑定到最终 evidence artifact。旧版本历史记录、fake relay 和合成 fixture 只能作为开发证据，不能替代这次发布组合验证。
