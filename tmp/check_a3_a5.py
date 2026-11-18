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
from authn.services import create_verified_session, revoke_verified_sid


assert connection.vendor == "postgresql"
assert connection.get_autocommit()
assert not connection.in_atomic_block

User = get_user_model()
CLIENT_ID = "app-lab"
ISSUER_A = "https://auth.readiness.test:9443/realms/issuer-a"
ISSUER_B = "https://auth.readiness.test:9443/realms/issuer-b"


def make_request(session_key=None):
    request = RequestFactory().get("/")
    request.session = SessionStore(session_key=session_key)
    request.user = AnonymousUser()
    return request


def check_session(binding, expected_user_id, expected_status):
    # Doc lai session backend bang key da luu trong binding.
    backend_user = get_user(make_request(binding.session_key))

    if expected_user_id is None:
        assert not backend_user.is_authenticated
    else:
        assert backend_user.is_authenticated
        assert backend_user.pk == expected_user_id

    # Kiem quyen theo dung issuer/client cua phien doi chung.
    with override_settings(
        OIDC_ISSUER=binding.group.issuer,
        OIDC_CLIENT_ID=binding.group.client_id,
        DEBUG=False,
    ):
        browser = Client(HTTP_HOST="app.readiness.test")
        browser.cookies[
            settings.SESSION_COOKIE_NAME
        ] = binding.session_key

        response = browser.get("/private/", secure=True)

    assert response.status_code == expected_status, (
        f"Expected HTTP {expected_status}, "
        f"got {response.status_code}"
    )

    if expected_user_id is not None:
        assert response.wsgi_request.user.pk == expected_user_id
        assert "no-store" in response.headers["Cache-Control"]


def run_case(case_id):
    prefix = f"probe-{case_id.lower()}-{uuid4().hex}"
    session_keys = []

    sid_1 = f"{prefix}-s01"
    sid_2 = f"{prefix}-s02"
    sid_3 = f"{prefix}-s03"
    subject_1 = f"{prefix}-sub-a-u1"
    subject_2 = f"{prefix}-sub-a-u2"
    subject_b = f"{prefix}-sub-b-u2"

    print(f"\n{case_id} started_at={timezone.now().isoformat()}")

    try:
        # Giao dich tao fixture se COMMIT truoc khi thu hoi.
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

            bindings = {}

            for ref, issuer, sid, subject, user in specifications:
                with override_settings(
                    OIDC_ISSUER=issuer,
                    OIDC_CLIENT_ID=CLIENT_ID,
                ):
                    binding = create_verified_session(
                        make_request(),
                        issuer=issuer,
                        client_id=CLIENT_ID,
                        sid=sid,
                        subject=subject,
                    )

                session_keys.append(binding.session_key)
                assert binding.user_id == user.pk
                bindings[ref] = binding

        assert not connection.in_atomic_block

        group_ids = {item.group_id for item in bindings.values()}
        binding_ids = [item.pk for item in bindings.values()]

        assert len(group_ids) == 4
        assert len(set(session_keys)) == 5
        assert bindings["D01"].group_id == bindings["D02"].group_id
        assert bindings["D01"].group.sid == bindings["D05"].group.sid
        assert bindings["D01"].group.issuer != bindings["D05"].group.issuer

        for binding in bindings.values():
            check_session(binding, binding.user_id, 200)

        print("Before revocation: all 5 sessions authenticated, HTTP 200")

        control_refs = ("D03", "D04", "D05")
        control_bindings = [bindings[ref] for ref in control_refs]
        control_group_ids = [item.group_id for item in control_bindings]
        control_binding_ids = [item.pk for item in control_bindings]
        control_keys = [item.session_key for item in control_bindings]

        def control_snapshot():
            return [
                list(
                    OIDCSessionGroup.objects.filter(
                        pk__in=control_group_ids,
                    ).order_by("pk").values()
                ),
                list(
                    SessionBinding.objects.filter(
                        pk__in=control_binding_ids,
                    ).order_by("pk").values()
                ),
                list(
                    Session.objects.filter(
                        session_key__in=control_keys,
                    ).order_by("session_key").values()
                ),
            ]

        before_controls = control_snapshot()

        # Day la giao dich thu hoi thuc, COMMIT khi ra khoi atomic.
        with transaction.atomic():
            result = revoke_verified_sid(
                issuer=ISSUER_A,
                client_id=CLIENT_ID,
                sid=sid_1,
                subject=subject_1,
            )

        assert not connection.in_atomic_block
        assert result == {
            "marker_created": True,
            "groups_revoked": 1,
            "bindings_revoked": 2,
            "sessions_deleted": 2,
        }

        print(f"Revocation COMMIT returned at {timezone.now().isoformat()}")

        # Doc lai DB sau COMMIT.
        stored_bindings = SessionBinding.objects.filter(
            pk__in=binding_ids,
        )
        stored_groups = OIDCSessionGroup.objects.filter(pk__in=group_ids)

        assert stored_bindings.count() == 5
        assert stored_bindings.filter(revoked_at__isnull=False).count() == 2
        assert stored_bindings.filter(revoked_at__isnull=True).count() == 3
        assert stored_groups.filter(revoked_at__isnull=False).count() == 1

        marker = SIDRevocationMarker.objects.get(
            issuer=ISSUER_A,
            client_id=CLIENT_ID,
            sid=sid_1,
        )
        target_group = OIDCSessionGroup.objects.get(
            pk=bindings["D01"].group_id,
        )
        assert target_group.revoked_at == marker.revoked_at

        for ref in ("D01", "D02"):
            binding = bindings[ref]
            binding.refresh_from_db()

            assert binding.revoked_at == marker.revoked_at
            assert not Session.objects.filter(
                session_key=binding.session_key,
            ).exists()

            check_session(binding, None, 403)
            print(
                f"{ref} expected=INVALIDATED/403 "
                "observed=INVALIDATED/403"
            )

        assert control_snapshot() == before_controls

        for ref in control_refs:
            binding = bindings[ref]
            binding.refresh_from_db()

            assert binding.revoked_at is None
            assert not SIDRevocationMarker.objects.filter(
                issuer=binding.group.issuer,
                client_id=binding.group.client_id,
                sid=binding.group.sid,
            ).exists()

            check_session(binding, binding.user_id, 200)
            print(
                f"{ref} expected=AUTHENTICATED/200 "
                "observed=AUTHENTICATED/200"
            )

        assert control_snapshot() == before_controls
        print(f"{case_id}: PASS")

    finally:
        # Chi don du lieu thu nghiem mang prefix rieng cua ca nay.
        with transaction.atomic():
            probe_groups = OIDCSessionGroup.objects.filter(
                issuer__in=[ISSUER_A, ISSUER_B],
                client_id=CLIENT_ID,
                sid__startswith=prefix,
            )

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

        print(f"{case_id}: probe data cleaned")


project_root = Path(settings.BASE_DIR).parents[1]
source_hash = hashlib.sha256()

for relative_path in (
    "apps/lab/authn/models.py",
    "apps/lab/authn/services.py",
    "apps/lab/authn/permissions.py",
    "apps/lab/authn/transactions.py",
    "apps/lab/authn/views.py",
    "tmp/check_a3_a5.py",
):
    source_hash.update(relative_path.encode("utf-8"))
    source_hash.update((project_root / relative_path).read_bytes())

print(f"Python={sys.version.split()[0]} Django={django.get_version()}")
print(f"Database={connection.vendor}")
print(f"Source bundle SHA256={source_hash.hexdigest()}")
print("Scope: verified-login service, PostgreSQL session backend, /private/")

for case_id in ("A3", "A4", "A5"):
    run_case(case_id)

print("\nAll A3/A4/A5 cases passed: OK")