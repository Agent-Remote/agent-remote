# Community local-trust 升级流程

本文记录当前社区自托管组合的升级顺序。准确版本、commit、artifact digest 和 evidence 只从已验证的根 `release-manifest.json` 读取；本文不固定版本号，也不替代发布负责人对候选组合的审核。

## 升级前

1. 备份数据库、Skill 内容和 Node 本地状态，见 [`backup-restore.md`](backup-restore.md)。
2. 对候选根清单运行完整的组件、迁移、合同和制品验证：

   ```sh
   python3 scripts/check-device-control-release-readiness.py \
     --manifest release-manifest.json --require-clean --require-tag --require-origin
   ```

3. 确认候选清单绑定同一 Server、Node、CLI、Admin Web、Device 和 ego-browser 组合；不要跨版本复制 evidence、证书或学习 bundle。
4. capability 保持关闭，先在一次性环境执行升级和回滚演练。

## 部署顺序

1. 升级 Server，等待数据库迁移完成并检查 `/healthz`；所有 Server worker 必须使用相同数据库、内容目录和 release evidence。
2. 升级 Node 与 runtime/helper；验证运行时依赖、工作区 ACL、WireGuard 端口和心跳能力。
3. 升级 CLI 与 Admin Web；确认登录、设备、账户、会话、同步和恢复查询仍使用原始上下文。
4. 按目标 Mac 的已验证 artifact 安装 Device Client 和 ego-browser Bridge；保留本机 profile，不上传浏览器数据。
5. 对一个一次性测试 session 执行 setup、claim、status、pause、resume、stop 和 revoke；确认未知结果不会生成第二个请求。
6. 复核签名、SBOM、provenance、证书 pin、学习 bundle digest、权限和日志零内容约束。
7. 只有目标主机、真实 Claude Code/MCP 会话、混合版本矩阵和所有外部门禁都通过后，部署方才可以显式开启 capability。

## 回滚

回滚必须选择同一根清单中已经验证的旧组合。先关闭 capability，再按相反顺序恢复 Server、Node、CLI/Admin 和本机组件；保留数据库迁移和不可变回执，不删除请求 journal，不重放未知结果。回滚后重新验证健康检查、设备撤销、会话停止、同步清理和日志边界。

正式发布、tag、上传和生产切换是独立的操作者决定；本流程不会自动执行这些动作。所有测试使用一次性数据，完成后删除测试用户、session、workspace、容器、socket、日志和 evidence。

相关合同：[`device-full-trust-refactor-plan.md`](device-full-trust-refactor-plan.md)、[`device-control-release-evidence.md`](device-control-release-evidence.md)、[`upgrade.md`](upgrade.md)。
