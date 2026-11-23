# Hồ sơ bằng chứng FR-03 — Điểm tổng

- **Yêu cầu (SRS 3.2, FR-03):** *"Điểm tổng bằng tổng điểm đã chấm. Thiếu một tiêu chí thì phiếu chưa hoàn thành."* (Mức: Bắt buộc)
- **Phương thức kiểm tra theo SRS:** `Kiểm thử`
- **Trạng thái hiện tại:** `Có test` (theo đối chiếu 23/11/2026)

## Bằng chứng hiện có
- Mã nguồn tính tổng: [`apps/readiness/evaluator.py`](../../apps/readiness/evaluator.py) (`evaluate_scorecard`), [`apps/readiness/models.py`](../../apps/readiness/models.py) (`ScorecardStatus`).
- Phiếu mẫu: [`phieu_cham_mau_day_du.csv`](../../DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_mau_day_du.csv) (tổng `29 / 37`), [`phieu_cham_mau_thieu.csv`](../../DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_mau_thieu.csv) (báo thiếu `NK-03, NK-04` -> `CHUA_HOAN_THANH`).
- Kiểm thử: [`tests/test_fr03_calculator.py`](../../tests/test_fr03_calculator.py) và [`tests/test_readiness_regressions.py`](../../tests/test_readiness_regressions.py); kết quả lưu tại [`docs/validation/readiness-2026-11-13/run-metadata.json`](../../docs/validation/readiness-2026-11-13/run-metadata.json).

## Giới hạn
- `29/37` là kết quả trên phiếu mẫu giả lập, không phải điểm mức sẵn sàng thực tế của lab.

## Ảnh / tệp cần bổ sung
- Sau khi chấm phiếu lab thực ở [`evidence/lab-scorecard/`](../lab-scorecard/ghi_chu_tieu_chi.md), lưu đầu ra CLI chấm phiếu lab thực.
