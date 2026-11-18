"""
Bộ nạp và kiểm tra danh mục tiêu chí từ file YAML (FR-01).
Căn cứ: SRS-TTTN-N15 v0.9 (FR-01) và HD-TTTN-N15 mục 7.
"""
from pathlib import Path
from typing import Union
import yaml

from apps.readiness.models import CriteriaCatalog, Criterion, ReadinessGroup


class CatalogValidationError(Exception):
    """Lỗi khi cấu trúc hoặc nội dung danh mục tiêu chí không hợp lệ."""
    pass


def load_criteria_from_yaml(file_path: Union[str, Path]) -> CriteriaCatalog:
    """
    Nạp danh mục tiêu chí từ file YAML và kiểm chứng tính hợp lệ theo FR-01:
    - Phải có đủ 4 nhóm: cau_hinh, va_loi, xac_thuc, nhat_ky.
    - Mỗi tiêu chí phải có diem_toi_da > 0.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file tiêu chí tại: {path}")

    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        location = f" tại dòng {mark.line + 1}, cột {mark.column + 1}" if mark else ""
        raise CatalogValidationError(f"YAML không hợp lệ{location}: {path}") from exc

    if not isinstance(data, dict):
        raise CatalogValidationError("Dữ liệu YAML phải là một đối tượng từ điển (dict)")

    phien_ban = str(data.get("phien_ban", "unknown"))
    ghi_chu = str(data.get("ghi_chu", ""))
    raw_criteria = data.get("tieu_chi", [])

    if not isinstance(raw_criteria, list) or len(raw_criteria) == 0:
        raise CatalogValidationError("Danh sách 'tieu_chi' trống hoặc không hợp lệ")

    catalog = CriteriaCatalog(phien_ban=phien_ban, ghi_chu=ghi_chu)

    for idx, item in enumerate(raw_criteria):
        if not isinstance(item, dict):
            raise CatalogValidationError(f"Mục tiêu chí thứ {idx+1} không phải định dạng đối tượng hợp lệ")

        try:
            criterion = Criterion(
                ma=item.get("ma", ""),
                nhom=item.get("nhom", ""),
                mo_ta=item.get("mo_ta", ""),
                diem_toi_da=item.get("diem_toi_da"),
                can_cu=item.get("can_cu", ""),
                cach_thu_bang_chung=item.get("cach_thu_bang_chung", ""),
            )
            catalog.add_criterion(criterion)
        except ValueError as exc:
            raise CatalogValidationError(f"Mục tiêu chí thứ {idx + 1}: {exc}") from exc

    # Kiểm tra FR-01: Phải có các tiêu chí thuộc bốn nhóm
    if not catalog.validate_four_groups():
        missing = {g.value for g in ReadinessGroup} - catalog.groups
        raise CatalogValidationError(
            f"Danh mục tiêu chí vi phạm FR-01: thiếu nhóm bắt buộc: {missing}"
        )

    return catalog
