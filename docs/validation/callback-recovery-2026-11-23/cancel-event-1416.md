# FR-07 — ca hủy đăng nhập ngày 23/11/2026

Kết quả: PASS_OBSERVED trong phạm vi ca thủ công được cung cấp bằng ảnh.
Không phải xác nhận toàn bộ sổ bằng chứng hoặc FR-08.

## Nguồn và thao tác

Người dùng gửi bốn ảnh để đáp ứng hướng dẫn đăng xuất, bắt đầu lượt đăng nhập,
bấm Cancel trong Windows Security, mở LOGIN_ERROR và thử /private/ trong
cùng trình duyệt. Ảnh cho thấy Chrome cho thao tác đăng nhập/truy cập app;
Edge dùng xem Keycloak Admin Console. Không có video ghi trực tiếp cú bấm
Cancel; diễn giải thao tác theo ngữ cảnh ca người dùng thực hiện.
Ảnh gốc nằm trong hội thoại, chưa sao chép vào repository.

## Expected và observed

| Kiểm tra | Expected | Observed |
| --- | --- | --- |
| Kết quả UI sau hủy | Đăng nhập không hoàn tất | Trang Passkey Error, thông báo operation not allowed or timed out |
| Ghi sự kiện | Có dòng thất bại | LOGIN_ERROR lúc 14:16 ngày 23/11/2026, client app-lab |
| Loại credential | Passwordless | credential_type=webauthn-passwordless |
| Mã lỗi | Ghi lỗi WebAuthn | error=not_allowed; web_authn_authentication_error=webauthn-error-api-not-allowed; detail có NotAllowedError |
| Truy cập trang bảo vệ | Bị từ chối sau ca hủy | Chrome tại app.readiness.test:9443/private/ hiển thị 403 Forbidden lúc đồng hồ 14:17 |
| Private key trong phần bằng chứng | Không xuất hiện | Các trường sự kiện trong ảnh không chứa private key; không suy ra toàn bộ DB/log an toàn |

Danh sách Events còn hiển thị LOGOUT cùng phút 14:16. Thời gian sự kiện
chỉ có độ chính xác theo phút; ảnh không hiển thị múi giờ trong trường event.
Không lưu IP, code_id hoặc query phiên vào báo cáo.

## Cách ghi dòng thất bại

- operation: authentication; outcome: failure; source_event_type: LOGIN_ERROR.
- lab_account từ nguồn event: chưa xác định (No user details).
- Tài khoản hiển thị trên UI thử nghiệm: lab-user-01, ghi riêng như ngữ cảnh.
- credential_id: chưa xác định, không gán ID của lần đăng nhập thành công trước.
- Nguyên nhân thao tác: hủy theo kịch bản người dùng thực hiện. NotAllowedError
  tự nó không phân biệt được cancel, timeout và các nguyên nhân bị từ chối khác.

403 chứng minh yêu cầu truy cập quan sát bị chặn; chưa phải kiểm tra database
khẳng định không tồn tại bất kỳ session row nào. Không gọi 403 là lỗi mới cần sửa.
Lỗi native cần Try again trước đây tiếp tục DEFERRED_OPEN và không được
đánh dấu đã khắc phục bởi kết quả của ca hủy.

## Bước tiếp theo

FR-08: rà schema và đường lưu dữ liệu/log/export của app và Keycloak,
phân biệt public key/credential ID, mật khẩu ứng dụng, khóa ký token/TLS
với private key của passkey. Không xuất giá trị secret để làm bằng chứng.
