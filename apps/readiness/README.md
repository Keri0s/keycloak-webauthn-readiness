# Bộ tính điểm readiness N15

Bộ CLI/CSV phục vụ FR-01, FR-02, FR-03 và DR-01, DR-02. Các quy ước dưới đây mô tả mã hiện tại; không thay thế rubric hoặc quyết định của giảng viên. Kết quả trên dữ liệu mẫu chỉ kiểm chứng logic, không chứng minh lab Keycloak đã được nghiệm thu.

## Chạy từ thư mục gốc project

Môi trường đã kiểm ngày 13/11/2026: Python 3.12.10, PyYAML 6.0.3, pytest 9.2.0 trên Windows 11. PyYAML cần cho ứng dụng; pytest cần khi chạy kiểm thử. Đây là ghi nhận môi trường chạy, chưa phải kiểm chứng dựng lại trên máy sạch.

```powershell
python -m apps.readiness.cli --scorecard DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_mau_day_du.csv --evaluator "Nguoi cham lab"
```

`--evaluator` bắt buộc, không còn mặc định danh tính một sinh viên. `--date YYYY-MM-DD` không bắt buộc: nếu bỏ qua, evaluator lấy ngày hiện tại theo giờ Việt Nam UTC+07:00. Ngày nhập phải tồn tại trên lịch và đúng định dạng; cho phép ngày cụ thể của fixture hoặc phiếu lịch sử, không suy diễn đó là thời điểm thực nghiệm.

## Quy tắc dữ liệu sau bản vá R02–R06

- Catalog có đúng bốn nhóm N15; số tiêu chí và tổng tối đa được tính từ dữ liệu, không cố định 16/37. Mã trùng bị từ chối trước khi ghi đè.
- `ma`, `nhom`, `mo_ta` phải là chuỗi không rỗng. `diem_toi_da` là số nguyên dương, không chấp nhận boolean. `can_cu` và `cach_thu_bang_chung` nếu được cung cấp phải là chuỗi. Lỗi trường/YAML được báo qua `CatalogValidationError`.
- Header CSV phải có `ma,diem,nguon_bang_chung`. Ô điểm rỗng hoặc chỉ có khoảng trắng được đọc thành `None`; dòng vẫn được giữ để kiểm mã và kiểm trùng. Dòng có dữ liệu nhưng thiếu mã, hoặc số ô không khớp header bị từ chối.
- API nghiệp vụ nhận điểm `int` hoặc `None`; giữ nguyên quy tắc số nguyên của phiên bản trước. Boolean, float (kể cả `1.0`, NaN, vô cực), chuỗi và cấu trúc khác không phải điểm hợp lệ. Quy tắc này không được trình bày như một yêu cầu kiểu điểm đã được giảng viên chốt.
- Điểm đã chấm phải nằm trong khoảng 0 đến max và có nguồn bằng chứng dạng chuỗi không rỗng. Dòng chưa chấm có thể để nguồn là chuỗi rỗng; mã vẫn phải thuộc catalog. Điểm 0 luôn khác `None` và vẫn cần nguồn.
- Thiếu dòng hoặc có `diem=None` đều đưa mã vào `missing_criteria`, trạng thái `chua_hoan_thanh`, tổng `None`. Chỉ khi mọi tiêu chí có điểm hợp lệ mới tính tổng.
- `evaluate_scorecard()` bắt buộc người chấm không rỗng, đồng thời kiểm/tự điền ngày cho cả phiếu đầy đủ và chưa đầy đủ. Bên gọi API phải truyền `nguoi_cham=...`.

Ví dụ API với một dòng chưa chấm:

```python
from apps.readiness import ScorecardItem, evaluate_scorecard, load_criteria_from_yaml

catalog = load_criteria_from_yaml("DU_LIEU_MAU/N15_San_sang_WebAuthn/tieu_chi.yaml")
result = evaluate_scorecard(
    [ScorecardItem("CH-01", None, "")],
    catalog,
    nguoi_cham="Nguoi cham lab",
)
assert result.tong_diem is None
```

## Kiểm thử

Chạy riêng `tests/`, không chạy bộ kiểm thử lịch sử trong `references/vdt-snapshot`.

```powershell
python -m pytest tests -q -p no:cacheprovider --basetemp D:/Projects/Do-an-thuctap-totnghiep/tmp/readiness-tests-new-run
```

Chọn một tên thư mục `--basetemp` mới trong `tmp/` cho mỗi lần chạy để không ghi đè kết quả cũ.

| Phát hiện review | Phần được kiểm hồi quy |
| --- | --- |
| R02 | Catalog trùng mã bị từ chối; tiêu chí cũ và max tổng không bị ghi đè |
| R03 | Ô trống, thiếu dòng, điểm 0; mã lạ/trùng dù chưa chấm; CSV sai cấu trúc |
| R04 | Nhóm ngoài phạm vi, mô tả/kiểu trường/max không hợp lệ, YAML sai cú pháp; catalog hợp lệ có số mục khác mẫu |
| R05 | Điểm NaN/vô cực/boolean/sai kiểu ở API; nguồn bằng chứng không hợp lệ |
| R06 | Người chấm bắt buộc; ngày mặc định UTC+07:00; ngày nhập hợp lệ; CLI không mặc định tên |

Kết quả ngày 13/11/2026: **81 passed** (8 ca cũ, 73 ca bổ sung). [Log](../../docs/validation/readiness-2026-11-13/pytest.txt), [JUnit](../../docs/validation/readiness-2026-11-13/results.xml). Không dùng số PASS này cho FR-04…FR-08 hoặc nghiệm thu an ninh lab.
