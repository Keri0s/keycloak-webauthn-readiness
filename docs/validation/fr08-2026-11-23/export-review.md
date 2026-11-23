# Phạm vi backup/export của lab

## Cập nhật rà soát bổ sung — 23/11/2026 14:09 UTC (21:09 UTC+7)

Sau khi người dùng hoàn tất kéo sổ bằng chứng live, cập nhật cấu hình preflight và hoàn thiện ma trận truy vết, đã chạy lại `.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\audit_fr08_exports.py` (tại `2026-11-23T14:09:19.104638+00:00`). Kết quả ghi nhận **62 tệp JSON/JSONL/CSV** đạt `SCANNED_HEURISTIC` (`tmp`: 39, `docs`: 15, `DU_LIEU_MAU`: 5, `evidence`: 3), cùng 3 tệp SQL (`2 SQL_SOURCE_NOT_EXPORT`, `1 SQL_REQUIRES_CLASSIFICATION` là `infra/passwordless/fr05-login.sql`); `flagged_paths = []`, `walk_errors = []`.

Các tệp mới kiểm tra đều có tất cả bộ đếm marker bằng `0`:
- `evidence/ledger/so_bang_chung.csv` (20.054 byte, SHA-256 `fca424aaf19fd59fc2ad9a759aaac685c103c0687fb5dd9c2d19a58192bae80f`)
- `evidence/ledger/pull-log.jsonl` (3.175 byte, SHA-256 `34ae201fbd352b0a3d71256b43756392c5efaa1b3e2d8f968041d5d9b28b2448`)
- `docs/validation/passwordless-preflight/20261123T135327930466Z/inspection.json` (34.545 byte, SHA-256 `28764e84e7b8ef5fa1563e4cc009840fc0c8faef9971288c1a9e748866c3b061`)
- `docs/truy_vet.csv` (9.900 byte, SHA-256 `3d4c4e4fa272e7a2d0e2b5a5425f8702a44025728decd35981345da54d6d7822`)
- `evidence/lab-scorecard/phieu_cham_lab_draft.csv` (1.550 byte, SHA-256 `9939e1f06eb0a948a1fab335a64f2eeeaaa1805202e8a534e279be785853147c`)

Mục gốc bên dưới giữ nguyên làm mốc lịch sử đợt rà 55 tệp trước đó.

Ngày rà: 23/11/2026. Đã hoàn tất kiểm kê và dò marker trong phạm vi dưới đây.
Không có thao tác xuất toàn bộ DB hoặc sao chép dữ liệu riêng tư.

## Phạm vi và kết quả

Các thư mục được kiểm kê: apps, docs, evidence, infra, tmp, tests và
DU_LIEU_MAU/N15_San_sang_WebAuthn trong project hiện tại.

| Nhóm | Số tệp đã dò | Phân loại |
|---|---:|---|
| docs | 11 | Báo cáo JSON, kết quả kiểm thử và export cấu hình preflight |
| tmp | 39 | CSV/JSON của các lần kiểm thử Readiness và báo cáo kiểm thử |
| Dữ liệu mẫu N15 | 5 | 4 CSV mẫu, 1 JSON realm mẫu; không phải export runtime |
| SQL | 2 | Hai script truy vấn FR-08, không phải dump DB; không tính vào 55 tệp |

Đã rà **55 tệp JSON/CSV**, không phát hiện marker private key theo bộ dò hiện có.
Không có lỗi duyệt thư mục hoặc parse; không có tệp ứng viên vượt giới hạn 8 MiB.
Không tìm thấy ứng viên backup/archive/database theo các đuôi .dump, .bak,
.backup, .zip, .gz, .tar, .7z, .sqlite, .sqlite3 hoặc .db trong phạm vi đã duyệt.
Đây không phải khẳng định không tồn tại backup ở nơi khác hoặc dưới tên/định dạng khác.

Export cấu hình Keycloak được xác định cụ thể là
`docs/validation/passwordless-preflight/20261122T071144990590Z/inspection.json`.
Đó là kết quả inspector theo allowlist, không phải bản export toàn bộ realm/users.
`DU_LIEU_MAU/N15_San_sang_WebAuthn/realm/webauthn-lab-realm.json` là tệp mẫu,
không dùng nó làm bằng chứng thay thế DB runtime.

[Danh mục từng tệp, hash và kết quả](export-inventory-2026-11-23.json).
Công cụ: `infra/passwordless/audit_fr08_exports.py`.

## Những phần không thuộc lần kiểm kê này

- references/vdt-snapshot, review và dữ liệu mẫu của các đề khác.
- Thư viện phụ thuộc, symlink/junction, file secret cấu hình và dữ liệu ngoài project.
- Nội dung các volume infra/.runtime/app-db, keycloak-db, caddy-data,
  caddy-config, keycloak-trust. Chỉ liệt kê tên thư mục cấp đầu để phân biệt
  runtime với export; DB/log đã có các phép kiểm tra riêng trong báo cáo FR-08.
- Backup bên ngoài project, lịch sử Git, bản lưu cloud, tệp mã hóa/định dạng
  không được nhận diện. Không có bằng chứng để kết luận về các phạm vi này.

Báo cáo audit có các tên bộ đếm như private_named_fields với giá trị 0; đây là
metadata của phép kiểm tra, không phải trường chứa khóa. Kết quả không có marker
không chứng minh mọi dạng mã hóa private key đều vắng mặt.

## Kết luận

Phần xác định backup/export trong project đã hoàn tất theo phạm vi công bố.
Kết hợp với DB, session và log đã rà, chưa phát hiện dấu hiệu lưu private key
passkey trong dữ liệu đã kiểm tra. Không tự nâng kết quả này thành chứng nhận
toàn máy hoặc PASS tuyệt đối cho FR-08; nguyên nhân 5 chữ ký session lỗi vẫn chưa rõ.
