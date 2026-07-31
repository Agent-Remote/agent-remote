# Community Local-Trust 生产发布

`community-local-trust` 是不依赖 Apple Developer Program 的正式自托管发布配置。它允许发布清单声明
`production_ready=true`，但同时必须声明 `apple_notarized=false`、`public_distribution=false` 和
`manual_trust_required=true`。该配置只适用于知情管理员控制的 Mac，不表示 Apple 已验证应用，也不适合
面向不受控终端的一键公开分发。

## 信任边界

GitHub 官方 runner 构建所有制品。macOS App、Network Broker XPC 和 GUI Executor XPC 使用同一份长期
项目自签名证书，并启用 Hardened Runtime。XPC 同时校验当前用户、精确 bundle identifier 和固定证书
SHA-1；SHA-1 仅用于 macOS requirement language 的证书定位，发布记录另外携带证书 DER 的 SHA-256。

安装器验证归档 SHA-256、GitHub Actions Sigstore bundle、provenance、三个 bundle 的代码签名及固定证书
身份后，才移除 quarantine 并安装。自签名证书不获得 Gatekeeper 或 Apple notarization 信任。

Network Broker 在此配置中使用应用级出站策略：控制面 origin 只来自本机登录凭据，必须为规范化 HTTPS
origin，远端 session、MCP 参数和项目文件均不能覆盖；Broker 拒绝 IP literal、非 DNS hostname 以及
Anthropic/Claude 域。此控制不等价于 MDM 或 Network Extension。

## 强制门禁

以下条件全部满足时，community 清单才允许写入 `production_ready=true`：

1. 六仓库同版本不可变 tag、CI、协议测试、跨组件 E2E 和 fuzz 通过。
2. 已知 Critical/High 依赖漏洞为零。
3. App 和两个 XPC 的 bundle identifier、Hardened Runtime、嵌套签名及固定证书身份通过验证。
4. SHA-256、SPDX SBOM、Sigstore workflow identity 和 GitHub provenance 通过验证。
5. 官方 macOS runner 完成安装器、代码签名和 XPC 启动自检；目标 Mac 未授予 Accessibility 与
   Screen Recording 时应用保持不可用，并在首次会话前引导用户授权。
6. 发布清单由部署方 Ed25519 密钥签署，绑定 Server、Node、App、proxy 和上述证据摘要。
7. 管理员显式接受未公证、手动信任、无系统级出站过滤和无独立第三方评审的剩余风险。

Apple Developer ID 配置仍使用原严格门禁。两种配置不得共享或转换签名/公证状态字段。

## GitHub 环境

Device 仓库使用 `production-community-release`，包含：

- secret `COMMUNITY_SIGNING_P12_BASE64`
- secret `COMMUNITY_SIGNING_P12_PASSWORD`
- secret `COMMUNITY_SIGNING_IDENTITY`
- variable `COMMUNITY_SIGNER_CERTIFICATE_SHA1`

Root 仓库继续使用 `production-device-release-evidence` 保存发布清单 Ed25519 私钥。community profile 不再
依赖自托管 runner 或 `production-device-release-gates` 本地目录；运行期权限仍由目标 Mac 用户显式授予。

官方清单验证公钥固定在 `deploy/compose/community-release-public-key.txt`，Compose 示例已引用同一个
Base64 raw Ed25519 公钥。私钥的本地备份位于 git-ignored 的
`dist/community-release-evidence-key`，必须另行离线备份。

## 明确接受的风险

- Gatekeeper 不会把 App 识别为已验证开发者，安装必须显式移除 quarantine。
- 项目自签名私钥泄露后，攻击者可以伪造本机组件；轮换会改变身份并可能要求重新授权 TCC。
- 应用级目的地校验不能替代系统网络过滤器，也不能证明进程没有通过未知缺陷泄漏数据。
- 未完成独立安全评审时，生产判断属于部署方风险接受，而不是第三方安全认证。
