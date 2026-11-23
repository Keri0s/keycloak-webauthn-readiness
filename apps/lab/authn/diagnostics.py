"""Callback diagnostics: never log query strings, tokens or exception messages."""

import logging
import uuid

logger = logging.getLogger("authn.callback")

KNOWN_CODES = {
    "invalid_login_state", "expired_login_state",
    "expired_or_invalid_login_state", "mismatching_state",
    "invalid_grant", "invalid_client", "missing_claim", "invalid_claim",
    "expired_token", "bad_signature", "unexpected_issuer",
    "unsupported_id_token_algorithm", "missing_validated_id_token",
    "invalid_callback_parameters", "provider_unavailable", "session_not_allowed",
    "access_denied",
}
KNOWN_CLAIMS = {"iss", "aud", "sub", "sid", "nonce", "exp", "iat", "azp"}


def record_callback_rejection(code, claim="-"):
    code = code if isinstance(code, str) and code in KNOWN_CODES else "other"
    claim = claim if isinstance(claim, str) and claim in KNOWN_CLAIMS else "-"
    reference = uuid.uuid4().hex[:12]
    logger.warning(
        "OIDC_CALLBACK_REJECTED reference=%s code=%s claim=%s",
        reference, code, claim,
    )
    return reference
