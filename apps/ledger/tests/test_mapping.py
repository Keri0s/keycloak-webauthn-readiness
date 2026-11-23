"""Unit tests for pure Keycloak event-to-ledger-row mapping."""
from __future__ import annotations

import hashlib
import sys
import unittest

from apps.ledger.mapping import event_to_row
from apps.ledger.schema import COLUMNS, LAB_ISSUER


class EventMappingTests(unittest.TestCase):
    def test_mapping_module_does_not_import_requests(self):
        before = "requests" in sys.modules
        # Reload-free check: mapping globals must not reference requests.
        import apps.ledger.mapping as mapping_mod

        self.assertNotIn("requests", mapping_mod.__dict__)
        if not before:
            self.assertNotIn("requests", sys.modules)

    def test_login_passwordless_maps_expected_fields(self):
        event = {
            "id": "3dd8052d-7006-4850-b711-678c59dc98ad",
            "time": 1795435195655,
            "type": "LOGIN",
            "realmId": "webauthn-lab",
            "clientId": "app-lab",
            "userId": "user-uuid-01",
            "sessionId": "sid-uuid-01",
            "details": {
                "username": "lab-user-01",
                "credential_type": "webauthn-passwordless",
                "public_key_credential_id": "gGCUOjoWoGQwWgLe3SMDow",
                "public_key_credential_label": "Edge-Passkey",
                "web_authn_authenticator_user_verification_checked": "true",
            },
        }
        row = event_to_row(
            event,
            username_lookup=lambda _: "should-not-override",
            pulled_at="2026-11-23T12:05:00.000Z",
        )
        self.assertIsNotNone(row)
        self.assertEqual(tuple(row.keys()), COLUMNS)
        self.assertEqual(row["evidence_id"], "3dd8052d-7006-4850-b711-678c59dc98ad")
        self.assertEqual(row["occurred_at_utc"], "2026-11-23T11:59:55.655Z")
        self.assertEqual(row["lab_account"], "lab-user-01")
        self.assertEqual(row["operation"], "authentication")
        self.assertEqual(row["outcome"], "success")
        self.assertEqual(row["credential_type"], "webauthn-passwordless")
        self.assertEqual(row["credential_id"], "gGCUOjoWoGQwWgLe3SMDow")
        self.assertEqual(row["uv_checked"], "true")
        self.assertEqual(row["registration_context"], "no")
        self.assertEqual(row["source_event_type"], "LOGIN")

    def test_update_credential_maps_registration_success(self):
        event = {
            "id": "reg-evt-0947",
            "time": 1795402020000,
            "type": "UPDATE_CREDENTIAL",
            "realmId": "realm-uuid-1",
            "clientId": "app-lab",
            "userId": "user-uuid-01",
            "details": {
                "username": "lab-user-01",
                "credential_type": "webauthn-passwordless",
                "custom_required_action": "webauthn-register-passwordless",
                "public_key_credential_id": "gGCUOjoWoGQwWgLe3SMDow",
                "public_key_credential_label": "Edge-Passkey",
            },
        }
        row = event_to_row(
            event,
            expected_realm_id="realm-uuid-1",
            pulled_at="2026-11-23T12:05:00.000Z",
        )
        self.assertIsNotNone(row)
        self.assertEqual(row["realm"], "webauthn-lab")
        self.assertEqual(row["operation"], "registration")
        self.assertEqual(row["outcome"], "success")
        self.assertEqual(row["credential_id"], "gGCUOjoWoGQwWgLe3SMDow")
        self.assertEqual(row["registration_context"], "yes")

    def test_login_error_null_user_and_long_detail_does_not_leak_description(self):
        long_detail = "NotAllowedError: The operation either timed out or was not allowed. See: https://www.w3.org/TR/webauthn-2/"
        event = {
            "id": "cancel-evt-1416",
            "time": 1795418160000,
            "type": "LOGIN_ERROR",
            "realmId": "webauthn-lab",
            "clientId": "app-lab",
            "userId": None,
            "sessionId": None,
            "error": "not_allowed",
            "details": {
                "credential_type": "webauthn-passwordless",
                "web_authn_authentication_error": "webauthn-error-api-not-allowed",
                "web_authn_error_detail": long_detail,
                "reason": long_detail,
            },
        }
        row = event_to_row(event, pulled_at="2026-11-23T12:05:00.000Z")
        self.assertIsNotNone(row)
        self.assertEqual(row["operation"], "authentication")
        self.assertEqual(row["outcome"], "failure")
        self.assertEqual(row["lab_account"], "unknown")
        self.assertEqual(row["credential_id"], "")
        self.assertEqual(row["error_code"], "not_allowed")
        self.assertEqual(row["webauthn_error"], "webauthn-error-api-not-allowed")
        self.assertNotIn("NotAllowedError", " ".join(row.values()))
        self.assertNotIn("timed out", " ".join(row.values()))

    def test_disallowed_details_and_ip_address_are_dropped(self):
        event = {
            "id": "evt-secret-check",
            "time": 1795435195655,
            "type": "LOGIN",
            "realmId": "webauthn-lab",
            "clientId": "app-lab",
            "userId": "user-uuid-01",
            "sessionId": "raw-sid-secret",
            "ipAddress": "203.0.113.99",
            "details": {
                "username": "lab-user-01",
                "credential_type": "webauthn-passwordless",
                "public_key_credential_id": "gGCUOjoWoGQwWgLe3SMDow",
                "privateKey": "SUPER_SECRET_PRIVATE_KEY",
                "code_id": "CODE_ID_LEAK",
                "redirect_uri": "https://app.readiness.test:9443/auth/callback/?code=xyz",
                "attestationObject": "RAW_ATTESTATION",
            },
        }
        row = event_to_row(event, pulled_at="2026-11-23T12:05:00.000Z")
        self.assertIsNotNone(row)
        serialized = "\n".join(row.values())
        for forbidden in (
            "203.0.113.99",
            "raw-sid-secret",
            "user-uuid-01",
            "SUPER_SECRET_PRIVATE_KEY",
            "CODE_ID_LEAK",
            "redirect_uri",
            "RAW_ATTESTATION",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_excluded_client_and_event_types_return_none(self):
        base = {
            "id": "evt-1",
            "time": 1795435195655,
            "realmId": "webauthn-lab",
            "clientId": "app-lab",
            "type": "LOGIN",
        }
        for patch in (
            {"clientId": "account-console"},
            {"realmId": "master"},
            {"type": "CODE_TO_TOKEN"},
            {"type": "CUSTOM_REQUIRED_ACTION"},
            {"type": "LOGOUT"},
        ):
            candidate = {**base, **patch}
            self.assertIsNone(event_to_row(candidate))

    def test_session_and_subject_ref_match_app_evidence_formula(self):
        # Independent formula matching apps/lab/authn/evidence.py and fr05-login.sql
        sid = "sid-sample-123"
        uid = "uid-sample-456"
        expected_session_ref = hashlib.sha256(
            f"{LAB_ISSUER}\napp-lab\n{sid}".encode("utf-8")
        ).hexdigest()
        expected_subject_ref = hashlib.sha256(
            f"{LAB_ISSUER}\n{uid}".encode("utf-8")
        ).hexdigest()
        row = event_to_row(
            {
                "id": "evt-ref-1",
                "time": 1795435195655,
                "type": "LOGIN",
                "realmId": "webauthn-lab",
                "clientId": "app-lab",
                "userId": uid,
                "sessionId": sid,
                "details": {"username": "lab-user-01"},
            },
            pulled_at="2026-11-23T12:05:00.000Z",
        )
        self.assertEqual(row["session_ref"], expected_session_ref)
        self.assertEqual(row["subject_ref"], expected_subject_ref)

    def test_username_lookup_used_when_details_username_missing(self):
        row = event_to_row(
            {
                "id": "evt-lookup",
                "time": 1795435195655,
                "type": "UPDATE_CREDENTIAL",
                "realmId": "webauthn-lab",
                "clientId": "app-lab",
                "userId": "uid-lookup-1",
                "details": {"credential_type": "webauthn-passwordless"},
            },
            username_lookup=lambda uid: "lab-user-01" if uid == "uid-lookup-1" else "unknown",
            pulled_at="2026-11-23T12:05:00.000Z",
        )
        self.assertEqual(row["lab_account"], "lab-user-01")


if __name__ == "__main__":
    unittest.main()
