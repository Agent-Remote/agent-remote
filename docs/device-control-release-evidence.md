# Device-Control Release Evidence Assembly

Production device control stays disabled by default. An evidence workflow only assembles and signs
a short-lived approval manifest; running it does not change Server configuration or enable the
capability.

Two release profiles are supported and their claims must not be mixed:

- `community-local-trust` is the default self-hosted profile for deployments without an Apple
  Developer account. It uses GitHub-hosted runners and the
  `community-device-control-release-evidence` workflow. A valid manifest declares
  `production_ready=true`, `apple_notarized=false`, `public_distribution=false`, and
  `manual_trust_required=true`.
- `apple-developer-id` uses Developer ID signing, Apple notarization, protected external gates, and
  the `device-control-release-evidence` workflow.

Both workflows run from the exact root distribution tag. `release-manifest.json` independently
pins the version, canonical repository, 40-character commit, and artifact-signing workflow for
Server, Node, CLI, Admin Web, and Device. The workflow checks out and downloads each component from
its own tag and rejects a tag whose commit or signing identity differs from the manifest.

## Independent Components And Certified Compositions

Release each component when it is ready. A component release changes only that repository's
version. To adopt it in the supported production composition, update only its root manifest pin:

```sh
python3 scripts/update-release-component.py COMPONENT VERSION FULL_COMMIT_SHA \
  --release-workflow release.yml
python3 scripts/check-device-control-release-readiness.py \
  --manifest release-manifest.json --require-clean --require-tag --require-origin
```

The production flow is:

1. Device publishes the macOS application and standalone proxy artifacts on its own cadence.
2. Node's `release-dependencies.json` explicitly pins the Device proxy version and commit embedded
   in Node archives. A Node release is required only when Node source or that embedded dependency
   changes; Node and Device version numbers need not match.
3. Server, CLI, and Admin Web publish independently.
4. A reviewed root manifest update selects an exact combination. CI verifies every declared source
   version, tag, commit, origin, and cross-component contract.
5. The root distribution release runs the protected evidence workflow and embeds both the source
   manifest and resolved, digest-pinned production manifest in its deployment bundle.

Legacy all-equal compositions continue to emit evidence schemas 1, 3, or 4 so an already released
Server can validate them during migration. A genuinely independently versioned composition emits
schema 5 (Community), schema 6 (Community with v2 evidence), or schema 7 (Apple). These schemas add
`distribution_version`, `release_manifest_sha256`, and the complete `components` identity map while
keeping `release_version` bound to the exact Server version checked at runtime.

The `release_workflow` pin is part of each component identity. Keep it unchanged when the component
continues using the same signer; pass `--release-workflow` when adopting a release whose signing
workflow changed. This preserves verification of older releases such as Device `v0.2.7`, which was
signed by `prepare-release.yml`, while later Device releases use `release.yml`.

## Community Local-Trust Profile

The normal root `release` workflow invokes community evidence automatically. To reissue a
short-lived manifest without rebuilding a deployment bundle, dispatch the same reusable workflow:

```sh
gh workflow run community-device-control-release-evidence.yml \
  --repo Agent-Remote/agent-remote \
  --ref vVERSION \
  -f version=VERSION \
  -f accept_reduced_security=true
```

This workflow runs only on `ubuntu-latest`. It verifies all `linux-amd64-glibc`,
`linux-arm64-glibc`, `linux-amd64-musl`, and `linux-arm64-musl` Node and proxy artifacts, plus the
exact release checksums, Sigstore workflow identities, GitHub provenance, signed SPDX SBOMs,
dependency vulnerability reports,
project self-signed App identity, and successful automation for every manifest-pinned commit. It then
records the administrator's explicit acceptance of the documented reduced-security profile and
signs the applicable legacy schema 3 or independently versioned schema 5 manifest with the
deployment-owned Ed25519 key.

Optional Community v2 quality evidence uses a second protected workflow. It is not required for
runtime capability negotiation. On the dedicated acceptance Mac, place
exactly `community-computer-use-v2-evidence.json` and
`community-computer-use-v2.evidence.tar.gz` in the directory configured by the protected
`COMMUNITY_COMPUTER_USE_V2_EVIDENCE_DIRECTORY` variable, then dispatch:

```sh
gh workflow run community-computer-use-v2-evidence.yml \
  --repo Agent-Remote/agent-remote --ref vVERSION -f version=VERSION
```

After that run succeeds, reissue the Community manifest with its run ID and the tested target:

```sh
gh workflow run community-device-control-release-evidence.yml \
  --repo Agent-Remote/agent-remote --ref vVERSION \
  -f version=VERSION -f accept_reduced_security=true \
  -f computer_use_v2_run_id=RUN_ID \
  -f computer_use_v2_target=linux-amd64-glibc
```

The evidence workflow accepts only a successful run from the dedicated workflow on the exact same
tag commit. It validates the report thresholds, archive member digest, collection age, selected
Node/proxy target, Server image, and application archive before signing schema 4 or 6. Both schemas
requires explicit acceptance of `community_computer_use_v2_without_apple_notarization`.

The workflow does not claim Apple notarization, Gatekeeper trust, system-level network filtering,
independent security review, or unattended public distribution. Those are accepted limitations of
this profile rather than missing fields that force `production_ready=false`. See
`community-local-trust-release.md` for signing, installation, and key configuration.

## Apple Developer ID Profile

The external gate suite is collected by `device-control-external-gates`. Configure its protected
`production-device-release-gates` environment with required reviewers and a dedicated self-hosted
Mac carrying the `agent-remote-device-gates` label. Set the protected environment variable
`DEVICE_CONTROL_EXTERNAL_GATE_DIRECTORY` to an administrator-owned, non-symlink directory on that
runner. The directory must contain exactly the six records and six raw archives listed below.
The workflow only validates and copies those existing files; it does not generate passing records,
infer results from source code, or replace any real test, sensor, notarization, policy, compatibility,
or independent-review procedure.

The readiness inventory proves only version, source, tag, and worktree coherence. It does not
replace artifact signatures, notarization, protected CI, runtime policy probes, or external gate
evidence.

The workflow uses the protected `production-device-release-evidence` environment. Store the
owner-only Ed25519 signing key in that environment as
`DEVICE_CONTROL_RELEASE_PRIVATE_KEY_PEM`. Require deployment-owner review on the environment; do
not expose the key through repository variables, release assets, logs, images, or deployment
bundles.

## External Gate Artifact

The `evidence_run_id` input must identify a successful run of the same root tag and commit. That
run must publish an artifact named `device-control-release-gates` containing exactly these real
validation records and their raw evidence archives:

- `security-tests.json`
- `security-review.json`
- `outbound-policy.json`
- `local-claude-isolation.json`
- `stop-revocation.json`
- `compatibility.json`

For every record, the artifact must also contain `<gate>.evidence.tar.gz`, for example
`security-tests.evidence.tar.gz`. The archive contains the durable raw report, logs, or sensor
export used to reach the recorded result. Its actual SHA-256 digest must equal the record's
`evidence_sha256`; a digest claim without the matching archive is rejected.

Every record uses exactly these common fields:

- `schema_version`: integer `1`.
- `release_version`: exact root distribution version exercised by the external gate run. Component
  versions and commits come from the root release manifest.
- `gate`: exact filename stem, such as `outbound-policy`.
- `status`: `approved` for `security-review`, otherwise `passed`.
- `artifacts`: an object containing exactly `server`, `node`, `application`, and `proxy`, with the
  verified lowercase SHA-256 digest for each release artifact. The server value is its immutable
  OCI digest without the `sha256:` prefix.
- `collected_at`: timezone-aware timestamp no later than manifest issuance and no more than 30
  days before it. Re-signing an old record cannot extend its validity.
- `producer` and `method`: bounded non-empty descriptions of who collected the evidence and how.
- `evidence_sha256`: lowercase SHA-256 digest of the durable underlying report or sensor output.
- `details`: the gate-specific result object below.

Unknown, duplicate, missing, cross-version, future-dated, or cross-artifact fields are rejected.
The gate-specific `details` contracts are:

- `security-tests`: positive `passed`, zero `failed`, at least 60
  `protocol_fuzz_seconds`, HTTPS `test_run_url`, and true
  `coverage_thresholds_passed`, `cross_tenant_e2e_passed`, `macos_permissions_passed`,
  `dedicated_macos_test_host`, `application_signature_verified`, and
  `notarization_ticket_verified`. `coverage` must contain actual and minimum percentages for Server
  lines (70), Node statements (45), CLI lines (45), Admin statements/branches/functions/lines
  (80/65/80/85), Device Rust lines (75), and Device Swift lines (55). Declared minima cannot be
  below these release floors and each actual value must meet its declared minimum. Its Apple
  `team_identifier` must match the notarized application.
  `macos_scenarios` is an exact object whose values must all be true. It covers Accessibility and
  Screen Recording first grant, denial, revocation and post-change restart; signed installation,
  same-version reinstall, upgrade, downgrade rejection, device revoke, uninstall and absence of
  permission residue; the three application control levels, per-session application and clipboard
  approval, the single-session machine lock and crash release; foreground preservation during
  approval and passive observation, prior-foreground restoration after interactive actions, and
  capture exclusion of unapproved windows; global Escape without delivery to the target; release of
  mouse-down, drag and modifier state after disconnect; Retina scaling, negative-origin
  multi-display coordinates, moving a window between displays, display hot-plug, fast user
  switching, sleep/wake, and network switching.
  `computer_use_v2` is also an exact object. It requires true artifact binding, signed installation,
  Safari/Chrome/Firefox/native-application/AX-incomplete-Electron runs, current MCP runtime,
  golden-prompt replay, model-usage-summary binding, and rollback rehearsal; false sensitive
  telemetry and success regression; zero wrong-target actions; at least 70 percent fewer
  model-visible images; action p95 at most 1000 ms; settle p95 at most 5000 ms; and coordinate
  fallback strictly below 20 percent. Its lowercase `report_sha256` must match an actual regular
  file inside `security-tests.evidence.tar.gz`; the archive digest and structured gate-record digest
  are separate bindings and cannot substitute for the report digest.
- `security-review`: non-empty `reviewer` and `report_signature_identity`, lowercase SHA-256
  `report_sha256`, exact review scope covering Server, Node, application, proxy, and release-evidence
  assembly, zero `critical_open` and `high_open`, and true `independence_confirmed`,
  `report_signature_verified`, and `retest_complete`. These structured assertions index the raw
  signed report archive; the assembler requires `report_sha256` to match a regular file inside that
  archive. They do not make a self-authored review independent.
- `outbound-policy`: active `policy_identifier`, exact ten-character `team_identifier`, fixed
  Network Broker bundle identifier, attestor mach service and lowercase SHA-256 of its raw Ed25519
  public key, non-empty HTTPS `allowed_destinations` with no Anthropic host, and true `active`,
  `network_extension_enforced`, `challenge_bound_probe`, `allowed_probe_succeeded`,
  `anthropic_probe_blocked`, and `unauthorized_probe_blocked`. The policy ID, process identity,
  attestor service, public-key digest, and Team ID must exactly match the values extracted from the
  signed notarized application; two independently valid records for different policies are rejected.
- `local-claude-isolation`: at least 60 `observation_seconds`, true
  `local_claude_installed` and `local_claude_logged_in`, and zero `claude_paths_accessed` and
  `anthropic_connections`. It also requires true `file_sensor_active`, `network_sensor_active`,
  `sensor_output_complete`, and `application_process_identity_verified`; the observed process Apple
  `team_identifier` must match the notarized application.
- `stop-revocation`: zero `failed`, false `permission_residue` and
  `unconfirmed_action_replayed`, and all required `scenarios`: device/server revocation, Escape,
  executor crash, lease expiry, relay disconnect, and screen lock.
- `compatibility`: non-empty `claude_code_version` and `mcp_protocol_version`, HTTPS
  `test_run_url`, zero `failed`, and the exact 16 public MCP `public_actions` exposed by the proxy.
  The same real Claude Code run must set true `managed_mcp_configuration_verified`,
  `mcp_image_results_verified`, `long_sequence_completed`, and `turn_stop_observed`; source-level
  schema tests do not satisfy these runtime observations.

The Device release also publishes a separately signed `signing-notarization` record. It binds the
application archive digest to the release version, Apple Team ID, fixed bundle identifier,
notarization submission, hardened runtime, artifact signature verification, stapler validation,
and Gatekeeper assessment. The assembler rejects a valid notarization result copied from another
application archive.

## Computer Use v2 Quality Evidence

Computer Use v2 is negotiated automatically for new generations when
`DEVICE_CONTROL_V2_ENABLED=true` and the assigned Node advertises the complete capability set.
General production release evidence remains mandatory, but `computer_use_v2_evidence_sha256` is
optional quality metadata rather than runtime authorization. The Apple-profile assembler validates
`security-tests.computer_use_v2`; the Community assembler validates the equivalent protected
schema 4 record and its selected multi-architecture target. Both write the validated record digest
to `computer_use_v2_evidence_sha256`, covered by the canonical Ed25519 signature. The object also
names the raw report with `report_sha256`, and assembly fails unless a file with that exact digest
exists in the bounded security-tests evidence archive.

The bound report must use only non-sensitive tasks and prove signed installation; Safari, Chrome,
Firefox, native application, and AX-incomplete Electron coverage; golden-prompt replay; zero
wrong-target actions; no success-rate regression; no sensitive telemetry; at least 70% fewer
model-visible images; action p95 no greater than 1 second; settle p95 no greater than 5 seconds;
coordinate fallback below 20%; and a rehearsed `true -> false` new-generation rollback. It must bind
the model/runtime token and image-usage summary to the same run and artifact digest without placing
prompts, responses, AX text, URLs, screenshots, input, coordinates, or clipboard data in device
telemetry.

The production Server verifies the general signed manifest at startup and while processing
device-control operations, but does not require this optional field. Community schema 2 and 3
manifests keep it `null`; schema 4 carries it only when a real report from the signed release
artifacts passes the stricter quality gate. Operators can set `DEVICE_CONTROL_V2_ENABLED=false` to
force new generations to v1 without changing release evidence.

The assembler verifies every raw evidence archive, hashes the complete validated records, and
copies both into the final evidence artifact under `gates/` for offline review. It does not infer
that source checks prove
runtime network enforcement, local Claude isolation, Apple notarization, compatibility, or
independent review.

The workflow verifies each Server, Node, application, and proxy SBOM with the exact producing
release workflow's Sigstore identity; checking SPDX structure alone is insufficient. It fails when
any release, external record, protected key, digest, signature, attestation, SBOM, or notarization
result is missing or invalid. On success it uploads an Actions
artifact containing the signed server manifest, unsigned draft, SBOM/provenance inventories, and
the validated gate records and raw archives, and checksums with 30-day retention. Deployment must
separately pin the matching Ed25519 public key
and explicitly configure the server evidence path. The server still verifies its own exact version,
signature, issue time, and expiry at startup.
