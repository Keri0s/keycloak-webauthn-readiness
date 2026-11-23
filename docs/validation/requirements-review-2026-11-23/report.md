# Đối chiếu FR/NFR/IF/DR ngày 23/11/2026

Đây là đối chiếu kỹ thuật với SRS N15 v0.9 hiện có, không phải xác nhận nghiệm thu
của giảng viên. Giữ nguyên 20 mã yêu cầu và không tự thêm điều kiện bắt buộc.
Hướng triển khai hiện tại: đăng ký passkey sau xác minh ban đầu, đăng nhập thường
ngày passwordless với UV bắt buộc. Không đồng nhất hướng thiết kế với bằng chứng
đã kiểm chứng tất cả nhánh đăng ký, recovery và fallback.

## Cách đọc trạng thái

- **Có test**: có kết quả test đã lưu và nguồn hiện tại khớp hash của kết quả đó.
- **Đã quan sát**: thao tác/sự kiện thực được người dùng cung cấp; phạm vi theo ca.
- **Đã rà có giới hạn**: đã hoàn tất phép rà trong phạm vi công bố.
- **Một phần**: có triển khai hoặc bằng chứng, nhưng còn phần cần nối/kiểm tra.

Các trạng thái trên không phải điểm readiness và không quy đổi thành phần trăm
hoàn thành đồ án. Không dùng số ca session 9/19 thay cho số yêu cầu SRS.

## Chức năng

| Mã | Nội dung cần đạt | Trạng thái | Bằng chứng hiện có | Phần cần bổ sung / giới hạn |
|---|---|---|---|---|
| FR-01 | Tiêu chí đủ bốn nhóm, mỗi tiêu chí có điểm tối đa | Có test | E01; catalog 16 tiêu chí, models/loader và test catalog | Kết quả trên catalog được kiểm tra, không tự chấm mức an ninh lab |
| FR-02 | Nhập điểm không vượt tối đa và nguồn ngắn | Có test | E01; validator, CSV parser, CLI; từ chối điểm vượt max | Nhập qua CSV/CLI đã có demo lưu; SRS không bắt buộc thêm web form |
| FR-03 | Tổng đúng, thiếu tiêu chí thì chưa hoàn thành | Có test | E01; fixture đầy đủ 29/37, fixture thiếu NK-03/NK-04 | 29/37 là điểm mẫu, không phải điểm thực của lab |
| FR-04 | Tài khoản lab đăng ký passkey trong realm lab | Đã quan sát | E02; UPDATE_CREDENTIAL 23/11 09:47, passwordless, account và credential ID | Ảnh gốc trong hội thoại, bản ghi đối chiếu ở repo; không chứng minh mọi luồng enrollment/recovery |
| FR-05 | Cùng tài khoản dùng passkey đó vào ứng dụng | Đã quan sát | E09: LOGIN 18:59:55 có ID trùng đăng ký, session_ref/subject_ref khớp app, binding tạo sau khoảng 206 ms, /private/ 200 | PASS_OBSERVED cho ca thực đã nối; không chứng minh mọi lần ổn định |
| FR-06 | Mỗi đăng ký/đăng nhập thành công có time/result/credential ID | Đã quan sát | E02, E10: 13 unit test offline `apps/ledger/tests/` PASS; sổ `so_bang_chung.csv` (67 dòng) ghi nhận 2 đăng ký và lượt LOGIN `20:40:42` thêm đúng 1 dòng khớp `X-Lab-Session-Ref`, kéo lặp `added=0` | Không đếm `CUSTOM_REQUIRED_ACTION`/`CODE_TO_TOKEN`; 1 dòng LOGIN `02:47:50Z` cũ không có `credential_type`; ảnh gốc ở hội thoại |
| FR-07 | Một lần hủy đăng nhập có dòng thất bại, không có private key | Đã quan sát | E04, E10: ca `14:16` và ca `20:47:34` (`LOGIN_ERROR/not_allowed`, `/private/` `403`, dòng `0bf7d697...` trong `so_bang_chung.csv` không có IP/`code_id`/private key) | Không suy cancel chỉ từ `NotAllowedError`; dòng hủy không có user/credential ghi `unknown`/rỗng |
| FR-08 | DB/log không có trường private key passkey | Đã rà có giới hạn | E05, E10: schema, credential, event, session, log, 62 JSON/JSONL/CSV (gồm `so_bang_chung.csv`, `pull-log.jsonl`, `inspection.json` mới); `flagged_paths=[]` | Không phát hiện marker trong phạm vi công bố; nguyên nhân 5 session `BadSignature` chưa xác định |

## Phi chức năng

| Mã | Nội dung cần đạt | Trạng thái | Bằng chứng hiện có | Phần cần bổ sung / giới hạn |
|---|---|---|---|---|
| NFR-01 | Công cụ không có chức năng quét địa chỉ ngoài lab | Đã rà có giới hạn | E06, E11: báo cáo rà tĩnh toàn bộ mã bàn giao (`apps/`, `infra/`, `tests/`, `tmp/` công bố) — 0 hàm quét mạng, đích gọi cố định lab local | Rà tĩnh mã nguồn tại thời điểm 23/11; không tự quét mạng để chứng minh |
| NFR-02 | Cấu hình không chứa địa chỉ cụm Keycloak vận hành | Đã rà có giới hạn | E06, E11, E12: 0 tên miền Trường; `inspection.json` `13:53:27Z` xác nhận `app-lab` override `browser-passkey-uv`, `RP ID=auth.readiness.test`, `UV=required` | Không đọc `.env` runtime (theo quy tắc bảo mật); `realm.browserFlow` mặc định vẫn là `browser-password-webauthn` |
| NFR-03 | README hướng dẫn đăng ký, đăng nhập, mở dòng bằng chứng | Một phần | E07, E10: `README.md` đã có mục Demo SRS; `infra/passwordless/README.md` đã cập nhật; đã chạy thực tế đăng nhập + `pull` + `show --id` ngày 23/11 | Chưa chạy một lượt demo liền mạch từ bước đăng ký → đăng nhập → mở dòng theo đúng README và lưu ảnh vào `evidence/NFR-03/` |
| NFR-04 | Sổ không hiển thị private key kể cả quản trị lab | Đã rà có giới hạn | E04, E05, E10: `nfr04-review.md` giải trình allowlist `apps/ledger` (test ca 4, 8 PASS) + `audit_fr08_exports.py` rà `so_bang_chung.csv` thực tế đạt `0` marker | Bộ dò heuristic không thay thế kiểm chứng mọi dạng mã hóa tùy biến |

## Giao diện và dữ liệu

| Mã | Nội dung cần đạt | Trạng thái | Bằng chứng hiện có | Phần cần bổ sung / giới hạn |
|---|---|---|---|---|
| IF-01 | Phiếu tiêu chí, điểm, nguồn | Có test | E01; CLI hiển thị từng tiêu chí, điểm và nguồn | Giao diện hiện tại là CLI; chưa chấm điểm phiếu lab thực (người chấm quyết định điểm) |
| IF-02 | Luồng đăng ký passkey | Đã quan sát | E02/E03/E10; Keycloak registration và 2 dòng `UPDATE_CREDENTIAL` trong `so_bang_chung.csv` | Bổ sung ảnh đã che dữ liệu phiên vào `evidence/FR-04/` nếu nộp độc lập hội thoại |
| IF-03 | Vào app bằng passkey vừa đăng ký | Đã quan sát | E09, E10; ca `18:59:55` (/private/ 200) và ca `20:40:42` khớp `X-Lab-Session-Ref`/`X-Lab-Subject-Ref` | `PASS_OBSERVED`; ảnh 4 ở lượt `20:40` chụp Response Headers, không chụp HTML `/private/` lượt đó |
| IF-04 | Xem time/result/credential ID | Đã quan sát | E10: chốt `evidence/ledger/so_bang_chung.csv` + `apps.ledger.cli show` / `show --id` làm điểm xem chính, kèm nguồn Keycloak Events | Sổ CSV dùng allowlist 18 cột, không dùng `so_bang_chung_mau.csv` thay sổ runtime |
| DR-01 | Tiêu chí có mã, nhóm, nội dung, điểm tối đa | Có test | E01; Criterion và catalog validation | Không thiếu trường bắt buộc trong phạm vi đã test |
| DR-02 | Phiếu có ngày, người chấm, từng điểm và tổng | Có test | E01; Scorecard, evaluator, CLI và regression tests | Dự thảo phiếu lab tại `evidence/lab-scorecard/phieu_cham_lab_draft.csv` đang để trống điểm |
| DR-03 | Event có account/time/type/result/credential ID, không private key | Đã quan sát | E08, E10: 67 dòng trong `so_bang_chung.csv` đúng schema 18 cột, không có khóa riêng; ca hủy ghi `unknown`/rỗng | Khung dữ liệu đối chiếu đã chạy thực; giữ quy ước loại bỏ mô tả lỗi tự do và IP/SID thô |
| DR-04 | Tài khoản giả và realm lab | Đã quan sát | E02/E04/E10: `lab-user-01` trong `webauthn-lab` | Không lấy `pk_user01` trong realm mẫu thay cho tài khoản runtime; không dùng tài khoản Trường |

## Danh mục bằng chứng đã đọc

| Mã tham chiếu | Nguồn | Phạm vi |
|---|---|---|
| E01 | [Readiness metadata 13/11](../readiness-2026-11-13/run-metadata.json), results.xml và nguồn apps/readiness, tests/test_fr*.py, test_readiness_regressions.py | Hồ sơ 81 tests PASS, ba CLI runs; trong lượt này đối chiếu 10/10 SHA-256 khớp, không gọi đây là lần chạy test mới |
| E02 | [Đăng ký và hai LOGIN](../callback-recovery-2026-11-23/registration-event-0947.md) | ID trùng, username/client trùng; hai LOGIN có UV=true; ảnh event không tự chứng minh app /private/ của chính lượt |
| E03 | [Enrollment và các lần đăng nhập quan sát](../passwordless-enrollment-2026-11-22/report.md) | Bản ghi ảnh UI, callback/private và retry; đọc các bổ sung theo thời gian, không chỉ đoạn đầu |
| E04 | [Ca hủy 14:16](../callback-recovery-2026-11-23/cancel-event-1416.md) | LOGIN_ERROR, thao tác hủy theo người thử, truy cập private bị chặn |
| E05 | [FR-08](../fr08-2026-11-23/report.md), [session](../fr08-2026-11-23/session-review.md), [export](../fr08-2026-11-23/export-review.md) | DB/event 67 dòng, log 461 dòng, session 21, export 55; từng báo cáo nêu giới hạn |
| E06 | apps/readiness/cli.py; apps/lab/config/urls.py; infra/Caddyfile; infra/passwordless/inspect_keycloak.py | Đã đọc các điểm vào và đích lab được chỉ ra, chưa gọi là audit network toàn bộ |
| E07 | README.md; apps/lab/README.md; infra/passwordless/README.md | Có hướng dẫn, có đoạn lỗi thời và phần chưa nối thành lượt demo |
| E08 | docs/evidence-contract.md | Quy ước đề xuất về nguồn, ID, cancel và trường cho phép; không phải implementation đầy đủ |
| E09 | [Ca FR-05 lúc 18:59:55](fr05-observed-185955.md) | Ba ảnh người dùng, LOGIN → binding → /private/ 200 cùng phiên và credential |
| E10 | [Báo cáo sổ live](../ledger-2026-11-23/report.md), [rà NFR-04](../ledger-2026-11-23/nfr04-review.md), [export-review.md](../fr08-2026-11-23/export-review.md) | 67 dòng trong `evidence/ledger/so_bang_chung.csv`, 5 lần pull trong `pull-log.jsonl`, Mục A–C (FR-06/FR-07) và quét 62 tệp export |
| E11 | [Báo cáo rà tĩnh NFR-01/NFR-02](../nfr01-02-2026-11-23/report.md) | Điểm gọi mạng, route, cấu hình không bí mật và grep tên miền Trường (0 kết quả) |
| E12 | [inspection.json 23/11](../passwordless-preflight/20261123T135327930466Z/inspection.json) và [review.md](../passwordless-preflight/20261123T135327930466Z/review.md) | Cấu hình hiệu lực `app-lab` override `browser-passkey-uv`, `RP ID=auth.readiness.test`, `UV=required` |

Các ảnh gốc chủ yếu ở hội thoại. Những JSON audit có sẵn trong repo đã được đọc
trong các lượt trước. Không tạo ảnh giả thay bằng chứng, không sửa SRS nguồn hoặc
nhật ký chạy cũ để khớp trạng thái mới.

## Công việc tiếp theo theo thứ tự

1. **Hoàn thành demo một lượt theo `README.md` (NFR-03)** và sao chép ảnh bằng chứng từ hội thoại (đã che thông tin phiên/IP/`code_id`) vào các thư mục `evidence/FR-04/`…`evidence/NFR-03/` nếu nộp hồ sơ độc lập.
2. **Chấm phiếu lab thực (`evidence/lab-scorecard/`)**: người đánh giá tự quyết định cột `diem` trong `phieu_cham_lab_draft.csv` dựa trên `ghi_chu_tieu_chi.md`, rồi chạy `python -m apps.readiness.cli`. Không biến `29/37` của fixture thành điểm lab.

Lỗi native cần Try again giữ DEFERRED_OPEN theo yêu cầu người dùng. Năm session
BadSignature đã rà nội dung, nguyên nhân chữ ký vẫn chưa xác định. Không đổi
trạng thái các vấn đề đó thành đã sửa để chốt ma trận. Các ca session còn lại
trong bộ 19 ca là tuyến kiểm thử riêng; không tự thêm toàn bộ thành điều kiện SRS.
