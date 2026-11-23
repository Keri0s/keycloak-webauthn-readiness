# Kiểm tra năm session BadSignature

Thời điểm: 18:38:37 ngày 23/11/2026 (UTC+7).
Nguồn: truy vấn trực tiếp DB ứng dụng trong transaction READ ONLY, timeout 10s.
Không thay đổi/xóa session, không xuất key, token hoặc payload.

## Kết quả

DB vẫn có 21 session: 16 xác minh chữ ký thành công, 5 BadSignature.
Năm bản ghi đều có cấu trúc bao ngoài dạng payload:timestamp:signature;
payload là JSON nén, giải mã biểu diễn được trong giới hạn 64 KiB.

| Nhóm | Số bản ghi | Quan sát |
|---|---:|---|
| Hết hạn | 4 | Hạn sử dụng thuộc ngày 16/11/2026 |
| Chưa hết hạn | 1 | Không có SessionBinding, không có trường xác thực Django; có state OIDC |
| Có binding | 3 | Cả ba binding đã hết hạn, đều tạo ngày 16/11; không bị đánh dấu revoked |
| Không có binding | 2 | Một hết hạn, một chưa hết hạn |
| Có trường xác thực Django | 3 | Chỉ kiểm tra sự hiện diện; không xuất giá trị |
| Có state OIDC | 3 | Một bản ghi đồng thời có trường xác thực Django |

Các nhóm có giao nhau. Không thấy tên trường private key, JWK có thành phần riêng
hoặc marker PEM/JSON mà bộ dò hỗ trợ trong cả năm payload đã giải mã.

[Kết quả metadata](session-diagnostics-20261123T113837686270Z.json).
Lần đầu chỉ kiểm tra bao ngoài được giữ lại trong tệp diagnostics trước đó;
kết quả lần sau bổ sung việc đọc JSON, không thay đổi kết quả chữ ký.

## Ý nghĩa và giới hạn

- Việc đọc JSON phục vụ rà dữ liệu lưu trữ; **không xác thực nguồn gốc payload**.
  Bộ dò không khôi phục payload thành session ứng dụng và không bỏ kiểm tra chữ ký
  trong mã chạy ứng dụng.
- Không xác định được nguyên nhân BadSignature. Có thể có nhiều nguyên nhân;
  không khẳng định đã đổi SECRET_KEY, có xâm nhập hoặc dữ liệu do test tạo.
- Thời hạn không phải nguyên nhân trực tiếp của lỗi trong lần rà: signing.loads
  được gọi không có max_age. Trạng thái hết hạn được tính riêng từ expire_date.
- Đã đọc các script kiểm thử tạo phiên và guard trong tmp, nhưng chưa có bằng chứng
  nối chính xác năm bản ghi này với một lần chạy test. Không gán nhãn test data.
- Mã Django đang cài (sessions/backends/base.py) trả dict rỗng khi decode gặp
  BadSignature. Guard ứng dụng yêu cầu đăng nhập, binding và hạn còn hiệu lực.
  Đây là kiểm tra nguồn, không phải một lần kiểm thử HTTP mới với năm cookie.
- Không phát hiện marker không phải chứng minh không thể có private key ở mọi
  dạng mã hóa. Dữ liệu state OIDC còn trong session không tự nó là private key passkey.

## Kiểm chứng công cụ

Bốn test tổng hợp PASS: JSON đọc được vẫn mang nhãn chữ ký không hợp lệ và không
xuất giá trị; phát hiện private JWK trong payload nén; chặn giải nén vượt 64 KiB;
từ chối dữ liệu không hợp lệ. Công cụ audit độc lập, không sửa code xác thực.

Đã giải quyết phần thiếu khả năng đọc nội dung năm bản ghi trong phạm vi dò marker
của FR-08. Chữ ký vẫn lỗi và nguyên nhân vẫn chưa xác định; chưa xóa bản ghi.
Phần tiếp theo của FR-08 là xác định và rà phạm vi backup/export.
