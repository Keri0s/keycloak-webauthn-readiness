# A10 — Phiên authenticated thiếu binding

Trợ lý trực tiếp thực thi trên PostgreSQL local ngày 18/11/2026 theo yêu cầu tiếp tục kiểm thử. Thời gian chính xác, phiên bản, hash nguồn và kết quả nằm trong [results.json](results.json). Script là `tmp/check_a10.py`.

Baseline PASS: tạo user tổng hợp không có mật khẩu khả dụng, một phiên OIDC bound và một phiên Django authenticated bằng force_login nhưng không có binding. Đọc backend chứng minh user đúng; truy vấn chứng minh thiếu binding; request mới `/private/` trả 403. Phiên có binding đối chứng trả 200 và đúng user. Không phát sinh binding cho phiên thiếu binding, không gọi django.contrib.auth.authenticate trong request thử.

`resolved_user: null` trong đặc tả được hiểu là route không chấp nhận danh tính để cấp quyền truy cập. Django request.user vẫn authenticated là điều kiện đầu vào có chủ đích, không phải kết quả cấp quyền.

Hai lỗi trong bộ nhớ đều bị phát hiện:

- Bỏ guard binding và trả đối tượng chứa request.user: phiên thiếu binding nhận HTTP 200, assertion orphan_denied thất bại.
- Guard luôn từ chối: phiên hợp lệ nhận HTTP 403, assertion valid_allowed thất bại.

Mỗi lượt dùng UUID mới; dữ liệu tổng hợp được cleanup và truy vấn xác minh không còn user, identity, session, group, binding, marker. Hàm guard được khôi phục và hash file nguồn theo dõi không đổi. Mã ứng dụng không sửa.

Giới hạn: test client nội bộ Django, không qua Caddy/HTTPS/Keycloak. force_login chỉ là cách tạo fixture authenticated không binding, không chứng minh luồng mật khẩu thực. Spy authenticate cùng user không có mật khẩu cung cấp bằng chứng cho route được kiểm tra, không phải rà soát mọi cơ chế fallback toàn ứng dụng. Mutation được chọn thủ công, không exhaustive.

Lượt chạy đầu bị ngắt khi PostgreSQL chưa nhận kết nối, chưa có kết quả A10. Sau khi người dùng bật Docker, lượt chạy ghi trong results.json hoàn tất cả ba thí nghiệm.

Chạy từ thư mục gốc:

```powershell
.\apps\lab\.venv\Scripts\python.exe apps/lab/manage.py shell -c "exec(compile(open('tmp/check_a10.py', encoding='utf-8-sig').read(), 'tmp/check_a10.py', 'exec'))"
```
