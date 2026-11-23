"""Pure mapping from Keycloak EventRepresentation objects to allowlisted ledger rows.

This module intentionally does not perform any network I/O or import requests.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Any, Callable, Mapping

from apps.ledger.schema import (
    COLUMNS,
    CREDENTIAL_ID_RE,
    CREDENTIAL_TYPE_RE,
    ERROR_CODE_RE,
    EVENT_ID_RE,
    EVENT_TYPE_MAP,
    LAB_ACCOUNT_RE,
    LAB_CLIENT_ID,
    LAB_ISSUER,
    LAB_REALM,
    LABEL_SAFE_RE,
    REGISTRATION_CONTEXT_ACTION,
)


def sha256_hex(*parts: str) -> str:
    """Compute SHA-256 hex digest matching apps.lab.authn.evidence.reference."""
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def format_epoch_ms_utc(epoch_ms: Any) -> str:
    """Convert Unix epoch milliseconds to ISO-8601 UTC string with milliseconds."""
    if type(epoch_ms) is not int or epoch_ms < 0:
        raise ValueError("Invalid event timestamp")
    seconds, millis = divmod(epoch_ms, 1000)
    dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
    return f"{dt:%Y-%m-%dT%H:%M:%S}.{millis:03d}Z"


def _normalize_code(value: Any, pattern) -> str:
    if value is None or value == "":
        return ""
    if not isinstance(value, str):
        return "other"
    return value if pattern.fullmatch(value) else "other"


def _normalize_credential_id(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value if CREDENTIAL_ID_RE.fullmatch(value) else ""


def _normalize_label(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value if LABEL_SAFE_RE.fullmatch(value) else ""


def _normalize_uv(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "false"):
            return lowered
    return ""


def _resolve_lab_account(
    details: Mapping[str, Any],
    user_id: Any,
    username_lookup: Callable[[str], str | None] | None,
) -> str:
    raw_username = details.get("username")
    if isinstance(raw_username, str) and LAB_ACCOUNT_RE.fullmatch(raw_username):
        return raw_username
    if isinstance(user_id, str) and user_id and username_lookup is not None:
        resolved = username_lookup(user_id)
        if isinstance(resolved, str) and LAB_ACCOUNT_RE.fullmatch(resolved):
            return resolved
    return "unknown"


def event_to_row(
    event: Mapping[str, Any],
    *,
    username_lookup: Callable[[str], str | None] | None = None,
    pulled_at: str | None = None,
    expected_realm_id: str | None = None,
) -> dict[str, str] | None:
    """Map one Keycloak user event to an allowlisted ledger row, or None if excluded."""
    if not isinstance(event, Mapping):
        return None

    realm_id = event.get("realmId")
    allowed_realm = expected_realm_id if expected_realm_id is not None else LAB_REALM
    if realm_id != allowed_realm:
        return None

    if event.get("clientId") != LAB_CLIENT_ID:
        return None

    event_type = event.get("type")
    if event_type not in EVENT_TYPE_MAP:
        return None

    event_id = event.get("id")
    if not isinstance(event_id, str) or not EVENT_ID_RE.fullmatch(event_id):
        raise ValueError("Eligible Keycloak event is missing a valid source id")

    occurred_at_utc = format_epoch_ms_utc(event.get("time"))
    operation, outcome = EVENT_TYPE_MAP[event_type]

    raw_details = event.get("details")
    details: Mapping[str, Any] = raw_details if isinstance(raw_details, Mapping) else {}

    user_id = event.get("userId")
    session_id = event.get("sessionId")

    lab_account = _resolve_lab_account(details, user_id, username_lookup)
    credential_type = _normalize_code(details.get("credential_type"), CREDENTIAL_TYPE_RE)
    credential_id = _normalize_credential_id(details.get("public_key_credential_id"))
    credential_label = _normalize_label(details.get("public_key_credential_label"))
    uv_checked = _normalize_uv(
        details.get("web_authn_authenticator_user_verification_checked")
    )
    registration_context = (
        "yes"
        if details.get("custom_required_action") == REGISTRATION_CONTEXT_ACTION
        else "no"
    )
    error_code = _normalize_code(event.get("error"), ERROR_CODE_RE)
    raw_webauthn_err = details.get("web_authn_authentication_error")
    if raw_webauthn_err in (None, ""):
        raw_webauthn_err = details.get("web_authn_registration_error")
    webauthn_error = _normalize_code(raw_webauthn_err, ERROR_CODE_RE)

    session_ref = (
        sha256_hex(LAB_ISSUER, LAB_CLIENT_ID, session_id)
        if isinstance(session_id, str) and session_id
        else ""
    )
    subject_ref = (
        sha256_hex(LAB_ISSUER, user_id)
        if isinstance(user_id, str) and user_id
        else ""
    )

    pulled_value = (
        pulled_at
        if isinstance(pulled_at, str) and pulled_at
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    )

    row = {
        "evidence_id": event_id,
        "occurred_at_utc": occurred_at_utc,
        "realm": LAB_REALM,
        "client_id": LAB_CLIENT_ID,
        "lab_account": lab_account,
        "operation": operation,
        "outcome": outcome,
        "credential_type": credential_type,
        "credential_id": credential_id,
        "credential_label": credential_label,
        "uv_checked": uv_checked,
        "registration_context": registration_context,
        "source_event_type": event_type,
        "error_code": error_code,
        "webauthn_error": webauthn_error,
        "session_ref": session_ref,
        "subject_ref": subject_ref,
        "pulled_at_utc": pulled_value,
    }
    return {col: row[col] for col in COLUMNS}
