"""Offline checks: prevent secret export and misleading flow selection."""
import json
import unittest
from unittest.mock import Mock

from inspect_keycloak import (
    BASE, CA, InspectionError, LabAPI, collect, observations,
    sanitize_client, sanitize_realm,
)


class InspectionTests(unittest.TestCase):
    def test_realm_excludes_secrets_and_unknown_fields(self):
        safe = sanitize_realm({
            "realm": "webauthn-lab", "webAuthnPolicyPasswordlessUserVerificationRequirement": "required",
            "smtpServer": {"password": "DO_NOT_EXPORT"},
            "privateKey": "DO_NOT_EXPORT", "attributes": {"secret": "DO_NOT_EXPORT"},
            "webAuthnPolicyPasswordlessFutureSecret": "DO_NOT_EXPORT",
        })
        self.assertEqual(safe["webAuthnPolicyPasswordlessUserVerificationRequirement"], "required")
        self.assertNotIn("DO_NOT_EXPORT", json.dumps(safe))

    def test_client_excludes_secret_and_unknown_attributes(self):
        safe = sanitize_client({
            "clientId": "app-lab", "secret": "DO_NOT_EXPORT",
            "attributes": {"pkce.code.challenge.method": "S256", "secret": "DO_NOT_EXPORT"},
        })
        self.assertEqual(safe["attributes"], {"pkce.code.challenge.method": "S256"})
        self.assertNotIn("DO_NOT_EXPORT", json.dumps(safe))

    def test_client_override_wins_over_realm_default(self):
        result = observations({"browserFlow": "browser"}, {
            "authenticationFlowBindingOverrides": {"browser": "new-id"},
        }, [{"id": "old-id", "alias": "browser"}, {"id": "new-id", "alias": "candidate"}])
        self.assertEqual(result["effective_browser_flow"], "candidate")
        self.assertEqual(result["result"], "INSPECTED_NOT_ACCEPTANCE_TESTED")

    def test_unresolved_override_is_unknown_not_default(self):
        result = observations({"browserFlow": "browser"}, {
            "authenticationFlowBindingOverrides": {"browser": "missing"},
        }, [{"id": "old-id", "alias": "browser"}])
        self.assertIsNone(result["effective_browser_flow"])

    def test_realm_default_and_disabled_execution(self):
        result = observations({"browserFlow": "browser"}, {}, [{
            "id": "old-id", "alias": "browser", "executions": [
                {"providerId": "password", "requirement": "DISABLED"},
                {"providerId": "passkey", "requirement": "REQUIRED"},
            ],
        }])
        self.assertEqual(result["enabled_execution_providers"], ["passkey"])

    def test_collection_only_reads_and_does_not_request_users(self):
        api = Mock()
        data = {
            "": {"realm": "webauthn-lab", "browserFlow": "browser"},
            "/clients": [{"clientId": "app-lab", "secret": "DO_NOT_EXPORT"}],
            "/authentication/flows": [{"id": "f", "alias": "browser", "topLevel": True}],
            "/authentication/flows/browser/executions": [{
                "providerId": "auth-cookie", "requirement": "ALTERNATIVE", "unknown": "DO_NOT_EXPORT",
            }],
            "/authentication/required-actions": [{"alias": "webauthn-register-passwordless",
                "enabled": True, "config": {"secret": "DO_NOT_EXPORT"}}],
        }
        api.get.side_effect = lambda path, **kwargs: data[path]
        report = collect(api)
        self.assertNotIn("DO_NOT_EXPORT", json.dumps(report))
        self.assertEqual({c[0] for c in api.mock_calls}, {"get"})
        self.assertEqual(len(api.get.call_args_list), 5)

    def test_http_errors_do_not_leak_response_and_redirects_disabled(self):
        api = LabAPI()
        self.assertEqual(api.session.verify, str(CA))
        self.assertFalse(api.session.trust_env)
        api.session.request = Mock(return_value=Mock(status_code=302, text="DO_NOT_EXPORT"))
        with self.assertRaisesRegex(InspectionError, "HTTP 302") as caught:
            api.request("GET", "/example")
        self.assertNotIn("DO_NOT_EXPORT", str(caught.exception))
        args, kwargs = api.session.request.call_args
        self.assertEqual(args, ("GET", BASE + "/example"))
        self.assertFalse(kwargs["allow_redirects"])
        api.session.close()

    def test_ambiguous_client_stops_collection(self):
        api = Mock()
        api.get.side_effect = [{"realm": "webauthn-lab"}, []]
        with self.assertRaises(InspectionError):
            collect(api)

    def test_token_error_only_exports_allowlisted_code(self):
        api = LabAPI()
        try:
            for payload, expected in [
                ({"error": "invalid_grant", "error_description": "SECRET"}, "invalid_grant"),
                ({"error": "SECRET"}, "unclassified"),
                ({"error": ["SECRET"]}, "unclassified"),
                (["SECRET"], "unclassified"),
            ]:
                response = Mock(status_code=400)
                response.json.return_value = payload
                api.session.request = Mock(return_value=response)
                with self.assertRaises(InspectionError) as caught:
                    api.request("POST", "/realms/master/protocol/openid-connect/token")
                self.assertIn("code=" + expected, str(caught.exception))
                self.assertNotIn("SECRET", str(caught.exception))
        finally:
            api.session.close()


if __name__ == "__main__":
    unittest.main()
