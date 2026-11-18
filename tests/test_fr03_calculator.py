"""
Kiểm thử FR-03: Tính điểm tổng và trạng thái hoàn thành của phiếu chấm.
Căn cứ: SRS-TTTN-N15 v0.9 (FR-03, DR-02) và HD-TTTN-N15 mục 7.
"""
from pathlib import Path
import pytest

from apps.readiness.loader import load_criteria_from_yaml
from apps.readiness.models import ScorecardStatus
from apps.readiness.evaluator import evaluate_scorecard
from apps.readiness.parser import parse_scorecard_csv


SAMPLE_CATALOG_PATH = Path("DU_LIEU_MAU/N15_San_sang_WebAuthn/tieu_chi.yaml")
SAMPLE_COMPLETE_CSV = Path("DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_mau_day_du.csv")
SAMPLE_INCOMPLETE_CSV = Path("DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_mau_thieu.csv")


class TestFR03Calculator:
    """Kiểm tra yêu cầu FR-03: Điểm tổng bằng tổng điểm đã chấm, thiếu tiêu chí thì chưa hoàn thành."""

    @pytest.fixture
    def catalog(self):
        return load_criteria_from_yaml(SAMPLE_CATALOG_PATH)

    def test_official_sample_full_scorecard_yields_29(self, catalog):
        """
        Kiểm tra với file mẫu đầy đủ phieu_cham_mau_day_du.csv:
        - Đủ 16 tiêu chí (bao gồm NK-03 chấm 0 điểm).
        - Trạng thái phiếu: HOAN_THANH.
        - Tổng điểm chính xác: 29 điểm (đáp án chuẩn theo hướng dẫn HD-TTTN-N15).
        - Danh sách thiếu: rỗng.
        """
        assert SAMPLE_COMPLETE_CSV.is_file(), f"Không tìm thấy {SAMPLE_COMPLETE_CSV}"
        items = parse_scorecard_csv(SAMPLE_COMPLETE_CSV)

        assert len(items) == 16, f"Kỳ vọng 16 dòng, thực tế {len(items)}"

        scorecard = evaluate_scorecard(
            items=items,
            catalog=catalog,
            ngay_cham="2026-11-20",
            nguoi_cham="Trần Trung Hiếu",
        )

        assert scorecard.trang_thai == ScorecardStatus.HOAN_THANH
        assert scorecard.tong_diem == 29, f"Kỳ vọng tổng điểm là 29, thực tế: {scorecard.tong_diem}"
        assert len(scorecard.missing_criteria) == 0

        # Kiểm tra tiêu chí NK-03 được tính đúng 0 điểm
        assert scorecard.items["NK-03"].diem == 0

    def test_official_sample_incomplete_scorecard(self, catalog):
        """
        Kiểm tra với file mẫu thiếu phieu_cham_mau_thieu.csv:
        - Chỉ có 14 tiêu chí (thiếu NK-03 và NK-04).
        - Trạng thái phiếu: CHUA_HOAN_THANH (theo đúng FR-03).
        - missing_criteria phải chỉ rõ: ['NK-03', 'NK-04'].
        - tong_diem phải là None (không công nhận điểm tổng khi chưa hoàn thành).
        """
        assert SAMPLE_INCOMPLETE_CSV.is_file(), f"Không tìm thấy {SAMPLE_INCOMPLETE_CSV}"
        items = parse_scorecard_csv(SAMPLE_INCOMPLETE_CSV)

        assert len(items) == 14, f"Kỳ vọng 14 dòng, thực tế {len(items)}"

        scorecard = evaluate_scorecard(
            items=items,
            catalog=catalog,
            ngay_cham="2026-11-20",
            nguoi_cham="Trần Trung Hiếu",
        )

        assert scorecard.trang_thai == ScorecardStatus.CHUA_HOAN_THANH
        assert scorecard.tong_diem is None
        assert scorecard.missing_criteria == ["NK-03", "NK-04"]
