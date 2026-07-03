# agent-remote Phase 2 完成记录

## 状态

Phase 2：核心数据模型，状态为完成。

Phase 2 的目标是在 `agent-remote-server` 中建立控制面权威数据模型，为后续认证、设备、节点任务、会话调度、同步会话和远端临时浏览器功能提供持久化基础。

## 已完成交付物

- [x] PostgreSQL 核心业务表设计
- [x] Alembic 初始业务迁移 `0001_core_schema`
- [x] SQLAlchemy ORM 模型
- [x] 模型按业务域拆分
- [x] Alembic metadata 自动加载模型包
- [x] 基础 repository 层
- [x] 基础 persistence service 层
- [x] 模型 metadata 测试
- [x] 核心索引测试
- [x] migration revision 测试
- [x] repository CRUD、更新和约束冲突测试
- [x] Docker server 镜像构建验证

## 仓库

```text
https://github.com/Agent-Remote/agent-remote-server
```

本地路径：

```text
/Users/rem/Documents/Git/agent-remote-server
```

完成提交：

```text
cabc1a9 feat: add core data model
4a70715 test: cover persistence update conflicts
```

## 核心表

Phase 2 已建立以下 16 张核心表：

- `users`
- `user_devices`
- `tool_accounts`
- `tool_account_profiles`
- `nodes`
- `node_heartbeats`
- `node_tasks`
- `node_task_results`
- `wireguard_peers`
- `ssh_keys`
- `workspaces`
- `sync_sessions`
- `sessions`
- `session_events`
- `browser_sessions`
- `audit_logs`

## 模型拆分

`agent-remote-server` 的模型不放在单一大文件中，而是按业务域拆分：

```text
src/agent_remote_server/models/
  audit.py
  mixins.py
  network.py
  nodes.py
  sessions.py
  tools.py
  users.py
  workspaces.py
```

统一导出入口保留在：

```text
src/agent_remote_server/models/__init__.py
```

## 数据层边界

Phase 2 建立了最小 repository/service 基础层：

- `repositories/base.py`：通用异步仓储，提供 `get`、`add`、`list`、`delete`
- `services/persistence.py`：持久化服务入口，按模型创建仓储

后续 Phase 3 开始实现用户、设备、认证等具体业务时，再按用例补专用 repository/service，避免 API handler 直接散写 SQLAlchemy 查询。

## 验证命令

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

- `scripts/run-quality-checks.sh` 通过
- `ruff format --check .` 通过
- `ruff check .` 通过
- `mypy` 通过
- `pytest` 通过，9 个测试通过
- `check_docstrings.py` 通过
- `alembic heads` 输出 `0001_core_schema (head)`
- `docker compose config` 通过
- `docker compose build server` 通过
- server 仓库禁用词扫描无命中

当前测试存在 1 个上游依赖 warning：FastAPI/Starlette `TestClient` 提示未来应迁移到 `httpx2`。该 warning 不影响 Phase 2 验收。

## Phase 3 进入条件

Phase 3 可以开始，前提是：

- `agent-remote-server` Phase 2 提交已推送
- 核心表和索引已在 Alembic 迁移中固化
- ORM metadata 与 migration 表集合保持一致
- repository/service 基础层已通过 CRUD 测试

## 下一步

进入 Phase 3：认证、用户、设备和密钥。

Phase 3 目标：

- 管理员 bootstrap
- 用户名/密码登录
- Argon2id 密码哈希
- 可选 TOTP 基础结构
- CLI device-code 或 browser login 流程
- CLI token 签发、刷新、撤销
- 设备注册
- SSH 公钥注册
- WireGuard peer 记录
- 审计日志写入
