# Dữ liệu mẫu — SRS-TTTN-N15: Đánh giá mức sẵn sàng an ninh và kiểm chứng WebAuthn/FIDO2

> Toàn bộ dữ liệu là giả lập, sinh bằng chương trình với hạt giống cố định. Không có người, tổ chức hay hệ thống thật.

## Mục đích

Cung cấp thang 16 tiêu chí mẫu có căn cứ, ba phiếu chấm (đủ, thiếu, sai) để kiểm thử logic phiếu, realm Keycloak bật lưu sự kiện để thử passkey, và mẫu sổ bằng chứng đúng các cột SRS yêu cầu.

## Danh mục tệp

| Tệp                                                           | Nội dung                                      | Phục vụ              |
| ------------------------------------------------------------- | --------------------------------------------- | -------------------- |
| `tieu_chi.yaml`                                               | 16 tiêu chí, 4 nhóm, tổng 37 điểm             | FR-01                |
| `phieu_cham_mau_day_du.csv / _thieu.csv / _loi_vuot_diem.csv` | Đủ 16 / thiếu 2 / điểm vượt và thiếu nguồn    | FR-02, FR-03         |
| `realm/webauthn-lab-realm.json`                               | Realm có Events bật, 2 tài khoản, client PKCE | FR-04..FR-07         |
| `so_bang_chung_mau.csv`                                       | Mẫu 3 dòng bằng chứng (thành công/thất bại)   | FR-06, FR-07, NFR-04 |

## Cách sử dụng

1. Nạp tieu_chi.yaml; nhóm sửa căn cứ cho đúng mục chuẩn và trình GV duyệt.
2. Kiểm thử phiếu: _day_du → có tổng điểm; _thieu → 'chưa hoàn thành'; _loi_vuot_diem → bị từ chối.
3. Nạp realm; cấu hình WebAuthn Passwordless Policy (RP ID = tên miền lab) và luồng đăng nhập trong giao diện quản trị (bước này làm tay và chụp ảnh).
4. Nếu máy lab không có authenticator: Chrome DevTools → More tools → WebAuthn → Enable virtual authenticator environment.
5. Đăng ký, đăng nhập, hủy một lần → trích sự kiện bằng Admin REST API → so định dạng với so_bang_chung_mau.csv.

## Kết quả mong đợi (đáp án để kiểm thử)

| Kiểm tra | Kết quả mong đợi |
|---|---|
| Tổng điểm tối đa thang mẫu | 37 |
| Phiếu đầy đủ — tổng | 29 |
| Phiếu thiếu | Trạng thái 'chưa hoàn thành' (thiếu NK-03, NK-04) |
| Phiếu lỗi | CH-01 điểm 5 > 3 bị từ chối; CH-02 thiếu nguồn bị từ chối |
| Sổ bằng chứng | Có ≥1 dòng thành công và ≥1 dòng thất bại; không cột nào chứa khóa |

## Lưu ý

- Tên loại sự kiện Keycloak trong enabledEventTypes phụ thuộc phiên bản [CẦN KIỂM CHỨNG]; nếu import báo lỗi, xóa trường này và bật Events trong giao diện.

## Sinh lại dữ liệu

`python gen_data.py <thư mục đầu ra>` trong thư mục `_build` — cùng hạt giống cho cùng kết quả.

## Trạng thái bản public ngày 18/11/2026

Realm JSON là cấu hình mẫu lịch sử, không phải export của lab đang chạy. Đã bỏ credentials của hai user mẫu; cần tự thiết lập credential trong lab của bạn. Các hướng dẫn passwordless phía trên thuộc dữ liệu gợi ý ban đầu; lab hiện kiểm chứng password kết hợp WebAuthn và quản lý phiên, chưa nghiệm thu passwordless. Quy trình gen_data.py trong _build thuộc nguồn sinh mẫu cũ, không được phân phối trong repository này. Không dùng đường dẫn đó như lệnh có sẵn sau clone.
