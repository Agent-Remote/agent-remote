# agent-remote Phase 4 完成记录

## 状态

Phase 4：节点注册、心跳和任务轮询，状态为完成。

Phase 4 的目标是让 `agent-remote-node` 成为可注册、可认证、可心跳、可轮询任务并回写结果的受控执行节点，同时在 `agent-remote-server` 中建立节点控制面 API 和任务 lease 模型。

## 已完成交付物

- [x] Go 节点端项目骨架
- [x] 节点配置文件
- [x] 节点注册命令
- [x] 节点凭证保存
- [x] 心跳上报
- [x] 资源快照
- [x] `/node-api/tasks/poll`
- [x] task lease
- [x] task start/complete/fail
- [x] 节点本地 task ledger
- [x] `reconcile_state` 基础实现
- [x] 管理端节点创建、更新、维护、禁用和注册 token 轮换
- [x] OpenAPI 契约同步
- [x] 服务端迁移、模型、repository、service、route 和测试

## 仓库提交

`agent-remote-protocol`：

```text
5611080 docs: extend node api contract
```

`agent-remote-server`：

```text
263d213 feat: add node control api
```

`agent-remote-node`：

```text
031a05b chore: initialize node runtime
```

## API 范围

已同步到 OpenAPI 并在服务端实现的主要接口：

- `GET /api/v1/nodes`
- `POST /api/v1/nodes`
- `GET /api/v1/nodes/{node_id}`
- `PATCH /api/v1/nodes/{node_id}`
- `POST /api/v1/nodes/{node_id}/registration-token`
- `POST /api/v1/nodes/{node_id}/maintenance`
- `POST /api/v1/nodes/{node_id}/disable`
- `POST /api/v1/node-api/register`
- `POST /api/v1/node-api/heartbeat`
- `POST /api/v1/node-api/tasks/poll`
- `POST /api/v1/node-api/tasks/{task_id}/start`
- `POST /api/v1/node-api/tasks/{task_id}/complete`
- `POST /api/v1/node-api/tasks/{task_id}/fail`
- `POST /api/v1/node-api/reconcile`

## 数据库变更

新增迁移：

```text
0003_node_control
```

变更内容：

- `nodes.registration_token_hash`
- `nodes.node_token_hash`
- `nodes.last_heartbeat_at`
- `nodes.version`
- `nodes_registration_token_hash_uidx`
- `nodes_node_token_hash_uidx`
- `nodes_status_heartbeat_idx`

节点注册 token 和节点长期 token 只保存哈希。

## 节点端范围

`agent-remote-node` 首期已具备以下能力：

- `register`
- `heartbeat`
- `poll-once`
- `reconcile`
- `run`
- JSON 配置读写
- 控制面 API client
- Docker、tmux 和基础系统资源快照
- file-backed task ledger
- 幂等任务处理
- 任务 start/complete/fail 回写
- Docker 镜像构建
- GitHub Actions 基础 CI

当前任务执行器只实现节点控制面所需的基础任务骨架。WireGuard、SSH、Mutagen、Docker sandbox、tmux session 和远端浏览器任务将在后续 Phase 中接入真实执行逻辑。

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

在 `agent-remote-node` 仓库执行：

```sh
gofmt -w cmd internal
```

```sh
go test ./...
```

```sh
docker build -t agent-remote-node:phase4 .
```

## 当前验证结果

- `agent-remote-protocol` OpenAPI YAML 解析通过
- `agent-remote-protocol` `git diff --check` 通过
- `agent-remote-server` `scripts/run-quality-checks.sh` 通过
- `ruff format --check .` 通过
- `ruff check .` 通过
- `mypy` 通过
- `pytest` 通过，18 个测试通过
- `check_docstrings.py` 通过
- `alembic heads` 输出 `0003_node_control (head)`
- `docker compose config` 通过
- `docker compose build server` 通过
- server 仓库禁用词扫描无命中
- `agent-remote-node` `gofmt -w cmd internal` 通过
- `agent-remote-node` `go test ./...` 通过
- `agent-remote-node` Docker 镜像构建通过

当前 server 测试仍存在 1 个上游依赖 warning：FastAPI/Starlette `TestClient` 提示未来应迁移到 `httpx2`。该 warning 不影响 Phase 4 验收。

## Phase 5 进入条件

Phase 5 可以开始，前提是：

- 协议仓库 OpenAPI 已包含节点管理和节点端专用 API
- server 仓库节点 API、任务 lease、节点认证和断线标记均有测试
- node 仓库可以从配置注册、上报心跳、轮询任务并回写任务结果
- 节点 token、注册 token 只保存哈希
- 重复上报同一 `task_id` 不会创建重复结果

## 下一步

进入 Phase 5：CLI 本地基础能力。

Phase 5 目标：

- 初始化 `agent-remote-cli`
- 实现 `agent-remote login/logout/status/doctor`
- 建立本地 SQLite 状态
- 建立本地凭证存储
- 建立托管依赖目录
- 将 WireGuard、Mutagen 等外部依赖的内置和版本管理作为 CLI 基础能力落地
