"""
Kiểm thử FR-01: Bộ tiêu chí đánh giá mức sẵn sàng an ninh.
Căn cứ: SRS-TTTN-N15 v0.9 (FR-01, DR-01) và HD-TTTN-N15 mục 7.
"""
from pathlib import Path
import pytest

from apps.readiness.loader import load_criteria_from_yaml, CatalogValidationError
from apps.readiness.models import ReadinessGroup


SAMPLE_CATALOG_PATH = Path("DU_LIEU_MAU/N15_San_sang_WebAuthn/tieu_chi.yaml")


class TestFR01CriteriaCatalog:
    """Kiểm tra yêu cầu FR-01: Bốn nhóm tiêu chí và điểm tối đa."""

    def test_load_official_sample_catalog(self):
        """Kiểm tra nạp danh mục tiêu chí chính thức từ file mẫu của đề tài."""
        assert SAMPLE_CATALOG_PATH.is_file(), f"Không tìm thấy {SAMPLE_CATALOG_PATH}"

        catalog = load_criteria_from_yaml(SAMPLE_CATALOG_PATH)

        # 1. Phải nạp đúng 16 tiêu chí
        assert len(catalog.criteria) == 16, f"Kỳ vọng 16 tiêu chí, thực tế: {len(catalog.criteria)}"

        # 2. Phải có đủ bốn nhóm bắt buộc
        expected_groups = {g.value for g in ReadinessGroup}
        assert catalog.groups == expected_groups, f"Kỳ vọng đủ 4 nhóm {expected_groups}, thực tế: {catalog.groups}"

        # Đếm số lượng tiêu chí trong từng nhóm
        group_counts = {}
        for c in catalog.criteria.values():
            group_counts[c.nhom] = group_counts.get(c.nhom, 0) + 1

        assert group_counts["cau_hinh"] == 4
        assert group_counts["va_loi"] == 4
        assert group_counts["xac_thuc"] == 4
        assert group_counts["nhat_ky"] == 4

        # 3. Tổng điểm tối đa thang mẫu phải bằng 37
        assert catalog.total_max_score == 37, f"Kỳ vọng tổng điểm tối đa 37, thực tế: {catalog.total_max_score}"

        # 4. Mọi tiêu chí đều có điểm tối đa > 0
        for ma, c in catalog.criteria.items():
            assert c.diem_toi_da > 0, f"Tiêu chí {ma} có điểm tối đa không hợp lệ: {c.diem_toi_da}"
            assert len(c.mo_ta) > 0, f"Tiêu chí {ma} thiếu mô tả"

    def test_reject_catalog_missing_group(self, tmp_path):
        """Kiểm tra từ chối danh mục nếu thiếu 1 trong 4 nhóm bắt buộc theo FR-01."""
        bad_yaml_content = """
phien_ban: 0.1-loi
ghi_chu: Danh mục thiếu nhóm nhat_ky
tieu_chi:
  - ma: CH-01
    nhom: cau_hinh
    mo_ta: Test
    diem_toi_da: 3
  - ma: VA-01
    nhom: va_loi
    mo_ta: Test
    diem_toi_da: 2
  - ma: XT-01
    nhom: xac_thuc
    mo_ta: Test
    diem_toi_da: 3
"""
        bad_file = tmp_path / "bad_catalog.yaml"
        bad_file.write_text(bad_yaml_content, encoding="utf-8")

        with pytest.raises(CatalogValidationError) as excinfo:
            load_criteria_from_yaml(bad_file)
        assert "thiếu nhóm bắt buộc" in str(excinfo.value)
