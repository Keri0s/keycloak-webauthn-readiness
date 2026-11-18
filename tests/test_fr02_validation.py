"""
Kiểm thử FR-02: Kiểm tra tính hợp lệ khi chấm điểm (Validator).
Căn cứ: SRS-TTTN-N15 v0.9 (FR-02) và HD-TTTN-N15 mục 7.
"""
from pathlib import Path
import pytest

from apps.readiness.loader import load_criteria_from_yaml
from apps.readiness.models import ScorecardItem
from apps.readiness.evaluator import validate_scorecard_item, ScorecardValidationError
from apps.readiness.parser import parse_scorecard_csv


SAMPLE_CATALOG_PATH = Path("DU_LIEU_MAU/N15_San_sang_WebAuthn/tieu_chi.yaml")
SAMPLE_ERROR_CSV = Path("DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_loi_vuot_diem.csv")


class TestFR02Validation:
    """Kiểm tra yêu cầu FR-02: Không vượt điểm tối đa và nguồn bằng chứng bắt buộc."""

    @pytest.fixture
    def catalog(self):
        return load_criteria_from_yaml(SAMPLE_CATALOG_PATH)

    def test_reject_official_error_sample_csv(self, catalog):
        """
        Kiểm tra với file lỗi mẫu chính thức phieu_cham_loi_vuot_diem.csv:
        - CH-01: Điểm 5 > tối đa 3 -> Bị từ chối.
        - CH-02: Thiếu nguồn bằng chứng -> Bị từ chối.
        """
        assert SAMPLE_ERROR_CSV.is_file(), f"Không tìm thấy {SAMPLE_ERROR_CSV}"
        error_items = parse_scorecard_csv(SAMPLE_ERROR_CSV)

        # Item 1: CH-01 điểm 5 (vượt max 3)
        ch01_item = next(it for it in error_items if it.ma == "CH-01")
        assert ch01_item.diem == 5
        with pytest.raises(ScorecardValidationError) as exc_max:
            validate_scorecard_item(ch01_item, catalog)
        assert "vượt quá điểm tối đa" in str(exc_max.value)

        # Item 2: CH-02 thiếu nguồn bằng chứng
        ch02_item = next(it for it in error_items if it.ma == "CH-02")
        assert ch02_item.nguon_bang_chung == ""
        with pytest.raises(ScorecardValidationError) as exc_source:
            validate_scorecard_item(ch02_item, catalog)
        assert "thiếu nguồn bằng chứng" in str(exc_source.value)

    def test_reject_negative_score(self, catalog):
        """Kiểm tra từ chối điểm âm."""
        bad_item = ScorecardItem(ma="CH-01", diem=-1, nguon_bang_chung="evidence/test.md")
        with pytest.raises(ScorecardValidationError) as exc:
            validate_scorecard_item(bad_item, catalog)
        assert "không được âm" in str(exc.value)

    def test_reject_unknown_criterion_code(self, catalog):
        """Kiểm tra từ chối mã tiêu chí không tồn tại trong danh mục."""
        bad_item = ScorecardItem(ma="UNKNOWN-99", diem=1, nguon_bang_chung="evidence/test.md")
        with pytest.raises(ScorecardValidationError) as exc:
            validate_scorecard_item(bad_item, catalog)
        assert "không tồn tại trong danh mục" in str(exc.value)

    def test_accept_valid_score_and_zero_score(self, catalog):
        """Kiểm tra chấp nhận điểm hợp lệ (bao gồm điểm 0 và điểm tối đa)."""
        # Điểm 0 hợp lệ nếu có nguồn bằng chứng
        zero_item = ScorecardItem(ma="NK-03", diem=0, nguon_bang_chung="evidence/NK-03.md")
        validate_scorecard_item(zero_item, catalog)  # Không bắn exception

        # Điểm tối đa (CH-01 max = 3)
        max_item = ScorecardItem(ma="CH-01", diem=3, nguon_bang_chung="evidence/CH-01.md")
        validate_scorecard_item(max_item, catalog)  # Không bắn exception
