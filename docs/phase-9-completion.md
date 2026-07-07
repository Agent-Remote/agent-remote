# agent-remote Phase 9 完成记录

## 状态

Phase 9：Claude session 和 `fclaude`，状态为完成。

本阶段目标是把已完成绑定和验证的 Claude 工具账户真正用于远端 Claude 运行 session，并提供本地 `fclaude` 启动入口，实现项目路径绑定恢复、参数透传、SSH attach、tmux 长久在线、Docker Sandbox 启动任务和同账户同节点约束。

## 交付内容

### agent-remote-server

- 新增工具 session 生命周期 API：
  - `GET /api/v1/sessions`
  - `POST /api/v1/sessions`
  - `GET /api/v1/sessions/current-project`
  - `POST /api/v1/sessions/{session_id}/stop`
  - 继续复用 `POST /api/v1/sessions/{session_id}/attach`
- 新增 session service / repository / schema。
- 创建 session 时校验：
  - 工具账户属于当前用户。
  - 工具账户状态为 `active`。
  - workspace 属于当前用户且 `project_key` 匹配。
  - workspace 已有远端路径。
- 创建 `create_tool_session` node task，payload 包含：
  - session、账户、workspace 和项目 key。
  - workspace/account 远端路径。
  - tmux session 名称。
  - Docker Sandbox 名称。
  - timezone、locale。
  - 透传给 Claude 的 argv。
- 停止 session 时创建 `stop_tool_session` node task。
- node task 完成后回写 session 状态：
  - `create_tool_session` 成功后进入 `running` / `active`。
  - `stop_tool_session` 成功后进入 `stopped`。
  - 失败时进入 `failed`。
- 同一个 Claude 账户已有活跃 session 时，新 session 强制复用同一节点，保证同账户出口 IP 一致。

### agent-remote-node

- 新增 `internal/toolsessions`。
- 支持 `create_tool_session`：
  - 准备 workspace 目录。
  - 准备账户 `.claude` 配置目录和 `.claude.json`。
  - 创建 `.agent-remote-session.json` 标记文件。
  - 使用 Docker Sandbox 官方 `claude` agent 创建 sandbox。
  - 使用 tmux 长期持有 `docker sandbox exec -it ... claude <argv>`。
  - 设置 `CLAUDE_CONFIG_DIR`、`TZ`、`LANG`、`LC_ALL`。
- 支持 `stop_tool_session`：
  - kill tmux session。
  - 删除 Docker Sandbox。
- 保持测试环境无 tmux/docker 时可验证目录、payload 和任务回写，不强依赖本机真实运行时。

### agent-remote-cli

- 新增 `fclaude` 二进制。
- 新增公共 library 导出，让 `fclaude` 复用 API、配置、SQLite、Mutagen、SSH、workspace 等模块。
- `fclaude` 支持：
  - `fclaude`
  - `fclaude new`
  - `fclaude list`
  - `fclaude attach <session_id>`
  - `fclaude stop <session_id>`
  - `fclaude -- <claude_args...>`
  - `fclaude --model opus` 这类未知参数直接透传给远端 Claude。
- 默认恢复逻辑：
  - 由当前启动路径生成 project key。
  - 先查找当前项目最近可恢复 Claude session。
  - 不恢复全局最近 session。
- 新 session 创建前会确保 workspace 同步存在。
- Mutagen 或服务端同步状态存在冲突时阻止进入 session。
- Claude 多账户选择规则：
  - `--account-id <id>` 显式指定最高优先级。
  - 否则使用本地默认 Claude 账户。
  - 否则如果只有一个 active Claude 账户，则自动使用。
  - 多个 active Claude 账户且无默认值时失败并要求用户选择。
- 新增：
  - `agent-remote account default set --tool claude --account-id <id>`
  - `agent-remote account default get --tool claude`
  - `agent-remote account default clear --tool claude`

  - session 创建。
  - 当前项目恢复。
  - attach。
  - stop 返回 session 数据。
- 同步 `Session` schema：
  - `running` 状态。
  - `create_task_id`。
  - `stop_task_id`。
- 同步 node task 类型：
  - `create_tool_session`
  - `stop_tool_session`
- 更新 create tool session 示例 payload。
- 更新 CLI contract 中的 `fclaude` 多账户选择和参数透传规则。

## 验证

已执行：

```bash
cd /Users/rem/Documents/Git/agent-remote-server
UV_CACHE_DIR=/Users/rem/Documents/Git/agent-remote-server/.uv-cache uv run ruff format .
UV_CACHE_DIR=/Users/rem/Documents/Git/agent-remote-server/.uv-cache uv run ruff check .
UV_CACHE_DIR=/Users/rem/Documents/Git/agent-remote-server/.uv-cache uv run mypy
UV_CACHE_DIR=/Users/rem/Documents/Git/agent-remote-server/.uv-cache uv run pytest
UV_CACHE_DIR=/Users/rem/Documents/Git/agent-remote-server/.uv-cache uv run python scripts/check_docstrings.py
```

结果：29 个 server 测试通过。当前仍存在 1 个上游依赖 warning：FastAPI/Starlette `TestClient` 提示未来应迁移到 `httpx2`，不影响本阶段验收。

```bash
cd /Users/rem/Documents/Git/agent-remote-node
gofmt -w internal/toolsessions/toolsessions.go internal/worker/worker.go internal/worker/worker_test.go
go test ./...
```

结果：node 全部测试通过。

```bash
cd /Users/rem/Documents/Git/agent-remote-cli
cargo fmt
cargo test
```

结果：CLI 全部测试通过。

```bash
```

结果：协议 YAML 和 JSON 均可解析。

## 进入下一阶段

Phase 10 可以开始，重点是远端临时浏览器：

- 管理端创建浏览器 session。
- node 创建短生命周期浏览器容器。
- 浏览器走 VPS 网络、时区和 locale。
- 管理端通过内嵌浏览器访问邮箱、Claude 等页面。
- 浏览器不持久化用户会话信息。
