# Local ego-browser Bridge 验收状态

更新：2026-10-24。Bridge 的组件版本、commit、artifact digest、Skill/runtime 版本和签名信息以根 `release-manifest.json` 的 `agent-remote-ego-browser` 条目为准；本文不复制固定版本号。

## 当前合同

- 远程 Skill 保持官方 heredoc 接口，经 Node broker 和 Server opaque relay 连接到本机 outbound-only Bridge。
- 用户必须显式选择一个准确的 remote tool session 并确认 full-trust；Bridge 不自动选择 session，也不提供远程浏览器、CDP 或 LAN listener。
- Device/Server/Node/Bridge 共同验证 binding generation、租约、序列、PoP、Task Space 所有权和 capability；断线、撤销、过期、监控失败或未知结果均 fail closed，不重放请求。
- 浏览器 profile、登录状态、脚本正文、截图和剪贴板内容留在本机边界；控制面只保存有界生命周期、策略和审计元数据。
- `native` 与 `docker_sandbox` 远端 runtime 都必须通过各自的能力和身份检查；不能静默降级或绕过 exact context。

## 组件证据

根 manifest 当前可表达组件级 `production_ready`、`release_published`、签名、学习 bundle 和 readiness blockers。即使 `production_ready=true`，也只表示组件级 evidence 完整；组件就绪不等于目标部署已经安装、登录并完成真实 ego lite canary。部署仍必须使用同一根组合和独立的目标主机证据。

已覆盖的自动化边界包括严格 schema、caller authorization、replay rejection、relay 生命周期、Task Space ownership、敏感内容不落盘、安装器校验和卸载隔离。合同/fixture 不能替代真实签名安装包上的 TCC、权限、睡眠/网络切换和登录用户 canary。

## 发布前门禁

1. 使用根 manifest 固定的完整组件组合和签名 evidence。
2. 在受控 macOS 目标机验证 Bridge 安装、证书 pin、Hardened Runtime、权限引导、升级、回滚和卸载隔离。
3. 完成一次性真实 ego lite 用户 canary，确认 claim、pause、resume、stop、revoke、Task Space takeover 和未知结果恢复。
4. 绑定原始报告、artifact digest、SBOM/provenance 和风险接受记录；在全部证据通过前保持 Server capability 关闭，生产 capability 不能提前启用。根清单的 `production_ready` 字段不能替代目标主机证据。

测试必须使用一次性账号、session、profile 和 workspace；结束后删除凭据、relay 状态、临时文件、日志和 evidence。发布与上传由操作者另行决定。

相关文档：[`ego-browser-humanized-lifecycle.md`](ego-browser-humanized-lifecycle.md)、[`ego-browser-bridge-deployment.md`](ego-browser-bridge-deployment.md)、[`ego-browser-bridge-security.md`](ego-browser-bridge-security.md)。
