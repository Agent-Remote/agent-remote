# Session Full-Trust Community 发布与升级手册

本文用于本次 `session_full_trust` 功能的 `community-local-trust` 发布、服务器升级和 macOS
本地程序升级。当前发布不要求 Apple Developer ID、公证或 Apple 真实 E2E；不得把合成 E2E、合同测试
或本次人工 Community 验收描述为 Apple 证据。真实新旧制品的五场景混合版本矩阵留到后续 Community
版本升级时执行。

本文中的命令只应由发布负责人逐步执行。不要并行触发多个 `prepare-release`，也不要跳过任一 CI 或
制品检查。

## 1. 本次版本与严格顺序

若下列版本在正式执行前已被占用，所有后续 patch 版本整体顺延，并同步替换本文命令中的变量。

| 顺序 | 仓库 | 当前版本 | 本次建议版本 | 说明 |
| --- | --- | --- | --- | --- |
| 1 | `agent-remote-device` | `0.2.11` | `0.2.12` | 先发布 macOS App 和四架构 standalone proxy |
| 2 | `agent-remote-node` | `0.2.12` | `0.2.13` | 必须嵌入并固定 Device `0.2.12` proxy |
| 3 | `agent-remote-server` | `0.2.10` | `0.2.11` | 包含 migration `0017_device_authorization` |
| 4 | `agent-remote-admin-web` | `0.2.8` | `0.2.9` | 展示授权策略和能力状态 |
| 5 | `agent-remote` | `0.2.18` | `0.2.19` | 最后固定全部组件并发布部署 bundle |

`agent-remote-cli` 本次没有代码修改，不需要发布；根清单继续固定已发布的 `0.2.9` 和 commit
`0cc856ab82378de0c9412bf4b639a64114f7eeef`。Community CLI 内置 Device 项目自签名证书指纹，
因此 Device 必须继续使用原有的持久化 Community 证书；不要为本次发布临时生成新证书。若证书确实
需要轮换，必须另行发布匹配新指纹的 CLI，并把它插入 Device 之前发布。

严格依赖为：

```text
Device release -> Node dependency pin -> Node release
                                      \
Server release ------------------------+-> Root manifest -> Root release
Admin Web release ---------------------/
Existing CLI v0.2.9 ------------------/
```

每个仓库内部必须遵循两个门禁：

```text
功能修改 commit -> push main -> 该 commit 的 ci.yml 成功
-> prepare-release -> release commit/tag -> release.yml 成功
```

`prepare-release` 会自行运行准备脚本、生成 `chore: release vX.Y.Z` 提交、push `main`、创建 tag，
并以该 tag 显式 dispatch `release.yml`。不要在本流程外手工再创建同名 tag 或重复触发 release。

## 2. 发布前一次性检查

在操作者电脑设置路径和版本变量：

```sh
export RELEASE_ROOT=/Users/rem/Documents/Git
export DEVICE_VERSION=0.2.12
export NODE_VERSION=0.2.13
export SERVER_VERSION=0.2.11
export ADMIN_VERSION=0.2.9
export CLI_VERSION=0.2.9
export ROOT_VERSION=0.2.19
```

确认 GitHub CLI 已登录正确账号，所有仓库的 `main` 与 `origin/main` 同步，并确认目标 tag 不存在：

```sh
gh auth status
for item in \
  "agent-remote-device:$DEVICE_VERSION" \
  "agent-remote-node:$NODE_VERSION" \
  "agent-remote-server:$SERVER_VERSION" \
  "agent-remote-admin-web:$ADMIN_VERSION" \
  "agent-remote:$ROOT_VERSION"; do
  repo=${item%%:*}
  version=${item#*:}
  git -C "$RELEASE_ROOT/$repo" fetch origin main --tags
  test "$(git -C "$RELEASE_ROOT/$repo" branch --show-current)" = main
  test "$(git -C "$RELEASE_ROOT/$repo" rev-parse HEAD)" = \
    "$(git -C "$RELEASE_ROOT/$repo" rev-parse origin/main)"
  ! git -C "$RELEASE_ROOT/$repo" show-ref --verify --quiet "refs/tags/v$version"
done
```

上述 `HEAD == origin/main` 检查应在提交本次修改之前执行；提交后则在 push 完成后再次检查。逐仓使用
`git status --short` 和 `git diff --check` 审阅修改，确认没有密钥、token、P12、密码、运行日志或
本机状态文件。当前五个工作树包含本任务修改，提交时仍需逐仓确认 `git diff --stat` 后再 `git add -A`。

确认仓库 Actions 的 Workflow permissions 允许 GitHub Actions 写 repository contents；各仓
`prepare-release` 依赖该权限 push release commit 和 tag。

### 2.1 Community Device 环境

Device 的 `production-community-release` 环境必须已有以下配置：

- secrets: `COMMUNITY_SIGNING_P12_BASE64`、`COMMUNITY_SIGNING_P12_PASSWORD`、
  `COMMUNITY_SIGNING_IDENTITY`
- variable: `COMMUNITY_SIGNER_CERTIFICATE_SHA1`

只检查名称，不打印 secret 内容：

```sh
gh secret list --repo Agent-Remote/agent-remote-device \
  --env production-community-release
gh variable list --repo Agent-Remote/agent-remote-device \
  --env production-community-release
```

现有 CLI `0.2.9` 只能安装与其编译时固定指纹一致的 Community App。确认 Device 与 CLI 环境使用同一
指纹（变量值会保存在 shell 中，不在命令输出中展开）：

```sh
DEVICE_SIGNER=$(gh variable get COMMUNITY_SIGNER_CERTIFICATE_SHA1 \
  --repo Agent-Remote/agent-remote-device --env production-community-release)
CLI_SIGNER=$(gh variable get COMMUNITY_SIGNER_CERTIFICATE_SHA1 \
  --repo Agent-Remote/agent-remote-cli --env production-community-release)
test "$DEVICE_SIGNER" = "$CLI_SIGNER"
case "$DEVICE_SIGNER" in
  ''|*[!A-F0-9]*) false ;;
esac
test ${#DEVICE_SIGNER} -eq 40
```

若任一配置缺失，停止发布并从离线备份恢复原 Community identity，再用以下命令重新配置 Device 环境：

```sh
cd "$RELEASE_ROOT/agent-remote-device"
scripts/configure-community-release-environment.sh
```

默认输入目录是 `dist/community-signing-identity`。配置后把该目录从日常工作目录移走并继续离线保管。
本次已有 Community App 和 CLI，不能运行 `create-community-signing-identity.sh` 新建身份，否则现有
CLI 会拒绝安装；证书轮换必须作为包含新 CLI 版本的独立发布处理。

### 2.2 Root evidence 环境

Root 的 `production-device-release-evidence` 环境必须包含 secret
`DEVICE_CONTROL_RELEASE_PRIVATE_KEY_PEM`：

```sh
gh secret list --repo Agent-Remote/agent-remote \
  --env production-device-release-evidence
```

若环境 secret 缺失，从离线备份恢复与固定公钥匹配的原私钥，再运行：

```sh
cd "$RELEASE_ROOT/agent-remote"
scripts/configure-community-release-evidence-environment.sh
cmp dist/community-release-evidence-key/public-key-base64.txt \
  deploy/compose/community-release-public-key.txt
```

若 `cmp` 不通过，停止发布。签名私钥、公钥、部署 `.env` 中的公钥和最终 evidence 必须属于同一密钥对。
本次不得运行 `create-community-release-evidence-key.sh` 生成替代密钥。证据签名键轮换必须作为独立变更，
并在 Root feature commit 前评审、同步更新固定公钥和部署配置。

### 2.3 新增运行期配置

本次唯一新增的运行期环境变量是 Server 的 `DEVICE_SESSION_AUTHORIZATION_MODE`，合法值只有：

- `per_application_approval`：默认兼容模式，升级期间必须使用。
- `session_full_trust`：完整新版本组合验证后，供本次功能测试显式启用。

Node、Device App 和 Admin Web 没有新增运行期环境变量。Device 和 Root 上述 secrets/variables 是既有
Community 发布基础设施，不是部署到服务器的运行期配置。

## 3. 通用 commit、CI 与 prepare 操作

每个仓库在运行 `prepare-release` 前执行以下模板。`QUALITY_COMMAND` 和 commit message 使用后续各节给出的值：

```sh
cd "$RELEASE_ROOT/<repository>"
git status --short
git diff --check
<QUALITY_COMMAND>
git diff --stat
git add -A
git diff --cached --check
git commit -m "<conventional commit message>"
git push origin main

FEATURE_SHA=$(git rev-parse HEAD)
test "$FEATURE_SHA" = "$(git rev-parse origin/main)"
FEATURE_CI=$(gh run list --workflow ci.yml --event push --commit "$FEATURE_SHA" \
  --limit 1 --json databaseId --jq '.[0].databaseId')
test -n "$FEATURE_CI"
gh run watch "$FEATURE_CI" --exit-status
```

CI 成功后才触发 prepare：

```sh
gh workflow run prepare-release.yml --ref main -f version="$TARGET_VERSION"
PREPARE_RUN=$(gh run list --workflow prepare-release.yml --event workflow_dispatch \
  --branch main --limit 1 --json databaseId --jq '.[0].databaseId')
test -n "$PREPARE_RUN"
gh run watch "$PREPARE_RUN" --exit-status

git pull --ff-only origin main
git fetch origin "refs/tags/v$TARGET_VERSION:refs/tags/v$TARGET_VERSION"
RELEASE_SHA=$(git rev-list -n 1 "v$TARGET_VERSION")
test "$RELEASE_SHA" = "$(git rev-parse HEAD)"

RELEASE_RUN=$(gh run list --workflow release.yml --event workflow_dispatch \
  --commit "$RELEASE_SHA" --limit 1 --json databaseId --jq '.[0].databaseId')
test -n "$RELEASE_RUN"
gh run watch "$RELEASE_RUN" --exit-status

gh release view "v$TARGET_VERSION"
```

`prepare-release` 使用仓库 `GITHUB_TOKEN` push release commit；GitHub 不会让这种 push 递归触发
`ci.yml`。因此必须在 prepare 之前验证人工 push 的 feature commit CI，prepare 自身再验证版本准备，
最后由 exact-tag `release.yml` 验证并发布 release commit。

必须确认查询到的 run 的 `headSha` 等于预期 SHA；若 GitHub 列表尚未出现该 run，等待页面创建完成后
重新执行查询，不要触发第二次 prepare。任一 prepare 失败后，先检查远端是否已经存在 release commit
或 tag；存在时不得复用版本号盲目重试。

## 4. 逐仓发布

### 4.1 Device `0.2.12`

```sh
cd "$RELEASE_ROOT/agent-remote-device"
scripts/run-quality-checks.sh
git add -A
git diff --cached --check
git commit -m "feat: add session full-trust device control"
git push origin main
```

按第 3 节等待该 feature commit 的 `ci.yml`，随后设置 `TARGET_VERSION=$DEVICE_VERSION` 并执行 prepare
模板。Device 的 prepare 会自动把 `build_number` 设为该 prepare run 的正整数 run number。

Device release 成功后，至少确认以下资产存在：

- `agent-remote-device-macos-${DEVICE_VERSION}.zip` 及 `.sha256`、`.sigstore.json`、SPDX
- `agent-remote-device-macos-${DEVICE_VERSION}.community-signing.json` 及校验和、Sigstore bundle
- 四个 `agent-remote-device-proxy-<target>-${DEVICE_VERSION}.tar.gz` 及校验和、Sigstore、SPDX

记录不可变 tag commit：

```sh
export DEVICE_COMMIT=$(gh api \
  "repos/Agent-Remote/agent-remote-device/commits/v$DEVICE_VERSION" --jq .sha)
test ${#DEVICE_COMMIT} -eq 40
```

### 4.2 Node `0.2.13`

Node 提交前先固定刚发布的 Device proxy。不要填 feature commit，必须填 `v$DEVICE_VERSION` 实际指向的
release commit：

```sh
cd "$RELEASE_ROOT/agent-remote-node"
tmp=$(mktemp)
jq --arg version "$DEVICE_VERSION" --arg commit "$DEVICE_COMMIT" \
  '.device_proxy.version = $version | .device_proxy.commit = $commit | .device_proxy.release_workflow = "release.yml"' \
  release-dependencies.json > "$tmp"
mv "$tmp" release-dependencies.json
jq -e --arg version "$DEVICE_VERSION" --arg commit "$DEVICE_COMMIT" \
  '.schema_version == 2 and .device_proxy.version == $version and .device_proxy.commit == $commit' \
  release-dependencies.json
scripts/run-quality-checks.sh
git add -A
git diff --cached --check
git commit -m "feat: propagate session full-trust capabilities"
git push origin main
```

按第 3 节等待 feature CI，设置 `TARGET_VERSION=$NODE_VERSION`，执行 prepare 和 release 检查。Node
release 会下载并验证 Device 四架构 proxy，把对应 proxy 嵌入每个 Node archive。

验证一个目标中的嵌入版本，并记录 Node commit：

```sh
work=$(mktemp -d)
gh release download "v$NODE_VERSION" --repo Agent-Remote/agent-remote-node \
  --dir "$work" --pattern "agent-remote-node-$NODE_VERSION-linux-amd64-glibc.tar.gz" \
  --pattern "agent-remote-node-$NODE_VERSION-linux-amd64-glibc.tar.gz.sha256"
(cd "$work" && sha256sum --check \
  "agent-remote-node-$NODE_VERSION-linux-amd64-glibc.tar.gz.sha256")
tar -xOf "$work/agent-remote-node-$NODE_VERSION-linux-amd64-glibc.tar.gz" \
  "agent-remote-node-$NODE_VERSION-linux-amd64-glibc/device/VERSION"
export NODE_COMMIT=$(gh api \
  "repos/Agent-Remote/agent-remote-node/commits/v$NODE_VERSION" --jq .sha)
```

输出必须是 `$DEVICE_VERSION`。

### 4.3 Server `0.2.11`

```sh
cd "$RELEASE_ROOT/agent-remote-server"
scripts/run-quality-checks.sh
git add -A
git diff --cached --check
git commit -m "feat: add session full-trust authorization"
git push origin main
```

按第 3 节等待 feature CI，设置 `TARGET_VERSION=$SERVER_VERSION`，执行 prepare 和 release 检查。确认
release 包含 image metadata、SHA-256、provenance、SBOM 和依赖审计，并记录：

```sh
export SERVER_COMMIT=$(gh api \
  "repos/Agent-Remote/agent-remote-server/commits/v$SERVER_VERSION" --jq .sha)
```

### 4.4 Admin Web `0.2.9`

```sh
cd "$RELEASE_ROOT/agent-remote-admin-web"
scripts/run-quality-checks.sh
git add -A
git diff --cached --check
git commit -m "feat: show device authorization policy"
git push origin main
```

按第 3 节等待 feature CI，设置 `TARGET_VERSION=$ADMIN_VERSION`，执行 prepare 和 release 检查。确认
GHCR 多架构 image、digest metadata、provenance、SPDX 和 npm audit 资产存在，并记录：

```sh
export ADMIN_COMMIT=$(gh api \
  "repos/Agent-Remote/agent-remote-admin-web/commits/v$ADMIN_VERSION" --jq .sha)
```

### 4.5 Root distribution `0.2.19`

只有前四个 release workflow 全部成功后才能更新 Root manifest：

```sh
cd "$RELEASE_ROOT/agent-remote"
python3 scripts/update-release-component.py \
  agent-remote-device "$DEVICE_VERSION" "$DEVICE_COMMIT" --release-workflow release.yml
python3 scripts/update-release-component.py \
  agent-remote-node "$NODE_VERSION" "$NODE_COMMIT" --release-workflow release.yml
python3 scripts/update-release-component.py \
  agent-remote-server "$SERVER_VERSION" "$SERVER_COMMIT" --release-workflow release.yml
python3 scripts/update-release-component.py \
  agent-remote-admin-web "$ADMIN_VERSION" "$ADMIN_COMMIT" --release-workflow release.yml
jq . release-manifest.json
```

确认 CLI pin 未改变，五个组件的 tag 均解析到 manifest commit。运行根合同测试和本地合成 E2E；这些
测试是发布门禁，但不是 Apple 或真实外部 E2E 证据：

```sh
python3 tests/release_workflow_contract_test.py
python3 tests/device_control_operations_runbook_contract_test.py
python3 tests/test_assemble_device_control_release_evidence.py
python3 tests/test_assemble_community_device_control_release_evidence.py
python3 tests/test_local_device_control_e2e_contract.py
AGENT_REMOTE_SERVER_REPO="$RELEASE_ROOT/agent-remote-server" \
AGENT_REMOTE_NODE_REPO="$RELEASE_ROOT/agent-remote-node" \
AGENT_REMOTE_DEVICE_REPO="$RELEASE_ROOT/agent-remote-device" \
  scripts/run-local-device-control-e2e.sh
docker compose --env-file deploy/compose/.env.example \
  -f deploy/compose/docker-compose.yml config --quiet
git diff --check
git add -A
git diff --cached --check
git commit -m "feat: certify session full-trust composition"
git push origin main
```

等待 Root feature commit 的完整 `ci.yml` 成功后，设置 `TARGET_VERSION=$ROOT_VERSION` 并执行第 3 节
prepare 模板。Root release 自动以 `accept_reduced_security=true` 调用 Community evidence workflow；
`computer_use_v2_run_id` 和 `computer_use_v2_target` 留空，不要求本次延期的真实混合版本矩阵。最终应得到：

- `agent-remote-deploy-${ROOT_VERSION}.tar.gz`
- 对应 `.sha256`、`.sigstore.json` 和 SPDX
- bundle 内 schema 9 `device-control-release-evidence.json`
- bundle 内按 digest 固定的新 Server 和 Admin image 配置

## 5. 服务器升级

升级期间先关闭新设备控制；不要让旧 Node、旧 Device 或旧 evidence 与 full-trust 策略混合运行。

### 5.1 下载并验证根部署 bundle

```sh
export ROOT_VERSION=0.2.19
export RELEASE_DIR="/opt/agent-remote/releases/$ROOT_VERSION"
export NEW_COMPOSE="$RELEASE_DIR/agent-remote-deploy-$ROOT_VERSION/deploy/compose"
mkdir -p "$RELEASE_DIR"
cd "$RELEASE_DIR"
gh release download "v$ROOT_VERSION" --repo Agent-Remote/agent-remote \
  --pattern "agent-remote-deploy-$ROOT_VERSION.tar.gz" \
  --pattern "agent-remote-deploy-$ROOT_VERSION.tar.gz.sha256" \
  --pattern "agent-remote-deploy-$ROOT_VERSION.tar.gz.sigstore.json"
sha256sum --check "agent-remote-deploy-$ROOT_VERSION.tar.gz.sha256"
cosign verify-blob \
  --bundle "agent-remote-deploy-$ROOT_VERSION.tar.gz.sigstore.json" \
  --certificate-identity \
    "https://github.com/Agent-Remote/agent-remote/.github/workflows/release.yml@refs/tags/v$ROOT_VERSION" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  "agent-remote-deploy-$ROOT_VERSION.tar.gz"
gh attestation verify "agent-remote-deploy-$ROOT_VERSION.tar.gz" \
  --repo Agent-Remote/agent-remote
tar -xzf "agent-remote-deploy-$ROOT_VERSION.tar.gz"
cd "$NEW_COMPOSE"
sha256sum --check device-control-release-evidence.SHA256SUMS
```

### 5.2 备份与第一阶段配置

在旧部署目录先备份数据库和配置：

```sh
export OLD_COMPOSE=/opt/agent-remote/current/deploy/compose
cd "$OLD_COMPOSE"
docker compose --env-file .env -f docker-compose.yml ps
docker compose --env-file .env -f docker-compose.yml exec -T postgres \
  pg_dump -U agent_remote -d agent_remote > "/opt/agent-remote/backup-$ROOT_VERSION.sql"
cp .env "/opt/agent-remote/env-before-$ROOT_VERSION"
cp .env "$NEW_COMPOSE/.env"
cd "$NEW_COMPOSE"
```

把旧 `.env` 的站点域名、secret、数据库密码、CORS、保留期复制到新 bundle 的
`deploy/compose/.env`，但 Server/Admin image 和 evidence 路径必须采用新 bundle `.env.example` 中的
不可变 digest 和同 bundle evidence。第一阶段明确设置：

```dotenv
DEVICE_CONTROL_ENABLED=false
DEVICE_CONTROL_V2_ENABLED=true
DEVICE_SESSION_AUTHORIZATION_MODE=per_application_approval
DEVICE_CONTROL_RELEASE_EVIDENCE_FILE=./device-control-release-evidence.json
DEVICE_CONTROL_RELEASE_PUBLIC_KEY=<与该 evidence 签名私钥匹配的 Base64 raw Ed25519 公钥>
DEVICE_SESSION_RETENTION_DAYS=<已批准的非零天数>
DEVICE_SESSION_AUDIT_RETENTION_DAYS=<不小于 session retention 的非零天数>
```

其中 `SERVER_IMAGE`、`ADMIN_WEB_IMAGE`、`DEVICE_CONTROL_RELEASE_EVIDENCE_FILE` 和
`DEVICE_CONTROL_RELEASE_PUBLIC_KEY` 应从新 bundle 的 `.env.example` 逐项复制；不要保留旧值。不要从
旧 release 复制 evidence，也不要只使用浮动 `latest` image。验证 Compose 展开结果：

```sh
docker compose --env-file .env -f docker-compose.yml config --quiet
docker compose --env-file .env -f docker-compose.yml config | \
  grep -E 'DEVICE_(CONTROL_ENABLED|SESSION_AUTHORIZATION_MODE)|image:'
```

### 5.3 启动、migration 与健康检查

```sh
cd "$NEW_COMPOSE"
docker compose --env-file .env -f docker-compose.yml pull
docker compose --env-file .env -f docker-compose.yml up -d
docker compose --env-file .env -f docker-compose.yml ps
docker compose --env-file .env -f docker-compose.yml logs --tail=200 server
curl -fsS "https://$AGENT_REMOTE_DOMAIN/healthz"
docker compose --env-file .env -f docker-compose.yml exec -T postgres \
  psql -U agent_remote -d agent_remote -Atc 'select version_num from alembic_version;'
```

Server image entrypoint 自动执行 `alembic upgrade head`，最后一条命令必须输出
`0017_device_authorization`。migration 会把历史 session 回填为 `per_application_approval`，不会把旧
session 自动提升为 full trust。

健康检查全部通过后，再按现有部署方式把 `/opt/agent-remote/current` 指向本次 versioned bundle；若
`current` 不是符号链接，不要用链接命令覆盖目录，继续以 `$NEW_COMPOSE` 作为当前运维目录即可。

## 6. Node 和本地 macOS 升级

### 6.1 Node

在每台 Node 上使用精确版本重跑安装器。复用现有配置和 node token，不要使用 `--force-register`：

```sh
export NODE_VERSION=0.2.13
export DEVICE_VERSION=0.2.12
curl -fsSL https://raw.githubusercontent.com/Agent-Remote/agent-remote-node/main/scripts/install.sh | \
  sudo bash -s -- \
  --version "$NODE_VERSION"
sudo systemctl status --no-pager agent-remote-runtime agent-remote-node
sudo journalctl -u agent-remote-node -n 100 --no-pager
sudo jq -r .version /etc/agent-remote-node/config.json
sudo cat /opt/agent-remote/device/current/VERSION
```

若原安装使用了非默认 `--prefix`、`--config-dir`、`--state-dir`、`--data-dir`、runtime backend 或
WireGuard 参数，升级时继续传入相同的非注册参数。已有 `/etc/agent-remote-node/config.json` 时不需要再次
提交一次性 registration token；安装器复用现有 node token。停止并重建升级前存在的 device-control
binding/session；已有进程不会在原 generation 中获得新 capability。最后两条命令应分别输出
`$NODE_VERSION` 和 `$DEVICE_VERSION`。

### 6.2 macOS CLI 和 Device App

CLI 本次继续使用 `0.2.9`。若本机不是该版本，先精确升级并保留原
`~/.config/agent-remote`：

```sh
export CLI_VERSION=0.2.9
export DEVICE_VERSION=0.2.12
curl -fsSL https://raw.githubusercontent.com/Agent-Remote/agent-remote-cli/main/scripts/install.sh | \
  bash -s -- --version "$CLI_VERSION"
agent-remote --version
agent-remote status --online
```

下载并验证 Device Community 制品：

```sh
work=$(mktemp -d)
gh release download "v$DEVICE_VERSION" --repo Agent-Remote/agent-remote-device \
  --dir "$work" \
  --pattern "agent-remote-device-macos-$DEVICE_VERSION.zip" \
  --pattern "agent-remote-device-macos-$DEVICE_VERSION.zip.sha256" \
  --pattern "agent-remote-device-macos-$DEVICE_VERSION.zip.sigstore.json"
(cd "$work" && shasum -a 256 --check \
  "agent-remote-device-macos-$DEVICE_VERSION.zip.sha256")
cosign verify-blob \
  --bundle "$work/agent-remote-device-macos-$DEVICE_VERSION.zip.sigstore.json" \
  --certificate-identity \
    "https://github.com/Agent-Remote/agent-remote-device/.github/workflows/release.yml@refs/tags/v$DEVICE_VERSION" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  "$work/agent-remote-device-macos-$DEVICE_VERSION.zip"
gh attestation verify "$work/agent-remote-device-macos-$DEVICE_VERSION.zip" \
  --repo Agent-Remote/agent-remote-device
osascript -e 'tell application "Agent Remote Device" to quit' 2>/dev/null || true
agent-remote device install \
  --source "$work/agent-remote-device-macos-$DEVICE_VERSION.zip"
agent-remote device diagnose
agent-remote device launch
```

安装命令会校验固定 bundle ID、App 与两个 XPC 的签名、CLI 内固定的 Community 证书指纹，随后只对
验证过的 staging bundle 移除 quarantine，并原子替换 `~/Applications/Agent Remote Device.app`。
不要手工删除旧 App、TCC 数据或 `~/.config/agent-remote`。如系统提示，重新授予 Accessibility 和
Screen Recording；Community 自签名只表示手动信任，不表示 Apple 已验证或公证。

## 7. 启用 full trust 与人工验收

只有所有 Node 和目标 Mac 升级、旧 session/binding 结束、Admin 显示新能力且服务器健康后，才编辑
服务器 `.env`：

```dotenv
DEVICE_CONTROL_ENABLED=true
DEVICE_CONTROL_V2_ENABLED=true
DEVICE_SESSION_AUTHORIZATION_MODE=session_full_trust
```

重建 Server 并确认配置生效：

```sh
docker compose --env-file .env -f docker-compose.yml up -d --force-recreate server
docker compose --env-file .env -f docker-compose.yml logs --tail=200 server
curl -fsS "https://$AGENT_REMOTE_DOMAIN/healthz"
```

创建全新 session/generation 后逐项人工验证：

- Device 选择 session 后自动激活 full trust，不出现逐应用审批 UI。
- 可 observe 多个普通 GUI 应用，并可在它们之间切换；Device 自身不可作为控制目标。
- `launch_application` 可用准确 Bundle ID 或唯一应用名启动；路径、URL、歧义名称和 Device 自身被拒绝。
- 未执行 observe 时 `read_clipboard` 仍可读取受长度限制的全局纯文本；不返回非文本或超限内容。
- session 切换、结束、过期、设备 revoke 后，旧 generation/lease/sequence 立即失效且不能重放。
- Escape、TCC 权限撤销、XPC 退出、网络断开均 fail closed；不自动重放结果未知的 launch/action。
- 高风险最终动作仍保留远端确认要求，full trust 不绕过该确认边界。
- Admin Web 同时显示 `session_full_trust` 授权模式、全局纯文本 clipboard scope 和完整 capability 状态。

记录本次人工验收为 Community 功能测试，不将其标记为 Apple E2E 或延期的真实五场景混合版本矩阵。

## 8. 失败处理与回滚

出现错误目标、能力不完整、签名不匹配、migration 异常或不确定执行结果时：

1. 立即把 `DEVICE_CONTROL_ENABLED=false`，重建 Server，阻止新 claim。
2. 结束所有 active device-control session/binding；不得把 active generation 原地降级或继续使用旧序号。
3. revoke 受影响设备或轮换 token，确认 Node 不再上报活动 binding。
4. 若仅 v2 行为异常，可在结束旧 generation 后设置 `DEVICE_CONTROL_V2_ENABLED=false`，新建 generation
   使用兼容路径；full-trust 本身缺能力时应保持整体关闭，不做部分 capability 降级。
5. 回滚时使用上一份完整 root bundle、其匹配的 Server/Admin digest、schema 8/9 evidence 和公钥；不能
   混用新旧 evidence、image、Node proxy 或 Device App。
6. Device 安装器拒绝降级。需要回退时先结束 session、关闭 capability、撤销设备，再按受支持的完整旧
   组合重新安装/注册；不要绕过 CLI 的版本和签名校验。
7. migration `0017` 增加的字段向后兼容旧记录。通常保留数据库向前 schema 并回滚应用；只有确认所有
   运行代码均不再依赖新字段、已有完整备份且停机维护时，才考虑 `alembic downgrade 0016_device_binding_rebind`。

发布阶段若某组件 release 已成功而后续仓库失败，不删除 tag、不覆盖 GitHub Release；修复后为失败仓库
选择新 patch 版本，并在 Root manifest 中只固定最终验证成功的不可变版本和 commit。Root release 未成功
前不要部署临时拼装组合。
