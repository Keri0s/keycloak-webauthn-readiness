# Tiến độ và công việc tiếp theo

## Video demo giữa kỳ, sổ bằng chứng 73 dòng và hoàn thiện BCGK — 27/11/2026 UTC+7

Đã hoàn tất quay và đính kèm video demo giữa kỳ liền mạch có thuyết minh tại [demo_giua_ky_N15.mp4](reports/demo_giua_ky_N15.mp4) (`04:23`, `19.96 MB`), trình bày đủ 5 cảnh theo `README.md` và cập nhật sổ bằng chứng lên **73 dòng** (6 lượt pull trong `evidence/ledger/pull-log.jsonl`, gồm đăng ký mới `GK-passkey` `36069e0a...`, đăng nhập `UV=true` `06e8c39a...`, ca hủy `513124f1...` `/private/` 403, sạch marker khóa riêng). Đã cập nhật báo cáo [BCGK_Nhom15_N15.md](reports/BCGK_Nhom15_N15.md), [BCGK_Nhom15_N15.docx](reports/BCGK_Nhom15_N15.docx), [evidence/NFR-03/README.md](../evidence/NFR-03/README.md) và [truy_vet.csv](truy_vet.csv). Còn lại ở nửa sau: kiểm chứng quy trình dựng sạch 9 bước trên máy Windows độc lập thứ hai (`Chung-01`), chép ảnh che phiên vào `evidence/`, đối chứng lỗi native retry (`DEFERRED_OPEN`) bằng Windows Hello cục bộ và mở rộng phần còn thiếu của `SESSION_MAPPING_A`.

## Chốt phiếu chấm lab thực `27 / 37` và hoàn thiện README dựng sạch — 26/11/2026 UTC+7

Đã hoàn tất thu bằng chứng bổ sung (`VA-02`, `VA-03`, `XT-03`, `NK-03`) và chạy CLI chốt phiếu chấm lab thực ngày `26/11/2026`: **`27 / 37` điểm** (`16/16` tiêu chí, `HOÀN THÀNH`, tách biệt với mẫu fixture `29/37`), lưu tại [báo cáo chấm lab 26/11](validation/scorecard-evidence-2026-11-26/report.md) và `evidence/lab-scorecard/phieu_cham_lab_2026-11-26.csv`. Đồng thời đã bổ sung bảng **Phiên bản công cụ và môi trường thực dùng** và quy trình **Hướng dẫn dựng lab từ trạng thái sạch (Clean Setup)** 9 bước vào `README.md` (đồng bộ `infra/README.md`, `apps/lab/README.md`, `evidence/NFR-03/README.md`, `docs/truy_vet.csv`). Tiếp theo: kiểm chứng dựng lại trên máy sạch độc lập (nếu triển khai máy khác), hoàn tất lượt demo liền mạch theo `README.md` (NFR-03) và sao chép ảnh bằng chứng từ hội thoại vào `evidence/` nếu nộp bản offline. Lỗi native retry giữ `DEFERRED_OPEN`.

## Hoàn tất kiểm chứng sổ live Mục A–D & đối chiếu inspection — 23/11/2026 21:05 UTC+7

Đã hoàn tất Mục A–D: `evidence/ledger/so_bang_chung.csv` (67 dòng) ghi nhận đủ đăng ký, đăng nhập mới khớp `X-Lab-Session-Ref`, kéo lặp `added=0` và ca hủy `/private/` `403` ([báo cáo sổ live](validation/ledger-2026-11-23/report.md)); `inspection.json` mới (`13:53:27Z`) xác nhận `app-lab` dùng `browser-passkey-uv` (`UV=required`, `RP ID=auth.readiness.test`) ([review](validation/passwordless-preflight/20261123T135327930466Z/review.md)); `audit_fr08_exports.py` quét 62 tệp JSON/JSONL/CSV không phát hiện marker ([export-review](validation/fr08-2026-11-23/export-review.md)). Tiếp theo: demo liền mạch theo `README.md` (NFR-03), sao chép ảnh vào `evidence/` và tự chấm phiếu lab tại `evidence/lab-scorecard/`. Lỗi native retry giữ `DEFERRED_OPEN`.

## Sổ bằng chứng, rà NFR-01/02/04 và hồ sơ nghiệm thu — 23/11/2026

Đã hoàn thiện phần offline: `apps/ledger` (13 unit test PASS), [rà tĩnh NFR-01/NFR-02](validation/nfr01-02-2026-11-23/report.md), [giải trình NFR-04](validation/ledger-2026-11-23/nfr04-review.md), cập nhật README demo (NFR-03), bộ `evidence/FR-01..08` / `NFR-01..04`, `docs/truy_vet.csv` và dự thảo phiếu lab tại `evidence/lab-scorecard/`. Tiếp theo cần người dùng chạy [runbook thu sổ live](validation/ledger-2026-11-23/runbook.md) (kéo sự kiện 22–23/11 trước 29/11, kiểm thử FR-06/FR-07, chạy lại `inspect_keycloak.py`), chạy demo README và quyết định điểm phiếu lab thực. Lỗi native retry giữ `DEFERRED_OPEN`.

## Đã nối LOGIN với ứng dụng — 23/11/2026 18:59:55

FR-05/IF-03 có [ca thực đã đối chiếu](validation/requirements-review-2026-11-23/fr05-observed-185955.md):
credential, mã phiên/subject khớp, binding và /private/ 200. Bước ưu tiên hiện tại
là sổ bằng chứng FR-06/IF-04/DR-03/NFR-04, sau đó rà NFR-01/02 và README NFR-03.
Các kế hoạch yêu cầu nối LOGIN ở phía dưới là lịch sử đã thực hiện.

## Thứ tự hoàn thiện sau đối chiếu — 23/11/2026

[Bảng đủ 20 yêu cầu và nguồn bằng chứng](validation/requirements-review-2026-11-23/report.md)
là trạng thái hiện hành; các mốc bên dưới giữ làm lịch sử.

1. Nối một LOGIN có credential ID đã đăng ký với /private/ của chính lượt đó (FR-05/IF-03).
2. Thống nhất điểm xem/xuất sổ và kiểm tra đủ dòng trong đợt thử (FR-06/IF-04/DR-03/NFR-04).
3. Rà điểm nhận địa chỉ và cấu hình hiệu lực không bí mật (NFR-01/NFR-02).
4. Cập nhật README passwordless và thực hiện một lượt demo theo hướng dẫn (NFR-03).
5. Hoàn thiện bộ bằng chứng và phiếu chấm lab thực, không dùng điểm mẫu 29/37.

FR-08 đã hoàn tất đợt rà trong phạm vi công bố. Sổ có thể sử dụng Keycloak Events;
không tự thêm portal/collector hoặc dựng máy sạch thành điều kiện bắt buộc SRS.

## Cập nhật FR-08 - 23/11/2026

FR-06 đã đối chiếu credential đăng ký với LOGIN 13:55/13:56; FR-07 có
PASS_OBSERVED cho ca hủy 14:16 và /private/ trả 403. FR-08 mới rà được một phần
ứng dụng: 16 session đọc được không có marker, 5 session BadSignature. Đã có
bằng chứng DB Keycloak do người dùng chạy (2 secret_data object rỗng; 67 event
không có marker trong hai cột) và 461 dòng log Keycloak/Caddy không có marker.
Đợt bổ sung đã đọc JSON của 5 session lỗi chữ ký để rà marker, không thấy phát hiện;
chữ ký vẫn không hợp lệ, chưa rõ nguyên nhân. Đã xác định phạm vi backup/export:
55 JSON/CSV không có marker, không tìm thấy backup theo định dạng đã nhận diện.
Đợt rà trong phạm vi công bố đã hoàn tất, có giới hạn; chưa ghi nghiệm thu đầy đủ FR-08 PASS.
Xem [báo cáo FR-08](validation/fr08-2026-11-23/report.md).
Các mục phía dưới là lịch sử; không thay thế cập nhật này.

## Ưu tiên hiện tại — 23/11/2026

Theo yêu cầu người dùng, tạm hoãn điều tra lỗi native passkey cần Try again
(DEFERRED_OPEN). Tiếp tục FR-06/FR-07 bằng sổ bằng chứng, rồi rà FR-08.
Đã có quan sát đăng ký passwordless, LOGIN thành công và lỗi sau Cancel;
chưa hoàn tất tương quan credential đăng ký–đăng nhập hoặc bộ thu thập.
Xem [quy ước và phần bằng chứng còn thiếu](evidence-contract.md).
Các mục bên dưới giữ lại theo mốc lịch sử, không thay thế cập nhật này.

## Ưu tiên mới: chuyển passwordless (21/11/2026)

Người dùng đã duyệt bắt đầu luồng xác minh ban đầu → đăng ký passkey → đăng nhập
thường ngày bằng passkey với UV bắt buộc. Thực hiện kiểm kê cấu hình trước khi
chuyển thử, sau đó thu bằng chứng FR-04–FR-07, rà FR-08 và hồi quy phiên liên quan.
Danh sách ca phiên còn lại bên dưới được giữ; không cần hoàn tất toàn bộ chúng
trước khi bắt đầu kiểm chứng WebAuthn.

Đã chuẩn bị [công cụ kiểm kê và runbook](../infra/passwordless/README.md): 8 test
offline PASS; kiểm tra HTTPS/issuer thật PASS. Chưa có báo cáo cấu hình quản trị,
chưa áp dụng flow mới. [Kết quả bước chuẩn bị](validation/passwordless-preflight/report.md).

Mốc 18/11/2026. Không quy đổi số test PASS thành phần trăm hoàn thành đồ án.

## Đã có bằng chứng

- Readiness: hồ sơ 81 tests PASS ngày 13/11 cho catalog, parsing, validation, tính điểm và CLI.
- Lab: có mã nguồn OIDC, group/binding, thu hồi SID, receipt, guard và advisory lock PostgreSQL.
- Ma trận phiên gồm 19 ca lá; đã ghi PASS A3, A4, A5, A7, A10, A11, A14, A15, A16 (9/19).
- Audit độ nhạy đã thử các lỗi chọn thủ công và đối chứng hợp lệ. A15/A16 đứng riêng có thể bỏ sót lỗi luôn từ chối; cần giữ đối chứng dương. Không gọi đây là exhaustive mutation coverage.
- Các báo cáo giữ thời điểm, hash nguồn và phạm vi giả lập. Đổi code sau mốc chạy cần kiểm tra lại ảnh hưởng, không tự kế thừa PASS.

## Việc tiếp theo theo ưu tiên

1. Hoàn thiện A1/A2 về tạo binding và đổi session key; A12 về từ chối danh tính chưa liên kết dù email trùng.
2. Kiểm chứng concurrency A6a/A6b/A9a bằng connection độc lập, barrier và commit trace. A9b kiểm marker đã lưu; không thay bằng chứng race.
3. A13a kiểm cách ly client khi thu hồi SID.
4. Chốt thiết kế cutoff/recovery cho subject-wide logout rồi triển khai A8/A13b; hiện còn OPEN, không ghi PASS.
5. Gom script thực nghiệm thành runner có cấu trúc, duy trì ca âm tính lẫn đối chứng dương, kiểm tra cleanup và đường đi thực sự được thực thi.
6. Dựng lại lab trên môi trường sạch; hoàn thiện provisioning CA, DB role, realm/client và hướng dẫn chạy.
7. Kiểm chứng end-to-end với Keycloak/WebAuthn thật, sổ sự kiện và trường hợp hủy xác thực; ghi rõ giới hạn quan sát.
8. Rà DB/log/export theo yêu cầu không lộ private key, đưa bằng chứng thực vào rubric và tổng hợp nghiệm thu FR/NFR/IF/DR.

## Giới hạn hiện tại

Django test client không đi qua Caddy. Các bài callback/backchannel dùng khóa RSA tổng hợp và giả lập JWKS; một số còn giả lập token exchange/metadata. Issuer thứ hai trong fixture thường là dữ liệu logic, không chứng minh hai realm thật. Dữ liệu trong evidence/ và DU_LIEU_MAU/ là mẫu. Chưa có chứng nhận an ninh, production readiness hay nghiệm thu toàn bộ đồ án.
