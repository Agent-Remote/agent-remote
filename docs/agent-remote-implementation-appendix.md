# Implementation and contract index

This file is an index of the current implementation. It is intentionally kept
short; command details and field definitions belong to the repository that owns
the contract. Do not add historical command drafts here.

## Current owners

- Rust CLI: `../agent-remote-cli/README.md` and `../agent-remote-cli/docs/`
- Control plane: `../agent-remote-server/README.md` and `../agent-remote-server/docs/`
- Node runtime: `../agent-remote-node/README.md` and `../agent-remote-node/docs/`
- Desktop workbench: `../agent-remote-desktop/README.md` and
  `../agent-remote-desktop/docs/`

## Cross repository boundaries

- The CLI owns local configuration, credentials, request keys, operation journals
  and user-facing command semantics.
- The Server owns authenticated control-plane state, durable task rows, immutable
  receipts and database migrations.
- The Node owns device-local runtime execution, exact session attachment,
  lifecycle fences, workspace safety and cleanup receipts.
- The desktop owns native presentation, layout and public session metadata. It
  calls the CLI through versioned structured contracts and never reads CLI
  secrets or reconstructs authorization from historical results.

## Contract index

- Exact session creation, stop, deletion and attachment: the matching
  `session-*.md` documents in the CLI, Server and Node repositories.
- Account binding and configuration import: `desktop-account-*.md` in the CLI and
  `account-*.md` / `config-import-*.md` in the Server.
- Synchronization and Mutagen recovery: `desktop-sync.md` in the CLI and
  `workspace-sync-safety.md` in the Server and Node.
- WireGuard inspection, tunnel execution and protected brokers: the
  `wireguard-*.md` documents in the desktop and CLI repositories.
- Ego-browser artifact and bridge policy: `ego-browser-*.md` in the Node and root
  repositories.

The release status for the desktop is maintained only in
`../agent-remote-desktop/docs/implementation-status.md`. Platform, broker, live
remote-chain and performance evidence must be recorded there before publishing.
