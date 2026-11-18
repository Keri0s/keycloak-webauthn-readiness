# Kiểm tra trước khi xuất bản ngày 18/11/2026

- Đã chạy `python -m pytest tests -q -p no:cacheprovider`: 81 passed in 1.51s.
- Đã chạy `apps/lab/manage.py check` bằng venv của lab: System check identified no issues (0 silenced).
- Đã đối chiếu remote main với local trước commit; cùng commit f1e97914bc6017bfa9436223acd7c67a150fed04.
- Đã kiểm tra danh sách file Git, loại .env/runtime/DB/private keys/venv và chỉ cho phép các probe cần thiết trong tmp/.
- Rà mẫu token/khóa và literal credential không thấy cờ cần xử lý còn lại trong danh sách đã rà. Đây không phải chứng nhận không có secrets bằng mọi phương pháp.
- Đã chuyển Django SECRET_KEY sang biến môi trường, thêm .env.example không có giá trị bí mật. Khóa local được tạo riêng nếu chưa có; thay khóa có thể yêu cầu đăng nhập lại.
- Đã bỏ credentials khỏi realm dữ liệu mẫu; không thay realm đang chạy.
- README cập nhật phạm vi thực tế; không giữ khẳng định đúng tuyệt đối hay chứng nhận không lộ khóa riêng khi chưa đủ bằng chứng.

Không chạy lại toàn bộ 19 kịch bản phiên trong lượt chuẩn bị publish. Metadata kiểm thử trước đó giữ nguyên thời điểm và hash lịch sử. Kiểm tra Django không thay thế kiểm thử end-to-end.
