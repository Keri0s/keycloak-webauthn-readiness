# Hồ sơ bằng chứng NFR-04 — Bằng chứng tối thiểu

- **Yêu cầu (SRS 3.4, NFR-04):** *"Sổ bằng chứng không hiện khóa riêng dù người xem là quản trị lab."*
- **Phương thức kiểm tra theo SRS:** `Rà soát`
- **Trạng thái hiện tại:** `Đã rà có giới hạn` (đã giải trình allowlist, test offline PASS và rà `audit_fr08_exports.py` trên dữ liệu sổ CSV thực tế 67 dòng do quản trị viên `lab-owner` kéo)

## Bằng chứng hiện có
- Báo cáo giải trình và đối chiếu sổ live NFR-04: [`docs/validation/ledger-2026-11-23/nfr04-review.md`](../../docs/validation/ledger-2026-11-23/nfr04-review.md).
- Kết quả quét tệp thực tế tại [`export-review.md`](../../docs/validation/fr08-2026-11-23/export-review.md): `evidence/ledger/so_bang_chung.csv` (67 dòng, 20.054 byte) và `evidence/ledger/pull-log.jsonl` (3.175 byte) đều có `0` marker khóa riêng; không chứa IP, `code_id`, `redirect_uri` hay chuỗi mô tả lỗi tự do.
- Mã nguồn kiểm soát allowlist: [`apps/ledger/schema.py`](../../apps/ledger/schema.py) (`COLUMNS`, `DISPLAY_COLUMNS`), [`apps/ledger/mapping.py`](../../apps/ledger/mapping.py), [`apps/ledger/store.py`](../../apps/ledger/store.py), [`apps/ledger/cli.py`](../../apps/ledger/cli.py) (không có cờ CLI mở rộng trường nhạy cảm cho admin).
- Kiểm thử offline (`apps/ledger/tests/`): xác nhận loại bỏ `privateKey`, `ipAddress`, `code_id`, `redirect_uri`, `attestationObject` và cột `private_key` chèn tay khi nạp/hiển thị CSV.

## Giới hạn
- Bộ dò heuristic phát hiện các dấu hiệu khóa riêng phổ biến, không thay thế kiểm chứng mọi dạng mã hóa tùy biến; kết quả áp dụng trong phạm vi 67 dòng đã kéo của `app-lab`.

## Ảnh người dùng cần tự lưu vào thư mục này (tùy chọn)
- Ảnh đầu ra `apps.ledger.cli show --id 5efcdcf3-8031-49c6-be2a-8ccd8f04e425` hoặc `--outcome failure` trên dữ liệu thật.
