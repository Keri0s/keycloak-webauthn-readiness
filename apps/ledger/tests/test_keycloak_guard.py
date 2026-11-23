"""Offline guard tests for Keycloak Admin Events API client."""
from __future__ import annotations

import unittest
from unittest.mock import Mock

from apps.ledger.keycloak import BASE, CA, LabEventsClient, LedgerAPIError


class KeycloakClientGuardTests(unittest.TestCase):
    def test_client_enforces_lab_ca_no_trust_env_no_redirects_and_path_guard(self):
        client = LabEventsClient()
        try:
            self.assertEqual(client.session.verify, str(CA))
            self.assertFalse(client.session.trust_env)

            for bad_path in ("//evil.example/steal", "http://evil.example/steal", "relative"):
                with self.assertRaises(LedgerAPIError):
                    client.request("GET", bad_path)

            client.session.request = Mock(
                return_value=Mock(status_code=302, text="SECRET_BODY_SHOULD_NOT_LEAK")
            )
            with self.assertRaisesRegex(LedgerAPIError, "HTTP 302") as caught:
                client.request("GET", "/admin/realms/webauthn-lab/events")
            self.assertNotIn("SECRET_BODY_SHOULD_NOT_LEAK", str(caught.exception))

            args, kwargs = client.session.request.call_args
            self.assertEqual(args, ("GET", BASE + "/admin/realms/webauthn-lab/events"))
            self.assertFalse(kwargs["allow_redirects"])
        finally:
            client.close()

    def test_events_paginates_and_username_caches_with_404_fallback(self):
        client = LabEventsClient()
        try:
            page1 = [{"id": "e1"}, {"id": "e2"}]
            page2 = [{"id": "e3"}]
            resp1 = Mock(status_code=200)
            resp1.json.return_value = page1
            resp2 = Mock(status_code=200)
            resp2.json.return_value = page2
            user_ok = Mock(status_code=200)
            user_ok.json.return_value = {"id": "u1", "username": "lab-user-01"}
            user_missing = Mock(status_code=404, text="not found")

            client.session.request = Mock(
                side_effect=[resp1, resp2, user_ok, user_missing]
            )
            events = client.events("2026-11-16", page_size=2)
            self.assertEqual([e["id"] for e in events], ["e1", "e2", "e3"])

            self.assertEqual(client.username("u1"), "lab-user-01")
            # Second lookup hits cache (no extra HTTP call).
            self.assertEqual(client.username("u1"), "lab-user-01")
            self.assertEqual(client.username("deleted-u"), "unknown")
            self.assertEqual(client.session.request.call_count, 4)
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main()
