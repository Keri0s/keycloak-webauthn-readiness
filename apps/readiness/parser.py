"""
Bộ đọc và xuất dữ liệu phiếu chấm (CSV Parser).
Định dạng file: ma,diem,nguon_bang_chung
"""
import csv
from pathlib import Path
from typing import List, Union

from apps.readiness.models import ScorecardItem


def parse_scorecard_csv(csv_path: Union[str, Path]) -> List[ScorecardItem]:
    """
    Đọc tệp CSV phiếu chấm điểm.
    Định dạng mong đợi (có header):
    ma,diem,nguon_bang_chung
    """
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Không tìm thấy file CSV tại: {path}")

    items = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"ma", "diem", "nguon_bang_chung"}
        headers = reader.fieldnames or []
        if not required.issubset(headers) or len(headers) != len(set(headers)):
            raise ValueError("Header CSV phải có ma, diem, nguon_bang_chung và không trùng tên cột")
        for row_idx, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Dòng {row_idx}: Số ô không khớp header CSV")
            ma = row.get("ma", "").strip() if row.get("ma") else ""
            raw_diem = row.get("diem", "").strip() if row.get("diem") is not None else ""
            nguon = row.get("nguon_bang_chung", "").strip() if row.get("nguon_bang_chung") else ""

            if not ma:
                if all(not value.strip() for value in row.values()):
                    continue
                raise ValueError(f"Dòng {row_idx}: Thiếu mã tiêu chí 'ma'")

            try:
                # Giữ dòng chưa chấm để evaluator vẫn kiểm mã và phát hiện trùng.
                diem = int(raw_diem) if raw_diem else None
            except ValueError:
                raise ValueError(f"Dòng {row_idx}: Điểm '{raw_diem}' của tiêu chí '{ma}' không phải số nguyên hợp lệ")

            items.append(ScorecardItem(ma=ma, diem=diem, nguon_bang_chung=nguon))

    return items
