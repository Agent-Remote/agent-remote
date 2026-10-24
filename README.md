# agent-remote

<p align="center"><img src="assets/agent-remote-icon.svg" alt="Agent Remote icon" width="96" height="96"></p>

English | [中文](README.zh-CN.md)

`agent-remote` is an open-source, self-hosted system for running AI coding agents in trusted remote environments while keeping the local workflow close to a native terminal.

## Components

| Repository | Responsibility |
| --- | --- |
| `agent-remote-server` | FastAPI control plane for users, devices, accounts, nodes, sessions, synchronization and audit data. |
| `agent-remote-node` | Poll-based Go runtime on a VPS node. It does not expose a public control HTTP API. |
| `agent-remote-cli` | Rust local CLI and launchers: `agent-remote`, `fclaude`, WireGuard, SSH, Mutagen and desktop-control contracts. |
| `agent-remote-desktop` | Native Go/mygo workbench for local Codex/Claude and remote `fclaude` sessions. |
| `agent-remote-admin-web` | React/Vite administration console. |
| `agent-remote-device` | Swift macOS Device app and managed MCP proxy. |
| `agent-remote-ego-browser` | macOS Bridge, Device Client, Linux wrapper and release tooling for explicit full-trust browser control. |

## Runtime model

- WireGuard provides the private device-to-node path.
- Mutagen synchronizes a selected project workspace.
- The control plane selects an administrator-approved `native` or `docker_sandbox` backend for each tool account.
- The node runs the selected Agent in an isolated runtime and keeps its shell in tmux.
- SSH attaches the local terminal to the authorized tmux session.
- The desktop shares CLI configuration, credentials and structured operation contracts; it does not maintain a second credential store.

The desktop is still under development. Its redesign is implemented, but a formal release still requires the platform, broker, remote-chain and performance evidence listed in its implementation status.

## Documentation

Use the current code contracts as the source of truth:

- Product and cross-repository plan: `docs/agent-remote-desktop-design.zh-CN.md`
- Desktop implementation and release status: `../agent-remote-desktop/docs/implementation-status.md`
- Deployment and upgrade: `docs/deployment.md`, `docs/upgrade.md`
- Runtime architecture: `docs/agent-remote-architecture.md`, `docs/native-runtime-design.md`
- Session forwarding: `docs/session-port-forwarding-design.md`
- Device-control security and operations: `docs/local-device-control-security-design.md`, `docs/device-control-operations-runbook.md`
- Ego-browser lifecycle and release: `docs/ego-browser-humanized-lifecycle.md`, `docs/ego-browser-bridge-release-promotion.md`
- Skills: `docs/skill-manager.md`, `docs/skill-manager-wire-v1.md`, `docs/skill-acceptance-plan.md`

Historical planning notes are retained only when they explain a current compatibility or migration boundary. They are not implementation status.

## Cross-repository checks

Run the component checks in each sibling repository. The root repository also provides contract and release-evidence scripts, for example:

```sh
python3 -m pytest
bash scripts/run-local-device-control-e2e.sh
python3 scripts/check-device-control-release-readiness.py
```

Use temporary homes, test credentials and disposable server/node data for acceptance runs. Do not use a production credential or a real user workspace.

The root repository keeps these cross-repository and release script entry points:

```sh
bash scripts/run-local-device-control-e2e.sh
bash scripts/run-session-port-forwarding-e2e.sh
python3 scripts/check-device-control-release-readiness.py
scripts/prepare-release.sh <version>
scripts/update-changelog.sh <version>
```

They operate on disposable test data or release metadata; they do not publish a release by themselves.

## Release policy

Each repository has its own version and release workflow. A root composition release must pin the exact component commits, artifacts, schemas and compatibility evidence. The desktop formal targets are `darwin/arm64`, `windows/amd64` and `linux/amd64`; macOS uses the project community self-signing identity, while Windows/Linux do not require publisher code signing. Apple Developer ID and notarization are outside this release policy.

Do not publish a release until every required native, remote, security and compatibility gate is green and reviewed by the user.

## License

GPL-3.0-only. Third-party notices are in `THIRD_PARTY_NOTICES.md`.
