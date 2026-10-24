# Agent Remote architecture

This document records the current repository boundaries. Detailed API fields,
operational procedures and historical migration notes belong to the owning
repository documents linked below.

## Components

| Component | Runtime | Owns |
| --- | --- | --- |
| `agent-remote-cli` | Rust | local home, credentials, command schemas, request keys, operation journals and SSH/Mutagen/WireGuard clients |
| `agent-remote-server` | Python/FastAPI/SQLAlchemy | authenticated users, devices, accounts, workspaces, sessions, task rows, immutable receipts and migrations |
| `agent-remote-node` | Go | device registration, runtime workers, exact session attachment, lifecycle fences, workspace safety and cleanup |
| `agent-remote-desktop` | Go/mygo | native window, Zen workbench, terminal panes, presentation, layout and public session metadata |

The desktop invokes the CLI through versioned structured contracts. The CLI,
Server and Node validate the complete context (home, server, device, account,
workspace, session and operation key) before any mutation. A lost response is
queried by its original key; it is never replayed with a new key or inferred
from the latest row.

## Data and security boundaries

- CLI secrets and operation journals remain in the CLI home. The desktop stores
  only its own layout, theme, project and public session metadata.
- Server task results are immutable observations. Historical success is not a
  current authorization or liveness proof.
- Node workers require exact device and runtime identity, use bounded managed
  paths, and keep cleanup pending when termination is not proven.
- Attachments, browser artifacts and WireGuard configuration are transferred
  only through their versioned, digest-bound contracts. Raw credentials, private
  keys, relay tickets and user content are not projected into generic UI or
  diagnostics.

## Main flows

1. A local desktop session starts a managed PTY/ConPTY process and persists only
   public presentation metadata.
2. A remote session freezes its exact context, asks the CLI to create or attach
   once, and then observes the original Server task and Node session.
3. Synchronization remains an explicit, separately observable phase. A successful
   sync observation does not claim that a session is running or that project files
   are fully saved.
4. Protected WireGuard operations use a platform broker with caller proof,
   configuration digest binding, one-time permits and post-action observation.
5. Account import, recovery, deletion and attachment cleanup preserve the
   original request key and receipt until the control plane proves a terminal
   result.

## Current documentation

- CLI commands and contracts: `../agent-remote-cli/README.md`,
  `../agent-remote-cli/docs/`
- Server API and persistence: `../agent-remote-server/README.md`,
  `../agent-remote-server/docs/`, `../agent-remote-server/migrations/`
- Node runtime and worker contracts: `../agent-remote-node/README.md`,
  `../agent-remote-node/docs/`
- Desktop product and release gates: `agent-remote-desktop-design.zh-CN.md` and
  `../agent-remote-desktop/docs/implementation-status.md`

The current source tree and tests are authoritative when an older external
reference disagrees. This index contains no superseded design or unreleased command draft.
