import hashlib
import sys
import time
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import django
from django.conf import settings
from django.contrib.auth import get_user, get_user_model
from django.contrib.auth.models import AnonymousUser
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
from authn.services import create_verified_session
from config.oidc import oauth


assert connection.vendor == "postgresql"
assert connection.get_autocommit()
assert not connection.in_atomic_block

User = get_user_model()
prefix = f"probe-a15-{uuid4().hex}"
issuer_a = settings.OIDC_ISSUER
issuer_b = "https://auth.readiness.test:9443/realms/issuer-b"
client_id = settings.OIDC_CLIENT_ID
subject_1 = f"{prefix}-sub-a-u1"
subject_2 = f"{prefix}-sub-a-u2"
subject_b = f"{prefix}-sub-b-u2"
sid_1 = f"{prefix}-s01"
session_keys = set()
bindings = {}

probe_groups = OIDCSessionGroup.objects.filter(
    issuer__in=[issuer_a, issuer_b],
    client_id=client_id,
    sid__startswith=prefix,
)


def make_request(session_key=None):
    request = RequestFactory().get("/")
    request.session = SessionStore(session_key=session_key)
    request.user = AnonymousUser()
    return request


def check_access(ref, binding):
    assert get_user(make_request(binding.session_key)).pk == binding.user_id

    with override_settings(
        OIDC_ISSUER=binding.group.issuer,
        OIDC_CLIENT_ID=client_id,
        DEBUG=False,
    ):
        browser = Client(HTTP_HOST="app.readiness.test")
        browser.cookies[settings.SESSION_COOKIE_NAME] = binding.session_key
        response = browser.get("/private/", secure=True)

    assert response.status_code == 200, ref
    assert response.wsgi_request.user.pk == binding.user_id, ref
    print(f"{ref} backend user matches; private expected=200 observed=200")


project_root = Path(settings.BASE_DIR).parents[1]
source_hash = hashlib.sha256()

for relative_path in (
    "apps/lab/authn/models.py",
    "apps/lab/authn/services.py",
    "apps/lab/authn/permissions.py",
    "apps/lab/authn/transactions.py",
    "apps/lab/authn/views.py",
    "apps/lab/config/oidc.py",
    "tmp/check_a15.py",
):
    source_hash.update(relative_path.encode("utf-8"))
    source_hash.update((project_root / relative_path).read_bytes())

print(f"Python={sys.version.split()[0]} Django={django.get_version()}")
print(f"Database={connection.vendor}")
print(f"Source bundle SHA256={source_hash.hexdigest()}")
print(f"A15 started_at={timezone.now().isoformat()}")
print("Scope: signed callback, SID ownership, PostgreSQL, /private/")

try:
    # Tao va COMMIT bo 5 phien ban dau.
    with transaction.atomic():
        user_1 = User.objects.create_user(
            username=f"{prefix}-u1",
            password=None,
        )
        user_2 = User.objects.create_user(
            username=f"{prefix}-u2",
            password=None,
        )

        for issuer, subject, user in (
            (issuer_a, subject_1, user_1),
            (issuer_a, subject_2, user_2),
            (issuer_b, subject_b, user_2),
        ):
            ExternalIdentity.objects.create(
                issuer=issuer,
                subject=subject,
                user=user,
            )

        specifications = [
            ("D01", issuer_a, sid_1, subject_1, user_1),
            ("D02", issuer_a, sid_1, subject_1, user_1),
            ("D03", issuer_a, f"{prefix}-s02", subject_1, user_1),
            ("D04", issuer_a, f"{prefix}-s03", subject_2, user_2),
            ("D05", issuer_b, sid_1, subject_b, user_2),
        ]

        for ref, issuer, sid, subject, user in specifications:
            with override_settings(
                OIDC_ISSUER=issuer,
                OIDC_CLIENT_ID=client_id,
            ):
                binding = create_verified_session(
                    make_request(),
                    issuer=issuer,
                    client_id=client_id,
                    sid=sid,
                    subject=subject,
                )

            session_keys.add(binding.session_key)
            assert binding.user_id == user.pk
            bindings[ref] = binding

    assert probe_groups.count() == 4
    assert len(session_keys) == 5
    assert bindings["D01"].group_id == bindings["D02"].group_id

    for ref, binding in bindings.items():
        check_access(ref, binding)

    original_keys = list(session_keys)

    def snapshot():
        return [
            list(probe_groups.order_by("pk").values()),
            list(
                SessionBinding.objects.filter(
                    group__in=probe_groups,
                ).order_by("pk").values()
            ),
            list(
                Session.objects.filter(
                    session_key__in=original_keys,
                ).order_by("session_key").values()
            ),
            list(
                SIDRevocationMarker.objects.filter(
                    issuer__in=[issuer_a, issuer_b],
                    client_id=client_id,
                    sid__startswith=prefix,
                ).order_by("pk").values()
            ),
        ]

    before = snapshot()

    # Tao phien anonymous cho callback cua U2.
    candidate = Client(HTTP_HOST="app.readiness.test")
    state = f"{prefix}-state"
    nonce = uuid4().hex
    verifier = uuid4().hex + uuid4().hex

    pending = candidate.session
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

    # Token hop le ve chu ky, mang sub U2 va SID da thuoc U1.
    key = RSAKey.generate_key(
        2048,
        parameters={"kid": "a15-probe"},
    )
    now = int(time.time())
    claims = {
        "iss": issuer_a,
        "aud": client_id,
        "sub": subject_2,
        "sid": sid_1,
        "nonce": nonce,
        "iat": now,
        "exp": now + 120,
    }
    token = {
        "access_token": "synthetic-a15-access",
        "token_type": "Bearer",
        "id_token": jwt.encode(
            {"alg": "RS256", "kid": "a15-probe"},
            claims,
            key,
            algorithms=["RS256"],
        ),
    }

    try:
        with (
            override_settings(DEBUG=False),
            patch.object(
                oauth.keycloak,
                "load_server_metadata",
                return_value={
                    "issuer": issuer_a,
                    "id_token_signing_alg_values_supported": ["RS256"],
                },
            ),
            patch.object(
                oauth.keycloak,
                "fetch_jwk_set",
                return_value={"keys": [key.as_dict(private=False)]},
            ),
            patch.object(
                oauth.keycloak,
                "fetch_access_token",
                return_value=token,
            ) as exchange,
            patch(
                "authn.views.create_verified_session",
                wraps=create_verified_session,
            ) as session_service,
        ):
            response = candidate.get(
                "/auth/callback/",
                {"state": state, "code": "synthetic-a15-code"},
                secure=True,
            )

        exchange.assert_called_once()
        assert exchange.call_args.kwargs["code_verifier"] == verifier

        # Xac nhan JWT da qua xac minh va toi service that.
        session_service.assert_called_once()
        assert session_service.call_args.kwargs["subject"] == subject_2
        assert session_service.call_args.kwargs["sid"] == sid_1

    finally:
        cookie = candidate.cookies.get(settings.SESSION_COOKIE_NAME)
        if cookie is not None:
            session_keys.add(cookie.value)

    assert response.status_code == 403
    assert not connection.in_atomic_block
    assert snapshot() == before
    assert not SessionBinding.objects.filter(
        session_key__in=session_keys - set(original_keys),
    ).exists()

    group = OIDCSessionGroup.objects.get(
        pk=bindings["D01"].group_id,
    )
    assert group.subject == subject_1
    assert group.revoked_at is None

    print("U2 claims passed JWT validation and reached the session service: OK")
    print("Conflicting SID callback expected=403 observed=403")
    print("Groups, bindings, markers and original backend sessions preserved: OK")
    print("G01 still belongs to U1: OK")

    candidate_key = candidate.cookies[settings.SESSION_COOKIE_NAME].value
    assert not get_user(make_request(candidate_key)).is_authenticated
    assert SessionStore(session_key=pending.session_key).get(
        f"_state_keycloak_{state}",
    ) is None

    with override_settings(DEBUG=False):
        protected = candidate.get("/private/", secure=True)

    assert protected.status_code == 403
    assert not protected.wsgi_request.user.is_authenticated
    print("D-CANDIDATE backend=ANONYMOUS; private=403")

    for ref, binding in bindings.items():
        check_access(ref, binding)

    assert snapshot() == before

finally:
    with transaction.atomic():
        probe_bindings = SessionBinding.objects.filter(
            user__username__in=[f"{prefix}-u1", f"{prefix}-u2"],
        )
        session_keys.update(
            probe_bindings.values_list("session_key", flat=True)
        )

        Session.objects.filter(session_key__in=session_keys).delete()
        probe_bindings.delete()
        probe_groups.delete()

        SIDRevocationMarker.objects.filter(
            issuer__in=[issuer_a, issuer_b],
            client_id=client_id,
            sid__startswith=prefix,
        ).delete()
        User.objects.filter(
            username__in=[f"{prefix}-u1", f"{prefix}-u2"],
        ).delete()

    assert not Session.objects.filter(
        session_key__in=session_keys,
    ).exists()
    assert not probe_groups.exists()
    assert not User.objects.filter(
        username__in=[f"{prefix}-u1", f"{prefix}-u2"],
    ).exists()
    assert not ExternalIdentity.objects.filter(
        subject__in=[subject_1, subject_2, subject_b],
    ).exists()
    assert not SIDRevocationMarker.objects.filter(
        issuer__in=[issuer_a, issuer_b],
        client_id=client_id,
        sid__startswith=prefix,
    ).exists()

    print("A15: probe data cleaned")

print("A15: PASS")