from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError
from django.utils import timezone

from .models import SessionBinding, SIDRevocationMarker
from .services import resolve_verified_user
from .transactions import oidc_session_transaction


def require_active_binding(request):
    """Chỉ chấp nhận phiên app có binding và danh tính hợp lệ."""
    issuer = settings.OIDC_ISSUER
    client_id = settings.OIDC_CLIENT_ID

    try:
        with oidc_session_transaction(issuer, client_id):
            if not request.user.is_authenticated:
                raise PermissionDenied("Can dang nhap.")

            session_key = request.session.session_key
            if not session_key:
                raise PermissionDenied("Phien khong hop le.")

            binding = SessionBinding.objects.select_related(
                "group", "user",
            ).get(session_key=session_key)

            group = binding.group
            now = timezone.now()

            if (
                group.issuer != issuer
                or group.client_id != client_id
                or not group.sid.strip()
                or group.revoked_at is not None
                or binding.revoked_at is not None
                or binding.expires_at <= now
            ):
                raise PermissionDenied("Phien khong con hieu luc.")

            user = resolve_verified_user(
                issuer=group.issuer,
                subject=group.subject,
            )

            if (
                binding.user_id != user.pk
                or request.user.pk != user.pk
            ):
                raise PermissionDenied("Danh tinh phien khong khop.")

            if not Session.objects.filter(
                session_key=session_key,
                expire_date=binding.expires_at,
                expire_date__gt=now,
            ).exists():
                raise PermissionDenied("Phien backend khong hop le.")

            if SIDRevocationMarker.objects.filter(
                issuer=issuer,
                client_id=client_id,
                sid=group.sid,
            ).exists():
                raise PermissionDenied("SID da bi thu hoi.")

            return binding

    except SessionBinding.DoesNotExist:
        raise PermissionDenied("Phien chua co binding.") from None
    except DatabaseError:
        raise PermissionDenied(
            "Khong the xac minh trang thai phien.",
        ) from None