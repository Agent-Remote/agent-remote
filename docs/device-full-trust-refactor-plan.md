# Device 控制当前合同与发布门禁

本文只记录当前 Device 控制代码提供的会话级授权合同。实施阶段、旧产品决策和历史版本不属于当前文档。

## 当前合同

- 用户必须明确选择一个远程 Claude tool session，授权绑定只属于该 session 和当前 Device generation。
- `pending_device`、`active`、`paused`、`stopped` 和 `revoked` 分别表示不同生命周期状态；空审批记录不能推导授权。
- Device Client、Server、Node、Bridge 各自验证完整的 user/device/session/generation/context；未知结果保留原 request key，不重放。
- 活跃绑定使用受保护 relay、租约、单调序列、一次性 permit 和 owner-only 本机 IPC；断线、撤销、过期、Task Space 所有权变化或监控失败均 fail closed。
- 当前 capability 协商支持受控 Computer Use v2；缺失或畸形 capability 时，新 generation 完整回退 v1，活动 generation 不中途降级。
- 浏览器 profile、登录状态、脚本正文、截图和剪贴板内容留在本机运行边界，不写入 Server 或通用审计日志。
- 旧 API 和旧 approval 数据只作为兼容读取路径存在，不能为新 session 授权，也不能覆盖当前 generation 的撤销结果。

## 当前发布配置

根 `release-manifest.json` 使用 schema 4 固定组件版本、commit 和 artifact；Device 控制的独立签名 evidence 使用 schema 9，并绑定同一根发布组合。Community local-trust 是当前支持的自托管配置，仍要求管理员接受自签名、手动信任和无系统级网络过滤的边界。

生产 capability 默认关闭。只有最终制品、签名 evidence、目标主机权限和真实运行验收全部绑定到同一发布组合后，部署方才可以启用它。

## 仍需的外部证据

- 真实签名安装包上的 macOS Accessibility、Screen Recording、锁屏、睡眠、网络切换、TCC 撤销和崩溃恢复。
- 新旧 Server/Node/Device/Bridge 混合版本矩阵，以及真实 Claude Code/MCP 会话。
- 独立安全评审、最终制品签名、SBOM/provenance 和发布组合审计。

仓库合同、合成 E2E 和 fixture 不能替代这些目标主机证据。操作顺序见 [`device-control-operations-runbook.md`](device-control-operations-runbook.md)，安全边界见 [`local-device-control-security-design.md`](local-device-control-security-design.md)。
