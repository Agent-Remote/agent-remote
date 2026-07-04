# agent-remote Phase 8 完成记录

## 状态

Phase 8：工具账户抽象和 Claude 绑定，状态为完成。

本阶段建立通用工具账户状态机，首个实现工具类型为 Claude。用户可以通过 CLI 创建多个 Claude 账户，绑定流程由控制面调度到匹配地区的远端节点，节点端准备账户归档目录，并通过 Docker Sandboxes 的 `claude` agent 创建官方 sandbox。tmux 负责持有交互式 `claude login` 会话，登录完成后由 verifier 校验远端账户目录并把账户置为 `active`。

当前实现完成源码、协议和本地自动化验证闭环。真实 Claude 登录仍需要部署环境中存在 Docker Sandboxes 插件、tmux、目标节点网络出口和账户目录权限；CLI 不保存 Claude 登录态，登录态只存在远端账户归档目录。

## 已完成交付物

- [x] `tool_type` registry
- [x] Claude 运行模板
- [x] 工具账户状态机
- [x] 工具账户创建、读取、列表、更新和禁用 API
- [x] 绑定启动、绑定状态查询和 verifier 触发 API
- [x] 节点任务 `create_binding_session`
- [x] 节点任务 `verify_tool_account`
- [x] Claude verifier
- [x] Docker Sandboxes `claude` agent 启动流程
- [x] 账户远端配置归档目录
- [x] 账户地区、时区和 locale 配置
- [x] 账户与节点亲和记录
- [x] `agent-remote account create`
- [x] `agent-remote account bind`
- [x] `agent-remote account verify`
- [x] `agent-remote account status`
- [x] `agent-remote account list`
- [x] `agent-remote account disable`
- [x] OpenAPI 合约更新

## 控制面能力

新增 API：

```text
GET    /api/v1/tool-accounts
POST   /api/v1/tool-accounts
GET    /api/v1/tool-accounts/{tool_account_id}
PATCH  /api/v1/tool-accounts/{tool_account_id}
POST   /api/v1/tool-accounts/{tool_account_id}/bind/start
GET    /api/v1/tool-accounts/{tool_account_id}/bind/status
POST   /api/v1/tool-accounts/{tool_account_id}/bind/verify
POST   /api/v1/tool-accounts/{tool_account_id}/disable
```

账户创建时状态为 `binding_requested`，并初始化远端账户路径引用。绑定启动时控制面按 `tool_type`、`region_code` 和 `preferred_node_tags` 选择可用节点，写入 `affinity_node_id`，状态进入 `binding_session_starting`，并创建 `create_binding_session:{tool_account_id}` 节点任务。

节点回传绑定会话准备成功后，控制面把账户状态更新为 `binding_waiting_user_login`。用户完成远端登录后触发 verifier，控制面创建 `verify_tool_account:{tool_account_id}` 节点任务；节点回传 `verified=true` 后账户状态更新为 `active`。

## 节点端能力

新增配置：

```json
{
  "account_root": "/var/lib/agent-remote/users",
  "docker_binary_path": "docker",
  "tmux_binary_path": "tmux"
}
```

`create_binding_session` 会在 `account_root` 下准备账户目录：

```text
<account_root>/<user_id>/accounts/<tool_account_id>/
  .claude/
  .claude.json
  cache/
  workspace/
  .agent-remote-tool-account.json
```

marker 文件只写非敏感元数据，例如账户 ID、工具类型、地区、时区、locale、sandbox 名称和 verifier 名称。节点端先执行：

```text
docker sandbox create --name <sandbox-name> claude <account_remote_path>
```

随后在 tmux 中持有交互式登录命令：

```text
docker sandbox exec -it \
  -e CLAUDE_CONFIG_DIR=<account_remote_path>/.claude \
  -e TZ=<timezone> \
  -e LANG=<locale> \
  -e LC_ALL=<locale> \
  -w <account_remote_path>/workspace \
  <sandbox-name> claude login
```

这样 Claude 的认证、用户设置和会话历史会持久化在 `<account_remote_path>/.claude`，而不是 VPS 共用 Linux 用户的真实 home。tmux 启动环境也会带上 `TZ`、`LANG`、`LC_ALL`、`AGENT_REMOTE_ACCOUNT_PATH`、`AGENT_REMOTE_TOOL_TYPE` 和 `AGENT_REMOTE_REGION`。

Claude verifier 检查账户目录中是否存在已知 Claude 登录态文件或目录，只回传匹配路径摘要，不回传文件内容。

## CLI 能力

新增命令：

```sh
agent-remote account create --tool claude --name "Claude US" --region US --timezone America/Los_Angeles --tag us
agent-remote account list
agent-remote account bind <account-id>
agent-remote account verify <account-id>
agent-remote account status <account-id>
agent-remote account disable <account-id>
```

CLI 使用当前设备 token 调用控制面。它只打印远端绑定状态、任务 ID、节点 ID、tmux 名称和连接命令，不把 Claude 登录态保存到本地 SQLite、配置文件或 credential store。

## 验收结果

- 普通用户可创建多个 `tool_type=claude` 账户。
- 账户可配置地区、时区、locale 和偏好节点标签。
- 绑定调度会选择匹配地区和标签的可用节点，并记录账户亲和节点。
- 节点端会准备远端账户归档目录并写入非敏感 marker。
- 绑定和 verifier 都通过节点任务执行。
- verifier 成功后账户状态变为 `active`。
- CLI 本地不保存工具账户登录态。

## 后续衔接

Phase 9 可以基于 `active` 工具账户创建真实 Claude session。重点需要接入账户配置注入、同账户节点亲和约束、项目绑定 session 恢复和 `fclaude` 启动路径。
