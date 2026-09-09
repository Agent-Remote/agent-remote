# Local ego-browser Bridge Security Boundary

## Scope

The local ego-browser Bridge is separate from the temporary VPS browser and
general GUI device control. It binds one explicitly selected remote `fclaude`
tool session to one independent local macOS Bridge identity and uses
`control_channel=ego_browser_bridge`, `relay_binding_kind=ego_browser`, and
`authorization_mode=ego_browser_script_full_trust`.

It does not reuse another device product's identity, credential, generation,
relay route, authorization, proxy, app, Keychain namespace, or runtime. That
product may be absent throughout build, installation, authorization, execution,
test, and rollback.

## Full-trust grant

The grant is arbitrary Node.js/heredoc execution under the macOS user running
the Bridge, without App Sandbox isolation. The remote session can use the full
ego lite browser surface, all tabs and Task Spaces, browser login state and
cookies, user-readable files and environment, localhost and LAN, network
requests, dynamic imports, and subprocesses. It can send accessible data to the
remote model or elsewhere.

A dedicated Task Space, the upload allowlist, and cooperative concurrency locks
protect the normal Skill workflow. None is a security sandbox. Explicit
full-trust code can select other tabs, use raw CDP, read files outside helper
paths, or use its own network and subprocess APIs.

The Node broker derives `agent-remote:<tool_session_id>` from the authenticated
session nonce and returns it in each one-time permit. The wrapper ignores shell
overrides when constructing the encrypted `default_task_space`, and the Bridge
preamble remaps the official Skill's normal `useOrCreateTaskSpace(...)` call to
that name. The preamble does not eagerly select a space and does not wrap
`claimTaskSpace`, `takeOverTaskSpace`, Tab helpers, or raw CDP.

The Server independently derives the same canonical label when the Device
Client claims the selected session and rejects a supplied mismatch. The Device
Client validates the claim/resume response before writing the label to its
owner-only active-binding handoff. The Bridge loads that bound value and rejects
an encrypted request whose default label or declared Task Space scope differs.

Takeover detection is not based on request exceptions or stderr. After binding
activation, a separate process supervised by the Bridge calls only native
`listTaskSpaces()` and reads the matching space's `ownership`. It first arms on
`agent`; only a later `agentDelegatedToUser` or `user` state is a takeover. It
never calls or wraps `useOrCreateTaskSpace`, `claimTaskSpace`, or
`takeOverTaskSpace`. Duplicate matches, unknown ownership, runtime failure, and
unexpected monitor exit fail closed. The Bridge holds the execution
supervisor's control pipe, so Bridge death also terminates the monitor runtime.

Stopping invalidates admission and externally terminates the supervised process
group. It cannot undo browser, file, or network side effects, and cannot promise
cleanup of hostile same-UID code that deliberately detached itself.

For Task Space takeover, the Bridge first revokes local admission and waits for
managed executions to terminate. It then requests a generation-bound Server
pause with the bounded reason `task_space_takeover`; monitor failure uses
`task_space_monitor_unavailable`. Failure to confirm that pause never restores
local admission. Recovery requires another explicit full-trust confirmation
and a new generation. Native claim/takeover helpers remain available for a
user-directed handback, but no component invokes them automatically.

## Identity and transport

- Device mutations use Ed25519 proof of possession with a Server-issued,
  short-lived, single-use challenge.
- The signed v2 transcript binds operation, exact canonical payload, challenge,
  device ID/generation, binding ID/generation, release and credential profiles,
  and Server host.
- Only the authenticated Node broker redeems the Node relay ticket. The wrapper
  receives one-time permits over an owner-only Unix socket.
- Each request uses an X25519-wrapped ChaCha20-Poly1305 key. Outer routing fields
  are authenticated associated data; the Server forwards opaque ciphertext.
- Production local clients accept one canonical HTTPS origin, disable redirects,
  derive WSS from that origin, and use only a Server-issued fixed relay path.
- The macOS Bridge opens no public or LAN listener. Its production connection is
  outbound only.

The control plane stores lifecycle, capability, version, digest, and audit
metadata. It must never store or log scripts, stdout/stderr bodies, page text,
screenshots, form input, cookies, URLs, local paths, tickets, keys, or plaintext
inner frames. Metrics may use bounded status, size, and duration labels only.

## Local and release trust

The community credential store uses current-UID owner-only directories and
singly linked regular files. The local installer separately pins the signing
certificate in a current-UID, singly linked `0400` file. It verifies the strict
release manifest, tag-bound Sigstore identities, artifact digest and inventory,
nested code signatures, Hardened Runtime, and leaf certificate before
installation; quarantine is cleared and recursively rechecked only after those
checks, followed by another installed-release verification.

`community-local-trust` is project self-signed, not Apple notarized, and not a
public-distribution profile. `application-enforced` origin policy is not a host
firewall. Operators must distribute the certificate digest through a separate
trusted channel and may add host egress controls.

## Production status

The root schema-v3 composition records the published Bridge `0.1.7` commit,
certificate pin, learning-bundle digest, and nested-signature evidence with
`production_ready=true` and an empty blocker list. The root release workflow
still verifies those facts, binds schema 9 evidence to the exact root tag, and
refuses a mismatched composition.

Production deployments must keep `EGO_BROWSER_BRIDGE_ENABLED=false` until the
root `0.2.21` bundle and its artifact-bound logged-in canary are approved.
Development mode remains limited to synthetic, non-sensitive data.
