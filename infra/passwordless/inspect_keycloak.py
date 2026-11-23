"""Inspect only the N15 lab; never export credentials, tokens or full realm data.

Run with the lab virtualenv. Admin configuration is read with GET requests only.
The token endpoint POST authenticates the operator; no admin mutation is made.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from getpass import getpass
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import quote

import requests

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://auth.readiness.test:9443"
REALM = "webauthn-lab"
CLIENT = "app-lab"
CA = ROOT / "infra/.runtime/keycloak-trust/readiness-root.pem"
OUT = ROOT / "docs/validation/passwordless-preflight"

REALM_FIELDS = (
    "realm", "enabled", "sslRequired", "browserFlow", "registrationFlow",
    "resetCredentialsFlow", "directGrantFlow", "registrationAllowed",
    "resetPasswordAllowed", "rememberMe", "loginWithEmailAllowed",
    "ssoSessionIdleTimeout", "ssoSessionMaxLifespan", "accessTokenLifespan",
    "actionTokenGeneratedByAdminLifespan", "actionTokenGeneratedByUserLifespan",
    "eventsEnabled", "eventsExpiration", "enabledEventTypes",
    "adminEventsEnabled", "adminEventsDetailsEnabled",
)
POLICY_SUFFIXES = (
    "RpEntityName", "RpId", "SignatureAlgorithms", "AttestationConveyancePreference",
    "AuthenticatorAttachment", "RequireResidentKey", "UserVerificationRequirement",
    "CreateTimeout", "AvoidSameAuthenticatorRegister", "AcceptableAaguids",
    "ExtraOrigins", "PasskeysEnabled",
)
CLIENT_FIELDS = (
    "id", "clientId", "enabled", "protocol", "publicClient", "bearerOnly",
    "standardFlowEnabled", "implicitFlowEnabled", "directAccessGrantsEnabled",
    "serviceAccountsEnabled", "redirectUris", "webOrigins",
)
CLIENT_ATTRIBUTES = (
    "pkce.code.challenge.method", "backchannel.logout.url",
    "backchannel.logout.session.required", "post.logout.redirect.uris",
)
FLOW_FIELDS = ("id", "alias", "providerId", "topLevel", "builtIn")
EXECUTION_FIELDS = (
    "id", "requirement", "displayName", "providerId", "authenticationFlow",
    "flowId", "level", "index", "priority", "authenticationConfig",
)


class InspectionError(Exception):
    pass


def pick(data, fields):
    return {key: data[key] for key in fields if key in data}


def sanitize_realm(data):
    result = pick(data, REALM_FIELDS)
    for prefix in ("webAuthnPolicy", "webAuthnPolicyPasswordless"):
        result.update(pick(data, [prefix + suffix for suffix in POLICY_SUFFIXES]))
    # Do not export realm attributes, SMTP credentials or keys.
    return result


def sanitize_client(data):
    result = pick(data, CLIENT_FIELDS)
    result["attributes"] = pick(data.get("attributes") or {}, CLIENT_ATTRIBUTES)
    result["authenticationFlowBindingOverrides"] = pick(
        data.get("authenticationFlowBindingOverrides") or {},
        ("browser", "direct_grant"),
    )
    return result


def observations(realm, client, flows):
    """Report configuration facts, not a WebAuthn security verdict."""
    override = client.get("authenticationFlowBindingOverrides", {}).get("browser")
    selected = [f for f in flows if (
        f.get("id") == override if override else f.get("alias") == realm.get("browserFlow")
    )]
    effective = selected[0] if len(selected) == 1 else None
    return {
        "browser_binding_source": "client_override" if override else "realm_default",
        "effective_browser_flow": effective.get("alias") if effective else None,
        "passwordless_uv_setting": realm.get("webAuthnPolicyPasswordlessUserVerificationRequirement"),
        "passwordless_rp_id": realm.get("webAuthnPolicyPasswordlessRpId"),
        "enabled_execution_providers": sorted({
            e.get("providerId", "subflow-or-unknown")
            for e in (effective or {}).get("executions", [])
            if e.get("requirement") != "DISABLED"
        }),
        "result": "INSPECTED_NOT_ACCEPTANCE_TESTED",
        "limits": [
            "Client policies, custom providers and existing SSO can affect behavior; review separately.",
            "No enrollment, UV-negative, recovery, replay or browser test was executed.",
            "No user or credential endpoint was read. Credential compatibility is still unknown.",
            "An execution list alone does not prove all fallback paths are closed.",
        ],
    }


class LabAPI:
    def __init__(self):
        self.session = requests.Session()
        # Ignore ambient proxies and .netrc; credentials go only to the fixed lab host.
        self.session.trust_env = False
        self.session.verify = str(CA)

    def request(self, method, path, **kwargs):
        if not path.startswith("/") or path.startswith("//"):
            raise InspectionError("Invalid lab path")
        response = self.session.request(
            method, BASE + path, timeout=15, allow_redirects=False, **kwargs,
        )
        if response.status_code != 200:
            # Only fixed, recognized OAuth codes; never print descriptions or raw bodies.
            code = "unclassified"
            if path == "/realms/master/protocol/openid-connect/token":
                try:
                    error = response.json()
                except ValueError:
                    error = None
                candidate = error.get("error") if isinstance(error, dict) else None
                if isinstance(candidate, str) and candidate in {
                    "invalid_grant", "invalid_client", "unauthorized_client",
                    "invalid_request", "unsupported_grant_type", "temporarily_unavailable",
                }:
                    code = candidate
            raise InspectionError(f"HTTP {response.status_code}; code={code}; response body omitted")
        try:
            return response.json()
        except ValueError:
            raise InspectionError("Expected JSON; response body omitted") from None

    def get(self, path, **kwargs):
        return self.request("GET", f"/admin/realms/{REALM}" + path, **kwargs)

    def authenticate(self, username, password, otp):
        form = {"grant_type": "password", "client_id": "admin-cli",
                "username": username, "password": password}
        if otp:
            form["totp"] = otp
        token = self.request("POST", "/realms/master/protocol/openid-connect/token", data=form)
        if not isinstance(token.get("access_token"), str):
            raise InspectionError("No access token; token response omitted")
        self.session.headers["Authorization"] = "Bearer " + token["access_token"]


def collect(api):
    realm = sanitize_realm(api.get(""))
    if realm.get("realm") != REALM:
        raise InspectionError("Unexpected realm")
    clients = api.get("/clients", params={"clientId": CLIENT})
    matches = [c for c in clients if c.get("clientId") == CLIENT]
    if len(matches) != 1:
        raise InspectionError("Expected exactly one app-lab client")
    client = sanitize_client(matches[0])
    flows = []
    for raw in api.get("/authentication/flows"):
        flow = pick(raw, FLOW_FIELDS)
        if raw.get("topLevel"):
            executions = api.get("/authentication/flows/" + quote(raw["alias"], safe="") + "/executions")
            flow["executions"] = [pick(e, EXECUTION_FIELDS) for e in executions]
        flows.append(flow)
    actions = [pick(a, ("alias", "providerId", "enabled", "defaultAction", "priority"))
               for a in api.get("/authentication/required-actions")]
    return {
        "schema_version": 1, "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "Keycloak Admin REST API over verified HTTPS; allowlisted fields only",
        "expected_version_from_compose": "26.8.2 (runtime version not queried)",
        "inspector_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "realm": realm, "client": client, "flows": flows, "required_actions": actions,
        "observations": observations(realm, client, flows),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-connectivity", action="store_true", help="Check TLS/discovery without admin login")
    args = parser.parse_args()
    if not CA.is_file():
        print("Missing lab public CA file: infra/.runtime/keycloak-trust/readiness-root.pem")
        return 1
    api = LabAPI()
    try:
        discovery = api.request("GET", f"/realms/{REALM}/.well-known/openid-configuration")
        if discovery.get("issuer") != f"{BASE}/realms/{REALM}":
            raise InspectionError("Unexpected OIDC issuer")
        print("HTTPS certificate and OIDC issuer: OK")
        if args.check_connectivity:
            return 0
        if not sys.stdin.isatty():
            raise InspectionError("Run interactively in your terminal; do not pipe a password")
        print("Enter the USERNAME you use for Keycloak Admin Console (not a command).")
        print("'master' is the realm name; use it here only if your admin username is also master.")
        username = input("Admin username: ").strip()
        if not username or "python.exe" in username.lower() or "inspect_keycloak.py" in username.lower():
            raise InspectionError("Enter an admin username, not the PowerShell command")
        password = getpass("Admin password (hidden; not saved): ")
        otp = getpass("Admin OTP if configured (otherwise Enter): ")
        try:
            api.authenticate(username, password, otp)
        finally:
            del password, otp
        report = collect(api)
        folder = OUT / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        folder.mkdir(parents=True, exist_ok=False)
        destination = folder / "inspection.json"
        with destination.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print("Saved: " + str(destination))
        print(json.dumps(report["observations"], ensure_ascii=False, indent=2))
        return 0
    except (InspectionError, requests.RequestException) as exc:
        if isinstance(exc, InspectionError):
            print("Inspection stopped: " + str(exc))
        else:
            print("Inspection stopped: HTTPS/network error (details omitted). Check lab DNS, CA and service.")
        print("No realm/client settings changed. Do not disable MFA to run this tool; use Admin Console if admin-cli login is unavailable.")
        return 1
    finally:
        api.session.headers.pop("Authorization", None)
        api.session.close()


if __name__ == "__main__":
    raise SystemExit(main())
