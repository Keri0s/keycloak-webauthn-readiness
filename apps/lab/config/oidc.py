import time

from authlib.integrations.django_client import (
    DjangoOAuth2App,
    OAuth,
    OAuthError,
)
from django.conf import settings


class LabKeycloakApp(DjangoOAuth2App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.framework.expires_in = 300

    def load_server_metadata(self):
        metadata = super().load_server_metadata()

        if metadata.get("issuer") != settings.OIDC_ISSUER:
            raise OAuthError(error="unexpected_issuer")

        supported = metadata.get(
            "id_token_signing_alg_values_supported", [],
        )
        if "RS256" not in supported:
            raise OAuthError(error="unsupported_id_token_algorithm")

        return {
            **metadata,
            "id_token_signing_alg_values_supported": ["RS256"],
        }

    def authorize_access_token(self, request, **kwargs):
        state = request.GET.get("state")
        entry = request.session.get(
            f"_state_{self.name}_{state}",
        )

        if not state or not isinstance(entry, dict):
            raise OAuthError(error="invalid_login_state")

        expires_at = entry.get("exp")
        data = entry.get("data")

        valid_expiry = (
            isinstance(expires_at, (int, float))
            and 0 < expires_at - time.time() <= 300
        )
        valid_data = (
            isinstance(data, dict)
            and isinstance(data.get("nonce"), str)
            and bool(data["nonce"])
            and isinstance(data.get("code_verifier"), str)
            and bool(data["code_verifier"])
        )

        if not valid_expiry or not valid_data:
            self.framework.clear_state_data(request.session, state)
            raise OAuthError(error="expired_or_invalid_login_state")

        kwargs["claims_options"] = {
            "iss": {
                "essential": True,
                "value": settings.OIDC_ISSUER,
            },
            "aud": {
                "essential": True,
                "value": settings.OIDC_CLIENT_ID,
            },
            "sub": {"essential": True},
            "sid": {"essential": True},
        }
        kwargs["leeway"] = 30

        try:
            token = super().authorize_access_token(request, **kwargs)
        finally:
            self.framework.clear_state_data(request.session, state)

        if (
            not token.get("id_token")
            or not isinstance(token.get("userinfo"), dict)
        ):
            raise OAuthError(error="missing_validated_id_token")

        return token


oauth = OAuth()

oauth.register(
    name="keycloak",
    client_cls=LabKeycloakApp,
    client_id=settings.OIDC_CLIENT_ID,
    client_secret=settings.OIDC_CLIENT_SECRET,
    server_metadata_url=(
        f"{settings.OIDC_ISSUER}/.well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid profile email",
        "code_challenge_method": "S256",
        "token_endpoint_auth_method": "client_secret_basic",
        "verify": settings.OIDC_CA_BUNDLE,
        "default_timeout": 10,
    },
)