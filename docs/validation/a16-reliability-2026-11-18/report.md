# Kiểm tra độ tin cậy A16

Thực thi trực tiếp bởi trợ lý theo yêu cầu người dùng, ngày 18/11/2026 lúc 00:28:00–00:28:03 (UTC+7). Thời gian chính xác và SHA256 từng file nằm trong [results.json](results.json). Đây là kiểm tra riêng A16, không phải đánh giá độ tin cậy của cả 19 ca.

## Kết luận

A16 gốc tái lập được PASS trên PostgreSQL thật. Nó phát hiện được hai lỗi cố ý đưa vào. Tuy nhiên, lỗi từ chối mọi logout vẫn vượt qua A16 gốc. Một ca chỉ kiểm tra từ chối không đủ chứng minh ứng dụng cũng chấp nhận yêu cầu hợp lệ.

Đã bổ sung đối chứng đúng chủ sở hữu trong harness riêng. Mã ứng dụng gốc vượt qua đối chứng, còn lỗi từ chối mọi logout bị phát hiện. Không sửa mã ứng dụng hoặc script A16 gốc. Số ca gốc được ghi nhận PASS vẫn là 8/19.

## Đối chiếu đặc tả

Nguồn yêu cầu là A16 trong `tests/fixtures/session-mapping-cases.yaml`. Điều kiện mong đợi được đối chiếu trước khi tạo lỗi.

| Yêu cầu | Kiểm tra trong script gốc |
| --- | --- |
| Logout dùng SID của U1 nhưng subject U2 bị từ chối | Token ký thật, xác minh JWT, spy gọi service thật với đúng tham số, HTTP 400 và JSON invalid_request |
| Groups, bindings, markers không đổi | So sánh toàn bộ giá trị trước/sau trong phạm vi fixture |
| Cả 5 backend session còn đăng nhập | `get_user` với từng session key, so sánh user ID |
| Cả 5 phiên được truy cập và giữ đúng danh tính | Request mới tới `/private/`, HTTP 200 và user ID |
| Không giữ receipt từ giao dịch bị từ chối | Snapshot receipt và truy vấn không tồn tại receipt |

Fixture có 4 group, 5 session, hai user, hai issuer logic. Giới hạn so sánh theo UUID riêng, không phải snapshot toàn database. Tạo fixture qua service thật có nguy cơ chia sẻ lỗi với implementation; việc kiểm tra số lượng, group dùng chung, user và truy cập ban đầu giảm nhưng không loại bỏ nguy cơ này.

## Thí nghiệm đã chạy

| Lần chạy | Thay đổi trong bộ nhớ | Quan sát | Diễn giải |
| --- | --- | --- | --- |
| 01 | Không thay đổi | PASS | Tái lập baseline |
| 02 | Bỏ kiểm tra chủ sở hữu trong revoke service | FAIL tại `response.status_code == 400` | Phát hiện chấp nhận logout sai chủ |
| 03 | Sửa subject group rồi ném PermissionDenied | FAIL tại `snapshot() == before` | Phát hiện sai dữ liệu dù HTTP 400 đúng |
| 04 | Revoke service luôn ném PermissionDenied | PASS | Lỗi sống sót qua ca âm tính gốc |
| 05 | Mã gốc, thêm logout đúng chủ | PASS | Đối chứng dương hoạt động |
| 06 | Service luôn từ chối, thêm đối chứng đúng chủ | FAIL tại `positive_owner_http` | Đối chứng bổ sung bắt lỗi sống sót |

Lỗi 02 dùng AST để bỏ đúng một nhánh kiểm tra trong function, không sửa file. Lỗi 03 thay processor trong bộ nhớ bằng một lỗi có chủ đích ghi sai group thuộc fixture và từ chối, nhằm thử oracle bảo toàn dữ liệu. Lỗi 04/06 thay revoke function bằng unconditional rejection. Đây là ba lỗi được chọn thủ công, không phải chiến dịch mutation toàn mã nguồn hay điểm chất lượng tổng quát.

Đối chứng dương ký token mới với subject U1 và JTI mới. Nó yêu cầu HTTP 200, hai backend session đích bị xóa và `/private/` trả 403, ba session đối chứng vẫn truy cập được đúng danh tính, receipt đã xử lý được lưu sau commit.

Mỗi lần chạy dùng fixture UUID mới. Harness chỉ chấp nhận mutant bị phát hiện khi lỗi là AssertionError đúng dòng dự kiến và cleanup thành công. Lỗi kết nối, setup, lỗi bất ngờ hoặc cleanup không được tính là phát hiện mutant. Mỗi lần cleanup được kiểm tra lại bằng query. Hàm đã được khôi phục và hash các file nguồn theo dõi không đổi.

## Tái lập

Chạy từ `D:\Projects\Do-an-thuctap-totnghiep\apps\lab` khi PostgreSQL lab đang chạy. Harness tạo rồi xóa dữ liệu tổng hợp, không dùng tài khoản người dùng hiện hữu.

```powershell
.\.venv\Scripts\python.exe manage.py shell -c "exec(compile(open('../../tmp/audit_a16_reliability.py', encoding='utf-8').read(), '../../tmp/audit_a16_reliability.py', 'exec'))"
```

Harness ở `tmp/audit_a16_reliability.py`. Sáu log `.txt` và `results.json` trong thư mục báo cáo được tạo trực tiếp từ lần chạy. Chạy lại sẽ thay các file kết quả ở đây. `matches_experiment_expectation: true` nghĩa là thí nghiệm cho kết quả dự kiến; với mutant sống sót ở lần 04, nó không có nghĩa mutant bị phát hiện.

## Giới hạn và bước tiếp theo

- JWT và database thật, nhưng JWKS được giả lập. HTTP sử dụng Django test client, không đi qua HTTPS proxy hay Keycloak thật.
- Không kiểm tra race, mạng, key rotation hoặc thu hồi theo subject trong đợt này.
- Không đọc hoặc ghi token/session key/private key vào hồ sơ. Khóa RSA tổng hợp chỉ tồn tại trong bộ nhớ.
- Hash chỉ bao phủ các file liệt kê trong metadata, không phải toàn môi trường hoặc toàn repository.
- Các ca A3/A4/A5/A7/A11/A14/A15 chưa được mutation audit trong đợt này. PASS cũ vẫn là bằng chứng trong phạm vi cũ, không được nâng thành chứng nhận an toàn.
- Nên chạy harness này cùng A16 để giữ đối chứng dương, rồi rà lần lượt các ca còn lại và bổ sung đối chứng phù hợp. Không tăng số ca gốc chỉ vì có thêm thí nghiệm mutation.
