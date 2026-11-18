"""
Mô hình dữ liệu Mức sẵn sàng an ninh (Security Readiness) N15.
Căn cứ: SRS-TTTN-N15 v0.9 (DR-01, DR-02) và HD-TTTN-N15 (05/11/2026).
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class ReadinessGroup(str, Enum):
    """Bốn nhóm tiêu chí bắt buộc theo SRS 3.2 (FR-01) và DR-01."""
    CAU_HINH = "cau_hinh"
    VA_LOI = "va_loi"
    XAC_THUC = "xac_thuc"
    NHAT_KY = "nhat_ky"


class ScorecardStatus(str, Enum):
    """Trạng thái phiếu chấm theo SRS 3.2 (FR-03) và DR-02."""
    HOAN_THANH = "hoan_thanh"
    CHUA_HOAN_THANH = "chua_hoan_thanh"


@dataclass
class Criterion:
    """DR-01: Thực thể tiêu chí đánh giá mức sẵn sàng an ninh."""
    ma: str
    nhom: str
    mo_ta: str
    diem_toi_da: int
    can_cu: str = ""
    cach_thu_bang_chung: str = ""

    def __post_init__(self):
        for name in ("ma", "nhom", "mo_ta"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Trường '{name}' phải là chuỗi không rỗng")
            setattr(self, name, value.strip())
        if self.nhom not in {group.value for group in ReadinessGroup}:
            raise ValueError(f"Trường 'nhom' của tiêu chí {self.ma} phải thuộc bốn nhóm N15")
        # bool là lớp con của int trong Python, nhưng không phải điểm hợp lệ.
        if type(self.diem_toi_da) is not int or self.diem_toi_da <= 0:
            raise ValueError(f"Trường 'diem_toi_da' của tiêu chí {self.ma} phải là số nguyên > 0")
        for name in ("can_cu", "cach_thu_bang_chung"):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise ValueError(f"Trường '{name}' phải là chuỗi")
            setattr(self, name, value.strip())


@dataclass
class CriteriaCatalog:
    """Tập hợp tiêu chí (Catalog) theo phiên bản cụ thể."""
    phien_ban: str
    ghi_chu: str
    criteria: Dict[str, Criterion] = field(default_factory=dict)

    def add_criterion(self, c: Criterion) -> None:
        if c.ma in self.criteria:
            raise ValueError(f"Mã tiêu chí '{c.ma}' bị trùng trong danh mục")
        self.criteria[c.ma] = c

    @property
    def total_max_score(self) -> int:
        """Tổng điểm tối đa của toàn bộ thang đo."""
        return sum(c.diem_toi_da for c in self.criteria.values())

    @property
    def groups(self) -> set:
        """Tập các nhóm hiện có trong danh mục."""
        return {c.nhom for c in self.criteria.values()}

    def validate_four_groups(self) -> bool:
        """Kiểm tra xem danh mục có đủ 4 nhóm bắt buộc theo FR-01 hay không."""
        required = {g.value for g in ReadinessGroup}
        return required == self.groups


@dataclass
class ScorecardItem:
    """Dòng chấm điểm (FR-02); diem=None là chưa chấm, khác điểm 0."""
    ma: str
    diem: Optional[int]
    nguon_bang_chung: str


@dataclass
class Scorecard:
    """DR-02: Thực thể Phiếu chấm mức sẵn sàng an ninh."""
    catalog_version: str
    items: Dict[str, ScorecardItem] = field(default_factory=dict)
    ngay_cham: Optional[str] = None
    nguoi_cham: Optional[str] = None
    tong_diem: Optional[int] = None
    trang_thai: ScorecardStatus = ScorecardStatus.CHUA_HOAN_THANH
    missing_criteria: List[str] = field(default_factory=list)
