# Độ tin cậy 7 ca PASS còn lại

Trợ lý trực tiếp chạy trên PostgreSQL local theo yêu cầu người dùng ngày 18/11/2026. Thời gian UTC chính xác, hash nguồn và kết quả từng lượt nằm trong results.json; log theo tên ca và variant nằm cùng thư mục. Harness: tmp/audit_remaining_reliability.py.

## Kết quả

Cả 7 baseline PASS. Cả 7 lỗi mục tiêu đều bị phát hiện bằng AssertionError đúng điều kiện hành vi dự kiến, sau đó cleanup hoàn thành. Một lỗi bổ sung sống sót qua A15 riêng lẻ.

| Ca | Lỗi cố ý trong bộ nhớ | Assertion bắt lỗi |
| --- | --- | --- |
| A3 | Sau thu hồi đúng, xóa backend phiên SID khác cùng subject | control_snapshot giữ nguyên |
| A4 | Sau thu hồi, khôi phục một backend session đích | backend session đích phải không tồn tại |
| A5 | Sau thu hồi đúng, xóa backend phiên cùng SID ở issuer khác | control_snapshot giữ nguyên |
| A7 | Lần thu hồi thứ hai đổi timestamp marker | revocation_snapshot giữ nguyên |
| A11 | Khi tạo binding thứ sáu, xóa backend các binding cũ cùng group | original_snapshot giữ nguyên |
| A14 | Service tạo phiên luôn từ chối, kể cả callback hợp lệ | callback hợp lệ phải trả 302 |
| A15 | Bỏ nhánh kiểm tra subject sở hữu group ở callback sau khi tạo fixture | callback xung đột phải trả 403 |
| A15 bổ sung | Sau 5 lần tạo fixture, từ chối mọi lần tạo phiên tiếp theo | Không phát hiện: ca gốc PASS |

A15 bổ sung cho thấy ca âm tính riêng lẻ không chứng minh callback hợp lệ được chấp nhận. Mutant được kích hoạt sau fixture để kiểm tra hành vi callback, không phải bằng chứng toàn hệ thống chấp nhận implementation luôn từ chối ngay từ setup. A14 có đối chứng callback hợp lệ và đã phát hiện unconditional rejection trong thí nghiệm riêng. Do đó cần giữ A14 và A15 chạy cùng bộ, không dùng A15 đứng riêng để kết luận cả hai chiều hợp lệ/không hợp lệ.

A3/A4/A5 dùng cùng script và fixture; harness chỉ giới hạn vòng lặp từng lần ở một ID để gắn đúng lỗi cần kiểm tra. Không tính chúng là ba bộ kiểm thử độc lập. Lỗi A4 chứng minh assertion kiểm tra backend có tác dụng ngay cả khi lớp guard có thể tiếp tục chặn truy cập.

## Cách thực hiện và giới hạn

Lỗi chỉ tồn tại trong process audit thông qua patch hoặc compile AST, mã ứng dụng và các script gốc không đổi. Các wrapper gây lỗi bảo toàn kết quả trả về bình thường khi phù hợp để thử assertion dữ liệu thay vì chỉ bắt số đếm. Mỗi lần tạo dữ liệu UUID tổng hợp riêng, finally dọn và assertion kiểm tra cleanup. Không ghi token, session key hoặc khóa riêng vào log.

Trong quá trình xây harness, bộ đếm dùng chung và patch sai vị trí import từng làm lỗi không được kích hoạt. Đã sửa, chạy lại toàn bộ; những lần đó không được tính là mutant bị phát hiện. Log hiện tại là lần chạy hoàn chỉnh cuối cùng.

Đây là 7 lỗi được chọn thủ công và 1 đối chứng sống sót, không phải exhaustive mutation coverage. Chưa kiểm tra bỏ từng kiểm tra JWT ở A14, race, mạng hay Keycloak thực trong đợt này. A14/A15 vẫn giả lập trao đổi token, metadata và JWKS. Tạo fixture qua service thật vẫn có rủi ro chia sẻ sai sót giữa setup và implementation. Không suy từ kết quả này ra không còn lỗi.

Giữ nguyên 8/19 ca gốc PASS. Kết hợp đợt A16 trước, cả 8 ca đã có ít nhất một thí nghiệm gây lỗi được phát hiện. Điều đó tăng bằng chứng về các assertion được thử, không chứng nhận toàn bộ yêu cầu hay cả hệ thống.

## Chạy lại

Từ thư mục gốc project:

```powershell
.\apps\lab\.venv\Scripts\python.exe apps/lab/manage.py shell -c "exec(compile(open('tmp/audit_remaining_reliability.py', encoding='utf-8-sig').read(), 'tmp/audit_remaining_reliability.py', 'exec'))"
```

Chạy lại thay log trong thư mục này. Cần PostgreSQL lab đang hoạt động. Không dùng Python -O vì script sử dụng assert.
