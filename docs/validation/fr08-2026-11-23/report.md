# FR-08: rà private key trong DB, log và export

Ngày kiểm tra: 23/11/2026. Đã hoàn tất đợt rà theo phạm vi công bố, có giới hạn;
**chưa tự đánh dấu nghiệm thu đầy đủ FR-08**. Các tệp audit cũ giữ trạng thái tại
thời điểm tạo để bảo toàn lịch sử.
Phạm vi: lab local Readiness; không đọc volume hoặc dữ liệu VDT tham chiếu.

## Kết quả thực tế

| Phần kiểm tra | Quan sát | Giới hạn |
|---|---|---|
| Schema PostgreSQL ứng dụng | 73 cột; không thấy cột dành cho private key của passkey | Tên cột không chứng minh nội dung các trường tự do |
| Django session | 21 bản ghi; 16 chữ ký hợp lệ. Đợt bổ sung đọc JSON của 5 BadSignature để rà, không thấy marker | 5 chữ ký vẫn không hợp lệ; việc đọc JSON không xác thực nguồn gốc |
| Callback log | 699 byte; không thấy marker private key | Chỉ tệp hiện có tại thời điểm kiểm tra |
| Export inspection.json | 33.728 byte; không thấy marker private key | Chỉ export cấu hình preflight đã chọn |
| Kiểm kê export bổ sung | 55 JSON/CSV đã dò, không có marker; không tìm thấy backup theo các định dạng được nhận diện | 7 gốc thư mục công bố; không gồm volume, dữ liệu ngoài project và định dạng không nhận diện |
| stdout/stderr lab server | Hai tệp đều 0 byte | Không cung cấp bằng chứng nội dung log lịch sử |
| DB Keycloak | Ảnh người dùng: 2 credential passwordless có secret_data object rỗng; 67 event thuộc 4 loại không có marker trong cả hai cột details_json và details_json_long_value | 66 event có nội dung cột dài; chỉ dò các marker đã định nghĩa |
| Log container | Người dùng chạy: Keycloak 297 dòng, Caddy 164 dòng; mọi bộ đếm marker đều 0 | Log hiện còn trong khoảng đã chọn; không gồm log xoay/xóa hoặc mọi dạng mã hóa key |

Chi tiết máy đọc, thời điểm UTC và SHA-256 của nguồn đã rà nằm trong
[app-audit.json](app-audit.json). Không ghi session key, session payload, token,
credential value hay private key vào báo cáo.

Session Django được ký và mã hóa biểu diễn; không được xem là đã mã hóa bảo mật.
BadSignature chỉ xác nhận không kiểm chứng được bằng cấu hình đang dùng. Chưa
xác định là do đổi secret, dữ liệu thử hay nguyên nhân khác; không xóa bản ghi
hoặc đổi secret để làm mất dấu vết.

## Rà nguồn và phương pháp

- Models lưu định danh OIDC, nhóm SID, session binding, revocation marker và receipt.
- Services tạo phiên từ claims đã xác minh; không thấy đường lưu private key WebAuthn.
- Back-channel xác minh token bằng JWKS; diagnostics ghi reason/claim theo allowlist.
- Caddyfile không khai báo access log riêng; điều này không chứng minh container không có log.
- Inspector cấu hình dùng allowlist. Việc không có key trong export này không chứng minh mọi export khác đều sạch.

Script `infra/passwordless/audit_fr08.py` dùng transaction READ ONLY, timeout 10s,
giới hạn 1.000 session và 8 MiB/tệp. Dò tên trường private key, JWK có thành phần
riêng `d`, PEM và một số marker JSON. Đây là dò dấu hiệu, không phải phát hiện mọi
khóa dạng nhị phân, mã hóa hoặc đặt tên khác. Không dump toàn bộ DB.

Năm kiểm thử đối chứng tổng hợp của bộ dò đã PASS: public credential, private JWK
lồng nhau, tên trường private key, marker log và trường `d` không phải JWK.
Các test này kiểm tra bộ dò; không phải năm ca nghiệm thu FR-08.

## Tổng hợp các bước đã thực hiện

1. Đã nhận kết quả `infra/passwordless/fr08-events-long.sql` qua ảnh người dùng;
   phần credential/schema và cả hai cột event đã có bằng chứng trong phạm vi truy vấn.
2. Đã có bản tổng hợp log Keycloak/Caddy do người dùng chạy đến 18:07:54 ngày 23/11
   UTC+7, không phát hiện marker trong phạm vi được quét; xem kết quả phía dưới.
3. Đã rà nội dung năm session BadSignature theo cách kiểm tra dữ liệu không tin cậy.
   Xem [kiểm tra session](session-review.md); không xác nhận nguồn gốc nội dung.
4. Đã kiểm kê và rà backup/export trong phạm vi project:
   [phạm vi và kết quả](export-review.md). Chưa phát hiện marker trong 55 tệp.
5. Đợt rà có bằng chứng cho từng phần DB/log/session/export đã chọn. Kết luận giới hạn:
   chưa phát hiện dấu hiệu private key passkey trong phần được kiểm tra. Không tự
   suy rộng ra dữ liệu ngoài phạm vi hoặc mọi dạng mã hóa khóa.

Từ PowerShell tại thư mục gốc project:

```powershell
Get-Content .\infra\passwordless\fr08-keycloak.sql -Raw |
    docker compose -f .\infra\compose.yaml exec -T keycloak-db psql -X -U keycloak_lab -d keycloak_lab -f -
```

Truy vấn ban đầu đã chạy thành công qua PowerShell của người dùng, ảnh có
BEGIN, SET và ROLLBACK. Bản bổ sung cột event dài cũng đã chạy thành công qua ảnh người dùng.
Agent vẫn không truy cập được Docker API. Có READ ONLY, timeout và ROLLBACK; giới hạn credential/event
ở realm `webauthn-lab`. JSON không hợp lệ làm dừng truy vấn; verbosity terse tránh
in chi tiết payload lỗi. Tên cột `secret_data` hoặc dữ liệu không rỗng tự nó chưa
chứng minh có private key passkey. Các khóa TLS, khóa ký JWT và secret OIDC là loại
khác, không được đánh đồng với private key passkey.

FR-06/FR-07 giữ nguyên mức bằng chứng đã ghi. Lỗi native Try again tiếp tục
**DEFERRED_OPEN**, không được coi là đã sửa bởi đợt rà này.

## Bằng chứng DB Keycloak do người dùng cung cấp

Nguồn: hai ảnh terminal gửi trong hội thoại ngày 23/11/2026, chép lại số liệu
quan sát được; không phải kết quả agent trực tiếp chạy. Ảnh gốc chưa sao chép vào repo.

- Schema credential/event_entity trả 21 cột, có `details_json_long_value`.
- `webauthn-passwordless`: credential_count=2, empty_secret_data_count=2.
- `secret_data`: JSON object, không có tên thuộc tính, occurrence_count=2.
- `credential_data`: mỗi object có aaguid, attestationStatementFormat, counter,
  credentialId, credentialPublicKey, transports; mỗi trường occurrence_count=2.
- CUSTOM_REQUIRED_ACTION: 2; LOGIN: 41; LOGIN_ERROR: 22; UPDATE_CREDENTIAL: 2.
  Tổng 67 event; marker_rows=0 cho cả bốn loại trong cột details_json.

Kết luận giới hạn: hai credential có secret_data rỗng và cấu trúc dữ liệu quan sát
phù hợp với lưu public key/metadata. Chưa kiểm tra giá trị hoặc mã hóa bên trong
credentialPublicKey; không suy ra nơi giữ private key là TPM hoặc chỉ trên thiết bị.
Số lượng credential tính toàn realm, không mặc định cả hai thuộc lab-user-01.
Không nâng toàn bộ FR-08 thành PASS từ các ảnh này.

### Bổ sung cột event dài

Ảnh terminal tiếp theo ngày 23/11/2026 có BEGIN, SET, bốn hàng và ROLLBACK:

| Loại | event_count | long_value_rows | marker_rows | long_marker_rows |
|---|---:|---:|---:|---:|
| CUSTOM_REQUIRED_ACTION | 2 | 2 | 0 | 0 |
| LOGIN | 41 | 41 | 0 | 0 |
| LOGIN_ERROR | 22 | 21 | 0 | 0 |
| UPDATE_CREDENTIAL | 2 | 2 | 0 | 0 |

Tổng 67 event, 66 có nội dung cột dài. Một LOGIN_ERROR không có nội dung cột dài;
đây không tự nó là lỗi hoặc bằng chứng thiếu sự kiện. Không thấy marker đã dò
trong cả hai cột. Không bao gồm mọi loại event hoặc log container.

### Bước rà log container đã chuẩn bị

```powershell
.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\audit_fr08_logs.py
```

Script lấy log hai service keycloak/caddy từ 00:00 ngày 22/11/2026 UTC+7 đến lúc
chạy, tối đa 10.000 dòng/container. Chỉ lưu JSON số lượng/trạng thái vào thư mục
báo cáo; không ghi hoặc in raw log. Đã nhận kết quả Docker thực tế do người dùng chạy.
Log đã xoay/xóa không được khôi phục; rỗng hoặc không đọc được không tính là sạch.
Ba kiểm thử tổng hợp kiểm tra đếm JWK riêng, marker PEM và log rỗng đã PASS.

### Kết quả log nhận lúc 18:08 ngày 23/11/2026

Đã đối chiếu ảnh terminal với tệp
[container-log-audit-20261123T110754904136Z.json](container-log-audit-20261123T110754904136Z.json)
trong workspace; số liệu khớp. Đây là lần người dùng chạy script, không phải agent
trực tiếp truy cập Docker. Khoảng yêu cầu: 00:00 ngày 22/11 đến 18:07:54 ngày 23/11
(UTC+7). Khoảng yêu cầu không chứng minh log còn lưu phủ kín mọi thời điểm đó.

| Service | Số dòng | Return code | Private named fields | Private JWK objects | Text markers |
|---|---:|---:|---:|---:|---:|
| keycloak | 297 | 0 | 0 | 0 | 0 |
| caddy | 164 | 0 | 0 | 0 | 0 |

Cả hai có SCANNED_HEURISTIC, stderr_present=false và tail_limit_may_apply=false.
Tổng 461 dòng, chưa chạm ngưỡng 10.000 dòng/container. Kết luận: không phát hiện
marker đã định nghĩa trong dữ liệu log được trả về. FR-08 vẫn PARTIAL_REVIEW;
còn phạm vi backup/export; năm session đã được rà thêm trong [báo cáo session](session-review.md).
Không cần chạy lại
bước log này nếu chưa phát sinh thay đổi hoặc câu hỏi kiểm chứng mới.
