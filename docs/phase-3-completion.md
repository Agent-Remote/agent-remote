# agent-remote Phase 3 完成记录

## 状态

Phase 3：认证、用户、设备和密钥，状态为完成。

Phase 3 的目标是在 `agent-remote-server` 中建立可撤销的用户身份、CLI 登录、设备凭证和审计基础，并同步 `agent-remote-protocol` 的 OpenAPI 契约。

## 已完成交付物

- [x] 管理员 bootstrap
- [x] 用户名/密码登录
- [x] Argon2id 密码哈希
- [x] 可选 TOTP setup/verify 基础结构
- [x] CLI device-code start/approve/complete 流程
- [x] Opaque bearer token 签发、刷新、撤销
- [x] 设备注册
- [x] 设备 token 签发和 rotate
- [x] SSH 公钥记录
- [x] WireGuard peer 记录
- [x] 设备撤销时联动撤销 token、SSH key、WireGuard peer
- [x] 审计日志写入
- [x] 审计日志敏感原文过滤测试
- [x] OpenAPI 契约同步

## 仓库提交

`agent-remote-protocol`：

```text
09a705d docs: extend identity api contract
```

`agent-remote-server`：

```text
c8ddb0e feat: add identity and device auth
```

## API 范围

已实现并纳入测试的主要接口：

- `POST /api/v1/auth/bootstrap`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/cli/start`
- `POST /api/v1/auth/cli/approve`
- `POST /api/v1/auth/cli/complete`
- `POST /api/v1/auth/totp/setup`
- `POST /api/v1/auth/totp/verify`
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/users/{user_id}`
- `PATCH /api/v1/users/{user_id}`
- `POST /api/v1/users/{user_id}/disable`
- `GET /api/v1/devices`
- `POST /api/v1/devices`
- `POST /api/v1/devices/register`
- `GET /api/v1/devices/{device_id}`
- `POST /api/v1/devices/{device_id}/disable`
- `POST /api/v1/devices/{device_id}/revoke`
- `POST /api/v1/devices/{device_id}/rotate-token`

## 数据库变更

新增迁移：

```text
0002_identity_auth
```

变更内容：

- `users.encrypted_totp_secret`
- `auth_tokens`
- `cli_login_codes`

令牌只保存哈希，TOTP secret 加密存储。

## 验证命令

在 `agent-remote-protocol` 仓库执行：

```sh
ruby -e 'require "yaml"; YAML.load_file("openapi/openapi.yaml"); puts "yaml ok"'
```

```sh
git diff --check
```

在 `agent-remote-server` 仓库执行：

```sh
UV_CACHE_DIR=/Users/rem/Documents/Git/agent-remote-server/.uv-cache uv sync
```

```sh
scripts/run-quality-checks.sh
```

```sh
UV_CACHE_DIR=/Users/rem/Documents/Git/agent-remote-server/.uv-cache uv run alembic heads
```

```sh
docker compose config
docker compose build server
```

server 仓库执行禁用词扫描，排除 `.git`、虚拟环境和工具缓存目录。

## 当前验证结果

- `agent-remote-protocol` OpenAPI YAML 解析通过
- `agent-remote-server` `scripts/run-quality-checks.sh` 通过
- `ruff format --check .` 通过
- `ruff check .` 通过
- `mypy` 通过
- `pytest` 通过，14 个测试通过
- `check_docstrings.py` 通过
- `alembic heads` 输出 `0002_identity_auth (head)`
- `docker compose config` 通过
- `docker compose build server` 通过
- server 仓库禁用词扫描无命中

当前测试仍存在 1 个上游依赖 warning：FastAPI/Starlette `TestClient` 提示未来应迁移到 `httpx2`。该 warning 不影响 Phase 3 验收。

## Phase 4 进入条件

Phase 4 可以开始，前提是：

- 协议仓库 OpenAPI 已包含身份认证、用户和设备接口
- server 仓库身份认证实现已提交并推送
- 管理员初始化、普通用户登录、CLI 登录闭环和设备撤销联动均有测试
- token、密码、TOTP secret、SSH key body、WireGuard key body 不进入审计日志

## 下一步

进入 Phase 4：节点注册、心跳和任务轮询。

Phase 4 目标：

- 初始化 `agent-remote-node`
- 建立节点注册和节点凭证
- 实现节点心跳上报
- 实现节点任务轮询和 task lease
- 实现任务 start/complete/fail 上报
- 为后续 WireGuard、SSH、session 和 browser task 做节点端执行底座
