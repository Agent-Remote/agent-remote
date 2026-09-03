#!/usr/bin/env python3
"""Run the real Server -> Node -> Rust -> Swift device-control data path."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

USER_ID = UUID("10000000-0000-4000-8000-000000000001")
DEVICE_ID = UUID("10000000-0000-4000-8000-000000000002")
TOOL_SESSION_ID = UUID("10000000-0000-4000-8000-000000000003")
NODE_ID = UUID("10000000-0000-4000-8000-000000000005")
TOOL_ACCOUNT_ID = UUID("10000000-0000-4000-8000-000000000006")
WORKSPACE_ID = UUID("10000000-0000-4000-8000-000000000007")
DEVICE_TOKEN_ID = UUID("10000000-0000-4000-8000-000000000008")
DEVICE_TOKEN = "device_e2e_0123456789abcdefghijklmnopqrstuvwxyz"
NODE_TOKEN = "node_e2e_0123456789abcdefghijklmnopqrstuvwxyz"
SECRET_KEY = "local-device-control-system-e2e-secret"
FULL_TRUST_CAPABILITIES = (
    "adaptive_settle_v2",
    "application_launch_v1",
    "ax_state_v2",
    "clipboard_payload_v2",
    "global_clipboard_v1",
    "observation_mode_v2",
    "session_full_trust_v1",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-repo", type=Path, required=True)
    parser.add_argument("--node-repo", type=Path, required=True)
    parser.add_argument("--device-repo", type=Path, required=True)
    parser.add_argument("--serve", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--port", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--state-root", type=Path, help=argparse.SUPPRESS)
    return parser.parse_args()


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def write_private_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, separators=(",", ":")), encoding="utf-8")
    path.chmod(0o600)


def normalize_api_timestamp(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"device-session response is missing {field}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise RuntimeError(f"device-session response contains an invalid {field}") from error
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")


async def seed_server(app: object) -> None:
    from agent_remote_server.db import Base
    from agent_remote_server.models import (
        AuthToken,
        Node,
        Session,
        ToolAccount,
        User,
        UserDevice,
        Workspace,
    )
    from agent_remote_server.security import hash_token

    now = datetime.now(UTC)
    async with app.state.database_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with app.state.session_factory() as session:
        session.add_all(
            [
                User(
                    id=USER_ID,
                    username="device-e2e",
                    display_name="Device E2E",
                    role="user",
                    status="active",
                    password_hash="not-used-by-system-e2e",
                    totp_enabled=False,
                ),
                Node(
                    id=NODE_ID,
                    name="device-e2e-node",
                    status="healthy",
                    region_code="local",
                    tags=[],
                    weight=1,
                    supported_tool_types=["claude"],
                    allowed_runtime_backends=["native"],
                    default_runtime_backend="native",
                    runtime_policy={},
                    runtime_capabilities={
                        "device_control": {
                            "supported": True,
                            "protocol_versions": [1],
                            "platforms": ["macos"],
                            "backends": ["native"],
                            "capabilities": list(FULL_TRUST_CAPABILITIES),
                        }
                    },
                    node_token_hash=hash_token(SECRET_KEY, NODE_TOKEN),
                    last_heartbeat_at=now,
                    version="system-e2e",
                ),
            ]
        )
        await session.flush()
        session.add(
            UserDevice(
                id=DEVICE_ID,
                user_id=USER_ID,
                name="device-e2e-mac",
                platform="macos",
                cli_version="system-e2e",
                status="active",
                last_seen_at=now,
            )
        )
        await session.flush()
        session.add_all(
            [
                AuthToken(
                    id=DEVICE_TOKEN_ID,
                    user_id=USER_ID,
                    user_device_id=DEVICE_ID,
                    token_hash=hash_token(SECRET_KEY, DEVICE_TOKEN),
                    token_type="device",
                    status="active",
                    expires_at=now + timedelta(minutes=10),
                ),
                ToolAccount(
                    id=TOOL_ACCOUNT_ID,
                    user_id=USER_ID,
                    tool_type="claude",
                    display_name="Device E2E",
                    status="active",
                    region_code="local",
                    timezone="UTC",
                    locale="en-US",
                    preferred_node_tags=[],
                    affinity_node_id=NODE_ID,
                    runtime_backend="native",
                ),
                Workspace(
                    id=WORKSPACE_ID,
                    user_id=USER_ID,
                    device_id=DEVICE_ID,
                    project_key="sha256:device-system-e2e",
                    local_start_path="/tmp/device-system-e2e",
                    display_name="Device E2E",
                    remote_path="/tmp/device-system-e2e",
                    sync_git=False,
                    git_sync_policy={},
                ),
            ]
        )
        await session.flush()
        session.add(
            Session(
                id=TOOL_SESSION_ID,
                tool_type="claude",
                user_id=USER_ID,
                tool_account_id=TOOL_ACCOUNT_ID,
                workspace_id=WORKSPACE_ID,
                node_id=NODE_ID,
                project_key="sha256:device-system-e2e",
                status="running",
                tmux_session_name="device-system-e2e",
                runtime_backend="native",
                runtime_resource_id="device-system-e2e",
                device_control_protocol_version=1,
            )
        )
        await session.flush()
        await session.commit()


def serve(args: argparse.Namespace) -> None:
    import uvicorn

    from agent_remote_server.config import Settings
    from agent_remote_server.device_relay_store import InMemoryDeviceRelayStore
    from agent_remote_server.main import create_app

    if args.port is None or args.state_root is None:
        raise SystemExit("server mode requires port and state root")
    settings = Settings(
        secret_key=SECRET_KEY,
        log_level="CRITICAL",
        database_url=f"sqlite+aiosqlite:///{args.state_root / 'server.sqlite3'}",
        device_control_enabled=True,
        device_session_authorization_mode="session_full_trust",
        device_relay_pair_timeout_seconds=30,
    )
    app = create_app(settings)
    app.state.device_relay_store = InMemoryDeviceRelayStore()
    asyncio.run(seed_server(app))
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="critical", access_log=False)


def wait_for_server(url: str, process: subprocess.Popen[str]) -> None:
    for _ in range(200):
        if process.poll() is not None:
            raise RuntimeError("server exited before becoming ready")
        try:
            with urllib.request.urlopen(url + "/api/v1/version", timeout=0.5) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError("server did not become ready")


def post_json(url: str, token: str, body: dict[str, object]) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body, separators=(",", ":")).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        error_code = "unknown"
        try:
            error_payload = json.load(error)
            if isinstance(error_payload, dict):
                error_data = error_payload.get("error")
                if isinstance(error_data, dict) and isinstance(error_data.get("code"), str):
                    error_code = error_data["code"]
        except (OSError, ValueError):
            pass
        raise RuntimeError(f"device-session API failed with HTTP {error.code}: {error_code}") from error
    if not isinstance(payload, dict):
        raise RuntimeError("device-session API returned a non-object response")
    return payload


def claim_full_trust_session(server_url: str) -> dict[str, object]:
    claimed_response = post_json(
        server_url + "/api/v1/device-sessions/claim",
        DEVICE_TOKEN,
        {
            "tool_session_id": str(TOOL_SESSION_ID),
            "device_capabilities": ["session_full_trust_v1"],
        },
    )
    claimed = claimed_response.get("data")
    if not isinstance(claimed, dict):
        raise RuntimeError("claim response is missing device-session data")
    if (
        claimed.get("status") != "pending_device"
        or claimed.get("authorization_mode") != "session_full_trust"
        or claimed.get("authorization_policy_version") != 1
        or claimed.get("authorized_at") is None
    ):
        raise RuntimeError("claim response did not establish pending full-trust authorization")
    device_session_id = claimed.get("id")
    generation = claimed.get("generation")
    expires_at = normalize_api_timestamp(claimed.get("expires_at"), "expiry")
    try:
        UUID(str(device_session_id))
    except (TypeError, ValueError) as error:
        raise RuntimeError("claim response contains an invalid device-session ID") from error
    if not isinstance(generation, int) or isinstance(generation, bool) or generation < 1:
        raise RuntimeError("claim response contains an invalid generation")
    connected_response = post_json(
        server_url + f"/api/v1/device-sessions/{device_session_id}/device-connected",
        DEVICE_TOKEN,
        {"generation": generation},
    )
    connected = connected_response.get("data")
    if not isinstance(connected, dict):
        raise RuntimeError("device-connected response is missing device-session data")
    expected_fields = {
        "id": device_session_id,
        "status": "active",
        "authorization_mode": "session_full_trust",
        "authorization_policy_version": 1,
        "generation": generation,
    }
    for field, expected in expected_fields.items():
        if connected.get(field) != expected:
            raise RuntimeError(f"device-connected response has an unexpected {field}")
    connected_expiry = normalize_api_timestamp(connected.get("expires_at"), "expiry")
    if connected_expiry != expires_at:
        raise RuntimeError("device-connected response changed the session expiry")
    lease_until = normalize_api_timestamp(connected.get("lease_until"), "active lease")
    connected["expires_at"] = expires_at
    connected["lease_until"] = lease_until
    return connected


def wait_for_path(path: Path, process: subprocess.Popen[str]) -> None:
    for _ in range(300):
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(f"bridge exited before becoming ready: {output}")
        if path.exists():
            return
        time.sleep(0.05)
    raise RuntimeError("bridge socket did not become ready")


def terminate(process: subprocess.Popen[str] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.send_signal(signal.SIGTERM)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def run(args: argparse.Namespace) -> None:
    for repo in (args.server_repo, args.node_repo, args.device_repo):
        if not repo.is_dir():
            raise SystemExit(f"repository is missing: {repo}")
    with tempfile.TemporaryDirectory(prefix="ard-e2e-", dir="/tmp") as raw_root:
        root = Path(raw_root)
        root.chmod(0o700)
        bridge_directory = root / "bridge"
        bridge_directory.mkdir(mode=0o700)
        bridge_socket = bridge_directory / "bridge.sock"
        node_binary = root / "node-bridge"
        subprocess.run(
            ["go", "build", "-o", str(node_binary), "./tests/device_control_bridge_e2e.go"],
            cwd=args.node_repo,
            check=True,
        )
        subprocess.run(
            ["cargo", "build", "--quiet", "--manifest-path", "proxy/Cargo.toml", "--example", "system_e2e_proxy"],
            cwd=args.device_repo,
            check=True,
        )
        subprocess.run(
            ["swift", "build", "--package-path", str(args.device_repo), "--product", "agent-remote-device-system-e2e-peer"],
            check=True,
        )
        swift_bin_path = subprocess.run(
            ["swift", "build", "--package-path", str(args.device_repo), "--show-bin-path"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        swift_peer = Path(swift_bin_path) / "agent-remote-device-system-e2e-peer"
        rust_peer = args.device_repo / "target/debug/examples/system_e2e_proxy"
        port = free_port()
        server_url = f"http://127.0.0.1:{port}"
        node_config = root / "node.json"
        managed_context = root / "managed-context.json"
        swift_config = root / "swift.json"
        server_process: subprocess.Popen[str] | None = None
        node_process: subprocess.Popen[str] | None = None
        swift_process: subprocess.Popen[str] | None = None
        try:
            server_process = subprocess.Popen(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--server-repo",
                    str(args.server_repo),
                    "--node-repo",
                    str(args.node_repo),
                    "--device-repo",
                    str(args.device_repo),
                    "--serve",
                    "--port",
                    str(port),
                    "--state-root",
                    str(root),
                ],
                cwd=args.server_repo,
                text=True,
            )
            wait_for_server(server_url, server_process)
            device_session = claim_full_trust_session(server_url)
            device_session_id = str(device_session["id"])
            generation = int(device_session["generation"])
            activation = {
                "protocol_version": 1,
                "user_id": str(USER_ID),
                "device_id": str(DEVICE_ID),
                "tool_session_id": str(TOOL_SESSION_ID),
                "device_session_id": device_session_id,
                "node_id": str(NODE_ID),
                "platform": "macos",
                "generation": generation,
                "authorization_mode": "session_full_trust",
                "authorization_policy_version": 1,
                "expires_at": device_session["expires_at"],
                "runtime_backend": "native",
                "runtime_resource_id": "device-system-e2e",
            }
            write_private_json(
                node_config,
                {
                    "server_url": server_url,
                    "node_token": NODE_TOKEN,
                    "node_id": str(NODE_ID),
                    "bridge_socket": str(bridge_socket),
                    "activation": activation,
                },
            )
            write_private_json(
                managed_context,
                {
                    "user_id": str(USER_ID),
                    "device_id": str(DEVICE_ID),
                    "tool_session_id": str(TOOL_SESSION_ID),
                    "device_session_id": device_session_id,
                    "node_id": str(NODE_ID),
                    "platform": "macos",
                    "generation": generation,
                    "next_sequence": 1,
                    "current_screenshot_generation": 0,
                    "current_state_generation": 0,
                    "capabilities": list(FULL_TRUST_CAPABILITIES),
                    "authorization_mode": "session_full_trust",
                    "authorization_policy_version": 1,
                    "lease_until": device_session["lease_until"],
                },
            )
            write_private_json(
                swift_config,
                {
                    "server_url": server_url,
                    "device_token": DEVICE_TOKEN,
                    "user_id": str(USER_ID),
                    "device_id": str(DEVICE_ID),
                    "tool_session_id": str(TOOL_SESSION_ID),
                    "device_session_id": device_session_id,
                    "node_id": str(NODE_ID),
                    "generation": generation,
                },
            )
            node_environment = os.environ.copy()
            node_environment["AGENT_REMOTE_DEVICE_E2E_CONFIG"] = str(node_config)
            node_process = subprocess.Popen(
                [str(node_binary)],
                cwd=args.node_repo,
                env=node_environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            wait_for_path(bridge_socket, node_process)
            swift_environment = os.environ.copy()
            swift_environment["AGENT_REMOTE_DEVICE_E2E_CONFIG"] = str(swift_config)
            swift_process = subprocess.Popen(
                [str(swift_peer)],
                cwd=args.device_repo,
                env=swift_environment,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            rust = subprocess.run(
                [
                    str(rust_peer),
                    "--managed-context",
                    str(managed_context),
                    "--bridge-socket",
                    str(bridge_socket),
                ],
                cwd=args.device_repo,
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if rust.returncode != 0:
                raise RuntimeError(f"Rust peer failed:\n{rust.stdout}{rust.stderr}")
            swift_output, _ = swift_process.communicate(timeout=30)
            if swift_process.returncode != 0:
                raise RuntimeError(f"Swift peer failed:\n{swift_output}")
            print(rust.stdout.strip())
            print(swift_output.strip())
        except Exception as error:
            terminate(swift_process)
            terminate(node_process)
            swift_output = (
                swift_process.stdout.read() if swift_process is not None and swift_process.stdout else ""
            )
            node_output = (
                node_process.stdout.read() if node_process is not None and node_process.stdout else ""
            )
            raise RuntimeError(
                f"{error}\nSwift peer output:\n{swift_output}\nNode bridge output:\n{node_output}"
            ) from error
        finally:
            terminate(swift_process)
            terminate(node_process)
            terminate(server_process)


def main() -> None:
    args = parse_args()
    sys.path.insert(0, str(args.server_repo / "src"))
    if args.serve:
        serve(args)
    else:
        run(args)


if __name__ == "__main__":
    main()
