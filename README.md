# agent-remote

English | [中文](README.zh-CN.md)

agent-remote is an open-source, self-hosted system for running AI coding agents from trusted remote environments while keeping local developer workflows close to native usage.

The project is designed for individuals and small teams that want Claude Code first, with room for future tools such as Codex. A local command such as `fclaude` connects to a remote node through WireGuard, keeps project files synchronized with Mutagen, and attaches to a long-lived tmux-backed agent shell inside a controlled Docker runtime.

## Repositories

- `agent-remote`: project-level deployment bundle, architecture, and cross-repository documentation.
- `agent-remote-server`: Python 3.13 control-plane API for users, devices, nodes, sessions, sync, browser tasks, and audit data.
- `agent-remote-admin-web`: React/Vite administrative console.
- `agent-remote-node`: Go node runtime deployed on VPS hosts.
- `agent-remote-cli`: Rust local CLI and tool launchers such as `agent-remote` and `fclaude`.

## Runtime Model

- WireGuard provides the local-to-node private network path.
- Mutagen provides project file synchronization.
- Docker isolates tool runtimes on the node.
- tmux keeps remote agent shells alive across local disconnects.
- SSH is used for native terminal attachment and forced-command node access.
- Remote temporary browser sessions use node-side browser containers and VPS network identity.

## Documentation

- `docs/agent-remote-architecture.md`
- `docs/agent-remote-implementation-appendix.md`
- `docs/deployment.md`
- `docs/e2e-acceptance.md`
- `docs/phase-12-completion.md`
- `docs/phase-13-completion.md`

## Releases

Each repository has a `prepare-release` workflow. Running it with a version updates repository-owned version files, updates `CHANGELOG.md`, commits `chore: release vX.Y.Z`, pushes the tag, and dispatches the release workflow.

Release workflows publish deployment archives, CLI/node binaries, GHCR images, and GitHub Release notes.

## License

agent-remote is licensed under GPL-3.0-only. See `LICENSE`.

Third-party dependency notices are listed in `THIRD_PARTY_NOTICES.md`.
