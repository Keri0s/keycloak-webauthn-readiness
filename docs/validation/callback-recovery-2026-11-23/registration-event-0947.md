# FR-06 — quan sát sự kiện đăng ký ngày 23/11/2026

Nguồn: ảnh chi tiết Keycloak Events do người dùng cung cấp trong hội thoại.
Ảnh gốc chưa được sao chép vào repository. Không phải bản xuất API.

| Trường | Giá trị quan sát |
| --- | --- |
| Thời gian hiển thị | November 23, 2026 at 9:47 AM; độ chính xác theo phút, ảnh không ghi múi giờ |
| Loại sự kiện | UPDATE_CREDENTIAL, biểu tượng thành công |
| Client | app-lab |
| Username | lab-user-01 |
| credential_type | webauthn-passwordless |
| custom_required_action | webauthn-register-passwordless |
| public_key_credential_label | Edge-Passkey |
| public_key_credential_id | Có giá trị, bắt đầu gGCU; chưa nhập toàn bộ từ ảnh để tránh sai ký tự |
| public_key_credential_aaguid | Có giá trị; không dùng trường này để suy ra nơi lưu khóa |

Sự kiện có đủ các loại trường cần thiết cho một dòng đăng ký thành công:
thời gian, kết quả, tài khoản và WebAuthn credential ID. Việc chép đầy đủ ID
và tương quan với LOGIN vẫn cần hoàn tất; chưa đánh dấu FR-06 toàn bộ PASS.
Nhãn Edge-Passkey do người dùng đặt không chứng minh provider hoặc TPM-only.

Đây là sự kiện khác ngày với lần đăng ký 22/11 khoảng 19:47 đã ghi trước đó.
Credential ID nhìn thấy cũng khác LOGIN 22/11 khoảng 20:03 (bắt đầu dndR).
Không ghép hai sự kiện đó thành cặp đăng ký–đăng nhập cùng credential.

Bước tiếp: lấy LOGIN thành công sau 09:47 ngày 23/11 có cùng username,
client, credential_type và đối chiếu toàn bộ public_key_credential_id.
Nếu có nhiều credential, chọn theo ID thay vì chỉ theo tên tài khoản hoặc nhãn.
Không lưu code_id, IP hoặc query phiên từ ảnh vào hồ sơ này.

## Đối chiếu ảnh LOGIN cùng lượt đăng ký

Ảnh tiếp theo do người dùng cung cấp hiển thị LOGIN thành công lúc 09:47
ngày 23/11/2026, username lab-user-01, client app-lab, credential_type
webauthn-passwordless. public_key_credential_id hiển thị khớp với ảnh
UPDATE_CREDENTIAL và nhãn Edge-Passkey cũng khớp.

LOGIN vẫn chứa custom_required_action=webauthn-register-passwordless;
code_id hiển thị giống sự kiện đăng ký (chỉ đối chiếu trực quan, không lưu giá trị).
Vì vậy hai ảnh hỗ trợ liên kết sự kiện trong cùng lượt đăng ký. Không coi
LOGIN này là bằng chứng độc lập rằng passkey mới đã được sử dụng để tạo
assertion trong một lần đăng nhập tiếp theo. Thời gian trùng phút đơn lẻ
không đủ cho kết luận; ở đây còn có required action và mã giao dịch khớp.

Phần đã xác nhận qua UI: sự kiện đăng ký và LOGIN trong lượt đó có cùng ID.
Phần còn cần: LOGIN từ lượt đăng nhập mới, không kèm thao tác đăng ký,
đối chiếu ID và kết quả vào ứng dụng. Có thể dùng một sự kiện đã tồn tại
sau 09:47; không bắt buộc đăng ký lại hoặc thử lại nếu có bằng chứng phù hợp.
FR-06 vẫn IN_PROGRESS; lỗi native retry tiếp tục DEFERRED_OPEN.

## Đã đối chiếu hai lần LOGIN tiếp theo — 13:55 và 13:56

Nguồn: hai ảnh Events người dùng cung cấp, ngày hiển thị 23/11/2026.
Không phải xuất API; độ chính xác thời gian theo phút, không có múi giờ
trong phần nội dung sự kiện. Ảnh gốc chưa sao chép vào repository.

| Trường | Đăng ký 09:47 | LOGIN 13:55 | LOGIN 13:56 |
| --- | --- | --- | --- |
| username | lab-user-01 | lab-user-01 | lab-user-01 |
| client | app-lab | app-lab | app-lab |
| credential_type | webauthn-passwordless | webauthn-passwordless | webauthn-passwordless |
| public_key_credential_id | gGCUOjoWoGQwWgLe3SMDow | gGCUOjoWoGQwWgLe3SMDow | gGCUOjoWoGQwWgLe3SMDow |
| Kết quả | UPDATE_CREDENTIAL thành công | LOGIN thành công | LOGIN thành công |
| web_authn_authenticator_user_verification_checked | Không thấy trường này | true | true |
| custom_required_action đăng ký | Có | Không thấy trong chi tiết ảnh | Không thấy trong chi tiết ảnh |

ID đầy đủ ở bảng được chép và đối chiếu trực quan giữa các ảnh; thay thế
ghi chú trước đó chỉ lưu tiền tố gGCU. Hai LOGIN có code_id khác nhau và
khác lượt đăng ký; chỉ ghi nhận sự khác nhau, không lưu giá trị code_id.
Danh sách có CODE_TO_TOKEN cùng phút với mỗi LOGIN, nhưng chưa mở chi tiết
để tương quan từng giao dịch. Không đếm CODE_TO_TOKEN thành login thứ hai.

Kết luận: đã có cặp bằng chứng UI đăng ký–đăng nhập sau đó bằng cùng WebAuthn
credential, và Keycloak ghi nhận kiểm tra UV=true trong hai LOGIN này.
Phép đối chiếu credential của FR-06 đạt trong phạm vi ba sự kiện quan sát.
Không suy ra mọi lần đều được ghi, server chắc chắn từ chối UV=0, hoặc
ứng dụng đã trả /private/ 200 ở chính hai lượt này chỉ từ ảnh Keycloak.
FR-06 toàn bộ còn phần thu thập/sổ có cấu trúc và kiểm tra tính đầy đủ.
Tiếp theo FR-07: dùng ca Cancel có quan sát thao tác, LOGIN_ERROR và kiểm tra
không tạo phiên ứng dụng mới; có thể tận dụng ca ngày 22/11 đã ghi nếu đủ dữ liệu.
