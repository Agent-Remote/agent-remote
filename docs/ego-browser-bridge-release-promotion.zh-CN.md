# ego-browser Bridge 发布晋级

根 composition 在 Bridge 有真实已发布 release、受保护 Site Learning 签名 key 和完整证据前曾必须保持阻塞。原四项 blocker 是证据要求，不是可以切换的配置开关。Bridge `0.1.9` 现在已经清除四项 blocker，stable root `0.2.26` release 也已将这次晋级绑定到 tag-bound schema 9 evidence；剩余工作是安装准确的 certified bundle，并完成最终 canary：

| 当前 blocker | 清除它所需的真实证据 | 记录位置 |
| --- | --- | --- |
| `unpublished_component_commit` | Bridge 有 clean commit、不可变 `vVERSION` tag，以及已发布且非 draft、非 prerelease 的 GitHub Release | 根 Bridge component 的 `commit` 与 `release_published=true` |
| `release_certificate_unpinned` | 持久 community P12 为 Bridge、Device Client 和 learning verifier 签名；叶证书 SHA-256 通过独立可信渠道分发，并与全部签名记录一致 | `signer_certificate_sha256` 与 Bridge signing evidence |
| `learning_bundle_signing_private_key_unavailable` | 恢复与 verifier 内置 production public key 匹配的受保护私钥，签发只读 bundle；verifier 返回固定 SHA-256 和 key ID | `learning_bundle_digest`、key ID 与 nested signatures |
| `production_release_evidence_unavailable` | 组件、制品、SBOM、Sigstore、provenance、canary 和风险证据全部组装为 schema 9，并由 deployment key 签名且绑定 candidate manifest hash | 已签名 schema 9 production evidence |

不要手工编辑 `production_ready`、`release_published` 或 blocker 列表。晋级工具会重新计算这些字段，并拒绝不匹配或只完成一部分签名的输入。测试私钥、开发 digest 和 prerelease 都不能清除 blocker。

开始晋级前，必须先发布包含 schema 9 Bridge admission 修复的
`agent-remote-server` 版本。当前已晋级的 root manifest 固定 Server `0.2.15` 及已评审 commit；
candidate 和 evidence 必须继续绑定该准确版本（或后续已评审替代版本）。不得把更旧 Server
release 用作生产 Bridge control plane。

## 固定顺序

1. 在 `agent-remote-ego-browser` 中完成评审后的源码、完整 quality gate、clean commit 和精确 `vVERSION` tag，push 两者，并让 tag-bound release workflow 发布全部制品。GitHub Release 必须 stable，不能是 draft 或 prerelease。
2. 在受保护的 `production-community-release` environment 配置持久 P12、signing identity 和小写证书 SHA-256。恢复与 Bridge verifier 内置 public key 匹配的 Site Learning 私钥，签发只读 bundle，记录 verifier digest 和 key ID。
3. 下载准确的 Bridge release manifest、macOS archive、checksums、signing evidence、Sigstore bundles 与 provenance。checkout 同一 Bridge tag，校验 clean HEAD、制品 inventory、nested signatures、证书 pin、stable GitHub Release 和 learning digest。
4. 生成 canonical root candidate。此阶段不修改 `release-manifest.json`，也不消耗 production evidence：

   ```sh
   python3 scripts/promote-ego-browser-release.py \
     --manifest release-manifest.json \
     --bridge-repository ../agent-remote-ego-browser \
     --bridge-release-manifest /secure/release/agent-remote-ego-browser-VERSION.release-manifest.json \
     --bridge-release-archive /secure/release/agent-remote-ego-browser-macos-universal-VERSION.tar.gz \
     --bridge-artifact-dir /secure/release \
     --bridge-signing-evidence /secure/release/agent-remote-ego-browser-macos-universal-VERSION.community-signing.json \
     --bridge-archive-sigstore /secure/release/agent-remote-ego-browser-macos-universal-VERSION.tar.gz.sigstore.json \
     --bridge-manifest-sigstore /secure/release/agent-remote-ego-browser-VERSION.release-manifest.json.sigstore.json \
     --bridge-provenance /secure/release/bridge-provenance.json \
     --learning-bundle /secure/release/learning-bundle \
     --learning-bundle-verifier ../agent-remote-ego-browser/scripts/verify-learning-bundle.sh \
     --certificate-sha256 CERTIFICATE_SHA256 \
     --learning-bundle-key-id KEY_ID \
     --commit BRIDGE_COMMIT \
     --version VERSION \
     --prepare-only \
     --candidate-output /secure/release/root-candidate.json
   ```

   命令会打印 candidate SHA-256。保留 candidate 原始字节和该 hash，作为 evidence signer 的输入。
5. 在受保护的 release environment 中生成绑定 candidate 的 schema 9 evidence。仓库内的
   `community-device-control-release-evidence.yml` 刻意要求准确 tag，并读取已提交的
   `release-manifest.json`；根 manifest 仍阻塞时，它不能直接消费这个未提交 candidate。
   不要临时提交 candidate，也不要编辑阻塞中的 manifest 让 workflow 通过。release owner
   必须完成以下受保护的手工/审核步骤：

   - 将 candidate 复制到 owner-only、不可覆盖的路径并校验 SHA-256；
   - checkout 已评审的 root source 和每个 component tag，执行 community workflow 中相同的
     制品、checksum、Sigstore、provenance、漏洞和 canary 校验；
   - 调用 `scripts/assemble-community-device-control-release-evidence.py`，传入
     `--release-manifest /secure/release/root-candidate.json`（以及 candidate 中的
     distribution/server version），并提供 workflow 原有的全部 artifact 与 gate 输入；
   - 使用受保护 deployment key，通过 Server 的
     `create_device_control_release_evidence.py` 为 `release-evidence-draft.json` 签名，并用
     pinned public key 验签；
   - 保留签名输出和审计日志，不覆盖任何已有文件。

   签名记录必须包含 candidate manifest SHA-256 和全部六个 `ego_browser_*` digest 字段。
   `release_manifest_sha256` 必须从 candidate 原始字节重新计算，不能取当前阻塞中的 root
   manifest。当前这是受保护的手工/审核步骤；只有晋级后的 manifest 已提交并打 tag 后，才可
   使用普通 tag-bound workflow。
6. 只有 schema 9 evidence 已生成后，才原子应用 candidate：

   ```sh
   python3 scripts/promote-ego-browser-release.py \
     --manifest release-manifest.json \
     --bridge-repository ../agent-remote-ego-browser \
     --bridge-release-manifest /secure/release/agent-remote-ego-browser-VERSION.release-manifest.json \
     --bridge-release-archive /secure/release/agent-remote-ego-browser-macos-universal-VERSION.tar.gz \
     --bridge-artifact-dir /secure/release \
     --bridge-signing-evidence /secure/release/agent-remote-ego-browser-macos-universal-VERSION.community-signing.json \
     --bridge-archive-sigstore /secure/release/agent-remote-ego-browser-macos-universal-VERSION.tar.gz.sigstore.json \
     --bridge-manifest-sigstore /secure/release/agent-remote-ego-browser-VERSION.release-manifest.json.sigstore.json \
     --bridge-provenance /secure/release/bridge-provenance.json \
     --learning-bundle /secure/release/learning-bundle \
     --learning-bundle-verifier ../agent-remote-ego-browser/scripts/verify-learning-bundle.sh \
     --certificate-sha256 CERTIFICATE_SHA256 \
     --learning-bundle-key-id KEY_ID \
     --commit BRIDGE_COMMIT \
     --version VERSION \
     --candidate-manifest /secure/release/root-candidate.json \
     --production-evidence /secure/release/device-control-release-evidence-VERSION.json \
     --production-evidence-public-key "$(cat deploy/compose/community-release-public-key.txt)"
   ```

   工具会再次校验全部输入、candidate hash 和签名，并用 `fsync` 支持的原子写替换根 manifest。任何失败都保持原 manifest 字节不变。
7. review 新 manifest 并在 root `main` 提交。用新的 distribution version 运行 root
   `prepare-release.yml`；版本变化也会改变 root manifest hash，因此 tag-bound community
   workflow 必须为新 tag 重新生成 schema 9 evidence。不要部署 tag 之前的 candidate evidence，
   也不要复用晋级前的 distribution tag。
8. 部署准确 bundle，完成 artifact-bound Admin 与真实 logged-in ego lite canary，最后才能设置 `EGO_BROWSER_BRIDGE_ENABLED=true`。运行时配置不能绕过 false 或缺失的 release manifest。

最终部署包的 `.env.example` 还必须写入
`EGO_BROWSER_EXPECTED_DISTRIBUTION_VERSION`、
`EGO_BROWSER_EXPECTED_ROOT_MANIFEST_SHA256`、
`EGO_BROWSER_EXPECTED_LEARNING_BUNDLE_SHA256`，以及六个
`EGO_BROWSER_EXPECTED_BRIDGE_*_SHA256`。这些是 Server 独立的 deployment pin，
只能从最终 tag-bound schema 9 evidence 和 root manifest 复制；root manifest
或任一 Bridge 制品变化后必须全部重新生成。

第一阶段可用新的 output path 重复执行。不要原地替换已有 candidate 或 evidence 文件。如果 Bridge commit、tag、certificate、learning digest、制品或 evidence hash 有任何变化，丢弃 candidate，从第 3 步重新开始。

## 状态检查

```sh
jq '.components["agent-remote-ego-browser"] |
  {commit, release_published, production_ready, readiness_blockers,
   signer_certificate_sha256, learning_bundle_digest,
   nested_signatures_verified}' release-manifest.json
python3 scripts/check-device-control-release-readiness.py \
  --manifest release-manifest.json
```

原始阻塞状态是 `release_published=false`、`production_ready=false`，并带有上表四项 blocker。
当前晋级后的 root component 已是 `release_published=true`、`production_ready=true`，且
`readiness_blockers=[]`。这不会自动打开 capability；stable root `0.2.26` release 已包含
tag-bound evidence，但仍需部署其准确的 certified bundle 并完成最终 logged-in canary。
