# agent-remote Phase 5 完成记录

## 状态

Phase 5：CLI 本地基础能力，状态为完成。

Phase 5 的目标是初始化 `agent-remote-cli`，建立本地身份、设备状态、诊断、SQLite、凭证存储和托管依赖目录基础，为后续 WireGuard、SSH、Mutagen 和工具启动命令提供本地执行底座。

本阶段同时按最新要求完成全仓库 GPL-3.0-only 许可落地，并标明 WireGuard 与 Mutagen 的第三方许可证注意事项。

## 已完成交付物

- [x] Rust CLI 项目结构
- [x] `agent-remote login`
- [x] `agent-remote logout`
- [x] `agent-remote status`
- [x] `agent-remote doctor`
- [x] `agent-remote doctor --fix`
- [x] `agent-remote deps status`
- [x] 本地目录 `~/.config/agent-remote/`
- [x] 本地 SQLite `state.sqlite3`
- [x] macOS Keychain 集成入口
- [x] Linux Secret Service 集成入口
- [x] owner-only 文件凭证兜底
- [x] 托管依赖目录 `bin/`
- [x] 托管依赖 manifest `dependencies/manifest.json`
- [x] Mutagen 与 WireGuard helper 版本检查框架
- [x] Mutagen 与 WireGuard helper 许可证字段
- [x] 全仓库 `GPL-3.0-only` 许可文件
- [x] 全仓库 `THIRD_PARTY_NOTICES.md`
- [x] CLI CI 和质量检查脚本

## 仓库提交

`agent-remote-cli`：

```text
93575e4 feat: initialize cli local foundation
```

`agent-remote-server`：

```text
9fc7d73 docs: add gpl license notices
```

`agent-remote-node`：

```text
39bc358 docs: add gpl license notices
```

```text
4738279 docs: add gpl license notices
```

`agent-remote-admin-web`：

```text
5851b01 docs: initialize license notices
```

## CLI 命令范围

已实现的命令：

- `agent-remote login`
- `agent-remote logout`
- `agent-remote status`
- `agent-remote doctor`
- `agent-remote deps status`

`login` 支持：

- 用户名密码登录
- CLI device-code 登录
- TOTP code 参数
- 自动读取 `~/.ssh/id_ed25519.pub` 或 `~/.ssh/id_rsa.pub`
- 显式 `--ssh-public-key`
- 显式 `--wireguard-public-key`
- `--skip-device-registration`
- 登录后注册设备并保存设备 token

## 本地状态边界

默认本地目录：

```text
~/.config/agent-remote/
```

主要文件：

```text
config.toml
state.sqlite3
dependencies/manifest.json
bin/
secrets/
```

SQLite 只保存：

- key-value 元数据
- 设备 ID
- server URL
- 设备名
- 平台
- 状态
- SSH key ID
- WireGuard peer ID
- 创建和最后在线时间

SQLite 不保存：

- access token
- refresh token
- device token
- SSH 私钥
- WireGuard 私钥
- 工具账户登录态
- cookies
- 浏览器 profile

## 凭证存储

凭证存储优先级：

1. macOS 使用系统 Keychain，通过 `security` 命令访问。
2. Linux 使用 Secret Service，通过 `secret-tool` 访问。
3. 如果系统凭据存储不可用，回退到 `~/.config/agent-remote/secrets/` 下的 owner-only 文件。

可以通过以下环境变量强制使用文件兜底，便于测试：

```sh
AGENT_REMOTE_SECRET_BACKEND=file
```

## 托管依赖

Phase 5 只建立托管依赖目录和检查框架，不下载或内置真实二进制。

当前 manifest 默认记录：

- `mutagen`
- `wireguard-helper`

每个托管依赖记录：

- name
- required version
- binary path
- source
- license
- license notice

后续发布包必须把实际二进制、版本、来源、checksum 和许可证文本写入发布产物。

## 许可决策

所有仓库统一使用：

```text
GPL-3.0-only
```

每个仓库都已添加：

```text
LICENSE
THIRD_PARTY_NOTICES.md
```

WireGuard 说明：

- `wireguard-tools` 使用 GPL-2.0-only。
- 不同平台 WireGuard 实现可能有不同许可证。
- 打包实际 WireGuard artifact 时必须记录具体 artifact 的许可证、来源、版本和 checksum。

Mutagen 说明：

- Mutagen 仓库说明默认代码许可证为 MIT，除非另有标明。
- Mutagen 官方说明 v0.17 起官方 release build 默认包含 SSPL 许可代码。
- 打包 Mutagen 时必须明确使用官方 build 还是自建 MIT-only build，并附带匹配的许可证 notice。

## 验证命令

在 `agent-remote-cli` 仓库执行：

```sh
scripts/run-quality-checks.sh
```

```sh
AGENT_REMOTE_HOME="$(mktemp -d)" cargo run -- doctor --fix
```

```sh
AGENT_REMOTE_HOME="$(mktemp -d)" cargo run -- deps status
```

在 `agent-remote-server` 仓库执行：

```sh
UV_CACHE_DIR=/Users/rem/Documents/Git/agent-remote-server/.uv-cache uv run python -m py_compile src/agent_remote_server/main.py
```

```sh
scripts/run-quality-checks.sh
```

server 仓库执行禁用词扫描，排除 `.git`、虚拟环境和工具缓存目录。

在 `agent-remote-node` 仓库执行：

```sh
go test ./...
```


所有仓库执行：

```sh
git diff --check
```

## 当前验证结果

- `agent-remote-cli` `scripts/run-quality-checks.sh` 通过
- `cargo fmt --check` 通过
- `cargo clippy --all-targets -- -D warnings` 通过
- `cargo test` 通过，6 个测试通过
- `agent-remote doctor --fix` 能创建本地目录、SQLite 和依赖 manifest
- `agent-remote deps status` 能输出 Mutagen 与 WireGuard helper 状态和许可证信息
- `agent-remote-server` 提交 hook 通过
- `agent-remote-server` 测试通过，18 个测试通过
- `agent-remote-server` `py_compile` 通过
- `agent-remote-server` 禁用词扫描无命中
- `agent-remote-node` `go test ./...` 通过
- 所有仓库 `git diff --check` 通过

当前 server 测试仍存在 1 个上游依赖 warning：FastAPI/Starlette `TestClient` 提示未来应迁移到 `httpx2`。该 warning 不影响 Phase 5 验收。

## Phase 6 进入条件

Phase 6 可以开始，前提是：

- `agent-remote-cli` 已能保存 server URL、设备 ID 和本地状态
- CLI token 不进入 SQLite
- `doctor --fix` 能准备本地目录、SQLite 和托管依赖 manifest
- 托管依赖 manifest 已能表达 Mutagen 与 WireGuard helper 的版本和许可证信息
- 全仓库 GPL-3.0-only 和第三方 notices 已提交并推送

## 下一步

进入 Phase 6：WireGuard 与 SSH 受控连接。

Phase 6 目标：

- 设备 WireGuard peer 配置
- 节点 WireGuard peer 配置
- CLI WireGuard helper 调用
- SSH key 管理和检查
- 节点受控 `authorized_keys`
- `agent-remote-attach`
- SSH forced command
- CLI 网络与 SSH 诊断
