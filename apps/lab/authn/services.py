from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied
from .models import (
    ExternalIdentity,
    OIDCSessionGroup,
    SessionBinding,
    SIDRevocationMarker,
)
from .transactions import oidc_session_transaction


from datetime import timedelta

from django.contrib.auth import login
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone

#LogoutReceipt
from .models import (
    ExternalIdentity,
    OIDCSessionGroup,
    SessionBinding,
    SIDRevocationMarker,
    LogoutReceipt,
)

def resolve_verified_user(*, issuer, subject):
    """Tìm user nội bộ sau khi kết quả OIDC đã được xác minh."""
    if issuer != settings.OIDC_ISSUER:
        raise PermissionDenied("Issuer khong duoc chap nhan.")

    if (
        not isinstance(subject, str)
        or not subject.strip()
        or len(subject) > 255
    ):
        raise PermissionDenied("Subject khong hop le.")

    try:
        identity = ExternalIdentity.objects.select_related("user").get(
            issuer=issuer,
            subject=subject,
        )
    except ExternalIdentity.DoesNotExist:
        raise PermissionDenied("Danh tinh chua duoc lien ket.") from None

    if not identity.user.is_active:
        raise PermissionDenied("Tai khoan noi bo da bi vo hieu hoa.")

    return identity.user

# Hàm dùng chung khóa giao dịch với Hàm thu hồi SID
def create_verified_session(
    request, *, issuer, client_id, sid, subject,
):
    """Tạo phiên app từ kết quả OIDC đã được xác minh."""
    if (
        issuer != settings.OIDC_ISSUER
        or client_id != settings.OIDC_CLIENT_ID
    ):
        raise PermissionDenied("Issuer hoac client khong duoc chap nhan.")

    if (
        not isinstance(sid, str)
        or not sid.strip()
        or len(sid) > 255
    ):
        raise PermissionDenied("SID khong hop le.")

    session_age = settings.OIDC_APP_SESSION_AGE
    if type(session_age) is not int or session_age <= 0:
        raise ValueError("OIDC_APP_SESSION_AGE phai la so nguyen duong.")

    scope = {
        "issuer": issuer,
        "client_id": client_id,
        "sid": sid,
    }

    previous_session = request.session
    previous_user = getattr(request, "user", AnonymousUser())

    try:
        with oidc_session_transaction(issuer, client_id):
            user = resolve_verified_user(
                issuer=issuer,
                subject=subject,
            )

            if SIDRevocationMarker.objects.filter(**scope).exists():
                raise PermissionDenied("SID da bi thu hoi.")

            group, _ = OIDCSessionGroup.objects.get_or_create(
                **scope,
                defaults={"subject": subject},
            )

            if group.subject != subject:
                raise PermissionDenied("Subject khong khop chu nhom phien.")

            if group.revoked_at is not None:
                raise PermissionDenied("Nhom phien da bi thu hoi.")

            now = timezone.now()
            expires_at = now + timedelta(seconds=session_age)

            request.session = SessionStore()
            request.session.set_expiry(expires_at)

            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            request.session.save()

            stored_session = Session.objects.get(
                session_key=request.session.session_key,
            )

            binding = SessionBinding.objects.create(
                group=group,
                user=user,
                session_key=stored_session.session_key,
                expires_at=stored_session.expire_date,
            )

            previous_key = previous_session.session_key
            if previous_key and previous_key != stored_session.session_key:
                SessionBinding.objects.filter(
                    session_key=previous_key,
                    group__issuer=issuer,
                    group__client_id=client_id,
                    revoked_at__isnull=True,
                ).update(revoked_at=now)

                Session.objects.filter(
                    session_key=previous_key,
                ).delete()

    except Exception:
        request.session = previous_session
        request.user = previous_user
        raise

    return binding

def revoke_verified_sid(*, issuer, client_id, sid, subject=None):
    """Thu hồi SID từ ngữ cảnh đã được lớp OIDC xác minh."""
    for value in (issuer, client_id, sid):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Issuer, client_id va sid phai co gia tri.")

    if subject is not None:
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("Subject duoc cung cap phai co gia tri.")

    scope = {
        "issuer": issuer,
        "client_id": client_id,
        "sid": sid,
    }

    with oidc_session_transaction(issuer, client_id):
        groups = OIDCSessionGroup.objects.filter(**scope)

        if subject is not None:
            if groups.exclude(subject=subject).exists():
                raise PermissionDenied("Subject khong khop chu nhom phien.")

        marker, marker_created = SIDRevocationMarker.objects.get_or_create(
            **scope,
        )

        groups_revoked = groups.filter(
            revoked_at__isnull=True,
        ).update(revoked_at=marker.revoked_at)

        bindings = SessionBinding.objects.filter(group__in=groups)

        bindings_revoked = bindings.filter(
            revoked_at__isnull=True,
        ).update(revoked_at=marker.revoked_at)

        sessions_deleted, _ = Session.objects.filter(
            session_key__in=bindings.values_list("session_key", flat=True),
        ).delete()

        return {
            "marker_created": marker_created,
            "groups_revoked": groups_revoked,
            "bindings_revoked": bindings_revoked,
            "sessions_deleted": sessions_deleted,
        }

#Hàm nhận dữ liệu sau khi Logout token được xác minh, ghi nhận thông báo rồi gọi lại hàm SID
def process_verified_sid_logout(
    *, issuer, client_id, jti, sid, subject=None,
):
    """Xu ly thong bao logout theo SID sau khi token da duoc xac minh."""
    if (
        issuer != settings.OIDC_ISSUER
        or client_id != settings.OIDC_CLIENT_ID
    ):
        raise PermissionDenied(
            "Issuer hoac client khong duoc chap nhan."
        )

    for value in (jti, sid):
        if (
            not isinstance(value, str)
            or not value.strip()
            or len(value) > 255
        ):
            raise PermissionDenied("JTI hoac SID khong hop le.")

    if subject is not None:
        if (
            not isinstance(subject, str)
            or not subject.strip()
            or len(subject) > 255
        ):
            raise PermissionDenied("Subject khong hop le.")

    with oidc_session_transaction(issuer, client_id):
        receipt, _ = LogoutReceipt.objects.get_or_create(
            issuer=issuer,
            client_id=client_id,
            jti=jti,
        )

        if receipt.processed_at is not None:
            return {
                "duplicate": True,
                "revocation": None,
            }

        result = revoke_verified_sid(
            issuer=issuer,
            client_id=client_id,
            sid=sid,
            subject=subject,
        )

        receipt.processed_at = timezone.now()
        receipt.save(update_fields=["processed_at"])

        return {
            "duplicate": False,
            "revocation": result,
        }