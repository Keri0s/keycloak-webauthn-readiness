# Hồ sơ bằng chứng FR-08 — Không lưu khóa riêng

- **Yêu cầu (SRS 3.2, FR-08):** *"Cơ sở dữ liệu và nhật ký không có trường khóa riêng của passkey."* (Mức: Bắt buộc)
- **Phương thức kiểm tra theo SRS:** `Rà soát`
- **Trạng thái hiện tại:** `Đã rà có giới hạn` (theo báo cáo ngày 23/11/2026)

## Bằng chứng hiện có
- Báo cáo tổng hợp FR-08: [`docs/validation/fr08-2026-11-23/report.md`](../../docs/validation/fr08-2026-11-23/report.md) và [`app-audit.json`](../../docs/validation/fr08-2026-11-23/app-audit.json).
  - DB ứng dụng: 73 cột schema không có cột khóa riêng passkey; 16/21 session giải mã không có marker.
  - 5 session `BadSignature`: [`session-review.md`](../../docs/validation/fr08-2026-11-23/session-review.md) — đã đọc JSON nén, không thấy marker khóa riêng (chưa rõ nguyên nhân chữ ký lỗi).
  - DB Keycloak (từ ảnh truy vấn `fr08-keycloak.sql` và `fr08-events-long.sql`): 2 bản ghi `webauthn-passwordless` có `secret_data` object rỗng và `credential_data` chỉ chứa `credentialPublicKey` cùng metadata công khai; 67 sự kiện thuộc 4 loại có `marker_rows=0` và `long_marker_rows=0`.
  - Log container (`container-log-audit-20261123T110754904136Z.json`): Keycloak 297 dòng, Caddy 164 dòng, mọi bộ đếm marker đều `0`.
  - Export/backup: [`export-review.md`](../../docs/validation/fr08-2026-11-23/export-review.md) — đợt rà bổ sung lúc `2026-11-23T14:04:31Z` kiểm tra **62 tệp JSON/JSONL/CSV** (bao gồm `evidence/ledger/so_bang_chung.csv`, `evidence/ledger/pull-log.jsonl`, `docs/truy_vet.csv`, `evidence/lab-scorecard/phieu_cham_lab_draft.csv` và `inspection.json` mới), không phát hiện marker (`flagged_paths = []`), không tìm thấy tệp backup theo định dạng nhận diện.

## Giới hạn
- Bộ dò heuristic phát hiện tên trường/JWK riêng `d`/PEM, không chứng nhận mọi dạng mã hóa nhị phân tùy biến; không kiểm tra volume ngoài phạm vi project hoặc log container đã xoay/xóa; nguyên nhân 5 Django session `BadSignature` chưa xác định.

## Ảnh người dùng cần tự lưu vào thư mục này
1. Hai ảnh terminal chạy `fr08-keycloak.sql` và `fr08-events-long.sql` ngày 23/11/2026.
