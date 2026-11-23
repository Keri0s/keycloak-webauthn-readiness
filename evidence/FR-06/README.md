# Hồ sơ bằng chứng FR-06 — Bằng chứng thành công

- **Yêu cầu (SRS 3.2, FR-06):** *"Mỗi lần đăng ký hoặc đăng nhập thành công tạo một dòng: thời điểm, kết quả thành công, mã thông tin xác thực."* (Mức: Bắt buộc)
- **Phương thức kiểm tra theo SRS:** `Kiểm thử`
- **Trạng thái hiện tại:** `Đã quan sát` (đã kéo 67 dòng live về sổ CSV + chạy kiểm thử "đăng nhập → có dòng mới" và kiểm tra chống trùng + 13 unit test offline PASS)

## Bằng chứng hiện có
- Báo cáo sổ bằng chứng live (Mục A–B): [`docs/validation/ledger-2026-11-23/report.md`](../../docs/validation/ledger-2026-11-23/report.md).
- Sổ bằng chứng thực tế: [`evidence/ledger/so_bang_chung.csv`](../ledger/so_bang_chung.csv) (67 dòng; SHA-256 `fca424aaf19fd59fc2ad9a759aaac685c103c0687fb5dd9c2d19a58192bae80f`) và [`evidence/ledger/pull-log.jsonl`](../ledger/pull-log.jsonl) (5 lần pull).
  - 2 dòng `UPDATE_CREDENTIAL` (`registration`/`success`) cho `lab-user-01` (`dndRW6XS6qIJg61vLgTUVw` ngày 22/11 và `gGCUOjoWoGQwWgLe3SMDow` ngày 23/11 09:47).
  - Kiểm thử Mục B ngày 23/11: trước khi đăng nhập `total=65`; sau đăng nhập lúc `20:40:42+07:00`, chạy `pull` tăng đúng 1 dòng (`added=1`, `total=66`) có `evidence_id=5efcdcf3-8031-49c6-be2a-8ccd8f04e425`, `credential_id=gGCUOjoWoGQwWgLe3SMDow`, `uv_checked=true`, khớp `X-Lab-Session-Ref`; chạy `pull` lặp lại ngay sau đó ghi `added=0, duplicates=43`.
- Quan sát Events UI trước đó: [`registration-event-0947.md`](../../docs/validation/callback-recovery-2026-11-23/registration-event-0947.md), [`fr05-observed-185955.md`](../../docs/validation/requirements-review-2026-11-23/fr05-observed-185955.md).
- Mã nguồn và 13 unit test offline PASS: [`apps/ledger/`](../../apps/ledger/README.md).

## Giới hạn
- Không đếm `CUSTOM_REQUIRED_ACTION` để tránh trùng với `UPDATE_CREDENTIAL` và không đếm `CODE_TO_TOKEN` thành lượt đăng nhập thứ hai.
- Một dòng `LOGIN` cũ lúc `2026-11-23T02:47:50.625Z` (`64584066-...`) không có `credential_type`/`credential_id` trên nguồn sự kiện Keycloak.

## Ảnh người dùng cần tự lưu vào thư mục này
1. Ảnh chi tiết `UPDATE_CREDENTIAL` 09:47 và `LOGIN` 13:55 / 13:56 (đã che `code_id`, IP).
2. Ảnh kết quả Mục A (`pull --since 2026-11-16`) và Mục B (`pull` → `show --since` → `pull` lặp `added=0`).
