# ego-browser Bridge 发布晋级

本文只描述当前证据晋级合同。准确版本、commit、制品 digest 和组件就绪状态由已验证的根 `release-manifest.json` 提供；本文不复制任何历史版本或固定 tag。

## 必需证据

- Bridge 组件具有干净、已评审的源码 commit，发布制品的 manifest、checksum、签名和 provenance 相互一致。
- 根清单固定 Server、Node、CLI、Admin Web、Device 和 Bridge 的准确发布组合。
- Community local-trust evidence 绑定候选根清单原始字节、组件身份、artifact/SBOM/provenance digest、证书 pin 和 learning bundle digest。根清单使用 schema 4；设备控制签名 evidence 文档使用 schema 9。
- 目标 macOS 安装通过证书、Hardened Runtime、权限、relay、Task Space 和已登录 ego lite canary 验证。
- 所有证据组装并独立复核前，生产 capability 必须保持关闭。

## 晋级顺序

1. 使用各仓库质量门禁构建并验证每个组件，把候选制品放在 owner-only 临时目录。
2. 只通过仓库发布工具更新候选根清单；校验 schema、组件 commit、origin、制品 inventory 和依赖 pin。
3. 针对候选清单原始字节组装 schema 9 evidence。使用受保护 deployment key 签名，并验证签名和全部绑定 digest。
4. 在一次性目标 Mac 安装准确候选，执行真实 Bridge canary。只记录有界状态、ID、digest 和结果码。
5. 由发布负责人复核候选、evidence、目标主机记录和风险接受；复核完成后才能应用到发布分支。
6. 在任何发布或启用 capability 前，针对最终 tag-bound 清单和 evidence 再跑一次验证。

晋级脚本会拒绝缺失、不匹配、过期或只完成部分签名的 evidence。手工编辑 `production_ready`、`release_published`、blocker 或 digest 无效。canary 失败或未知时必须保留失败/未知状态，不能通过重放请求或选择新 session 修复。

发布、上传、打 tag 和启用生产 capability 都是独立的操作者决定。每次演练结束后必须删除临时凭据、profile、session、socket、制品和日志。
