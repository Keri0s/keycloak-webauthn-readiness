# Hồ sơ bằng chứng NFR-03 — Dựng lại

- **Yêu cầu (SRS 3.4, NFR-03):** *"README đăng ký passkey, đăng nhập và mở một dòng bằng chứng."*
- **Phương thức kiểm tra theo SRS:** `Demo`
- **Trạng thái hiện tại:** `Một phần` (đã cập nhật README, thực hiện thành công bước đăng nhập + kéo/mở dòng bằng chứng trong Mục B–C; còn thiếu chạy liền mạch một lượt demo từ bước đăng ký → đăng nhập → mở dòng và lưu ảnh vào thư mục này)

## Bằng chứng hiện có
- Hướng dẫn 3 bước demo tại [`README.md`](../../README.md) (mục **Demo nghiệm thu SRS (NFR-03)**): chuẩn bị môi trường → đăng ký passkey (`FR-04`) → đăng nhập `/private/` (`FR-05`) → chạy `apps.ledger.cli pull` và `show --id <evidence_id>` (`FR-06`/`IF-04`).
- Hướng dẫn chi tiết module: [`apps/lab/README.md`](../../apps/lab/README.md), [`apps/ledger/README.md`](../../apps/ledger/README.md), [`infra/README.md`](../../infra/README.md), [`infra/passwordless/README.md`](../../infra/passwordless/README.md).
- Các phần đã thực hiện thực tế ngày 23/11: đăng ký passkey (`09:47`), đăng nhập `/private/` (`18:59:55` và `20:40:42`), kéo sổ và mở chi tiết dòng bằng chứng bằng `show --id 5efcdcf3-8031-49c6-be2a-8ccd8f04e425` và `0bf7d697-a7c6-4d95-9e22-f60c2402dd31` ([báo cáo sổ live](../../docs/validation/ledger-2026-11-23/report.md)).

## Phần còn thiếu / giới hạn
- Cần thực hiện (hoặc ghi nhận trong buổi nghiệm thu) một lượt chạy liền mạch từ bước 1 đến bước 3 theo đúng [`README.md`](../../README.md), ghi rõ chỗ làm thủ công (gán required action, nhập PIN, nhập tài khoản admin terminal).
- Dựng máy sạch hoàn toàn là cải thiện khả năng tái lập thêm, không bắt buộc gộp thành điều kiện SRS này.

## Ảnh / log người dùng cần tự lưu vào thư mục này
- Ảnh chụp hoặc nhật ký terminal một lượt demo: (1) đăng ký passkey, (2) trang `/private/` sau đăng nhập passkey, (3) lệnh `apps.ledger.cli show --id <evidence_id>` mở đúng 1 dòng bằng chứng.
