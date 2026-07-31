#!/usr/bin/env python3
"""Cross-repository session port-forwarding data-path smoke test."""

from __future__ import annotations

import argparse
import array
import base64
import hashlib
import http.client
import json
import os
import signal
import socket
import socketserver
import sqlite3
import struct
import subprocess
import tempfile
import threading
import time
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


FORWARD_ID = "11111111-1111-4111-8111-111111111111"
SESSION_ID = "22222222-2222-4222-8222-222222222222"
DEVICE_ID = "33333333-3333-4333-8333-333333333333"
SSH_KEY_ID = "44444444-4444-4444-8444-444444444444"
NODE_ID = "55555555-5555-4555-8555-555555555555"
USER_ID = "66666666-6666-4666-8666-666666666666"


def timestamp(seconds: int = 0) -> str:
    return (datetime.now(UTC) + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")


class State:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.requests: list[tuple[str, str, dict[str, Any]]] = []
        self.remote_port = 0
        self.local_port = 0
        self.token_generation = 0

    def record(self, method: str, path: str, body: dict[str, Any]) -> None:
        with self.lock:
            self.requests.append((method, path, body))

    def next_token(self) -> str:
        with self.lock:
            self.token_generation += 1
            return f"e2e-connect-token-{self.token_generation:04d}-0123456789abcdef"


def forward_data(state: State, status: str) -> dict[str, Any]:
    return {
        "id": FORWARD_ID,
        "user_id": USER_ID,
        "device_id": DEVICE_ID,
        "session_id": SESSION_ID,
        "node_id": NODE_ID,
        "remote_port": state.remote_port,
        "requested_local_port": state.local_port,
        "client_instance_id": "ci_e2e",
        "status": status,
        "bytes_up": 0,
        "bytes_down": 0,
        "connection_count": 0,
        "last_connected_at": None,
        "lease_expires_at": None,
        "expires_at": timestamp(3600),
        "stopped_at": timestamp() if status == "stopped" else None,
        "stop_reason": "client_stopped" if status == "stopped" else None,
        "created_at": timestamp(),
        "updated_at": timestamp(),
    }


def session_data() -> dict[str, Any]:
    return {
        "id": SESSION_ID,
        "tool_type": "claude",
        "user_id": USER_ID,
        "tool_account_id": "77777777-7777-4777-8777-777777777777",
        "workspace_id": "88888888-8888-4888-8888-888888888888",
        "workspace_local_path": None,
        "workspace_remote_path": "/workspace",
        "node_id": NODE_ID,
        "project_key": "e2e-project",
        "status": "running",
        "tmux_session_name": "e2e",
        "container_id": None,
        "runtime_backend": "native",
        "runtime_resource_id": "e2e-runtime",
        "replaces_session_id": None,
        "create_task_id": None,
        "stop_task_id": None,
        "created_at": timestamp(),
        "updated_at": timestamp(),
    }


def lease_data(state: State) -> dict[str, Any]:
    return {
        "forward_id": FORWARD_ID,
        "session_id": SESSION_ID,
        "runtime_backend": "native",
        "runtime_resource_id": "e2e-runtime",
        "remote_port": state.remote_port,
        "generation": 1,
        "lease_expires_at": timestamp(60),
        "max_streams": 128,
        "bytes_per_second": 0,
        "control_plane_grace_seconds": 10,
    }


class ControlHandler(BaseHTTPRequestHandler):
    state: State

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def _body(self) -> dict[str, Any]:
        length = int(self.headers.get("content-length", "0"))
        if length == 0:
            return {}
        value = json.loads(self.rfile.read(length))
        if not isinstance(value, dict):
            raise ValueError("request body must be an object")
        return value

    def _send(self, status: int, value: dict[str, Any] | None = None) -> None:
        payload = b"" if value is None else json.dumps(value, separators=(",", ":")).encode()
        self.send_response(status)
        if payload:
            self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.send_header("connection", "close")
        self.end_headers()
        if payload:
            self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        body: dict[str, Any] = {}
        self.state.record("GET", self.path, body)
        if self.path == "/api/v1/sessions":
            self._send(200, {"data": {"items": [session_data()]}})
            return
        if self.path == "/api/v1/port-forwards":
            self._send(200, {"data": {"items": [forward_data(self.state, "active")]}})
            return
        self._send(404, {"error": {"code": "NOT_FOUND", "message": "not found"}})

    def do_POST(self) -> None:  # noqa: N802
        body = self._body()
        self.state.record("POST", self.path, body)
        if self.path == f"/api/v1/sessions/{SESSION_ID}/port-forwards":
            self.state.remote_port = int(body["remote_port"])
            self.state.local_port = int(body["local_port"])
            created = forward_data(self.state, "pending")
            created.update(
                {
                    "node_wireguard_ip": "127.0.0.1",
                    "ssh_user": "agent-remote",
                    "ssh_port": 22,
                    "connection": {
                        "token": self.state.next_token(),
                        "expires_at": timestamp(60),
                    },
                }
            )
            self._send(200, {"data": created})
            return
        if self.path == f"/api/v1/port-forwards/{FORWARD_ID}/connections":
            self._send(
                200,
                {
                    "data": {
                        "token": self.state.next_token(),
                        "expires_at": timestamp(60),
                    }
                },
            )
            return
        if self.path == "/api/v1/node-api/port-forwards/redeem":
            if body.get("forward_id") != FORWARD_ID or body.get("device_id") != DEVICE_ID:
                self._send(403, {"error": {"code": "AUTH_INVALID", "message": "invalid"}})
                return
            token = str(body.get("connect_token", ""))
            if len(token) < 32 or body.get("ssh_key_id") != SSH_KEY_ID:
                self._send(403, {"error": {"code": "AUTH_INVALID", "message": "invalid"}})
                return
            self._send(200, {"data": lease_data(self.state), "request_id": "e2e-redeem"})
            return
        if self.path == f"/api/v1/node-api/port-forwards/{FORWARD_ID}/renew":
            self._send(200, {"data": lease_data(self.state), "request_id": "e2e-renew"})
            return
        if self.path == f"/api/v1/node-api/port-forwards/{FORWARD_ID}/release":
            self._send(204)
            return
        self._send(404, {"error": {"code": "NOT_FOUND", "message": "not found"}})

    def do_DELETE(self) -> None:  # noqa: N802
        body: dict[str, Any] = {}
        self.state.record("DELETE", self.path, body)
        if self.path == f"/api/v1/port-forwards/{FORWARD_ID}":
            self._send(200, {"data": forward_data(self.state, "stopped")})
            return
        self._send(404, {"error": {"code": "NOT_FOUND", "message": "not found"}})


class DevHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    concurrency_barrier = threading.Barrier(100)

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def do_GET(self) -> None:  # noqa: N802
        if self.headers.get("upgrade", "").lower() == "websocket":
            self._websocket()
            return
        if self.path == "/asset.js":
            self._payload(b"window.__agentRemoteE2E = true;", "application/javascript")
            return
        if self.path == "/events":
            payload = b"event: ready\ndata: first\n\nevent: update\ndata: second\n\n"
            self._payload(payload, "text/event-stream")
            return
        if self.path.startswith("/concurrent/"):
            payload = self.path.encode()
            self.concurrency_barrier.wait(timeout=30)
            self.send_response(200)
            self.send_header("content-type", "text/plain")
            self.send_header("content-length", str(len(payload)))
            self.send_header("connection", "close")
            self.end_headers()
            self.wfile.write(payload)
            return
        self._payload(b"agent-remote-e2e", "text/plain")

    def _payload(self, payload: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(payload)))
        self.send_header("connection", "close")
        self.end_headers()
        self.wfile.write(payload)

    def _websocket(self) -> None:
        key = self.headers["sec-websocket-key"]
        accept = base64.b64encode(
            hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()
        ).decode()
        self.send_response(101)
        self.send_header("upgrade", "websocket")
        self.send_header("connection", "Upgrade")
        self.send_header("sec-websocket-accept", accept)
        self.end_headers()
        first, second = self.rfile.read(2)
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", self.rfile.read(2))[0]
        mask = self.rfile.read(4)
        payload = bytes(value ^ mask[index % 4] for index, value in enumerate(self.rfile.read(length)))
        self.wfile.write(bytes([first & 0x8F, len(payload)]) + payload)
        self.wfile.flush()


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 128


class ReusableUnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    request_queue_size = 128


class RuntimeHelperHandler(socketserver.BaseRequestHandler):
    target_port: int

    def handle(self) -> None:
        stream = self.request.makefile("rb")
        request = json.loads(stream.readline())
        payload = request.get("payload", {})
        if request.get("operation") != "dial_session_loopback" or payload.get("runtime_backend") != "native":
            raise RuntimeError("unexpected Runtime Helper request")
        if int(payload.get("port", 0)) != self.target_port:
            raise RuntimeError("Runtime Helper target port changed")
        upstream = socket.create_connection(("127.0.0.1", self.target_port), timeout=3)
        try:
            response = b'{"version":1,"ok":true,"result":{"connected":true}}\n'
            rights = array.array("i", [upstream.fileno()])
            self.request.sendmsg([response], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, rights)])
        finally:
            upstream.close()


def free_port() -> int:
    with socket.socket() as value:
        value.bind(("127.0.0.1", 0))
        return int(value.getsockname()[1])


def prepare_cli_home(home: Path, server_url: str) -> None:
    home.mkdir(parents=True)
    (home / "config.toml").write_text(
        f'server_url = "{server_url}"\nactive_device_id = "{DEVICE_ID}"\n', encoding="utf-8"
    )
    secrets = home / "secrets"
    secrets.mkdir()
    key = f"device-token:{server_url}:{DEVICE_ID}"
    sanitized = "".join(value if value.isalnum() or value in "-_." else "_" for value in key)
    secret = secrets / f"{sanitized}.secret"
    secret.write_text("e2e-device-token", encoding="utf-8")
    secret.chmod(0o600)
    database = sqlite3.connect(home / "state.sqlite3")
    try:
        database.executescript(
            """
            CREATE TABLE kv (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            CREATE TABLE devices (
              id TEXT PRIMARY KEY, server_url TEXT NOT NULL, name TEXT NOT NULL,
              platform TEXT NOT NULL, status TEXT NOT NULL, ssh_key_id TEXT,
              wireguard_peer_id TEXT, created_at TEXT, last_seen_at TEXT,
              updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        database.execute(
            "INSERT INTO kv (key, value) VALUES (?, ?)",
            (f"device-token-refresh-at:{server_url}:{DEVICE_ID}", str(2**63 - 1)),
        )
        database.execute(
            "INSERT INTO devices (id, server_url, name, platform, status, ssh_key_id) VALUES (?, ?, ?, ?, ?, ?)",
            (DEVICE_ID, server_url, "e2e-device", "linux", "active", SSH_KEY_ID),
        )
        database.commit()
    finally:
        database.close()


def write_gateway_files(
    root: Path, node_attach: Path, server_url: str, runtime_socket: Path
) -> tuple[Path, Path, Path]:
    config = root / "node-config.json"
    config.write_text(
        json.dumps(
            {
                "server_url": server_url,
                "node_id": NODE_ID,
                "node_token": "e2e-node-token",
                "allowed_runtime_backends": ["native"],
                "runtime_socket_path": str(runtime_socket),
            }
        ),
        encoding="utf-8",
    )
    count = root / "ssh-count"
    disconnect = root / "disconnect-first-ssh"
    fake_bin = root / "bin"
    fake_bin.mkdir()
    ssh = fake_bin / "ssh"
    ssh.write_text(
        f"""#!/usr/bin/env python3
import os
import subprocess
import sys
import time

count_path = {str(count)!r}
disconnect_path = {str(disconnect)!r}
try:
    count = int(open(count_path, encoding="utf-8").read()) + 1
except (FileNotFoundError, ValueError):
    count = 1
with open(count_path, "w", encoding="utf-8") as value:
    value.write(str(count))
environment = os.environ.copy()
environment["SSH_ORIGINAL_COMMAND"] = {f"agent-remote-tunnel --forward {FORWARD_ID} --protocol 1"!r}
command = [
    {str(node_attach)!r}, "--config", {str(config)!r}, "--device", {DEVICE_ID!r},
    "--ssh-key", {SSH_KEY_ID!r},
]
if count == 1:
    child = subprocess.Popen(
        command, stdin=sys.stdin.buffer, stdout=sys.stdout.buffer, env=environment
    )
    deadline = time.monotonic() + 30
    while (
        child.poll() is None
        and not os.path.exists(disconnect_path)
        and time.monotonic() < deadline
    ):
        time.sleep(0.05)
    if child.poll() is None:
        child.kill()
    child.wait()
    raise SystemExit(1)
os.execve(command[0], command, environment)
""",
        encoding="utf-8",
    )
    ssh.chmod(0o700)
    return fake_bin, count, disconnect


def wait_for(predicate: Any, message: str, timeout: float = 15) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.05)
    raise TimeoutError(message)


def http_get(port: int, path: str, timeout: float = 3) -> bytes:
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        payload = response.read()
        if response.status != 200:
            raise AssertionError(f"GET {path} returned {response.status}: {payload!r}")
        return payload
    finally:
        connection.close()


def read_raw_http_response(connection: socket.socket) -> bytes:
    response = bytearray()
    while payload := connection.recv(4096):
        response.extend(payload)
    headers, separator, body = bytes(response).partition(b"\r\n\r\n")
    if not separator or not headers.startswith(b"HTTP/1.1 200"):
        raise AssertionError(f"invalid concurrent HTTP response: {bytes(response)!r}")
    return body


def concurrent_http_gets(port: int, count: int = 100) -> None:
    paths = [f"/concurrent/{index}" for index in range(count)]
    connections: list[socket.socket] = []
    try:
        for path in paths:
            connection = socket.create_connection(("127.0.0.1", port), timeout=60)
            connection.sendall(
                (
                    f"GET {path} HTTP/1.1\r\n"
                    f"Host: 127.0.0.1:{port}\r\n"
                    "Connection: close\r\n\r\n"
                ).encode()
            )
            connection.shutdown(socket.SHUT_WR)
            connections.append(connection)
        payloads = [read_raw_http_response(connection) for connection in connections]
    finally:
        for connection in connections:
            connection.close()
    expected = [path.encode() for path in paths]
    if payloads != expected:
        raise AssertionError("concurrent HTTP/2 streams crossed response payloads")


def websocket_echo(port: int) -> bytes:
    connection = socket.create_connection(("127.0.0.1", port), timeout=3)
    try:
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            "GET /hmr HTTP/1.1\r\n"
            f"Host: 127.0.0.1:{port}\r\n"
            "Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n"
        )
        connection.sendall(request.encode())
        response = b""
        while b"\r\n\r\n" not in response:
            response += connection.recv(4096)
        if not response.startswith(b"HTTP/1.1 101"):
            raise AssertionError(f"WebSocket upgrade failed: {response!r}")
        payload = b"vite-hmr"
        mask = os.urandom(4)
        masked = bytes(value ^ mask[index % 4] for index, value in enumerate(payload))
        connection.sendall(bytes([0x81, 0x80 | len(payload)]) + mask + masked)
        header = connection.recv(2)
        if len(header) != 2:
            raise AssertionError("WebSocket response header was truncated")
        length = header[1] & 0x7F
        echoed = b""
        while len(echoed) < length:
            echoed += connection.recv(length - len(echoed))
        return echoed
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--node-attach", type=Path, required=True)
    parser.add_argument("--skip-concurrency-stress", action="store_true")
    args = parser.parse_args()
    cli = args.cli.resolve()
    node_attach = args.node_attach.resolve()
    if not cli.is_file() or not node_attach.is_file():
        parser.error("--cli and --node-attach must point to built executables")

    state = State()
    control_handler = type("BoundControlHandler", (ControlHandler,), {"state": state})
    control = ReusableThreadingHTTPServer(("127.0.0.1", 0), control_handler)
    dev = ReusableThreadingHTTPServer(("127.0.0.1", 0), DevHandler)
    state.remote_port = int(dev.server_address[1])
    control_thread = threading.Thread(target=control.serve_forever, daemon=True)
    dev_thread = threading.Thread(target=dev.serve_forever, daemon=True)
    control_thread.start()
    dev_thread.start()

    with tempfile.TemporaryDirectory(prefix="agent-remote-e2e-") as temporary:
        root = Path(temporary)
        runtime_socket = root / "runtime.sock"
        runtime_handler = type(
            "BoundRuntimeHelperHandler", (RuntimeHelperHandler,), {"target_port": state.remote_port}
        )
        runtime = ReusableUnixServer(str(runtime_socket), runtime_handler)
        runtime_thread = threading.Thread(target=runtime.serve_forever, daemon=True)
        runtime_thread.start()
        server_url = f"http://127.0.0.1:{control.server_address[1]}"
        cli_home = root / "cli-home"
        prepare_cli_home(cli_home, server_url)
        fake_bin, ssh_count, disconnect_first_ssh = write_gateway_files(
            root, node_attach, server_url, runtime_socket
        )
        state.local_port = free_port()
        environment = os.environ.copy()
        environment["PATH"] = f"{fake_bin}{os.pathsep}{environment['PATH']}"
        environment["AGENT_REMOTE_SECRET_BACKEND"] = "file"
        process = subprocess.Popen(
            [
                str(cli),
                "--home",
                str(cli_home),
                "forward",
                str(state.remote_port),
                "--session",
                SESSION_ID,
                "--local-port",
                str(state.local_port),
            ],
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        failure: BaseException | None = None
        try:
            wait_for(lambda: ssh_count.exists(), "CLI did not start the SSH gateway")
            wait_for(
                lambda: any(
                    path == "/api/v1/node-api/port-forwards/redeem"
                    for _method, path, _body in state.requests
                ),
                "Node did not redeem the initial connection token",
            )
            wait_for(
                lambda: _http_matches(state.local_port, "/", b"agent-remote-e2e"),
                "initial forward did not carry HTTP traffic",
            )
            if int(ssh_count.read_text() or "0") != 1:
                raise AssertionError("SSH failure injection ran before the initial data-path checks")
            if http_get(state.local_port, "/asset.js") != b"window.__agentRemoteE2E = true;":
                raise AssertionError("static HTTP asset changed in transit")
            events = http_get(state.local_port, "/events")
            if b"event: ready" not in events or b"event: update" not in events:
                raise AssertionError(f"SSE payload changed in transit: {events!r}")
            if websocket_echo(state.local_port) != b"vite-hmr":
                raise AssertionError("WebSocket/HMR payload changed in transit")

            disconnect_first_ssh.touch()
            wait_for(
                lambda: ssh_count.exists() and int(ssh_count.read_text() or "0") >= 2,
                "CLI did not reconnect after the forced SSH disconnect",
            )
            wait_for(
                lambda: _http_matches(state.local_port, "/", b"agent-remote-e2e"),
                "forward did not recover after SSH reconnect",
            )
            if not args.skip_concurrency_stress:
                concurrent_http_gets(state.local_port)
            if http_get(state.local_port, "/") != b"agent-remote-e2e":
                raise AssertionError("forward did not remain usable after the final data-path check")
        except BaseException as error:
            failure = error
        finally:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
            try:
                output, _ = process.communicate(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                output, _ = process.communicate()
            runtime.shutdown()
            runtime.server_close()

        if failure is not None:
            raise AssertionError(
                f"E2E failed: {failure}\nCLI output:\n{output}\n"
                f"Control requests: {state.requests}"
            ) from failure
        if process.returncode != 0:
            raise AssertionError(f"CLI exited with {process.returncode}:\n{output}")
        paths = [(method, path) for method, path, _body in state.requests]
        required = {
            ("POST", f"/api/v1/sessions/{SESSION_ID}/port-forwards"),
            ("POST", "/api/v1/node-api/port-forwards/redeem"),
            ("POST", f"/api/v1/port-forwards/{FORWARD_ID}/connections"),
            ("POST", f"/api/v1/node-api/port-forwards/{FORWARD_ID}/release"),
            ("DELETE", f"/api/v1/port-forwards/{FORWARD_ID}"),
        }
        missing = sorted(required.difference(paths))
        if missing:
            raise AssertionError(f"E2E control flow omitted requests: {missing}; observed={paths}")
        if any("connect-token" in path for _method, path in paths):
            raise AssertionError("connection token leaked into an HTTP path")

    control.shutdown()
    control.server_close()
    dev.shutdown()
    dev.server_close()
    print("session port-forwarding cross-repository E2E passed")
    return 0


def _http_matches(port: int, path: str, expected: bytes) -> bool:
    try:
        return http_get(port, path) == expected
    except (OSError, TimeoutError, http.client.HTTPException, AssertionError):
        return False


if __name__ == "__main__":
    raise SystemExit(main())
