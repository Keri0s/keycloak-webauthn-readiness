"""Offline regression tests; no provider, database or real passkey is used."""

import logging
from unittest.mock import patch

from authlib.integrations.django_client import DjangoOAuth2App, OAuthError
from django.test import RequestFactory, SimpleTestCase

from config.oidc import oauth
from .diagnostics import record_callback_rejection
from .views import oidc_callback


class CallbackRecoveryTests(SimpleTestCase):
    def setUp(self):
        # Synthetic failures must not pollute the runtime diagnosis file.
        logger = logging.getLogger("authn.callback")
        previous_handlers = logger.handlers
        logger.handlers = [logging.NullHandler()]
        self.addCleanup(setattr, logger, "handlers", previous_handlers)
        self.factory = RequestFactory()
        self.app = oauth.keycloak
        self.key = "_state_keycloak_test-state"
        self.request = self.factory.get(
            "/auth/callback/", {"state": "test-state", "code": "test-code"},
        )
        self.request.session = {
            self.key: {
                "exp": 1300,
                "data": {"nonce": "test-nonce", "code_verifier": "test-verifier"},
            },
        }

    def test_expired_attempt_cannot_exchange_code_and_can_restart(self):
        with patch("config.oidc.time.time", return_value=1301), patch.object(
            DjangoOAuth2App, "authorize_access_token",
        ) as exchange, patch("authn.views.create_verified_session") as create:
            response = oidc_callback(self.request)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Lượt đăng nhập đã hết thời gian", status_code=400)
        self.assertContains(response, 'href="/auth/login/"', status_code=400)
        self.assertEqual(response["Referrer-Policy"], "no-referrer")
        self.assertIn("no-store", response["Cache-Control"])
        self.assertNotIn(self.key, self.request.session)
        exchange.assert_not_called()
        create.assert_not_called()

    def test_missing_state_does_not_call_provider(self):
        self.request.session.clear()
        with patch.object(DjangoOAuth2App, "authorize_access_token") as exchange:
            response = oidc_callback(self.request)
        self.assertEqual(response.status_code, 400)
        exchange.assert_not_called()

    def test_nonce_and_pkce_are_still_required(self):
        for missing in ("nonce", "code_verifier"):
            with self.subTest(missing=missing):
                self.setUp()
                del self.request.session[self.key]["data"][missing]
                with patch("config.oidc.time.time", return_value=1000), patch.object(
                    DjangoOAuth2App, "authorize_access_token",
                ) as exchange:
                    with self.assertRaises(OAuthError) as caught:
                        self.app.authorize_access_token(self.request)
                self.assertEqual(caught.exception.error, "expired_or_invalid_login_state")
                exchange.assert_not_called()

    def test_valid_state_is_consumed_and_replay_is_rejected(self):
        token = {"id_token": "synthetic-token", "userinfo": {"sub": "synthetic-user"}}
        with patch("config.oidc.time.time", return_value=1000), patch.object(
            DjangoOAuth2App, "authorize_access_token", return_value=token,
        ) as exchange:
            self.assertEqual(self.app.authorize_access_token(self.request), token)
            with self.assertRaises(OAuthError) as caught:
                self.app.authorize_access_token(self.request)
        self.assertEqual(caught.exception.error, "invalid_login_state")
        exchange.assert_called_once()
        self.assertTrue(exchange.call_args.kwargs["claims_options"]["sid"]["essential"])

    def test_provider_error_still_consumes_state_and_hides_description(self):
        with patch("config.oidc.time.time", return_value=1000), patch.object(
            DjangoOAuth2App, "authorize_access_token",
            side_effect=OAuthError(error="invalid_grant", description="SECRET_PROVIDER_DETAIL"),
        ), self.assertLogs("authn.callback", level="WARNING") as logs:
            response = oidc_callback(self.request)
        self.assertEqual(response.status_code, 400)
        self.assertNotIn(self.key, self.request.session)
        self.assertNotContains(response, "SECRET_PROVIDER_DETAIL", status_code=400)
        self.assertNotIn("SECRET_PROVIDER_DETAIL", " ".join(logs.output))
        self.assertIn("code=invalid_grant", " ".join(logs.output))

    def test_duplicate_callback_parameters_are_rejected(self):
        for query in ("state=a&state=b&code=c", "state=a&code=b&code=c"):
            with self.subTest(query=query), patch.object(
                self.app, "authorize_access_token",
            ) as exchange:
                response = oidc_callback(self.factory.get("/auth/callback/?" + query))
            self.assertEqual(response.status_code, 400)
            exchange.assert_not_called()

    def test_success_still_creates_binding_and_redirects(self):
        claims = {"iss": "test-issuer", "sid": "test-sid", "sub": "test-user"}
        with patch.object(self.app, "authorize_access_token", return_value={"userinfo": claims}), patch(
            "authn.views.create_verified_session",
        ) as create:
            response = oidc_callback(self.request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/private/")
        create.assert_called_once()

    def test_log_uses_allowlist_and_never_raw_external_values(self):
        with self.assertLogs("authn.callback", level="WARNING") as logs:
            reference = record_callback_rejection("SECRET\nforged_log", "SECRET_CLAIM")
        self.assertRegex(reference, r"^[0-9a-f]{12}$")
        output = " ".join(logs.output)
        self.assertIn("code=other claim=-", output)
        self.assertNotIn("SECRET", output)

    def test_far_future_state_is_still_rejected(self):
        with patch("config.oidc.time.time", return_value=999), patch.object(
            DjangoOAuth2App, "authorize_access_token",
        ) as exchange:
            response = oidc_callback(self.request)
        self.assertEqual(response.status_code, 400)
        exchange.assert_not_called()
