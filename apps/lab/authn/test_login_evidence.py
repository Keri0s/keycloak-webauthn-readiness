"""Offline header/guard tests; not a real WebAuthn acceptance run."""
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import patch
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase
from .evidence import reference
from .views import private_page


class LoginEvidenceTests(SimpleTestCase):
    def test_guarded_page_exposes_correlations_not_raw_identifiers(self):
        group = SimpleNamespace(issuer="https://synthetic.test/realm", client_id="test-app",
                                sid="synthetic-secret-sid", subject="synthetic-subject")
        binding = SimpleNamespace(group=group, user=object(),
                                  created_at=datetime(2026, 11, 23, tzinfo=timezone.utc))
        with patch("authn.views.require_active_binding", return_value=binding) as guard, \
                patch("authn.views.render", return_value=HttpResponse("synthetic page")):
            response = private_page(RequestFactory().get("/private/"))
        guard.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Lab-Session-Ref"], reference(group.issuer, group.client_id, group.sid))
        self.assertEqual(response["X-Lab-Subject-Ref"], reference(group.issuer, group.subject))
        self.assertEqual(response["X-Lab-Binding-Created"], "2026-11-23T00:00:00+00:00")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotIn(group.sid, str(response.headers))
        self.assertNotIn(group.subject, str(response.headers))

    def test_rejected_request_never_gets_evidence_headers(self):
        with patch("authn.views.require_active_binding", side_effect=PermissionDenied), \
                patch("authn.views.attach_binding_evidence") as attach:
            with self.assertRaises(PermissionDenied):
                private_page(RequestFactory().get("/private/"))
        attach.assert_not_called()

    def test_scope_and_subject_changes_are_distinguishable(self):
        self.assertNotEqual(reference("issuer-a", "client", "sid"), reference("issuer-b", "client", "sid"))
        self.assertNotEqual(reference("issuer", "client-a", "sid"), reference("issuer", "client-b", "sid"))
        self.assertNotEqual(reference("issuer", "subject-a"), reference("issuer", "subject-b"))
