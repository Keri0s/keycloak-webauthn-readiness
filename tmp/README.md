# Script thực nghiệm được công bố

Thư mục này giữ tên lịch sử để đối chiếu hash trong báo cáo. Chỉ các file liệt kê dưới được đưa vào Git; các tệp tạm khác tiếp tục bị bỏ qua.

| Script | Mục đích |
| --- | --- |
| check_a3_a5.py | Thu hồi đúng SID, đủ backend sessions và cách ly issuer |
| check_a7.py | Thu hồi lặp bảo toàn trạng thái |
| check_a10.py | Phiên authenticated thiếu binding và hai lỗi đối chứng |
| check_a11.py | Thêm binding vào group có sẵn |
| check_a14.py | Callback thiếu/rỗng SID và callback hợp lệ đối chứng |
| check_a15.py | Callback SID/subject xung đột |
| check_a16.py | Logout SID/subject xung đột |
| audit_a16_reliability.py | Gây lỗi có chủ đích trong bộ nhớ, đối chứng logout hợp lệ |
| audit_remaining_reliability.py | Audit các ca PASS còn lại tại mốc trước A10 |

Cần lab PostgreSQL đã migrate, .env local và dependencies apps/lab. Từ gốc project, ví dụ:

```powershell
.\apps\lab\.venv\Scripts\python.exe apps/lab/manage.py shell -c "exec(compile(open('tmp/check_a10.py', encoding='utf-8-sig').read(), 'tmp/check_a10.py', 'exec'))"
```

Script dùng dữ liệu tổng hợp riêng và cleanup; chỉ chạy trong lab của bạn. Mutation chỉ trong process kiểm thử, không sửa file ứng dụng. Không coi lỗi setup là mutant bị phát hiện. Đọc giới hạn của từng báo cáo trong docs/validation/ trước khi diễn giải kết quả.
