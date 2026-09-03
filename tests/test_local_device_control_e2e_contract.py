#!/usr/bin/env python3
"""Keep the synthetic cross-repository E2E aligned with full-trust claims."""

from pathlib import Path


source = Path("tests/local_device_control_e2e.py").read_text(encoding="utf-8")

required_fragments = (
    'device_session_authorization_mode="session_full_trust"',
    '"/api/v1/device-sessions/claim"',
    '"device_capabilities": ["session_full_trust_v1"]',
    'claimed.get("status") != "pending_device"',
    '/device-connected",',
    '"status": "active",',
    'if connected.get(field) != expected:',
    '"authorization_mode": "session_full_trust"',
    '"authorization_policy_version": 1',
    '"application_launch_v1"',
    '"global_clipboard_v1"',
    '"session_full_trust_v1"',
    '"capabilities": list(FULL_TRUST_CAPABILITIES)',
)
missing = [fragment for fragment in required_fragments if fragment not in source]
if missing:
    raise SystemExit(f"full-trust E2E harness is missing: {', '.join(missing)}")

if source.count('"capabilities": list(FULL_TRUST_CAPABILITIES)') != 2:
    raise SystemExit("Server and managed context must use the same full-trust capability set")

for forbidden in ("DeviceSession(", "DEVICE_SESSION_ID ="):
    if forbidden in source:
        raise SystemExit(f"full-trust E2E must not seed an active device session: {forbidden}")

device_peer = Path("../agent-remote-device/macos/SystemE2EPeer/main.swift")
rust_peer = Path("../agent-remote-device/proxy/examples/system_e2e_proxy.rs")
if device_peer.exists() and rust_peer.exists():
    device_source = device_peer.read_text(encoding="utf-8")
    rust_source = rust_peer.read_text(encoding="utf-8")
    for fragment in ("case .readClipboard:", 'case .launchApplication("TextEdit"):',
                     "case .observe(application: nil):"):
        if fragment not in device_source:
            raise SystemExit(f"Swift full-trust E2E peer is missing: {fragment}")
    for fragment in ("ActionV2::ReadClipboard", "ActionV2::LaunchApplication",
                     "ActionV2::Observe"):
        if fragment not in rust_source:
            raise SystemExit(f"Rust full-trust E2E peer is missing: {fragment}")
