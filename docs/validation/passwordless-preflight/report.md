# Chuẩn bị chuyển passwordless — 21/11/2026

Trạng thái: PREPARING / chưa áp dụng flow mới. Người dùng yêu cầu bắt đầu triển khai
chiến lược đã đề xuất. Nguồn: kiểm tra trực tiếp từ workspace N15 của trợ lý.

| Phép kiểm tra | Expected | Observed | Phạm vi |
| --- | --- | --- | --- |
| Đọc cấu hình bằng kcadm trong container | Đọc được realm lab | Docker API permission denied, exit 1 | Không xác định được cấu hình runtime qua Docker |
| HTTPS discovery qua CA public của lab | TLS hợp lệ, issuer đúng realm | `HTTPS certificate and OIDC issuer: OK`, exit 0 | Kết nối thực tới auth.readiness.test:9443; không kiểm flow |
| Unittest công cụ kiểm kê | 8 test đạt | Ran 8 tests, OK, exit 0 | Offline; mock Admin API/HTTP, không đăng nhập thật |

Lệnh đã chạy từ thư mục gốc:

```powershell
.\apps\lab\.venv\Scripts\python.exe -m unittest discover -s infra/passwordless -p "test_*.py" -v
.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\inspect_keycloak.py --check-connectivity
```

Test kiểm việc loại bỏ secret/SMTP/unknown fields khỏi báo cáo; ưu tiên client
override, không fallback khi override không giải được; bỏ execution disabled khỏi
danh sách hoạt động; collector chỉ GET; HTTP redirect không được theo; client
thiếu hoặc không rõ thì dừng. Đây không phải đánh giá toàn diện rò rỉ dữ liệu.

Mã ứng dụng và cấu hình Keycloak chưa thay đổi. Chưa đọc được Browser Flow thực
tế, required actions hoặc WebAuthn Passwordless Policy bằng quyền quản trị.
Không tăng số ca SESSION_MAPPING_A PASS và không nghiệm thu FR-04–FR-08.

Người dùng chạy công cụ không kèm `--check-connectivity`, nhập thông tin quản trị
ngay tại terminal. Báo cáo mới nằm trong thư mục UTC con, chứa allowlist cấu hình,
thời điểm và SHA256 script. Không đọc user/credential hoặc lưu token/mật khẩu.
Nếu admin-cli không phù hợp với cách đăng nhập quản trị, dùng Admin Console;
không tắt MFA để phục vụ công cụ.

Bước phụ thuộc tiếp theo: đối chiếu báo cáo cấu hình rồi tạo thay đổi flow/policy
và phương án khởi tạo có kiểm soát. Không đoán cấu hình từ file realm mẫu.
