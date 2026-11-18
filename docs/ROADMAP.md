# Tiến độ và công việc tiếp theo

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
