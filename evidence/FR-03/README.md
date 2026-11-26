# Hồ sơ bằng chứng FR-03 — Điểm tổng

- **Yêu cầu (SRS 3.2, FR-03):** *"Điểm tổng bằng tổng điểm đã chấm. Thiếu một tiêu chí thì phiếu chưa hoàn thành."* (Mức: Bắt buộc)
- **Phương thức kiểm tra theo SRS:** `Kiểm thử`
- **Trạng thái hiện tại:** `Có test` (theo đối chiếu 23/11/2026)

## Bằng chứng hiện có
- Mã nguồn tính tổng: [`apps/readiness/evaluator.py`](../../apps/readiness/evaluator.py) (`evaluate_scorecard`), [`apps/readiness/models.py`](../../apps/readiness/models.py) (`ScorecardStatus`).
- Phiếu mẫu: [`phieu_cham_mau_day_du.csv`](../../DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_mau_day_du.csv) (tổng `29 / 37`), [`phieu_cham_mau_thieu.csv`](../../DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_mau_thieu.csv) (báo thiếu `NK-03, NK-04` -> `CHUA_HOAN_THANH`).
- Kiểm thử: [`tests/test_fr03_calculator.py`](../../tests/test_fr03_calculator.py) và [`tests/test_readiness_regressions.py`](../../tests/test_readiness_regressions.py); kết quả lưu tại [`docs/validation/readiness-2026-11-13/run-metadata.json`](../../docs/validation/readiness-2026-11-13/run-metadata.json).
- Phiếu chấm lab thực ngày `26/11/2026`: [`evidence/lab-scorecard/phieu_cham_lab_2026-11-26.csv`](../lab-scorecard/phieu_cham_lab_2026-11-26.csv) — đạt trạng thái `HOÀN THÀNH` (`16/16` tiêu chí, tổng **`27 / 37`** điểm; [`cli-output.txt`](../../docs/validation/scorecard-evidence-2026-11-26/cli-output.txt), [`scorecard-run.json`](../../docs/validation/scorecard-evidence-2026-11-26/scorecard-run.json)).

## Giới hạn
- `29/37` là kết quả trên phiếu mẫu giả lập, tách biệt với kết quả thực tế **`27/37`** của cụm lab ngày `26/11/2026`.
- Khi chấm lại trên máy mới, dùng mẫu trống [`phieu_cham_lab_draft.csv`](../lab-scorecard/phieu_cham_lab_draft.csv) (cả 16 ô `diem` để trống).
