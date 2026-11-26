# Hồ sơ minh chứng và sổ bằng chứng N15

## Cấu trúc thư mục hiện hành
- `CH-01.md`…`CH-04.md`, `VA-01.md`…`VA-04.md`, `XT-01.md`…`XT-04.md`, `NK-01.md`…`NK-04.md`: 16 hồ sơ mẫu/fixture phục vụ rubric và bộ kiểm thử `29/37`, không phải kết quả nghiệm thu lab.
- [`FR-01/`](FR-01/README.md)…[`FR-08/`](FR-08/README.md) và [`NFR-01/`](NFR-01/README.md)…[`NFR-04/`](NFR-04/README.md): hồ sơ bằng chứng theo từng mã yêu cầu SRS N15, kèm danh sách ảnh người dùng tự bổ sung nếu nộp offline.
- [`ledger/so_bang_chung.csv`](ledger/so_bang_chung.csv) và [`ledger/pull-log.jsonl`](ledger/pull-log.jsonl): sổ bằng chứng WebAuthn thực tế (67 dòng) được kéo từ Keycloak Admin Events qua `apps/ledger`.
- [`lab-scorecard/phieu_cham_lab_2026-11-26.csv`](lab-scorecard/phieu_cham_lab_2026-11-26.csv) và [`lab-scorecard/ghi_chu_tieu_chi.md`](lab-scorecard/ghi_chu_tieu_chi.md): phiếu chấm lab thực đã chốt ngày `26/11/2026` (**`27 / 37`** điểm, tách biệt với mẫu fixture `29/37`), cùng [`phieu_cham_lab_draft.csv`](lab-scorecard/phieu_cham_lab_draft.csv) để trống điểm cho lần triển khai trên máy khác.

Bằng chứng kiểm thử và báo cáo chi tiết nằm ở [`docs/validation/`](../docs/validation/README.md).
