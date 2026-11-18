import hashlib
import sys
from pathlib import Path
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

from authn.models import (
    ExternalIdentity,
    OIDCSessionGroup,
    SessionBinding,
    SIDRevocationMarker,
)
from authn.services import create_verified_session


assert connection.vendor == "postgresql"
assert connection.get_autocommit()
assert not connection.in_atomic_block

User = get_user_model()
CLIENT_ID = "app-lab"
ISSUER_A = "https://auth.readiness.test:9443/realms/issuer-a"
ISSUER_B = "https://auth.readiness.test:9443/realms/issuer-b"

prefix = f"probe-a11-{uuid4().hex}"
session_keys = []
bindings = {}


def make_request(session_key=None):
    request = RequestFactory().get("/")
    request.session = SessionStore(session_key=session_key)
    request.user = AnonymousUser()
    return request


def create_binding(issuer, sid, subject):
    with override_settings(
        OIDC_ISSUER=issuer,
        OIDC_CLIENT_ID=CLIENT_ID,
    ):
        return create_verified_session(
            make_request(),
            issuer=issuer,
            client_id=CLIENT_ID,
            sid=sid,
            subject=subject,
        )


def check_access(ref, binding):
    backend_user = get_user(make_request(binding.session_key))
    assert backend_user.is_authenticated
    assert backend_user.pk == binding.user_id

    with override_settings(
        OIDC_ISSUER=binding.group.issuer,
        OIDC_CLIENT_ID=CLIENT_ID,
        DEBUG=False,
    ):
        browser = Client(HTTP_HOST="app.readiness.test")
        browser.cookies[settings.SESSION_COOKIE_NAME] = binding.session_key
        response = browser.get("/private/", secure=True)

    assert response.status_code == 200, ref
    assert response.wsgi_request.user.pk == binding.user_id, ref
    assert "no-store" in response.headers["Cache-Control"], ref

    print(f"{ref} expected=AUTHENTICATED/200 observed=AUTHENTICATED/200")


project_root = Path(settings.BASE_DIR).parents[1]
source_hash = hashlib.sha256()

for relative_path in (
    "apps/lab/authn/models.py",
    "apps/lab/authn/services.py",
    "apps/lab/authn/permissions.py",
    "apps/lab/authn/transactions.py",
    "apps/lab/authn/views.py",
    "tmp/check_a11.py",
):
    source_hash.update(relative_path.encode("utf-8"))
    source_hash.update((project_root / relative_path).read_bytes())

print(f"Python={sys.version.split()[0]} Django={django.get_version()}")
print(f"Database={connection.vendor}")
print(f"Source bundle SHA256={source_hash.hexdigest()}")
print(f"A11 started_at={timezone.now().isoformat()}")

sid_1 = f"{prefix}-s01"
sid_2 = f"{prefix}-s02"
sid_3 = f"{prefix}-s03"

subject_1 = f"{prefix}-sub-a-u1"
subject_2 = f"{prefix}-sub-a-u2"
subject_b = f"{prefix}-sub-b-u2"

probe_groups = OIDCSessionGroup.objects.filter(
    issuer__in=[ISSUER_A, ISSUER_B],
    client_id=CLIENT_ID,
    sid__startswith=prefix,
)

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
            (ISSUER_A, subject_1, user_1),
            (ISSUER_A, subject_2, user_2),
            (ISSUER_B, subject_b, user_2),
        ):
            ExternalIdentity.objects.create(
                issuer=issuer,
                subject=subject,
                user=user,
            )

        specifications = [
            ("D01", ISSUER_A, sid_1, subject_1, user_1),
            ("D02", ISSUER_A, sid_1, subject_1, user_1),
            ("D03", ISSUER_A, sid_2, subject_1, user_1),
            ("D04", ISSUER_A, sid_3, subject_2, user_2),
            ("D05", ISSUER_B, sid_1, subject_b, user_2),
        ]

        for ref, issuer, sid, subject, user in specifications:
            binding = create_binding(issuer, sid, subject)
            session_keys.append(binding.session_key)
            assert binding.user_id == user.pk
            bindings[ref] = binding

    assert not connection.in_atomic_block
    assert probe_groups.count() == 4
    assert len(set(session_keys)) == 5

    target_group_id = bindings["D01"].group_id
    assert bindings["D02"].group_id == target_group_id

    target_scope = {
        "issuer": ISSUER_A,
        "client_id": CLIENT_ID,
        "sid": sid_1,
    }

    assert OIDCSessionGroup.objects.filter(**target_scope).count() == 1
    assert SessionBinding.objects.filter(
        group_id=target_group_id,
        revoked_at__isnull=True,
    ).count() == 2

    for ref, binding in bindings.items():
        check_access(ref, binding)

    print("Before new login: G01 has 2 active bindings")

    original_binding_ids = [item.pk for item in bindings.values()]
    original_keys = session_keys.copy()

    def original_snapshot():
        return [
            list(probe_groups.order_by("pk").values()),
            list(
                SessionBinding.objects.filter(
                    pk__in=original_binding_ids,
                ).order_by("pk").values()
            ),
            list(
                Session.objects.filter(
                    session_key__in=original_keys,
                ).order_by("session_key").values()
            ),
            list(
                SIDRevocationMarker.objects.filter(
                    issuer__in=[ISSUER_A, ISSUER_B],
                    client_id=CLIENT_ID,
                    sid__startswith=prefix,
                ).order_by("pk").values()
            ),
        ]

    before = original_snapshot()

    # Request moi co SessionStore rieng, mo phong trinh duyet doc lap.
    with transaction.atomic():
        new_binding = create_binding(
            ISSUER_A,
            sid_1,
            subject_1,
        )
        session_keys.append(new_binding.session_key)

    assert not connection.in_atomic_block
    print(f"New login COMMIT returned at {timezone.now().isoformat()}")

    # Doc lai DB sau COMMIT.
    new_binding.refresh_from_db()
    target_group = OIDCSessionGroup.objects.get(pk=target_group_id)
    stored_session = Session.objects.get(
        session_key=new_binding.session_key,
    )

    assert new_binding.group_id == target_group_id
    assert new_binding.user_id == user_1.pk
    assert new_binding.revoked_at is None
    assert new_binding.expires_at == stored_session.expire_date
    assert stored_session.expire_date > timezone.now()
    assert new_binding.session_key not in original_keys

    assert target_group.subject == subject_1
    assert target_group.revoked_at is None
    assert OIDCSessionGroup.objects.filter(**target_scope).count() == 1
    assert probe_groups.count() == 4

    target_bindings = SessionBinding.objects.filter(
        group_id=target_group_id,
    )
    assert target_bindings.count() == 3
    assert target_bindings.filter(revoked_at__isnull=True).count() == 3
    assert target_bindings.values("session_key").distinct().count() == 3

    assert SessionBinding.objects.filter(
        group__in=probe_groups,
    ).count() == 6
    assert len(set(session_keys)) == 6
    assert original_snapshot() == before

    print("Target group count expected=1 observed=1")
    print("Active bindings in G01 expected=3 observed=3")
    print("New binding uses the existing group and correct user: OK")
    print("Original 5 bindings and backend sessions preserved: OK")

    for ref, binding in bindings.items():
        binding.refresh_from_db()
        assert binding.revoked_at is None
        check_access(ref, binding)

    check_access("D-NEW", new_binding)
    assert original_snapshot() == before

finally:
    with transaction.atomic():
        Session.objects.filter(session_key__in=session_keys).delete()
        SessionBinding.objects.filter(group__in=probe_groups).delete()
        probe_groups.delete()

        SIDRevocationMarker.objects.filter(
            issuer__in=[ISSUER_A, ISSUER_B],
            client_id=CLIENT_ID,
            sid__startswith=prefix,
        ).delete()

        User.objects.filter(
            username__in=[f"{prefix}-u1", f"{prefix}-u2"],
        ).delete()

    assert not Session.objects.filter(
        session_key__in=session_keys,
    ).exists()
    assert not OIDCSessionGroup.objects.filter(
        sid__startswith=prefix,
    ).exists()
    assert not SIDRevocationMarker.objects.filter(
        sid__startswith=prefix,
    ).exists()
    assert not User.objects.filter(
        username__in=[f"{prefix}-u1", f"{prefix}-u2"],
    ).exists()
    assert not ExternalIdentity.objects.filter(
        subject__in=[subject_1, subject_2, subject_b],
    ).exists()

    print("A11: probe data cleaned")

print("A11: PASS")