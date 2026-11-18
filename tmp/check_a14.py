import hashlib
import sys
import time
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import django
from django.conf import settings
from django.contrib.auth import get_user, get_user_model
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.sessions.models import Session
from django.db import connection, transaction
from django.test import Client, RequestFactory, override_settings
from django.utils import timezone
from joserfc import jwt
from joserfc.jwk import RSAKey

from authn.models import (
    ExternalIdentity,
    OIDCSessionGroup,
    SessionBinding,
    SIDRevocationMarker,
)
from config.oidc import oauth


assert connection.vendor == "postgresql"
assert connection.get_autocommit()
assert not connection.in_atomic_block

User = get_user_model()
prefix = f"probe-a14-{uuid4().hex}"
subject = f"{prefix}-subject"
issuer = settings.OIDC_ISSUER
client_id = settings.OIDC_CLIENT_ID
session_keys = set()
rejected_keys = []

key = RSAKey.generate_key(
    2048,
    parameters={"kid": "a14-probe"},
)
jwks = {"keys": [key.as_dict(private=False)]}
metadata = {
    "issuer": issuer,
    "id_token_signing_alg_values_supported": ["RS256"],
}


def state_counts():
    return (
        OIDCSessionGroup.objects.count(),
        SessionBinding.objects.count(),
        SIDRevocationMarker.objects.count(),
    )


def backend_user(session_key):
    request = RequestFactory().get("/")
    request.session = SessionStore(session_key=session_key)
    return get_user(request)


def private_response(session_key):
    browser = Client(HTTP_HOST="app.readiness.test")
    browser.cookies[settings.SESSION_COOKIE_NAME] = session_key
    return browser.get("/private/", secure=True)


def run_callback(label, include_sid, sid):
    browser = Client(HTTP_HOST="app.readiness.test")
    state = f"{prefix}-{label}"
    nonce = uuid4().hex
    verifier = uuid4().hex + uuid4().hex

    # Tao trang thai OIDC tam giong trang thai truoc callback.
    pending = browser.session
    pending[f"_state_keycloak_{state}"] = {
        "exp": time.time() + 240,
        "data": {
            "nonce": nonce,
            "code_verifier": verifier,
            "redirect_uri": settings.OIDC_REDIRECT_URI,
        },
    }
    pending.save()
    session_keys.add(pending.session_key)

    now = int(time.time())
    claims = {
        "iss": issuer,
        "aud": client_id,
        "sub": subject,
        "nonce": nonce,
        "iat": now,
        "exp": now + 120,
    }

    if include_sid:
        claims["sid"] = sid

    signed_token = jwt.encode(
        {"alg": "RS256", "kid": "a14-probe"},
        claims,
        key,
        algorithms=["RS256"],
    )

    token_response = {
        "access_token": "synthetic-a14-access",
        "token_type": "Bearer",
        "id_token": signed_token,
    }

    try:
        # Gia lap du lieu tu Keycloak.
        # Authlib van tu kiem chu ky, nonce va cac claim.
        with (
            patch.object(
                oauth.keycloak,
                "load_server_metadata",
                return_value=metadata,
            ),
            patch.object(
                oauth.keycloak,
                "fetch_jwk_set",
                return_value=jwks,
            ),
            patch.object(
                oauth.keycloak,
                "fetch_access_token",
                return_value=token_response,
            ) as exchange,
        ):
            response = browser.get(
                "/auth/callback/",
                {"state": state, "code": "synthetic-a14-code"},
                secure=True,
            )

        exchange.assert_called_once()
        assert exchange.call_args.kwargs["code_verifier"] == verifier

    finally:
        cookie = browser.cookies.get(settings.SESSION_COOKIE_NAME)
        if cookie is not None:
            session_keys.add(cookie.value)

    current_key = browser.cookies[settings.SESSION_COOKIE_NAME].value

    assert SessionStore(
        session_key=pending.session_key,
    ).get(f"_state_keycloak_{state}") is None

    return response, current_key


project_root = Path(settings.BASE_DIR).parents[1]
source_hash = hashlib.sha256()

for relative_path in (
    "apps/lab/authn/models.py",
    "apps/lab/authn/services.py",
    "apps/lab/authn/permissions.py",
    "apps/lab/authn/transactions.py",
    "apps/lab/authn/views.py",
    "apps/lab/config/oidc.py",
    "tmp/check_a14.py",
):
    source_hash.update(relative_path.encode("utf-8"))
    source_hash.update((project_root / relative_path).read_bytes())

print(f"Python={sys.version.split()[0]} Django={django.get_version()}")
print(f"Database={connection.vendor}")
print(f"Source bundle SHA256={source_hash.hexdigest()}")
print(f"A14 started_at={timezone.now().isoformat()}")
print("Scope: callback, real JWT validation, database, /private/")


try:
    with transaction.atomic():
        user = User.objects.create_user(
            username=prefix,
            password=None,
        )
        ExternalIdentity.objects.create(
            issuer=issuer,
            subject=subject,
            user=user,
        )

    with override_settings(DEBUG=False):
        for label, include_sid, sid in (
            ("D-MISSING", False, None),
            ("D-EMPTY", True, ""),
        ):
            before = state_counts()

            response, candidate_key = run_callback(
                label,
                include_sid,
                sid,
            )

            assert response.status_code == 400, label
            assert state_counts() == before, label

            assert not OIDCSessionGroup.objects.filter(
                issuer=issuer,
                subject=subject,
            ).exists()
            assert not SessionBinding.objects.filter(user=user).exists()
            assert not backend_user(candidate_key).is_authenticated

            protected = private_response(candidate_key)
            assert protected.status_code == 403, label
            assert not protected.wsgi_request.user.is_authenticated

            rejected_keys.append(candidate_key)

            print(
                f"{label} callback expected=400 observed=400; "
                "new groups=0; new bindings=0; "
                "backend=ANONYMOUS; private=403"
            )

        # Token hop le lam doi chung cho cung bo kiem thu.
        before = state_counts()
        valid_sid = f"{prefix}-valid"

        response, valid_key = run_callback(
            "VALID-CONTROL",
            True,
            valid_sid,
        )

        assert response.status_code == 302
        assert response.headers["Location"] == "/private/"
        assert state_counts() == (
            before[0] + 1,
            before[1] + 1,
            before[2],
        )

        binding = SessionBinding.objects.select_related("group").get(
            user=user,
        )
        assert binding.session_key == valid_key
        assert binding.group.issuer == issuer
        assert binding.group.client_id == client_id
        assert binding.group.subject == subject
        assert binding.group.sid == valid_sid
        assert backend_user(valid_key).pk == user.pk

        protected = private_response(valid_key)
        assert protected.status_code == 200
        assert protected.wsgi_request.user.pk == user.pk

        print("VALID-CONTROL callback=302; backend=AUTHENTICATED; private=200")

        for rejected_key in rejected_keys:
            assert not backend_user(rejected_key).is_authenticated
            assert private_response(rejected_key).status_code == 403

        print("Both rejected sessions remain denied after valid login: OK")

finally:
    with transaction.atomic():
        probe_bindings = SessionBinding.objects.filter(
            user__username=prefix,
        )
        session_keys.update(
            probe_bindings.values_list("session_key", flat=True)
        )

        Session.objects.filter(session_key__in=session_keys).delete()
        probe_bindings.delete()
        OIDCSessionGroup.objects.filter(
            issuer=issuer,
            subject=subject,
        ).delete()
        SIDRevocationMarker.objects.filter(
            issuer=issuer,
            client_id=client_id,
            sid__startswith=prefix,
        ).delete()
        User.objects.filter(username=prefix).delete()

    assert not Session.objects.filter(
        session_key__in=session_keys,
    ).exists()
    assert not OIDCSessionGroup.objects.filter(
        issuer=issuer,
        subject=subject,
    ).exists()
    assert not User.objects.filter(username=prefix).exists()
    assert not ExternalIdentity.objects.filter(
        issuer=issuer,
        subject=subject,
    ).exists()
    assert not SIDRevocationMarker.objects.filter(
        issuer=issuer,
        client_id=client_id,
        sid__startswith=prefix,
    ).exists()

    print("A14: probe data cleaned")

print("A14: PASS")