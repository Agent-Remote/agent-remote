# ego-browser Bridge release promotion

This document describes the current evidence promotion contract. Exact versions, commits, artifact digests and component readiness come from the verified root `release-manifest.json`; no historical version or tag is copied into this runbook.

## Required evidence

- The Bridge component has a clean, reviewed source commit and a release artifact whose manifest, checksum, signature and provenance agree.
- The root manifest pins the exact Server, Node, CLI, Admin Web, Device and Bridge composition.
- The community local-trust evidence binds the candidate manifest bytes, component identities, artifact/SBOM/provenance digests, certificate pin and learning bundle digest. The root manifest is schema 4; the signed Device-control evidence document is schema 9.
- The target macOS installation passes certificate, Hardened Runtime, permission, relay, Task Space and logged-in ego lite canary checks.
- Production capability remains disabled until all evidence is assembled and independently reviewed.

## Promotion order

1. Build and verify each component with its repository quality gate. Keep the candidate artifacts in an owner-only temporary directory.
2. Update a candidate root manifest only through the repository's release tooling; validate schema, component commits, origin, artifact inventory and dependency pins.
3. Assemble the schema 9 evidence against the exact candidate manifest bytes. Sign it with the protected deployment key and verify the signature and every bound digest.
4. Install the exact candidate on a disposable target Mac and run the real Bridge canary. Record only bounded status, IDs, digests and result codes.
5. Have the release owner review the candidate, evidence, target-host records and risk acceptance. Apply the candidate to the release branch only after review.
6. Re-run verification against the final tag-bound manifest and evidence before any publication or capability enablement.

The promotion scripts reject missing, mismatched, stale or partially signed evidence. Editing `production_ready`, `release_published`, blocker fields or a digest by hand is invalid. A failed or unknown canary remains failed/unknown; it is never repaired by replaying a request or selecting a newer session.

Publishing, uploading, tagging and enabling production capability are separate operator decisions. Every rehearsal must remove temporary credentials, profiles, sessions, sockets, artifacts and logs after the record is captured.
