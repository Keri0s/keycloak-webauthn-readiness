"""
Giao diện dòng lệnh (CLI) chấm điểm mức sẵn sàng an ninh N15.
Sử dụng:
    python -m apps.readiness.cli --catalog <path_to_yaml> --scorecard <path_to_csv> --evaluator "Tên người chấm"
"""
import argparse
import sys

from apps.readiness.loader import load_criteria_from_yaml, CatalogValidationError
from apps.readiness.evaluator import evaluate_scorecard, ScorecardValidationError
from apps.readiness.parser import parse_scorecard_csv
from apps.readiness.models import ScorecardStatus


def main():
    parser = argparse.ArgumentParser(
        description="Hệ thống chấm điểm mức sẵn sàng an ninh N15 (Security Readiness Scorecard CLI)"
    )
    parser.add_argument(
        "--catalog",
        default="DU_LIEU_MAU/N15_San_sang_WebAuthn/tieu_chi.yaml",
        help="Đường dẫn file YAML danh mục tiêu chí (mặc định: DU_LIEU_MAU/N15_San_sang_WebAuthn/tieu_chi.yaml)",
    )
    parser.add_argument(
        "--scorecard",
        required=True,
        help="Đường dẫn file CSV phiếu chấm cần đánh giá",
    )
    parser.add_argument(
        "--evaluator",
        required=True,
        help="Tên người thực hiện chấm (bắt buộc)",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Ngày chấm YYYY-MM-DD (mặc định: ngày hiện tại theo giờ Việt Nam UTC+07:00)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("   HỆ THỐNG ĐÁNH GIÁ MỨC SẴN SÀNG AN NINH N15 (SRS-TTTN-N15)")
    print("=" * 70)

    # 1. Nạp danh mục tiêu chí
    try:
        catalog = load_criteria_from_yaml(args.catalog)
        print(f"[+] Đã nạp danh mục: Phiên bản '{catalog.phien_ban}'")
        print(f"    - Tổng số tiêu chí: {len(catalog.criteria)}")
        print(f"    - Điểm tối đa toàn thang: {catalog.total_max_score}")
        print(f"    - Bốn nhóm: {', '.join(sorted(catalog.groups))}")
    except (FileNotFoundError, CatalogValidationError) as e:
        print(f"[-] LỖI DANH MỤC TIÊU CHÍ: {e}")
        sys.exit(1)

    # 2. Đọc phiếu chấm
    try:
        items = parse_scorecard_csv(args.scorecard)
        print(f"[+] Đã đọc phiếu chấm từ: {args.scorecard} ({len(items)} dòng)")
    except Exception as e:
        print(f"[-] LỖI ĐỌC FILE PHIẾU CHẤM: {e}")
        sys.exit(1)

    # 3. Đánh giá và tính điểm
    try:
        scorecard = evaluate_scorecard(
            items=items,
            catalog=catalog,
            ngay_cham=args.date,
            nguoi_cham=args.evaluator,
        )
    except ScorecardValidationError as e:
        print("\n[!] TỪ CHỐI PHIẾU CHẤM DO DỮ LIỆU KHÔNG HỢP LỆ (FR-02/FR-03/DR-02):")
        print(f"    -> {e}")
        sys.exit(2)

    # 4. Hiển thị kết quả
    print("\n" + "-" * 70)
    print("KẾT QUẢ ĐÁNH GIÁ PHIẾU CHẤM:")
    print("-" * 70)
    print(f"Người chấm       : {scorecard.nguoi_cham}")
    if scorecard.ngay_cham:
        print(f"Ngày chấm        : {scorecard.ngay_cham}")

    print("\nChi tiết các tiêu chí trong phiếu:")
    print(f"{'Mã':<8} | {'Nhóm':<10} | {'Điểm/Max':<10} | {'Nguồn bằng chứng':<30}")
    print("-" * 70)
    for ma, item in scorecard.items.items():
        c = catalog.criteria[ma]
        score_text = "Chưa chấm" if item.diem is None else f"{item.diem}/{c.diem_toi_da}"
        print(f"{ma:<8} | {c.nhom:<10} | {score_text:<10} | {item.nguon_bang_chung:<30}")

    print("-" * 70)
    if scorecard.trang_thai == ScorecardStatus.HOAN_THANH:
        print(f"TRẠNG THÁI       : [✓] HOÀN THÀNH (Đủ {len(catalog.criteria)}/{len(catalog.criteria)} tiêu chí)")
        print(f"TỔNG ĐIỂM SẴN SÀNG: {scorecard.tong_diem} / {catalog.total_max_score} điểm")
    else:
        print(f"TRẠNG THÁI       : [✗] CHƯA HOÀN THÀNH (Theo FR-03)")
        print(f"Tiêu chí bị thiếu: {', '.join(scorecard.missing_criteria)}")
        print(f"Tổng điểm        : Chưa được công nhận (Cần bổ sung tiêu chí còn thiếu)")
    print("=" * 70)


if __name__ == "__main__":
    main()
