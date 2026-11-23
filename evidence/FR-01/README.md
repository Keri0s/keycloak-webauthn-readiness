# Hồ sơ bằng chứng FR-01 — Bộ tiêu chí

- **Yêu cầu (SRS 3.2, FR-01):** *"Hệ thống có các tiêu chí thuộc bốn nhóm: cấu hình, vá lỗi, xác thực, nhật ký. Mỗi tiêu chí có điểm tối đa."* (Mức: Bắt buộc)
- **Phương thức kiểm tra theo SRS:** `Rà soát`
- **Trạng thái hiện tại:** `Có test` (theo đối chiếu 23/11/2026)

## Bằng chứng hiện có
- Danh mục tiêu chí: [`DU_LIEU_MAU/N15_San_sang_WebAuthn/tieu_chi.yaml`](../../DU_LIEU_MAU/N15_San_sang_WebAuthn/tieu_chi.yaml) (16 tiêu chí, 4 nhóm: `cau_hinh`, `va_loi`, `xac_thuc`, `nhat_ky`; tổng tối đa 37 điểm).
- Mã nguồn mô hình & bộ nạp: [`apps/readiness/models.py`](../../apps/readiness/models.py), [`apps/readiness/loader.py`](../../apps/readiness/loader.py).
- Kiểm thử: [`tests/test_fr01_catalog.py`](../../tests/test_fr01_catalog.py) và [`tests/test_readiness_regressions.py`](../../tests/test_readiness_regressions.py) (nằm trong bộ 81 tests readiness PASS; hồ sơ hash ngày 13/11 tại [`docs/validation/readiness-2026-11-13/run-metadata.json`](../../docs/validation/readiness-2026-11-13/run-metadata.json)).

## Giới hạn
- Kiểm chứng khả năng nạp, kiểm tra đủ 4 nhóm, chặn mã trùng và `diem_toi_da > 0` trên danh mục YAML mẫu; không tự đánh giá mức an ninh của lab.

## Ảnh cần bổ sung vào thư mục này (nếu nộp kèm bản cứng/offline)
- Không bắt buộc ảnh chụp UI vì phương thức SRS là `Rà soát`; có thể lưu kết quả chạy `python -m pytest tests/test_fr01_catalog.py -v` nếu cần.
