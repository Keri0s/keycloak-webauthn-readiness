"""
Bộ kiểm tra tính hợp lệ (Validator - FR-02) và Bộ tính điểm (Evaluator - FR-03).
Căn cứ: SRS-TTTN-N15 v0.9 (FR-02, FR-03).
"""
from typing import List, Optional
from datetime import date, datetime, timedelta, timezone

from apps.readiness.models import CriteriaCatalog, Scorecard, ScorecardItem, ScorecardStatus


class ScorecardValidationError(Exception):
    """Lỗi dữ liệu phiếu chấm (FR-02, FR-03, DR-02)."""
    pass


def validate_scorecard_item(item: ScorecardItem, catalog: CriteriaCatalog) -> None:
    """
    Kiểm tra một dòng chấm điểm theo yêu cầu FR-02:
    - Tiêu chí phải tồn tại trong danh mục.
    - Điểm không được vượt quá điểm tối đa và không được âm (0 <= diem <= diem_toi_da).
    - None là chưa chấm; điểm đã chấm phải là số nguyên và có nguồn bằng chứng.
    """
    if not isinstance(item, ScorecardItem):
        raise ScorecardValidationError("Dòng chấm phải là ScorecardItem")
    if not isinstance(item.ma, str) or not item.ma.strip():
        raise ScorecardValidationError("Mã tiêu chí phải là chuỗi không rỗng")
    criterion = catalog.criteria.get(item.ma)
    if not criterion:
        raise ScorecardValidationError(f"Mã tiêu chí '{item.ma}' không tồn tại trong danh mục {catalog.phien_ban}")

    if not isinstance(item.nguon_bang_chung, str):
        raise ScorecardValidationError(f"Tiêu chí '{item.ma}' phải có nguồn bằng chứng dạng chuỗi")
    if item.diem is None:
        return
    if type(item.diem) is not int:
        raise ScorecardValidationError(f"Điểm của tiêu chí '{item.ma}' phải là số nguyên; None dành cho chưa chấm")

    # Điểm 0 cũng là đã chấm nên vẫn phải có nguồn bằng chứng.
    if not item.nguon_bang_chung.strip():
        raise ScorecardValidationError(f"Tiêu chí '{item.ma}' bị thiếu nguồn bằng chứng (FR-02 bắt buộc)")

    # Kiểm tra khoảng điểm hợp lệ
    if item.diem < 0:
        raise ScorecardValidationError(f"Điểm của tiêu chí '{item.ma}' không được âm (nhập: {item.diem})")

    if item.diem > criterion.diem_toi_da:
        raise ScorecardValidationError(
            f"Điểm {item.diem} của tiêu chí '{item.ma}' vượt quá điểm tối đa cho phép là {criterion.diem_toi_da} (FR-02)"
        )


def evaluate_scorecard(
    items: List[ScorecardItem],
    catalog: CriteriaCatalog,
    ngay_cham: Optional[str] = None,
    nguoi_cham: Optional[str] = None,
) -> Scorecard:
    """
    Thực hiện chấm điểm và tính tổng điểm theo yêu cầu FR-03:
    - Kiểm tra từng dòng điểm bằng validate_scorecard_item.
    - Phân biệt điểm 0 (đã chấm và tính vào tổng) với ô thiếu (chưa chấm).
    - Nếu thiếu dù chỉ một tiêu chí trong danh mục, phiếu ở trạng thái 'chưa hoàn thành' (CHUA_HOAN_THANH).
    - Nếu đủ toàn bộ tiêu chí, phiếu ở trạng thái 'hoàn thành' (HOAN_THANH) và tổng điểm bằng tổng các điểm đã chấm.
    - Người chấm bắt buộc; ngày mặc định theo UTC+07:00, hoặc ngày YYYY-MM-DD được cung cấp.
    """
    if not isinstance(nguoi_cham, str) or not nguoi_cham.strip():
        raise ScorecardValidationError("Người chấm phải là chuỗi không rỗng (DR-02)")
    nguoi_cham = nguoi_cham.strip()
    if ngay_cham is None:
        ngay_cham = datetime.now(timezone(timedelta(hours=7))).date().isoformat()
    else:
        try:
            if not isinstance(ngay_cham, str) or date.fromisoformat(ngay_cham).isoformat() != ngay_cham:
                raise ValueError
        except ValueError as exc:
            raise ScorecardValidationError("Ngày chấm phải là ngày hợp lệ theo YYYY-MM-DD (DR-02)") from exc

    # 1. Kiểm tra validation cho từng dòng đã nộp
    items_dict = {}
    for item in items:
        validate_scorecard_item(item, catalog)
        if item.ma in items_dict:
            raise ScorecardValidationError(f"Mã tiêu chí '{item.ma}' bị chấm trùng lặp nhiều lần trong phiếu")
        items_dict[item.ma] = item

    # 2. Rà soát danh mục để tìm tiêu chí bị thiếu
    all_catalog_codes = set(catalog.criteria.keys())
    submitted_codes = {ma for ma, item in items_dict.items() if item.diem is not None}
    missing_codes = sorted(list(all_catalog_codes - submitted_codes))

    # 3. Tính toán trạng thái và tổng điểm theo FR-03
    if missing_codes:
        # Thiếu một tiêu chí thì phiếu chưa hoàn thành
        return Scorecard(
            catalog_version=catalog.phien_ban,
            items=items_dict,
            ngay_cham=ngay_cham,
            nguoi_cham=nguoi_cham,
            tong_diem=None,
            trang_thai=ScorecardStatus.CHUA_HOAN_THANH,
            missing_criteria=missing_codes,
        )

    # Đầy đủ tất cả tiêu chí
    tong_diem = sum(item.diem for item in items_dict.values())
    return Scorecard(
        catalog_version=catalog.phien_ban,
        items=items_dict,
        ngay_cham=ngay_cham,
        nguoi_cham=nguoi_cham,
        tong_diem=tong_diem,
        trang_thai=ScorecardStatus.HOAN_THANH,
        missing_criteria=[],
    )
