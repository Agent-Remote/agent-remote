# agent-remote Phase 12 完成记录

## 状态

Phase 12：打包、安装和部署，状态为完成。

本阶段目标是让自部署用户可以部署控制面、安装节点、打包 CLI，并具备升级、备份和恢复的基础文档。

## 完成内容

- 新增控制面 Docker Compose：
  - server
  - admin-web
  - PostgreSQL
  - Redis
  - Caddy
- 新增 Caddy 和 Nginx 反向代理示例。
- 新增部署、升级、备份恢复文档。
- server 镜像补齐 Alembic 迁移启动入口。
- admin-web 新增静态镜像构建。
- node 新增 systemd service、环境文件、安装器和 release 构建脚本。
- CLI 新增 macOS/Linux release 打包脚本，包含 Mutagen 下载和托管依赖 manifest。
- 新增 GitHub Actions：
  - 主仓库校验 Compose，并在 `v*` tag 发布部署包。
  - server 在 `v*` tag 构建并推送 GHCR 镜像。
  - admin-web 在 `v*` tag 构建并推送 GHCR 镜像。
  - node 在 `v*` tag 构建 Linux 节点归档。
  - CLI 在 `v*` tag 构建 macOS/Linux CLI 归档。

## 验收

- Compose 配置可通过 `docker compose config` 校验。
- server Dockerfile 包含迁移入口。
- admin-web 可构建静态镜像。
- node 可通过 systemd 运行 `agent-remote-node run`。
- CLI release 脚本生成包含 `agent-remote`、`fclaude`、WireGuard helper 和 Mutagen 的归档。
- 推送 `vX.Y.Z` tag 会自动生成对应 GitHub Release 或 GHCR 镜像。

## Phase 13 进入条件

Phase 13 可以开始，前提是：

- Phase 12 提交已推送。
- 至少完成一次空环境控制面部署。
- 至少完成一次新 VPS 节点注册。
- 至少完成一次 macOS 或 Linux CLI 安装并执行 `agent-remote init`。

进入 Phase 13：端到端验收和 MVP 发布。
