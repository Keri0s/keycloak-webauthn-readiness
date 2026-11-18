# Hồ sơ kiểm chứng

| Thư mục | Bằng chứng | Giới hạn |
| --- | --- | --- |
| readiness-2026-11-13 | pytest, XML, metadata của 81 tests | Logic readiness trên fixture |
| a16-reliability-2026-11-18 | 6 thí nghiệm baseline/fault injection/đối chứng | PostgreSQL thật, JWKS giả lập |
| remaining-reliability-2026-11-18 | 15 lượt cho A3/A4/A5/A7/A11/A14/A15 | Các lỗi chọn thủ công, không exhaustive |
| a10-2026-11-18 | Baseline và hai lỗi guard được phát hiện | Django client, authenticated fixture bằng force_login |

`results.json` lưu quan sát và hash tại thời điểm chạy. FAIL có chủ đích trong mutation audit chứng minh test bắt lỗi, không phải baseline ứng dụng FAIL. File báo cáo mô tả chi tiết từng lần. Không chỉnh sửa log lịch sử để khớp code mới.

Các script gốc giữ ở tmp/ theo đường dẫn lịch sử để hash có thể đối chiếu. Một số metadata chứa đường dẫn máy Windows của tác giả; không chứa credential. Chạy lại script có thể ghi đè kết quả, nên lưu bản cũ trước khi tái lập nếu cần bảo toàn mốc lịch sử.
