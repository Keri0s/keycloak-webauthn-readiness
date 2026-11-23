# Hồ sơ kiểm chứng

| Thư mục | Bằng chứng | Giới hạn |
| --- | --- | --- |
| [requirements-review-2026-11-23](requirements-review-2026-11-23/report.md) | Đối chiếu đủ 20 mã FR/NFR/IF/DR, kiểm tra hash nguồn và các phần còn thiếu | Phân loại mức bằng chứng, không phải nghiệm thu toàn bộ |
| [ledger-2026-11-23](ledger-2026-11-23/report.md) | Kiểm chứng sổ bằng chứng live `apps/ledger` (Mục A–C), runbook và giải trình NFR-04 | Quan sát trên lab local; lỗi native Try again giữ DEFERRED_OPEN |
| [nfr01-02-2026-11-23](nfr01-02-2026-11-23/report.md) | Rà tĩnh NFR-01 (0 hàm quét mạng) và NFR-02 (0 tên miền Trường) | Rà tĩnh mã nguồn/cấu hình công bố; không đọc `.env` thực tế |
| [fr08-2026-11-23](fr08-2026-11-23/report.md) | Rà DB, session, log và 62 tệp export/CSV; có kết quả tổng hợp | Phạm vi và mẫu dò được công bố, không phải chứng nhận toàn máy |
| [passwordless-preflight](passwordless-preflight/report.md) | Kiểm kê cấu hình Keycloak passwordless (22/11 và `20261123T135327930466Z`) | Chỉ đọc trường allowlist, chưa đọc users/credentials |
| [passwordless-enrollment-2026-11-22](passwordless-enrollment-2026-11-22/report.md) | Quan sát giao diện đăng ký passkey, policy PL-POL-01 và lỗi native | Ảnh gốc ở hội thoại; lỗi retry giữ DEFERRED_OPEN |
| [callback-recovery-2026-11-23](callback-recovery-2026-11-23/report.md) | Đối chiếu đăng ký `09:47`, `LOGIN` `13:55`/`13:56`, ca hủy `14:16` và chẩn đoán callback | Quan sát theo ca; bổ sung cùng sổ live `ledger-2026-11-23` |
| readiness-2026-11-13 | pytest, XML, metadata của 81 tests | Logic readiness trên fixture |
| a16-reliability-2026-11-18 | 6 thí nghiệm baseline/fault injection/đối chứng | PostgreSQL thật, JWKS giả lập |
| remaining-reliability-2026-11-18 | 15 lượt cho A3/A4/A5/A7/A11/A14/A15 | Các lỗi chọn thủ công, không exhaustive |
| a10-2026-11-18 | Baseline và hai lỗi guard được phát hiện | Django client, authenticated fixture bằng force_login |

`results.json` lưu quan sát và hash tại thời điểm chạy. FAIL có chủ đích trong mutation audit chứng minh test bắt lỗi, không phải baseline ứng dụng FAIL. File báo cáo mô tả chi tiết từng lần. Không chỉnh sửa log lịch sử để khớp code mới.

Các script gốc giữ ở tmp/ theo đường dẫn lịch sử để hash có thể đối chiếu. Một số metadata chứa đường dẫn máy Windows của tác giả; không chứa credential. Chạy lại script có thể ghi đè kết quả, nên lưu bản cũ trước khi tái lập nếu cần bảo toàn mốc lịch sử.
