import hashlib
import sys
import time
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlencode
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

from authn.backchannel import LOGOUT_EVENT
from authn.models import (
    ExternalIdentity,
    LogoutReceipt,
    OIDCSessionGroup,
    SessionBinding,
    SIDRevocationMarker,
)
from authn.services import (
    create_verified_session,
    process_verified_sid_logout,
)
from config.oidc import oauth


assert connection.vendor == "postgresql"
assert connection.get_autocommit()
assert not connection.in_atomic_block

User = get_user_model()
prefix = f"probe-a16-{uuid4().hex}"
issuer_a = settings.OIDC_ISSUER
issuer_b = "https://auth.readiness.test:9443/realms/issuer-b"
client_id = settings.OIDC_CLIENT_ID

subject_1 = f"{prefix}-sub-a-u1"
subject_2 = f"{prefix}-sub-a-u2"
subject_b = f"{prefix}-sub-b-u2"
sid_1 = f"{prefix}-s01"
jti = f"{prefix}-message"

session_keys = set()
bindings = {}

probe_groups = OIDCSessionGroup.objects.filter(
    issuer__in=[issuer_a, issuer_b],
    client_id=client_id,
    sid__startswith=prefix,
)
probe_markers = SIDRevocationMarker.objects.filter(
    issuer__in=[issuer_a, issuer_b],
    client_id=client_id,
    sid__startswith=prefix,
)
probe_receipts = LogoutReceipt.objects.filter(
    issuer=issuer_a,
    client_id=client_id,
    jti__startswith=prefix,
)


def make_request(session_key=None):
    request = RequestFactory().get("/")
    request.session = SessionStore(session_key=session_key)
    request.user = AnonymousUser()
    return request


def check_access(ref, binding):
    backend_user = get_user(make_request(binding.session_key))
    assert backend_user.is_authenticated, ref
    assert backend_user.pk == binding.user_id, ref

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
    "apps/lab/authn/backchannel.py",
    "apps/lab/config/oidc.py",
    "tmp/check_a16.py",
):
    source_hash.update(relative_path.encode("utf-8"))
    source_hash.update((project_root / relative_path).read_bytes())

print(f"Python={sys.version.split()[0]} Django={django.get_version()}")
print(f"Database={connection.vendor}")
print(f"Source bundle SHA256={source_hash.hexdigest()}")
print(f"A16 started_at={timezone.now().isoformat()}")
print("Scope: signed logout token, SID/sub ownership, database, /private/")


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

    assert not connection.in_atomic_block
    assert probe_groups.count() == 4
    assert len(session_keys) == 5
    assert bindings["D01"].group_id == bindings["D02"].group_id
    assert not probe_markers.exists()
    assert not probe_receipts.exists()

    for ref, binding in bindings.items():
        check_access(ref, binding)

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
                    session_key__in=session_keys,
                ).order_by("session_key").values()
            ),
            list(probe_markers.order_by("pk").values()),
            list(probe_receipts.order_by("pk").values()),
        ]

    before = snapshot()

    # Token co chu ky hop le, SID cua U1 va subject cua U2.
    key = RSAKey.generate_key(
        2048,
        parameters={"kid": "a16-probe"},
    )
    now = int(time.time())
    claims = {
        "iss": issuer_a,
        "aud": client_id,
        "sub": subject_2,
        "sid": sid_1,
        "iat": now,
        "exp": now + 120,
        "jti": jti,
        "events": {LOGOUT_EVENT: {}},
    }
    signed_token = jwt.encode(
        {"alg": "RS256", "kid": "a16-probe"},
        claims,
        key,
        algorithms=["RS256"],
    )

    sender = Client(
        enforce_csrf_checks=True,
        HTTP_HOST="app.readiness.test",
    )
    assert not sender.cookies

    with (
        override_settings(DEBUG=False),
        patch.object(
            oauth.keycloak,
            "fetch_jwk_set",
            return_value={"keys": [key.as_dict(private=False)]},
        ),
        patch(
            "authn.views.process_verified_sid_logout",
            wraps=process_verified_sid_logout,
        ) as processor,
    ):
        response = sender.post(
            "/auth/backchannel-logout/",
            data=urlencode({"logout_token": signed_token}),
            content_type="application/x-www-form-urlencoded",
            secure=True,
        )

    # Spy goi service that. Den day token da qua xac minh.
    processor.assert_called_once_with(
        issuer=issuer_a,
        client_id=client_id,
        sid=sid_1,
        subject=subject_2,
        jti=jti,
    )

    assert response.status_code == 400
    assert response.json() == {"error": "invalid_request"}
    assert not connection.in_atomic_block
    assert not sender.cookies
    assert snapshot() == before

    group = OIDCSessionGroup.objects.get(
        pk=bindings["D01"].group_id,
    )
    assert group.subject == subject_1
    assert group.revoked_at is None
    assert not probe_markers.exists()
    assert not probe_receipts.exists()

    print("Logout token passed JWT validation and reached real service: OK")
    print("Wrong subject logout expected=400 observed=400")
    print("Groups, bindings, markers and backend sessions preserved: OK")
    print("No logout receipt retained after rejection: OK")
    print("G01 still belongs to U1: OK")

    for ref, binding in bindings.items():
        binding.refresh_from_db()
        assert binding.revoked_at is None
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
        probe_markers.delete()
        probe_receipts.delete()

        User.objects.filter(
            username__in=[f"{prefix}-u1", f"{prefix}-u2"],
        ).delete()

    assert not Session.objects.filter(
        session_key__in=session_keys,
    ).exists()
    assert not probe_groups.exists()
    assert not probe_markers.exists()
    assert not probe_receipts.exists()
    assert not User.objects.filter(
        username__in=[f"{prefix}-u1", f"{prefix}-u2"],
    ).exists()
    assert not ExternalIdentity.objects.filter(
        subject__in=[subject_1, subject_2, subject_b],
    ).exists()

    print("A16: probe data cleaned")

print("A16: PASS")