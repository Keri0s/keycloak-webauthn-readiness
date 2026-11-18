
# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone

class ExternalIdentity(models.Model):
    issuer = models.URLField(max_length=512)
    subject = models.CharField(max_length=255)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="external_identities",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["issuer", "subject"],
                name="uq_external_identity_issuer_subject",
            ),
        ]

class OIDCSessionGroup(models.Model):
    issuer = models.URLField(max_length=512)
    client_id = models.CharField(max_length=255)
    sid = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["issuer", "client_id", "sid"],
                name="uq_oidc_group_issuer_client_sid",
            ),
            models.CheckConstraint(
                condition=~models.Q(sid=""),
                name="oidc_group_sid_not_empty",
            ),
        ]

class SessionBinding(models.Model):
    group = models.ForeignKey(
        OIDCSessionGroup,
        on_delete=models.PROTECT,
        related_name="bindings",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="session_bindings",
    )

    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(session_key=""),
                name="session_binding_key_not_empty",
            ),
        ]


class SIDRevocationMarker(models.Model):
    issuer = models.URLField(max_length=512)
    client_id = models.CharField(max_length=255)
    sid = models.CharField(max_length=255)

    revoked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["issuer", "client_id", "sid"],
                name="uq_sid_marker_issuer_client_sid",
            ),
            models.CheckConstraint(
                condition=~models.Q(sid=""),
                name="sid_marker_sid_not_empty",
            ),
        ]

#Hàm để ghi nhận một thông báo logout đã được xử lý ()
class LogoutReceipt(models.Model):                                    
    issuer = models.URLField(max_length=512)
    client_id = models.CharField(max_length=255)
    jti = models.CharField(max_length=255)                          #Mã định danh thông báo trong token (Unique)

    received_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["issuer", "client_id", "jti"],
                name="uq_logout_receipt_issuer_client_jti",
            ),
            models.CheckConstraint(
                condition=~models.Q(jti=""),
                name="logout_receipt_jti_not_empty",
            ),
        ]