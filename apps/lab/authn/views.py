from django.http import HttpResponse
from django.utils.html import format_html
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from .permissions import require_active_binding
from .diagnostics import record_callback_rejection
from .evidence import attach_binding_evidence

from authlib.common.errors import AuthlibBaseError
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from joserfc.errors import JoseError
from requests.exceptions import RequestException

from config.oidc import oauth
from .services import create_verified_session

#Point to private html (template)
import time

from django.contrib.auth import logout as django_logout
from django.db import DatabaseError
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from .services import revoke_verified_sid

#Ghep noi voi endpoint
from django.core.exceptions import TooManyFieldsSent
from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt

from .backchannel import verify_sid_logout_token
from .services import process_verified_sid_logout


def callback_failure(request, code, *, claim="-", status=400):
    reference = record_callback_rejection(code, claim)
    response = render(
        request,
        "authn/login_retry.html",
        {"expired": code == "expired_login_state", "reference": reference},
        status=status,
    )
    response["Referrer-Policy"] = "no-referrer"
    return response

@never_cache
@require_GET
def private_page(request):
    binding = require_active_binding(request)

    response = render(
        request,
        "authn/private.html",
        {"lab_user": binding.user},
    )
    return attach_binding_evidence(response, binding)

@never_cache
@require_GET
def oidc_login(request):
    try:
        return oauth.keycloak.authorize_redirect(
            request,
            redirect_uri=settings.OIDC_REDIRECT_URI,
        )
    except (AuthlibBaseError, RequestException):
        return HttpResponse("Không thể bắt đầu đăng nhập với Keycloak.", status=503)


@never_cache
@require_GET
def oidc_callback(request):
    if len(request.GET.getlist("state")) != 1:
        return callback_failure(request, "invalid_callback_parameters")

    if "error" not in request.GET and (
        len(request.GET.getlist("code")) != 1 or not request.GET.get("code")
    ):
        return callback_failure(request, "invalid_callback_parameters")

    try:
        token = oauth.keycloak.authorize_access_token(request)
        claims = token["userinfo"]

        create_verified_session(
            request,
            issuer=claims["iss"],
            client_id=settings.OIDC_CLIENT_ID,
            sid=claims["sid"],
            subject=claims["sub"],
        )
    except (AuthlibBaseError, JoseError) as exc:
        return callback_failure(
            request,
            getattr(exc, "error", ""),
            claim=getattr(exc, "claim", ""),
        )
    except RequestException:
        return callback_failure(request, "provider_unavailable", status=503)
    except PermissionDenied:
        return callback_failure(request, "session_not_allowed", status=403)

    return redirect("private")

@never_cache
@require_POST
@csrf_protect
def oidc_logout(request):
    binding = require_active_binding(request)
    group = binding.group

    try:
        revoke_verified_sid(
            issuer=group.issuer,
            client_id=group.client_id,
            sid=group.sid,
            subject=group.subject,
        )
    except DatabaseError:
        return HttpResponse(
            "Không thể xác nhận thu hồi phiên. Hãy thử lại.",
            status=503,
        )

    django_logout(request)
    request.session.set_expiry(300)

    try:
        return oauth.keycloak.logout_redirect(
            request,
            post_logout_redirect_uri=(
                settings.OIDC_POST_LOGOUT_REDIRECT_URI
            ),
            client_id=settings.OIDC_CLIENT_ID,
        )
    except (AuthlibBaseError, RequestException):
        return HttpResponse(
            "Phiên app đã được thu hồi, nhưng chưa kết nối được "
            "với Keycloak để kết thúc phiên SSO.",
            status=503,
        )

# Session phase on private web
@never_cache
@require_GET
def oidc_logged_out(request):
    states = request.GET.getlist("state")
    if len(states) != 1 or not states[0]:
        return HttpResponse("Giao dịch đăng xuất không hợp lệ.", status=400)

    state = states[0]
    state_key = f"_state_{oauth.keycloak.name}_{state}"
    entry = request.session.get(state_key)

    if not isinstance(entry, dict):
        return HttpResponse("Không tìm thấy giao dịch đăng xuất.", status=400)

    expires_at = entry.get("exp")
    if (
        not isinstance(expires_at, (int, float))
        or not 0 < expires_at - time.time() <= 300
    ):
        request.session.pop(state_key, None)
        return HttpResponse("Giao dịch đăng xuất đã hết hạn.", status=400)

    try:
        data = oauth.keycloak.validate_logout_response(request)
    except AuthlibBaseError:
        return HttpResponse("Không xác minh được giao dịch đăng xuất.", status=400)

    if data.get("post_logout_redirect_uri") != (
        settings.OIDC_POST_LOGOUT_REDIRECT_URI
    ):
        return HttpResponse("Giao dịch đăng xuất không hợp lệ.", status=400)

    request.session.flush()

    return HttpResponse(
        format_html(
            "<h1>Đã đăng xuất khỏi ứng dụng</h1>"
            '<a href="{}">Đăng nhập lại</a>',
            reverse("oidc_login"),
        ),
    )

# When logout and choose "back to application"
@never_cache
@require_GET
def home(request):
    return HttpResponse(
        format_html(
            "<h1>Readiness Lab</h1>"
            '<a href="{}">Đăng nhập</a>',
            reverse("oidc_login"),
        ),
    )

#Ghep noi voi endpoint
@csrf_exempt
@never_cache
@require_POST
def oidc_backchannel_logout(request):
    if request.content_type != "application/x-www-form-urlencoded":
        return JsonResponse(
            {"error": "invalid_request"},
            status=400,
        )

    try:
        body = request.read(65_537)

        if len(body) > 65_536:
            return JsonResponse(
                {"error": "invalid_request"},
                status=400,
            )

        form = QueryDict(
            body.decode("utf-8"),
            encoding="utf-8",
        )
    except (UnicodeDecodeError, TooManyFieldsSent):
        return JsonResponse(
            {"error": "invalid_request"},
            status=400,
        )

    tokens = form.getlist("logout_token")
    if len(tokens) != 1 or not tokens[0]:
        return JsonResponse(
            {"error": "invalid_request"},
            status=400,
        )

    try:
        verified = verify_sid_logout_token(tokens[0])
        process_verified_sid_logout(**verified)
    except (JoseError, AuthlibBaseError, PermissionDenied):
        return JsonResponse(
            {"error": "invalid_request"},
            status=400,
        )
    except (RequestException, DatabaseError):
        return JsonResponse(
            {"error": "temporarily_unavailable"},
            status=503,
        )

    return HttpResponse(
        "OK",
        content_type="text/plain",
        status=200,
    )
