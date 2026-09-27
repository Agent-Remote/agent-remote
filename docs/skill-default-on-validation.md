# Skill default-on validation — 2026-09-27

Skill management now defaults to enabled in Server settings, Compose and fresh/missing-field Node
configuration. Explicit false remains an administrative override, including through upgrades.
Older installations containing the previous generated false need a one-time migration.

## Real deployment checks

The operator's environment ran CLI **0.2.33**, Server **0.2.28**, and Node **0.2.30**. Server was
already enabled. After proving no sessions or pending Node work, only the Node Skill switch was
changed to true with atomic replacement and unchanged ownership/permissions. Helper and Worker
restarted successfully. All four Skill probes passed; Server received a fresh complete Native
protocol/manifest/deployment version-1 report with writable copies, finalization and recovery.

The following checks used the installed CLI against the actual authenticated HTTPS Server. A
temporary unbound account scoped the test skill away from the existing account. No host tool
credentials were copied and no model sessions were created.

| Check | Result |
| --- | --- |
| Local discovery and dry-run | Passed; preview did not advance generation |
| Account-scoped installation and effective queries | Passed; user default stayed disabled and existing account did not select the fixture |
| Content download | Both files in each of two revisions matched exact source bytes, sizes and SHA-256 hashes |
| Original operation status and local-source check | Passed |
| Stage update | Registered r2 while r1 remained active |
| Activate update with an account pin | User default advanced to r2 while the account retained r1 |
| Unpin and rollback | Unpin selected r2; explicit rollback restored r1 |
| Disable, enable and enabled-field inheritance | Effective values matched each operation and inherited disabled user default |
| State and storage diagnostics | Passed; unbound account had no runtime checkpoint |
| Source identity guard | Reusing a local source path with a different skill name returned SOURCE_LAYOUT_CHANGED |
| Remove and account cleanup | Fixture archived, temporary accounts deleted, existing account list exactly matched baseline |

Cleanup verified empty active user/local libraries, no pending deletion tasks, zero package/state
reservations and zero runtime-state bytes. The normal retention policy kept **1270 bytes** of package
content in total (**739 bytes** before this test, **531 bytes** added). Immutable operation receipts
and monotonic generation **13 → 27** were preserved; no SQL deletion or generation rollback was used.
Local source fixtures were removed. The intentionally enabled Node switch remains enabled.

## Applicability and boundaries

The new releases change installation defaults; Skill execution, content, API and protocol logic are
unchanged from the versions used above. These results therefore apply to that business logic. New
release configuration behavior is separately covered by default/missing/explicit-false tests,
Node registration and save/upgrade round trips, and rendered Compose configuration. Published Node
0.2.31 archive checksum, provenance and enabled installer configuration were also verified.

The unbound account correctly reported `stored` with `deploy_on_first_use=true`. This proves durable
configuration and content, not actual Node deployment. Real bound-account takeover, Claude skill
discovery/learning and next-session inheritance remain separate acceptance work. Docker Sandbox
managed Skill support is not claimed.

## Repository checks

Node full gates passed at 63.1% coverage. Server full gates passed with 1868 tests, 104 skips and
91.50% coverage; its explicit-disabled admission test now sets false instead of assuming the former
default. CLI full local gates passed all 608 tests. Its three-platform CI passed after the macOS
blocked-output cancellation test timed out once, then passed both isolated local verification and
an unchanged failed-job rerun; no threshold or product logic was modified for that timing event.
