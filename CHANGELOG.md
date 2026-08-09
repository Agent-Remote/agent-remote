# Changelog

All notable changes to this repository are recorded here.

## v0.2.5 - 2026-08-09

- feat(device-control): make computer use v2 upgrade-ready (9384d41)

## v0.2.4 - 2026-08-09

- feat(release): authorize community computer use v2 evidence (f5ed754)

## v0.2.3 - 2026-08-09

- test: add device acceptance deployment profile (542a14b)

## v0.2.2 - 2026-08-07

- Release metadata update.

## v0.2.1 - 2026-08-05

- feat: add computer use v2 release controls (1d1a4b5)

## v0.2.0 - 2026-08-04

- Release metadata update.

## v0.1.9 - 2026-08-04

- Release metadata update.

## v0.1.8 - 2026-08-03

- feat: add local device session binding (54cdad8)

## v0.1.7 - 2026-08-01

- fix: avoid automated release evidence deadlock (4b452a5)
- chore: release v0.1.7 (6da03c0)
- feat: embed automated release evidence in deployment bundles (7f5a23f)

## v0.1.6 - 2026-08-01

- docs: document safe client identity upgrades (5d3b1cc)

## v0.1.5 - 2026-07-31

- Release metadata update.

## v0.1.4 - 2026-07-31

- fix: accept protected release automation evidence (b88ffa5)
- fix: commit all prepared release files (be71834)
- feat: add community local-trust release evidence (0b84ce4)
- build: package multi-architecture test images (4eac630)
- docs: record verified release gate runs (dcae759)
- test: harden release and tunnel readiness (9c1baf2)
- test: stabilize macOS tunnel readiness (40ce1f2)
- ci: run device E2E with Swift 6 (6db29cd)
- feat: coordinate secure device control releases (68e24e3)
- ci: disable noisy cross-repo Go cache (692c2cb)
- ci: separate platform tunnel stress coverage (e033734)
- test: stabilize concurrent tunnel e2e (a82b94b)
- ci: run tunnel e2e on macos (c704035)
- test: verify 100 concurrent tunnel streams (dc959e1)
- ci: fix cross-repo Go caching (dd9ffb5)

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
