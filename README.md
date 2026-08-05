# agent-remote

<p align="center"><img src="assets/agent-remote-icon.svg" alt="Agent Remote icon" width="96" height="96"></p>

English | [中文](README.zh-CN.md)

agent-remote is an open-source, self-hosted system for running AI coding agents from trusted remote environments while keeping local developer workflows close to native usage.

The project is designed for individuals and small teams that want Claude Code first, with room for future tools such as Codex. A local command such as `fclaude` connects to a remote node through WireGuard, keeps project files synchronized with Mutagen, and attaches to a long-lived tmux-backed agent shell. Claude can run in the default Linux-native isolation runtime without KVM or Docker, while Docker Sandbox remains an optional compatible backend.

## Repositories

- `agent-remote`: project-level deployment bundle, architecture, and cross-repository documentation.
- `agent-remote-server`: Python 3.13 control-plane API for users, devices, nodes, sessions, sync, browser tasks, and audit data.
- `agent-remote-admin-web`: React/Vite administrative console.
- `agent-remote-node`: Go node runtime deployed on VPS hosts.
- `agent-remote-cli`: Rust local CLI and tool launchers such as `agent-remote` and `fclaude`.
- `agent-remote-device`: Swift macOS device application and Rust managed MCP proxy.

## Runtime Model

- WireGuard provides the local-to-node private network path.
- Mutagen provides project file synchronization.
- The control plane pins each tool account to an administrator-approved `native` or `docker_sandbox` backend.
- Native Runtime uses per-user Linux identities, systemd cgroups, Bubblewrap, network namespaces, and nftables; it does not require KVM or Docker.
- Docker Sandbox remains available on nodes that explicitly enable and report that capability.
- tmux keeps remote agent shells alive across local disconnects.
- SSH is used for native terminal attachment and forced-command node access.
- Remote temporary browser sessions use node-side browser containers and VPS network identity.
- `Agent Remote Device.app` uses its device credential to list and claim a currently running remote
  Claude session; rebind revokes old device control without stopping remote Claude.

## Documentation

- `docs/agent-remote-architecture.md`
- `docs/agent-remote-implementation-appendix.md`
- `docs/native-runtime-design.md`
- `docs/session-port-forwarding-design.md`
- `docs/local-device-control-security-design.md`
- `docs/local-device-control-binding-design.md`
- `docs/local-device-control-release-gate-status.md`
- `docs/device-control-operations-runbook.md`
- `docs/deployment.md`

Computer Use v2 的完整优化方案以
`docs/local-device-control-security-design.md` 第 6.5 节为架构与安全事实源；协议状态机、benchmark
和模型调用规则分别位于 sibling Device 仓库的 `docs/protocol.md`、
`docs/optimization-benchmark.md` 和 `skills/agent-remote-device/`。生产灰度与回滚按
`docs/device-control-operations-runbook.md` 执行，不能只修改 skill 提示词或 Server 百分比。

## Cross-Repository Tests

With the server, node, and device repositories checked out as sibling directories, run the real
device-control data path through FastAPI/WebSocket, the Go Node bridge, Rust nested TLS, and the
Swift Network.framework peer. The current harness negotiates the complete v2 capability set and
verifies an `observe(auto)` AX-full response without a screenshot:

```sh
scripts/run-local-device-control-e2e.sh
```

The harness uses loopback-only `http/ws` for its temporary control plane. Production device
credentials and relay clients continue to require `https/wss`.

## Releases

Each repository has a `prepare-release` workflow. Running it with a version updates repository-owned version files, updates `CHANGELOG.md`, commits `chore: release vX.Y.Z`, pushes the tag, and dispatches the release workflow.

Release workflows publish deployment archives, CLI/node binaries, GHCR images, and GitHub Release notes.
Device-control production evidence has a separate protected assembly flow documented in
`docs/device-control-release-evidence.md`. The coordinated root release embeds the signed
multi-architecture community manifest in its deployment bundle; it never enables the capability
automatically.

## License

agent-remote is licensed under GPL-3.0-only. See `LICENSE`.

Third-party dependency notices are listed in `THIRD_PARTY_NOTICES.md`.
