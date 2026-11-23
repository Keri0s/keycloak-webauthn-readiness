"""Schema constants and allowlists for the N15 WebAuthn evidence ledger."""
from __future__ import annotations

import re

LAB_BASE_URL = "https://auth.readiness.test:9443"
LAB_REALM = "webauthn-lab"
LAB_CLIENT_ID = "app-lab"
LAB_ISSUER = f"{LAB_BASE_URL}/realms/{LAB_REALM}"

COLUMNS: tuple[str, ...] = (
    "evidence_id",
    "occurred_at_utc",
    "realm",
    "client_id",
    "lab_account",
    "operation",
    "outcome",
    "credential_type",
    "credential_id",
    "credential_label",
    "uv_checked",
    "registration_context",
    "source_event_type",
    "error_code",
    "webauthn_error",
    "session_ref",
    "subject_ref",
    "pulled_at_utc",
)

DISPLAY_COLUMNS: tuple[str, ...] = (
    "evidence_id",
    "occurred_at_utc",
    "occurred_at_vn",
    "lab_account",
    "operation",
    "outcome",
    "credential_id",
    "uv_checked",
    "registration_context",
    "source_event_type",
    "error_code",
)

EVENT_TYPE_MAP: dict[str, tuple[str, str]] = {
    "LOGIN": ("authentication", "success"),
    "LOGIN_ERROR": ("authentication", "failure"),
    "UPDATE_CREDENTIAL": ("registration", "success"),
    "UPDATE_CREDENTIAL_ERROR": ("registration", "failure"),
}

REGISTRATION_CONTEXT_ACTION = "webauthn-register-passwordless"

EVENT_ID_RE = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
LAB_ACCOUNT_RE = re.compile(r"^[A-Za-z0-9._@-]{1,64}$")
ERROR_CODE_RE = re.compile(r"^[A-Za-z0-9_.-]{1,80}$")
CREDENTIAL_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,512}$")
CREDENTIAL_TYPE_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
LABEL_SAFE_RE = re.compile(r"^[A-Za-z0-9 ._()/-]{1,80}$")
