# FR-05/IF-03: nối LOGIN với lượt vào ứng dụng

Trạng thái: đã thực hiện ca thật; [kết quả 18:59:55](fr05-observed-185955.md)
ghi PASS_OBSERVED cho FR-05/IF-03. Hướng dẫn dưới đây giữ để tái lập khi cần;
không yêu cầu chạy lại ca đã có bằng chứng.

## Cơ chế đối chiếu

`/private/` chỉ tạo response headers sau khi `require_active_binding` thành công:

- X-Lab-Session-Ref: SHA-256 của issuer, client_id, SID, nối bằng newline.
- X-Lab-Subject-Ref: SHA-256 của issuer và subject, nối bằng newline.
- X-Lab-Binding-Created: thời điểm tạo binding, UTC.

Các mã này không cấp quyền truy cập. Không đưa cookie, token, SID gốc hoặc state
vào header bằng chứng. Vẫn giữ no-store, kiểm tra binding và mọi kiểm tra OIDC.
Không thêm nội dung kỹ thuật lên giao diện sử dụng thường ngày.

SQL `infra/passwordless/fr05-login.sql` chỉ đọc LOGIN thành công của lab-user-01,
app-lab, realm webauthn-lab trong 30 phút gần nhất (tối đa 20 bản ghi). Nó xuất
credential ID và các mã băm tương ứng từ event. Chi tiết JSON ngắn/dài được ghép;
nếu các trường dùng đối chiếu khác nhau thì detail_conflict=true, không chốt kết quả.

Giả thuyết cần xác minh khi chạy thật: event.session_id khớp claim sid và
event.user_id khớp claim sub trong cấu hình lab này. Không tự đổi ánh xạ để ép khớp.
Mã session có thể dùng chung giữa nhiều lượt trong cùng phiên SSO; chỉ mã khớp
chưa đủ xác định một lần đăng nhập. Cần thời gian binding, quan sát trình duyệt
và một LOGIN passwordless phù hợp; nếu nhiều ứng viên thì giữ chưa xác định.

## Thao tác một lượt

1. Nạp code mới bằng cách dừng đúng terminal Django với Ctrl+C rồi chạy lại:

   ```powershell
   cd D:\Projects\Do-an-thuctap-totnghiep\apps\lab
   .\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:18000 --noreload
   ```

   Không khởi động máy chủ thứ hai nếu cổng đã được dùng; nếu server đang autoreload
   thì có thể code đã nạp. Xác nhận bằng việc thấy ba response headers bên dưới.

2. Đăng xuất nếu còn đăng nhập. Trong trình duyệt mở DevTools → Network, bật
   Preserve log/Keep log rồi bắt đầu từ
   `https://app.readiness.test:9443/auth/login/`. Dùng lab-user-01 và passkey đã có.
   Nếu lỗi native xảy ra, có thể Try again theo cách đã dùng và ghi nhận điều đó;
   không tuyên bố lỗi đã hết.
3. Khi vào trang chào lab-user-01, chọn request `private/` → Headers.
   Ghi HTTP 200 cùng ba **Response Headers** X-Lab-* ở trên. Chỉ chụp phần đó
   và tên trang/tài khoản; không gửi Request Headers, Cookie, Set-Cookie hoặc HAR.
4. Trong vòng 30 phút, từ thư mục gốc project chạy:

   ```powershell
   Get-Content .\infra\passwordless\fr05-login.sql -Raw |
       docker compose -f .\infra\compose.yaml exec -T keycloak-db psql -X -U keycloak_lab -d keycloak_lab -f -
   ```

5. Đối chiếu: session_ref và subject_ref khớp header; LOGIN xảy ra trước binding
   được tạo trong cùng lượt; credential_type=webauthn-passwordless;
   credential ID trùng đăng ký 09:47 (`gGCUOjoWoGQwWgLe3SMDow`), UV=true;
   không phải LOGIN kèm required action đăng ký; detail_conflict=false.
   Nếu ID khác, tìm đăng ký tương ứng thay vì khẳng định cùng credential cũ.

Giữ nguồn ảnh/metadata và độ chính xác thời gian thực tế; không đoán timestamp
hoặc dựng bằng chứng. Chưa chạy SQL trên DB Keycloak từ agent do hạn chế Docker.
Các test offline chỉ kiểm tra headers được tạo sau guard, không lộ định danh gốc,
phân biệt scope và giữ hồi quy callback; không thay thế thao tác trình duyệt thật.
