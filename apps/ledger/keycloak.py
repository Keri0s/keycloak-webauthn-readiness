"""Bounded Keycloak Admin REST API client for reading N15 lab events.

Follows the safety guardrails of infra/passwordless/inspect_keycloak.py:
fixed lab BASE/REALM/CLIENT, explicit CA verification, trust_env=False,
allow_redirects=False, allowlisted token error codes, no response body dumps.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

from apps.ledger.schema import EVENT_TYPE_MAP, LAB_BASE_URL, LAB_CLIENT_ID, LAB_REALM

ROOT = Path(__file__).resolve().parents[2]
BASE = LAB_BASE_URL
REALM = LAB_REALM
CLIENT = LAB_CLIENT_ID
CA = ROOT / "infra/.runtime/keycloak-trust/readiness-root.pem"

TOKEN_ERROR_CODES = frozenset(
    {
        "invalid_grant",
        "invalid_client",
        "unauthorized_client",
        "invalid_request",
        "unsupported_grant_type",
        "temporarily_unavailable",
    }
)


class LedgerAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class LabEventsClient:
    def __init__(self, ca_path: Path | None = None):
        self.ca_path = ca_path or CA
        self.session = requests.Session()
        # Ignore ambient proxies and .netrc; requests go only to fixed lab host.
        self.session.trust_env = False
        self.session.verify = str(self.ca_path)
        self._user_cache: dict[str, str] = {}

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        if not isinstance(path, str) or not path.startswith("/") or path.startswith("//"):
            raise LedgerAPIError("Invalid lab path")
        response = self.session.request(
            method,
            BASE + path,
            timeout=15,
            allow_redirects=False,
            **kwargs,
        )
        if response.status_code != 200:
            code = "unclassified"
            if path == "/realms/master/protocol/openid-connect/token":
                try:
                    error = response.json()
                except ValueError:
                    error = None
                candidate = error.get("error") if isinstance(error, dict) else None
                if isinstance(candidate, str) and candidate in TOKEN_ERROR_CODES:
                    code = candidate
            raise LedgerAPIError(
                f"HTTP {response.status_code}; code={code}; response body omitted",
                status_code=response.status_code,
            )
        try:
            return response.json()
        except ValueError:
            raise LedgerAPIError("Expected JSON; response body omitted") from None

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", f"/admin/realms/{REALM}" + path, **kwargs)

    def authenticate(self, username: str, password: str, otp: str = "") -> None:
        form = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": username,
            "password": password,
        }
        if otp:
            form["totp"] = otp
        token = self.request(
            "POST",
            "/realms/master/protocol/openid-connect/token",
            data=form,
        )
        if not isinstance(token, dict) or not isinstance(token.get("access_token"), str):
            raise LedgerAPIError("No access token; token response omitted")
        self.session.headers["Authorization"] = "Bearer " + token["access_token"]

    def realm_id(self) -> str:
        realm = self.get("")
        if not isinstance(realm, dict) or realm.get("realm") != REALM:
            raise LedgerAPIError("Unexpected realm")
        raw_id = realm.get("id")
        return raw_id if isinstance(raw_id, str) and raw_id else REALM

    def events(self, date_from: str, page_size: int = 100) -> list[dict[str, Any]]:
        if page_size <= 0:
            raise ValueError("page_size must be positive")
        collected: list[dict[str, Any]] = []
        first = 0
        types = sorted(EVENT_TYPE_MAP)
        while True:
            params: list[tuple[str, str | int]] = [
                ("client", CLIENT),
                ("dateFrom", date_from),
                ("first", first),
                ("max", page_size),
            ]
            for ev_type in types:
                params.append(("type", ev_type))
            batch = self.get("/events", params=params)
            if not isinstance(batch, list):
                raise LedgerAPIError("Expected list of events; response body omitted")
            collected.extend(batch)
            if len(batch) < page_size:
                break
            first += len(batch)
        return collected

    def username(self, user_id: str) -> str:
        if not isinstance(user_id, str) or not user_id:
            return "unknown"
        if user_id in self._user_cache:
            return self._user_cache[user_id]
        try:
            user = self.get("/users/" + quote(user_id, safe=""))
        except LedgerAPIError as exc:
            if exc.status_code == 404:
                self._user_cache[user_id] = "unknown"
                return "unknown"
            raise
        name = user.get("username") if isinstance(user, dict) else None
        resolved = name if isinstance(name, str) and name else "unknown"
        self._user_cache[user_id] = resolved
        return resolved

    def close(self) -> None:
        self.session.headers.pop("Authorization", None)
        self.session.close()
