# Changelog

All notable changes to this repository are recorded here.

## v0.1.0 - 2026-07-31

- feat: coordinate secure local device control release evidence and external gates
- build: assemble a unified multi-component local device control test release
- test: verify the Server-to-Node-to-Rust-to-Swift device control path
- ci: run Swift 6 device control E2E on macOS 15
- test: use a retryable HTTP readiness window in the macOS tunnel E2E
- build: package Server and Admin test images for both Linux amd64 and arm64
- ci: disable noisy cross-repo Go cache (692c2cb)
- ci: separate platform tunnel stress coverage (e033734)
- test: stabilize concurrent tunnel e2e (a82b94b)
- ci: run tunnel e2e on macos (c704035)
- test: verify 100 concurrent tunnel streams (dc959e1)
- ci: fix cross-repo Go caching (dd9ffb5)

## v0.0.6 - 2026-07-29

- feat: document and verify session port forwarding (ae17178)

## v0.0.5 - 2026-07-27

- feat: add agent remote brand icon (e6e6d9c)
- docs: document Windows CLI support (3375c5d)
- docs: refresh third-party notices (55b128a)
- docs: remove obsolete phase and e2e artifacts (e5ab17c)
- docs: document session lifecycle improvements (1420613)
- docs: document node development runtime (44ee577)
- docs: add developer credential acceptance (6dde354)
- docs: document dynamic terminal resizing (a4c0f87)
- fix: replace release script atomically (1a87fd6)

## v0.0.4 - 2026-07-23

- docs: document native runtime architecture (db0b938)
- fix: keep release version examples in sync (3f5df20)
- docs: complete phase 13 acceptance (7700090)

## v0.0.3 - 2026-07-07

- docs: remove protocol repository references (90dde30)
- docs: sync Chinese README with English (701e984)
- chore: standardize release metadata (603e33d)
- ci: allow manual release dispatch (edfe50c)

## v0.0.2 - 2026-07-07

- ci: allow manual release dispatch (edfe50c)
- chore: release v0.0.2 (2608c93)
- ci: add release preparation workflow (d01d4ba)
