# Hồ sơ bằng chứng FR-05 — Đăng nhập

- **Yêu cầu (SRS 3.2, FR-05):** *"Cùng tài khoản đăng nhập bằng passkey đó và vào được ứng dụng lab."* (Mức: Bắt buộc)
- **Phương thức kiểm tra theo SRS:** `Demo`
- **Trạng thái hiện tại:** `Đã quan sát` (`PASS_OBSERVED` cho ca thực đã nối 18:59:55 ngày 23/11/2026)

## Bằng chứng hiện có
- Báo cáo đối chiếu cùng lượt đăng nhập ngày 23/11/2026 lúc `18:59:55`: [`docs/validation/requirements-review-2026-11-23/fr05-observed-185955.md`](../../docs/validation/requirements-review-2026-11-23/fr05-observed-185955.md) — chứng minh chuỗi `UPDATE_CREDENTIAL` 09:47 (`gGCUOjoWoGQwWgLe3SMDow`) → `LOGIN` `18:59:55.655Z` (cùng credential ID, `uv_checked=true`) → binding Django tạo sau khoảng `206 ms` → `/private/` trả `HTTP 200`, chào `lab-user-01`, khớp `X-Lab-Session-Ref` và `X-Lab-Subject-Ref`.
- Lượt đăng nhập mới lúc `20:40:42+07:00` ngày 23/11/2026 ([báo cáo sổ live Mục B](../../docs/validation/ledger-2026-11-23/report.md)): `LOGIN` `5efcdcf3-8031-49c6-be2a-8ccd8f04e425` (`13:40:42.491Z`, cùng `credential_id=gGCUOjoWoGQwWgLe3SMDow`, `uv_checked=true`) khớp `X-Lab-Session-Ref` và `X-Lab-Subject-Ref` trong Response Headers của `/private/` (`X-Lab-Binding-Created` sau khoảng `344 ms`).
- Cấu hình hiệu lực mới tại [`inspection.json` 23/11](../../docs/validation/passwordless-preflight/20261123T135327930466Z/review.md): xác nhận `app-lab` dùng override `browser-passkey-uv` (`auth-username-form` + `webauthn-authenticator-passwordless`, `UV=required`, `RP ID=auth.readiness.test`).
- Hai lượt `LOGIN` passwordless trước đó lúc `13:55` và `13:56` dùng cùng credential: [`docs/validation/callback-recovery-2026-11-23/registration-event-0947.md`](../../docs/validation/callback-recovery-2026-11-23/registration-event-0947.md).
- Kiểm thử offline header/recovery: [`apps/lab/authn/test_login_evidence.py`](../../apps/lab/authn/test_login_evidence.py), [`apps/lab/authn/test_oidc_recovery.py`](../../apps/lab/authn/test_oidc_recovery.py) (12 tests PASS).

## Giới hạn
- Lỗi Windows Security phải bấm *Try again* ở một số lần trước đó đang giữ trạng thái `DEFERRED_OPEN`; các ca quan sát chưa chứng minh mọi lần đăng nhập đều ổn định không cần thử lại hoặc máy chủ chắc chắn từ chối `UV=0`.

## Ảnh người dùng cần tự lưu vào thư mục này
1. Ba ảnh của lượt `18:59:55` ngày 23/11: trang `/private/` chào `lab-user-01` (HTTP 200), ảnh Response Headers (`X-Lab-Session-Ref`, `X-Lab-Subject-Ref`, **bắt buộc che `Cookie`/`Set-Cookie` nếu có**), và ảnh kết quả truy vấn `fr05-login.sql`.
2. Ảnh Mục B lượt `20:40` (Passkey login, Windows Security PIN, Response Headers `X-Lab-*`).
