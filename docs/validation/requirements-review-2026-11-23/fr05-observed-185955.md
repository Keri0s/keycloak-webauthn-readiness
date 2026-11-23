# FR-05 / IF-03 — lượt đăng nhập 18:59:55 ngày 23/11/2026

Kết quả: **PASS_OBSERVED cho ca thực được đối chiếu**. Người dùng thực hiện trong
Edge và gửi ba ảnh: trang /private/ với HTTP 200, ba response headers, kết quả
truy vấn SQL chỉ đọc Keycloak. Agent đối chiếu ảnh, không trực tiếp dùng PIN.
Ảnh gốc ở hội thoại, chưa sao chép vào repo. Không chép Cookie/Set-Cookie hoặc
query string xuất hiện trong ảnh tổng thể vào bằng chứng này.

| Điểm kiểm tra | Quan sát |
|---|---|
| Tài khoản / client | lab-user-01 / app-lab |
| Credential đăng ký 09:47 | gGCUOjoWoGQwWgLe3SMDow |
| Credential LOGIN mới | gGCUOjoWoGQwWgLe3SMDow — trùng đăng ký |
| Loại / UV | webauthn-passwordless / true |
| Required action | Không có giá trị hiển thị ở dòng SQL |
| detail_conflict | f (false) |
| LOGIN UTC | 2026-11-23T11:59:55.655Z |
| Binding created UTC | 2026-11-23T11:59:55.861010+00:00 |
| Thứ tự | Binding tạo sau LOGIN khoảng 206 ms |
| Trình duyệt | GET https://app.readiness.test:9443/private/ → 200 OK |
| Giao diện | Trang được bảo vệ; Xin chào, lab-user-01 |
| Cache | Response có no-store |
| Số ứng viên trong kết quả SQL | 1 LOGIN trong cửa sổ 30 phút theo bộ lọc |

Hai mã sau khớp toàn bộ giữa response headers và SQL (ghép các dòng bị xuống hàng
trong ảnh headers, không thay đổi ký tự):

```text
session_ref = 8f926a52360d7ee6c83b0ecccf2230e9181d5a39df5cd56c65c874bd53855f59
subject_ref = 2401d8295d0a54f76cfed1b892ecc4e94e112cbbeffdd7cd50a7b69862d2a8e3
```

Source event ID: `3dd8052d-7006-4850-b711-678c59dc98ad`.
Đây là ID bản ghi sự kiện, không phải authorization code hoặc cookie.

Chuỗi đối chiếu: [đăng ký 09:47](../callback-recovery-2026-11-23/registration-event-0947.md)
→ LOGIN với cùng credential ID → cùng issuer/client/SID và subject qua mã băm
→ binding tạo sau đó → HTTP 200 và tên tài khoản trên trang. Bằng chứng hỗ trợ
đúng khoảng trống FR-05/IF-03 đã nêu trong ma trận.

## Giới hạn

- Thời gian rất gần nhau chỉ là một kiểm tra bổ trợ; kết luận dựa thêm vào mã
  phiên, subject, credential ID và kết quả truy cập, không chỉ dựa vào cùng phút.
- SQL đọc các LOGIN còn lưu theo bộ lọc, không chứng minh tính đầy đủ của toàn sổ.
- UV=true thuộc lần thành công này, không thay thế kiểm thử âm UV=0.
- Không biết lần này có cần Try again hay không từ ba ảnh; giữ lỗi native
  DEFERRED_OPEN. Không suy ra tất cả lần đăng nhập đều ổn định.
- Kết quả này không thay đổi nguyên nhân năm session BadSignature hoặc tổng số
  ca session trong bộ kiểm thử riêng. FR-06 toàn bộ vẫn một phần.
