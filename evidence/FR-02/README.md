# Hồ sơ bằng chứng FR-02 — Chấm

- **Yêu cầu (SRS 3.2, FR-02):** *"Người đánh giá nhập điểm không vượt điểm tối đa và một nguồn bằng chứng ngắn."* (Mức: Bắt buộc)
- **Phương thức kiểm tra theo SRS:** `Demo`
- **Trạng thái hiện tại:** `Có test` (theo đối chiếu 23/11/2026)

## Bằng chứng hiện có
- Mã nguồn kiểm tra & parser: [`apps/readiness/evaluator.py`](../../apps/readiness/evaluator.py), [`apps/readiness/parser.py`](../../apps/readiness/parser.py), [`apps/readiness/cli.py`](../../apps/readiness/cli.py).
- Dữ liệu mẫu lỗi vượt điểm: [`DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_loi_vuot_diem.csv`](../../DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_loi_vuot_diem.csv) (chạy CLI trả exit code `2`).
- Kiểm thử: [`tests/test_fr02_validation.py`](../../tests/test_fr02_validation.py) và [`tests/test_readiness_regressions.py`](../../tests/test_readiness_regressions.py), cùng kết quả 3 lần chạy CLI trong [`docs/validation/readiness-2026-11-13/run-metadata.json`](../../docs/validation/readiness-2026-11-13/run-metadata.json).
- Phiếu chấm lab thực ngày `26/11/2026`: [`evidence/lab-scorecard/phieu_cham_lab_2026-11-26.csv`](../lab-scorecard/phieu_cham_lab_2026-11-26.csv) với đủ 16 nguồn bằng chứng thực tế ([`cli-output.txt`](../../docs/validation/scorecard-evidence-2026-11-26/cli-output.txt), [`scorecard-run.json`](../../docs/validation/scorecard-evidence-2026-11-26/scorecard-run.json)).

## Giới hạn
- Giao diện hiện tại là CLI nhận file CSV (SRS không bắt buộc phải có web form).
- Kiểm tra tính hợp lệ định dạng và khoảng điểm `0 <= diem <= diem_toi_da`, không tự xác minh nội dung thực của nguồn bằng chứng.

## Ảnh / kết quả cần bổ sung (tùy chọn cho demo trực tiếp)
- Chụp terminal khi chạy `python -m apps.readiness.cli --scorecard DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_loi_vuot_diem.csv --evaluator "<tên>"` cho thấy hệ thống từ chối điểm vượt tối đa (lỗi vượt điểm). Đầu ra chấm phiếu lab thực `27/37` đã lưu tại [`cli-output.txt`](../../docs/validation/scorecard-evidence-2026-11-26/cli-output.txt).
