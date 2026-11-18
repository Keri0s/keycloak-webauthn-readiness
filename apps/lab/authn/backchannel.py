import time

from django.conf import settings
from joserfc import jwt
from joserfc.errors import InvalidClaimError, InvalidKeyIdError
from joserfc.jwk import KeySet

from config.oidc import oauth


LOGOUT_EVENT = "http://schemas.openid.net/event/backchannel-logout"
LOGOUT_TOKEN_MAX_AGE = 300
LOGOUT_CLOCK_SKEW = 30
LOGOUT_TOKEN_MAX_LENGTH = 16_384


def verify_sid_logout_token(raw_token):
    """Xac minh Logout Token cho profile lab yeu cau SID."""
    if (
        not isinstance(raw_token, str)
        or not raw_token
        or len(raw_token) > LOGOUT_TOKEN_MAX_LENGTH
        or not raw_token.isascii()
        or raw_token.count(".") != 2
    ):
        raise InvalidClaimError("logout_token")

    client = oauth.keycloak
    key_set = KeySet.import_key_set(client.fetch_jwk_set())

    try:
        token = jwt.decode(
            raw_token,
            key=key_set,
            algorithms=["RS256"],
        )
    except InvalidKeyIdError:
        key_set = KeySet.import_key_set(
            client.fetch_jwk_set(force=True),
        )
        token = jwt.decode(
            raw_token,
            key=key_set,
            algorithms=["RS256"],
        )

    claims = token.claims
    now = int(time.time())

    registry = jwt.JWTClaimsRegistry(
        now=now,
        leeway=LOGOUT_CLOCK_SKEW,
        iss={
            "essential": True,
            "value": settings.OIDC_ISSUER,
        },
        aud={
            "essential": True,
            "value": settings.OIDC_CLIENT_ID,
        },
        iat={"essential": True},
        exp={"essential": True},
        jti={"essential": True},
        sid={"essential": True},
    )
    registry.validate(claims)

    if now - claims["iat"] > LOGOUT_TOKEN_MAX_AGE + LOGOUT_CLOCK_SKEW:
        raise InvalidClaimError("iat")

    if claims["exp"] <= claims["iat"]:
        raise InvalidClaimError("exp")

    for name in ("jti", "sid", "sub"):
        if name == "sub" and name not in claims:
            continue

        value = claims.get(name)
        if (
            not isinstance(value, str)
            or not value.strip()
            or len(value) > 255
        ):
            raise InvalidClaimError(name)

    events = claims.get("events")
    if (
        not isinstance(events, dict)
        or LOGOUT_EVENT not in events
        or not isinstance(events[LOGOUT_EVENT], dict)
    ):
        raise InvalidClaimError("events")

    if "nonce" in claims:
        raise InvalidClaimError("nonce")

    return {
        "issuer": claims["iss"],
        "client_id": settings.OIDC_CLIENT_ID,
        "jti": claims["jti"],
        "sid": claims["sid"],
        "subject": claims.get("sub"),
    }