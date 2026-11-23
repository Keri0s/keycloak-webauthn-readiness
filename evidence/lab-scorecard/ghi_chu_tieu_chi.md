# Đối chiếu 16 tiêu chí sẵn sàng trên cụm lab hiện tại (Dự thảo — 23/11/2026)

Tài liệu này tổng hợp những gì **đã quan sát được** (hoặc **chưa có bằng chứng**) từ mã nguồn, cấu hình và các báo cáo kiểm chứng hiện hành của lab N15 cho từng tiêu chí trong [`tieu_chi.yaml`](../../DU_LIEU_MAU/N15_San_sang_WebAuthn/tieu_chi.yaml).

> [!IMPORTANT]
> Cột `diem` trong [`phieu_cham_lab_draft.csv`](phieu_cham_lab_draft.csv) được **để trống** (`None` = chưa chấm, khác điểm `0`). Người đánh giá trực tiếp xem đối chiếu bên dưới và quyết định điểm từng tiêu chí trước khi chạy CLI chấm chính thức. Không dùng điểm `29/37` của bộ fixture mẫu.

---

## Nhóm 1: Cấu hình an toàn (`cau_hinh` — tối đa 10 điểm)

| Mã | Nội dung (Max) | Quan sát thực tế từ repo & báo cáo | Khoảng trống / lưu ý cho người chấm |
| --- | --- | --- | --- |
| `CH-01` | TLS bật cho mọi điểm vào; chuyển hướng HTTP→HTTPS (3 đ) | `infra/compose.yaml` mở Caddy ở `127.0.0.1:9443`; `infra/Caddyfile` bật `tls internal` cho cả `https://auth.readiness.test:9443` và `https://app.readiness.test:9443`; `apps/lab/config/settings.py` đặt `SECURE_PROXY_SSL_HEADER`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`; `inspection.json` (`23/11 13:53Z`) có `sslRequired="external"`. | `infra/Caddyfile` dòng 2 ghi `auto_https disable_redirects`, không mở cổng HTTP 80 để tự chuyển hướng HTTP→HTTPS. Cần quyết định mức điểm phù hợp. |
| `CH-02` | Tắt chế độ debug/thông báo lỗi chi tiết ở môi trường chạy (2 đ) | `apps/lab/config/settings.py` đặt `DEBUG = False`; `apps/lab/authn/views.py` (`callback_failure`) hiển thị trang `login_retry.html` kèm `reference`, ẩn ngoại lệ chi tiết; `oidc_backchannel_logout` trả thông báo cố định; `apps/ledger/keycloak.py` và `inspect_keycloak.py` không in response body lỗi; `infra/compose.yaml` chạy Keycloak bằng `command: ["start"]`. | Chưa có kiểm tra riêng cấu hình trang lỗi/logging bên trong Caddy hoặc header phản hồi của mọi route lỗi Django 404/500 trên runtime. |
| `CH-03` | Tiêu đề bảo mật HTTP: CSP, HSTS, X-Content-Type-Options (2 đ) | `apps/lab/config/settings.py` bật `SecurityMiddleware` và `XFrameOptionsMiddleware`; `apps/lab/authn/views.py` gắn `Referrer-Policy: no-referrer` trên `callback_failure` và `@never_cache`. | `infra/Caddyfile` chưa cấu hình header `Strict-Transport-Security` (HSTS) hoặc `Content-Security-Policy` (CSP); `settings.py` chưa đặt `SECURE_HSTS_SECONDS` hay CSP. Chưa có bằng chứng chụp response headers kiểm tra đầy đủ CSP/HSTS/`X-Content-Type-Options` trên `/private/`. |
| `CH-04` | Bí mật không nằm trong mã/ảnh container; nạp từ biến môi trường hoặc kho bí mật (3 đ) | `apps/lab/config/settings.py` đọc `DJANGO_SECRET_KEY`, `LAB_DB_PASSWORD`, `OIDC_CLIENT_SECRET` từ `os.environ` (`.env`); `infra/compose.yaml` đọc `KEYCLOAK_DB_PASSWORD`, `LAB_DB_ADMIN_PASSWORD` từ biến môi trường; `.env.example` để trống giá trị; `.gitignore` loại trừ `.env`, `.runtime/`, `*.key`, `*.pem`; `docs/validation/fr08-2026-11-23/export-review.md` rà 55 tệp JSON/CSV không thấy khóa riêng. | Chưa rà soát `.env` runtime (bị loại trừ theo quy tắc không xuất bí mật); 5 Django session `BadSignature` chưa xác định nguyên nhân. |

---

## Nhóm 2: Vá lỗi (`va_loi` — tối đa 9 điểm)

| Mã | Nội dung (Max) | Quan sát thực tế từ repo & báo cáo | Khoảng trống / lưu ý cho người chấm |
| --- | --- | --- | --- |
| `VA-01` | Có danh mục thành phần (SBOM) hoặc danh sách phụ thuộc có phiên bản (2 đ) | `apps/lab/requirements.txt` ghim phiên bản chính xác (`Django==5.2.19`, `Authlib==1.9.6`, `requests==2.34.2`, `psycopg[binary]==3.3.9`, `python-dotenv==1.2.4`); `infra/compose.yaml` ghim tag image (`caddy:2.11.9-alpine`, `postgres:17.12-bookworm`, `quay.io/keycloak/keycloak:26.8.2`). | Root `requirements.txt` vẫn dùng khoảng phiên bản cho `pyyaml>=6.0.0`, `pytest>=9.0.0` (chưa ghim cứng); chưa có tệp SBOM chuẩn SPDX/CycloneDX. |
| `VA-02` | Không còn phụ thuộc có lỗ hổng mức Critical đã có bản vá (3 đ) | Chưa có bằng chứng. | Chưa có kết quả chạy công cụ quét lỗ hổng (ví dụ `pip-audit`, `trivy`) trên môi trường lab N15 lưu trong `docs/validation/`. |
| `VA-03` | Ảnh nền hệ điều hành/container còn được hỗ trợ (chưa EOL) (2 đ) | `infra/compose.yaml` ghi rõ phiên bản `caddy:2.11.9-alpine`, `postgres:17.12-bookworm`, `quay.io/keycloak/keycloak:26.8.2`. | Chưa có tài liệu đối chiếu ngày kiểm tra với vòng đời hỗ trợ (EOL) chính thức của nhà cung cấp lưu tại `docs/validation/`. |
| `VA-04` | Quy trình cập nhật có ghi chép (ai, khi nào, phiên bản) (2 đ) | Có nhật ký thay đổi kèm ngày, người thực hiện và kiểm chứng trong `WORKFLOW-STATE.md`, `docs/ROADMAP.md` và thư mục `docs/validation/`. | Chưa có quy trình/nhật ký riêng cho thao tác nâng cấp định kỳ phiên bản image và thư viện. |

---

## Nhóm 3: Xác thực (`xac_thuc` — tối đa 10 điểm)

| Mã | Nội dung (Max) | Quan sát thực tế từ repo & báo cáo | Khoảng trống / lưu ý cho người chấm |
| --- | --- | --- | --- |
| `XT-01` | Đăng nhập qua IdP tập trung (OIDC), ứng dụng không tự lưu mật khẩu (3 đ) | `apps/lab/config/oidc.py`, `apps/lab/authn/views.py`, `apps/lab/authn/models.py` triển khai OIDC Authorization Code + PKCE S256 qua Keycloak `webauthn-lab`, ánh xạ `ExternalIdentity(issuer, subject)` → `SessionBinding`; xác thực thật đã quan sát tại [`fr05-observed-185955.md`](../../docs/validation/requirements-review-2026-11-23/fr05-observed-185955.md); 12 unit tests `test_oidc_recovery` + `test_login_evidence` PASS. | `apps/lab/config/settings.py` vẫn có `django.contrib.auth` cho `/admin/`, nhưng route nghiệp vụ `/private/` kiểm tra `require_active_binding` (chặn phiên không có binding OIDC hợp lệ). |
| `XT-02` | Có xác thực chống giả mạo (passkey/WebAuthn) cho tài khoản quản trị (3 đ) | Tài khoản thử `lab-user-01` trên `app-lab` đã đăng ký và đăng nhập passkey passwordless với `UV=true` ([`registration-event-0947.md`](../../docs/validation/callback-recovery-2026-11-23/registration-event-0947.md), [`fr05-observed-185955.md`](../../docs/validation/requirements-review-2026-11-23/fr05-observed-185955.md), [`ledger-2026-11-23/report.md`](../../docs/validation/ledger-2026-11-23/report.md)); [`inspection.json` 23/11](../../docs/validation/passwordless-preflight/20261123T135327930466Z/review.md) xác nhận `app-lab` dùng `browser-passkey-uv` (`UV=required`). | Tiêu chí nêu *"cho tài khoản quản trị"*: chưa có bằng chứng bắt buộc WebAuthn/passkey đối với tài khoản quản trị Keycloak `master` (`lab-owner` dùng password grant `admin-cli` ở Mục A–D) và tài khoản Django `/admin/`; lỗi native Try again giữ `DEFERRED_OPEN`. |
| `XT-03` | Giới hạn đăng nhập sai (brute-force protection) (2 đ) | Chưa có bằng chứng. | `inspect_keycloak.py` chưa truy vấn trường `bruteForceProtected` của realm `webauthn-lab` (không có trong `inspection.json` `23/11`) và chưa kiểm thử khóa đăng nhập sai nhiều lần. |
| `XT-04` | Phiên hết hạn khi nhàn rỗi và đăng xuất hủy phiên ở IdP (2 đ) | `apps/lab/config/settings.py` đặt `OIDC_APP_SESSION_AGE = 15 * 60` (900s); `inspection.json` (`23/11 13:53Z`) ghi `ssoSessionIdleTimeout = 1800` (30 phút); `apps/lab/authn/views.py` triển khai `oidc_logout` (`revoke_verified_sid` + `logout_redirect`) và `oidc_backchannel_logout`; 9/19 kịch bản `SESSION_MAPPING_A` đã ghi PASS trong `docs/validation/a10-2026-11-18/` và `remaining-reliability-2026-11-18/` (chứng minh thu hồi SID và từ chối phiên cũ). | Chưa kiểm thử hết hạn thời gian thực End-to-End trên Keycloak; các ca `A8`/`A13b` về subject-wide logout còn OPEN. |

---

## Nhóm 4: Nhật ký (`nhat_ky` — tối đa 8 điểm)

| Mã | Nội dung (Max) | Quan sát thực tế từ repo & báo cáo | Khoảng trống / lưu ý cho người chấm |
| --- | --- | --- | --- |
| `NK-01` | Ghi sự kiện đăng nhập thành công/thất bại có thời điểm (3 đ) | `inspection.json` (`23/11`): `eventsEnabled = true`; đã kéo 67 dòng sự kiện thực (`2` đăng ký, `43` LOGIN, `22` LOGIN_ERROR) vào [`evidence/ledger/so_bang_chung.csv`](../ledger/so_bang_chung.csv) và kiểm thử thành công sinh dòng mới Mục B–C ([`ledger-2026-11-23/report.md`](../../docs/validation/ledger-2026-11-23/report.md)); 13 unit tests `apps/ledger/tests/` PASS. | Lỗi native Try again giữ `DEFERRED_OPEN`. |
| `NK-02` | Nhật ký không chứa mật khẩu, token, khóa (2 đ) | `apps/lab/config/settings.py` (`omit_callback_log`) loại `/auth/callback/` và `/auth/logged-out/` khỏi log server; `apps/lab/authn/diagnostics.py` chỉ ghi allowlist mã lỗi; `apps/ledger` loại bỏ IP/SID/UID thô, token, raw WebAuthn response, `privateKey`; [`fr08-2026-11-23/report.md`](../../docs/validation/fr08-2026-11-23/report.md) và [`export-review.md`](../../docs/validation/fr08-2026-11-23/export-review.md) xác nhận 0 marker khóa riêng trên 699 byte `oidc-callback.log`, 297 dòng Keycloak, 164 dòng Caddy, 67 event DB Keycloak và 62 tệp JSON/JSONL/CSV (gồm `so_bang_chung.csv` thực tế); [`nfr04-review.md`](../../docs/validation/ledger-2026-11-23/nfr04-review.md). | Phép rà tập trung vào marker khóa riêng (chưa rà mọi token/mật khẩu trong log lịch sử đã xoay); nguyên nhân 5 session `BadSignature` chưa xác định. |
| `NK-03` | Đồng hồ đồng bộ (NTP) giữa các máy (1 đ) | Chưa có bằng chứng. | Chưa có kết quả kiểm tra đồng bộ thời gian NTP/W32Time giữa host Windows và container Docker lưu trong `docs/validation/`. |
| `NK-04` | Nhật ký được lưu tập trung và giữ tối thiểu theo quy định của đơn vị (2 đ) | `apps/lab/config/settings.py` lưu log callback xoay vòng cục bộ (`oidc-callback.log`, `maxBytes=1 MiB`, `backupCount=2`); `inspection.json` (`23/11`) đặt `eventsExpiration = 604800` (7 ngày); `apps/ledger` kéo sự kiện về [`evidence/ledger/so_bang_chung.csv`](../ledger/so_bang_chung.csv). | Chưa có hệ thống thu thập log tập trung (syslog/SIEM) cho toàn bộ Caddy/Keycloak/Django, và thời hạn lưu 7 ngày trên Keycloak ngắn hơn mức lưu dài hạn thông thường (chưa có quy định cụ thể từ đơn vị/giảng viên). |

---

## Lệnh chấm sau khi người đánh giá điền cột `diem`

Sau khi mở [`phieu_cham_lab_draft.csv`](phieu_cham_lab_draft.csv), điền điểm số nguyên (`0 <= diem <= diem_toi_da`) cho từng dòng hoặc tạo bản sao đã điền đầy đủ, chạy từ thư mục gốc:

```powershell
python -m apps.readiness.cli --scorecard evidence/lab-scorecard/phieu_cham_lab_draft.csv --evaluator "<Tên người chấm>"
```
