from pathlib import Path


runbook = Path("docs/device-control-operations-runbook.md").read_text(encoding="utf-8")
compose = Path("deploy/compose/docker-compose.yml").read_text(encoding="utf-8")
acceptance_compose = Path(
    "deploy/compose/docker-compose.device-acceptance.yml"
).read_text(encoding="utf-8")

required_sections = (
    "## 2. 数据保留",
    "## 3. 激活、安装与升级",
    "## 4. 正常停用、撤销与卸载",
    "## 5. 事件响应",
    "## 6. 密钥与凭据轮换",
    "### 6.1 设备令牌",
    "### 6.2 发布证据签名键",
    "### 6.3 出站策略证明键",
    "## 7. 回滚与演练",
)
required_contracts = (
    "`DEVICE_CONTROL_ENABLED` 必须保持 `false`",
    "DEVICE_SESSION_RETENTION_DAYS",
    "DEVICE_SESSION_AUDIT_RETENTION_DAYS",
    "不得用未经评审的原始 SQL",
    "--version VERSION --require-clean --require-tag --require-origin",
    'agent-remote device install --source "/path/to/Agent Remote Device.app"',
    "agent-remote device revoke --device DEVICE_ID --yes",
    "agent-remote device uninstall --yes",
    "不得颠倒 `revoke` 和 `uninstall`",
    "agent-remote device rotate-token --yes",
    "DEVICE_CONTROL_RELEASE_PRIVATE_KEY_PEM",
    "DEVICE_CONTROL_RELEASE_PUBLIC_KEY",
    "新的签名、公证 App 和新的协调 release",
    "不要自动重放未确认动作",
)

missing = [value for value in (*required_sections, *required_contracts) if value not in runbook]
if missing:
    raise SystemExit(f"device-control operations runbook is missing: {', '.join(missing)}")

required_compose_contracts = (
    "DEVICE_CONTROL_ENABLED: ${DEVICE_CONTROL_ENABLED:-false}",
    "DEVICE_CONTROL_V2_ROLLOUT_PERCENT: ${DEVICE_CONTROL_V2_ROLLOUT_PERCENT:-0}",
    "DEVICE_CONTROL_RELEASE_EVIDENCE_PATH: /run/agent-remote/device-control-release-evidence.json",
    "source: ${DEVICE_CONTROL_RELEASE_EVIDENCE_FILE:-/dev/null}",
    "read_only: true",
    "DEVICE_SESSION_RETENTION_DAYS: ${DEVICE_SESSION_RETENTION_DAYS:-0}",
    "DEVICE_SESSION_AUDIT_RETENTION_DAYS: ${DEVICE_SESSION_AUDIT_RETENTION_DAYS:-0}",
)
missing_compose = [value for value in required_compose_contracts if value not in compose]
if missing_compose:
    raise SystemExit(f"compose device-control deployment is missing: {', '.join(missing_compose)}")

required_acceptance_contracts = (
    "DEVICE_CONTROL_V2_ACCEPTANCE_DEVICE_ID is required",
    "DEVICE_CONTROL_V2_ACCEPTANCE_EXPIRES_AT is required",
)
missing_acceptance = [
    value for value in required_acceptance_contracts if value not in acceptance_compose
]
if missing_acceptance:
    raise SystemExit(
        "compose v2 acceptance deployment is missing: " + ", ".join(missing_acceptance)
    )

revoke_position = runbook.index("agent-remote device revoke --device DEVICE_ID --yes")
uninstall_position = runbook.index("agent-remote device uninstall --yes")
if revoke_position >= uninstall_position:
    raise SystemExit("the runbook must revoke remote access before uninstalling the app")

for forbidden_claim in ("生产门禁已满足", "production ready", "ready: true"):
    if forbidden_claim in runbook:
        raise SystemExit(f"the runbook makes a forbidden readiness claim: {forbidden_claim}")
