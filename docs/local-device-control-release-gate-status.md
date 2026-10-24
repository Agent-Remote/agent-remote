# 本机设备控制发布门禁状态

更新：2026-10-24。本文只记录当前 Device/Server/Node/CLI/Admin 代码的证据边界。生产设备控制继续默认关闭；仓库合同、合成 E2E 和 fixture 不能替代目标主机证据。

| 门禁 | 当前状态 | 仍需的证据 |
| --- | --- | --- |
| 依赖、静态检查和协议合同 | 已通过当前仓库质量门禁 | 将最终 tag-bound 组件和签名扫描报告绑定到根清单 |
| session-level full-trust 生命周期 | 代码和合同已实现 | 真实签名安装包上的 claim、pause、resume、stop、revoke、抢占和未知结果恢复 |
| Computer Use v2 协商 | 代码已实现，缺失 capability 时新 generation 回退 v1 | 真实 Claude Code/MCP 会话和新旧组件混合版本矩阵 |
| 本机权限与安全边界 | 自动化 fail-closed 合同已实现 | macOS Accessibility、Screen Recording、TCC 撤销、锁屏、睡眠、网络切换和崩溃恢复 |
| 发布供应链 | 根 manifest schema 4 与 Device-control evidence schema 9 的绑定代码已实现 | 最终制品签名、SBOM、provenance、证书 pin、learning bundle 和独立复核 |
| Community local-trust | 当前支持；自签名、手动信任和应用级出站策略边界已明确 | 目标 Mac 安装、单用户 ego lite canary 和部署方风险接受 |
| 数据与日志边界 | 零内容 schema、bounded error 和审计合同已实现 | 真实运行中确认浏览器内容、剪贴板和脚本正文不落盘、不进日志 |

## 当前运行语义

- 新绑定必须来自用户选择的准确 session；空 approval、历史成功回执和默认设备都不能授予新授权。
- binding generation、lease、sequence、caller proof 和 Task Space ownership 必须同时匹配；断线、撤销、过期、监控失败或未知结果均 fail closed。
- Device/Bridge 的本机 profile 和凭据不进入 Server；Server 只保存有界生命周期、策略、请求 ID 和结果码。
- `production_ready` 只表示组件/证据组合满足自动化发布条件，不能单独开启生产 capability。

## 验收入口

```sh
python3 scripts/check-device-control-release-readiness.py \
  --manifest release-manifest.json --require-clean --require-tag --require-origin
```

目标主机验收必须使用最终制品、临时账号和一次性 session；结束后删除临时凭据、profile、relay 状态、日志、socket、工作区和 evidence。发布、上传、tag 和生产切换由操作者另行决定。

相关文档：[`device-control-release-evidence.md`](device-control-release-evidence.md)、[`device-control-operations-runbook.md`](device-control-operations-runbook.md)、[`community-local-trust-release.md`](community-local-trust-release.md)。
