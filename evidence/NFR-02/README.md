# Hồ sơ bằng chứng NFR-02 — Tách realm

- **Yêu cầu (SRS 3.4, NFR-02):** *"Tệp cấu hình không chứa địa chỉ cụm Keycloak đang vận hành."*
- **Phương thức kiểm tra theo SRS:** `Rà soát`
- **Trạng thái hiện tại:** `Đã rà có giới hạn` (đã rà tĩnh cấu hình và đối chiếu `inspection.json` hiệu lực ngày 23/11/2026)

## Bằng chứng hiện có
- Báo cáo rà soát tĩnh NFR-01/NFR-02: [`docs/validation/nfr01-02-2026-11-23/report.md`](../../docs/validation/nfr01-02-2026-11-23/report.md):
  - Bảng cấu hình không bí mật từ `infra/compose.yaml`, `infra/Caddyfile`, `apps/lab/config/settings.py`, `apps/lab/.env.example`, `apps/ledger/schema.py`, `infra/passwordless/inspect_keycloak.py`: chỉ dùng `auth.readiness.test`, `app.readiness.test`, `127.0.0.1`, `webauthn-lab`, `app-lab`.
  - Grep tên miền Trường (`stu.edu`, `hutech`, `.edu.vn`) trên mã nguồn, cấu hình, mẫu và tài liệu công bố: **0 kết quả**.
- Bản kiểm kê cấu hình hiệu lực ngày `23/11/2026 13:53:27Z`: [`inspection.json`](../../docs/validation/passwordless-preflight/20261123T135327930466Z/inspection.json) và [`review.md`](../../docs/validation/passwordless-preflight/20261123T135327930466Z/review.md) xác nhận client `app-lab` gắn `client_override` sang `browser-passkey-uv`, `RP ID=auth.readiness.test`, `UV=required`, mọi redirect/logout URI trỏ `https://app.readiness.test:9443/...`.
- Bản kiểm kê mốc lịch sử `22/11/2026`: [`docs/validation/passwordless-preflight/20261122T071144990590Z/inspection.json`](../../docs/validation/passwordless-preflight/20261122T071144990590Z/inspection.json).

## Giới hạn
- Chưa đọc tệp `.env` runtime trên máy người dùng (bị loại trừ theo quy tắc không xuất bí mật).
- `realm.browserFlow` mặc định toàn realm vẫn là `browser-password-webauthn` trong khi `app-lab` dùng override `browser-passkey-uv`.

## Ảnh người dùng cần tự lưu vào thư mục này (tùy chọn)
- Ảnh cấu hình `webAuthnPolicyPasswordless` (`PL-POL-01`) hoặc ảnh terminal chạy `inspect_keycloak.py` ngày 23/11.
