# ego-browser Bridge Release Promotion

The root composition was initially blocked until the Bridge had a real,
published release and a protected Site Learning signing key. The original four
blockers are evidence requirements, not configuration switches. Bridge `0.1.8`
now clears all four, and the stable root `0.2.25` release binds that promotion
to tag-bound schema 9 evidence. The remaining work is installing the exact
certified bundle and completing the final canary.

| Current blocker | Evidence that clears it | Where it is recorded |
| --- | --- | --- |
| `unpublished_component_commit` | A clean Bridge commit has an exact immutable `vVERSION` tag and a published, non-draft, non-prerelease GitHub Release | Root Bridge component `commit` and `release_published=true` |
| `release_certificate_unpinned` | The persistent community P12 signs Bridge, Device Client, and learning verifier binaries; the leaf certificate SHA-256 is independently distributed and matches every signing record | `signer_certificate_sha256` and Bridge signing evidence |
| `learning_bundle_signing_private_key_unavailable` | A retained protected key matching the embedded production public key signs a read-only bundle; the verifier returns its exact SHA-256 and pinned key ID | `learning_bundle_digest`, key ID, and nested signatures |
| `production_release_evidence_unavailable` | All component, artifact, SBOM, Sigstore, provenance, canary, and risk evidence is assembled as schema 9 and signed by the deployment key, bound to the candidate manifest hash | Signed schema 9 production evidence |

Do not edit `production_ready`, `release_published`, or the blocker list by
hand. The promotion tool recomputes those fields and refuses a mismatched or
partially signed input. Test keys, development digests, and a prerelease do not
clear any blocker.

Before starting this promotion, publish an `agent-remote-server` release that
contains the schema-9 Bridge admission fix. The promoted root manifest pins
Server `0.2.14` at the reviewed commit; keep candidate and evidence bound to
that exact release (or a subsequently reviewed replacement). Do not substitute
an older Server release as the production Bridge control plane.

## Required order

1. In `agent-remote-ego-browser`, finish the reviewed source, run its complete
   quality gate, create the clean commit and exact `vVERSION` tag, push both,
   and let the tag-bound release workflow publish all artifacts. The GitHub
   Release must be stable, not draft or prerelease.
2. Configure the protected `production-community-release` environment with the
   persistent P12, signing identity, and lowercase certificate SHA-256. Restore
   the retained Site Learning private key that matches the Bridge verifier's
   embedded public key. Build a signed, read-only bundle and record its verifier
   digest and key ID.
3. Download the exact Bridge release manifest, macOS archive, checksums,
   signing evidence, Sigstore bundles, and provenance. Check out the same
   Bridge tag and verify its clean HEAD, artifact inventory, nested signatures,
   certificate pin, stable GitHub Release, and learning digest.
4. Prepare a canonical root candidate. This phase does not modify
   `release-manifest.json` and does not consume production evidence:

   ```sh
   python3 scripts/promote-ego-browser-release.py \
     --manifest release-manifest.json \
     --bridge-repository ../agent-remote-ego-browser \
     --bridge-release-manifest /secure/release/agent-remote-ego-browser-VERSION.release-manifest.json \
     --bridge-release-archive /secure/release/agent-remote-ego-browser-macos-universal-VERSION.tar.gz \
     --bridge-artifact-dir /secure/release \
     --bridge-signing-evidence /secure/release/agent-remote-ego-browser-macos-universal-VERSION.community-signing.json \
     --bridge-archive-sigstore /secure/release/agent-remote-ego-browser-macos-universal-VERSION.tar.gz.sigstore.json \
     --bridge-manifest-sigstore /secure/release/agent-remote-ego-browser-VERSION.release-manifest.json.sigstore.json \
     --bridge-provenance /secure/release/bridge-provenance.json \
     --learning-bundle /secure/release/learning-bundle \
     --learning-bundle-verifier ../agent-remote-ego-browser/scripts/verify-learning-bundle.sh \
     --certificate-sha256 CERTIFICATE_SHA256 \
     --learning-bundle-key-id KEY_ID \
     --commit BRIDGE_COMMIT \
     --version VERSION \
     --prepare-only \
     --candidate-output /secure/release/root-candidate.json
   ```

   The command prints the candidate SHA-256. Preserve the candidate bytes and
   that hash as the input to the evidence signer.
5. Produce candidate-bound schema 9 evidence in the protected release
   environment. The checked-in `community-device-control-release-evidence.yml`
   is deliberately tag-bound and reads the committed `release-manifest.json`;
   it cannot consume this uncommitted candidate while the root manifest is
   blocked. Do not temporarily commit the candidate or edit the blocked
   manifest to make the workflow pass. Instead, the release owner must:

   - copy the candidate to an owner-only, immutable path and verify its SHA-256;
   - check out the reviewed root source and every pinned component tag, then
     run the same artifact, checksum, Sigstore, provenance, vulnerability, and
     canary checks used by the community workflow;
   - invoke `scripts/assemble-community-device-control-release-evidence.py`
     with `--release-manifest /secure/release/root-candidate.json` (and the
     candidate's distribution/server versions), supplying all of the workflow's
     ordinary artifact and gate inputs;
   - sign the resulting `release-evidence-draft.json` with the protected
     deployment key through the Server
     `create_device_control_release_evidence.py` tool, and verify the signature
     with the pinned public key; and
   - retain the signed output and audit log without replacing an existing file.

   The signed record must contain the candidate manifest SHA-256 and all six
   `ego_browser_*` digest fields. The `release_manifest_sha256` value must be
   recomputed from the exact candidate bytes, not from the currently blocked
   root manifest. This is a protected manual/approval step today; the normal
   tag-bound workflow can be used only after the promoted manifest has been
   committed and tagged.
6. Apply the candidate atomically only after schema 9 evidence is available:

   ```sh
   python3 scripts/promote-ego-browser-release.py \
     --manifest release-manifest.json \
     --bridge-repository ../agent-remote-ego-browser \
     --bridge-release-manifest /secure/release/agent-remote-ego-browser-VERSION.release-manifest.json \
     --bridge-release-archive /secure/release/agent-remote-ego-browser-macos-universal-VERSION.tar.gz \
     --bridge-artifact-dir /secure/release \
     --bridge-signing-evidence /secure/release/agent-remote-ego-browser-macos-universal-VERSION.community-signing.json \
     --bridge-archive-sigstore /secure/release/agent-remote-ego-browser-macos-universal-VERSION.tar.gz.sigstore.json \
     --bridge-manifest-sigstore /secure/release/agent-remote-ego-browser-VERSION.release-manifest.json.sigstore.json \
     --bridge-provenance /secure/release/bridge-provenance.json \
     --learning-bundle /secure/release/learning-bundle \
     --learning-bundle-verifier ../agent-remote-ego-browser/scripts/verify-learning-bundle.sh \
     --certificate-sha256 CERTIFICATE_SHA256 \
     --learning-bundle-key-id KEY_ID \
     --commit BRIDGE_COMMIT \
     --version VERSION \
     --candidate-manifest /secure/release/root-candidate.json \
     --production-evidence /secure/release/device-control-release-evidence-VERSION.json \
     --production-evidence-public-key "$(cat deploy/compose/community-release-public-key.txt)"
   ```

   The tool re-verifies every input, checks the candidate hash and signature,
   and replaces the root manifest with an `fsync`-backed atomic write. Any
   failure leaves the original manifest bytes unchanged.
7. Review the resulting manifest and commit it on the root `main` branch. Run
   the root `prepare-release.yml` with a new distribution version; changing that
   version also changes the root manifest hash, so the tag-bound community
   workflow must generate a fresh schema 9 evidence file for the new tag. Do
   not deploy the pre-tag candidate evidence and do not reuse a distribution tag
   that predates the promotion.
8. Deploy that exact bundle, complete the artifact-bound Admin and real logged-in
   ego lite canaries, and only then set
   `EGO_BROWSER_BRIDGE_ENABLED=true`. Runtime configuration cannot override a
   false or missing release manifest.

The generated deployment `.env.example` must carry the candidate's
`EGO_BROWSER_EXPECTED_DISTRIBUTION_VERSION`,
`EGO_BROWSER_EXPECTED_ROOT_MANIFEST_SHA256`,
`EGO_BROWSER_EXPECTED_LEARNING_BUNDLE_SHA256`, and the six
`EGO_BROWSER_EXPECTED_BRIDGE_*_SHA256` values. These are independent Server
deployment pins; copy them only from the final tag-bound schema 9 evidence and
regenerate them whenever the root manifest or any Bridge artifact changes.

The first candidate phase can be repeated with a new output path. Never replace
an existing candidate or evidence file in place. If a Bridge commit, tag,
certificate, learning digest, artifact, or evidence hash changes, discard the
candidate and start at step 3.

## Status checks

```sh
jq '.components["agent-remote-ego-browser"] |
  {commit, release_published, production_ready, readiness_blockers,
   signer_certificate_sha256, learning_bundle_digest,
   nested_signatures_verified}' release-manifest.json
python3 scripts/check-device-control-release-readiness.py \
  --manifest release-manifest.json
```

The original blocked state was `release_published=false`,
`production_ready=false`, with the four blockers listed above. The current
promoted root component is `release_published=true`, `production_ready=true`,
and has `readiness_blockers=[]`. This does not switch the capability on: the
stable root `0.2.25` release contains the tag-bound evidence, but deployment of
its exact certified bundle and the final logged-in canary are still required.
