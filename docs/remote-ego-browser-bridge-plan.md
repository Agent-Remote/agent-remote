# Ego-browser Bridge 当前边界与发布状态

本文是 root 仓库对 `agent-remote-ego-browser` Bridge 的当前索引。它只描述现有代码和可核对的发布证据；详细协议、部署步骤和安全约束分别以同目录验收、部署和安全文档为准。

## 当前产品边界

- 远端 `fclaude` 通过受限 Bridge 请求本机已明确绑定的 ego-browser runtime；远端不启动第二个浏览器，也不直接获得 CDP 或通用远程桌面能力。
- Bridge 使用 owner-only 本机 IPC、出站 relay、绑定 generation、短租约、序列号、一次性 permit 和显式 stop/revoke。未知结果保留原 binding 身份，不自动重放。
- 本机 runtime 与当前登录用户同 UID，且 full-trust 模式不提供 sandbox。用户可见确认、权限警告和 stop/revoke 是产品边界的一部分；Bridge 不把 full-trust 误称为浏览器操作沙箱。
- 请求、artifact 和学习资源受固定 schema、大小上限、canonical path allowlist、版本/摘要绑定和零内容日志约束。浏览器页面内容不写入控制面数据库、普通审计或指标。
- 当前支持的发布组合和 capability 由 release manifest 固定。未知版本、能力、binding、generation、role 或 permit 一律 fail closed。

## 当前发布记录

根清单中的 Bridge 条目记录当前组件级 `production_ready`、`release_published`、证书 pin、learning bundle digest、制品摘要和嵌套签名。该字段只表示 manifest 内的自动化 promotion 条件；部署 profile 的 capability 默认保持关闭，只有最终部署方完成本节门禁并显式启用后才可执行真实流量。版本、commit 和 digest 必须从已验证根清单读取，未绑定最终 manifest 的候选包不继承该状态。

## 已有实现与证据

- Bridge、Device Client、Linux wrapper、Server relay、Node broker、CLI 和 Admin 的协议测试、竞态测试、撤销/恢复测试和真实分布式 relay E2E 已接入。
- 当前验收记录见 [`ego-browser-bridge-acceptance.md`](ego-browser-bridge-acceptance.md)，其中明确区分自动化、合成 E2E、开发 runtime canary 和发布组合证据。
- 部署、升级、轮换、恢复和清理流程见 [`ego-browser-bridge-deployment.md`](ego-browser-bridge-deployment.md)。安全边界见 [`ego-browser-bridge-security.md`](ego-browser-bridge-security.md)。
- 已验证的能力包括：绑定/暂停/恢复/停止/撤销、generation 轮换、断线与超时 fail closed、owner-only listener、artifact 清理、Task Space 复用和独立卸载。

## 当前未完成的发布门禁

1. 用最终 release manifest 绑定的制品完成登录站点真实 runtime canary，覆盖导航、Snapshot、输入、点击、截图、Task Space 复用、显式 full-trust bypass、断线和清理。
2. 在最终签名/公证或明确的社区签名组合上复验部署证据、SBOM、provenance、certificate pin、learning bundle digest 和内容零泄漏审计。
3. 运行 exact tagged commits 的全部跨仓库质量门禁，并把原始报告摘要写入最终 evidence artifact。

开发机上的 fake relay、合成 fixture、临时 runtime 和旧版本记录不能直接标记生产 ready。发布前必须重新解析最终 manifest 的版本、commit、摘要和策略；不得用修改配置的方式跳过 canary 或门禁。

## 相关事实源

- [`ego-browser-bridge-acceptance.md`](ego-browser-bridge-acceptance.md)：验收项目与证据状态。
- [`ego-browser-bridge-deployment.md`](ego-browser-bridge-deployment.md)：安装、升级、恢复和清理。
- [`ego-browser-bridge-security.md`](ego-browser-bridge-security.md)：权限、数据和网络边界。
- `../agent-remote-ego-browser/README.md` 与其 `docs/`：实现 API、wrapper 和 release tooling。
