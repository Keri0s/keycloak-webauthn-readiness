# Báo cáo thu thập bằng chứng bổ sung cho phiếu chấm lab (26/11/2026)

- **Thời điểm thực hiện:** `2026-11-26` (khoảng `22:23–22:29` UTC+7).
- **Người thực hiện live:** Trần Trung Hiếu.
- **Môi trường:** Windows 11 + Docker Compose (`infra/compose.yaml`) + Python `3.12.10` (`apps/lab/.venv` và môi trường gốc).
- **Nguồn đối chiếu:** 6 ảnh chụp màn hình PowerShell, 1 ảnh Keycloak Admin Console trong hội thoại cùng 2 tệp JSON xuất trực tiếp vào thư mục này.

---

## 1. VA-02 — Kiểm tra lỗ hổng phụ thuộc Python (`pip-audit`)

- **Công cụ:** `pip-audit 2.10.1` chạy trong môi trường tạm `tmp/audit-venv` trên danh sách gói đầy đủ (`pip freeze`, bao gồm cả phụ thuộc bắc cầu).
- **Kết quả quan sát:**

| Phạm vi | Tệp kết quả | Số gói đã quét | Lỗ hổng phát hiện | SHA-256 tệp JSON |
| --- | --- | ---: | ---: | --- |
| `apps/lab/.venv` (`tmp/lab-freeze.txt`) | [`va02-pip-audit.json`](va02-pip-audit.json) | 18 | **0** (`No known vulnerabilities found`) | `569048faf9a45824730ff71d33de0038a40a852e3f27cc09d489afbd3e91e76a` |
| Python gốc (`tmp/root-freeze.txt`) | [`va02-root-pip-audit.json`](va02-root-pip-audit.json) | 7 | **0** (`No known vulnerabilities found`) | `4ef7308e13fc74c47069a1f5cf5fa72f65917f93abb610bc2584d5a03731cc27` |

- **Giới hạn:** Chỉ quét các gói Python thông qua cơ sở dữ liệu lỗ hổng PyPI/OSV tại ngày `26/11/2026`; chưa chạy công cụ quét lỗ hổng tầng hệ điều hành/JAR bên trong container Docker (như Trivy).

---

## 2. VA-03 — Ảnh nền OS/container chưa EOL

- Đã xác nhận `/etc/os-release` thực tế bên trong 3 container đang chạy và đối chiếu vòng đời hỗ trợ tại [`va03-eol-review.md`](va03-eol-review.md):
  - `caddy` (`caddy:2.11.9-alpine`): `Alpine Linux v3.24` (`3.24.4`, EOL `01/06/2028`); Caddy 2.11.9 là bản mới nhất tháng 11/2026.
  - `app-db` (`postgres:17.12-bookworm`): `Debian GNU/Linux 12 (bookworm)` (LTS EOL `30/06/2028`); PostgreSQL 17 EOL `08/11/2029`.
  - `keycloak` (`quay.io/keycloak/keycloak:26.8.2`): `Red Hat Enterprise Linux 9.9 (Plow)` (`platform:el9`, Full Support đến `31/05/2027`, Maintenance Support đến `31/05/2032`); Keycloak 26.8.2 là bản mới nhất nhánh cộng đồng tháng 11/2026.
- Python `3.12.10` (EOL `31/10/2028`) và Django `5.2.19` LTS (EOL `30/04/2028`) đều còn trong hạn hỗ trợ.

---

## 3. NK-03 — Kiểm tra đồng bộ đồng hồ NTP (`w32tm`)

- **Expected:** Kiểm tra trạng thái dịch vụ NTP trên máy host Windows (`w32tm`) và đối chiếu giờ UTC với các container Docker.
- **Observed:**
  - Chạy `w32tm /query /status` và `w32tm /query /source` bằng PowerShell Administrator lúc `22:29` (`15:24 UTC` trong terminal) đều trả về: `The service has not been started. (0x80070426)`.
  - **Kết luận thực tế:** Dịch vụ đồng bộ thời gian Windows Time (`W32Time`) trên máy host hiện **chưa được khởi động** (không chạy đồng bộ NTP tự động).
  - Phần lệnh `docker compose -f .\infra\compose.yaml exec -T ... date -u` ở lượt chạy này thực thi từ một thư mục khác nên không tìm thấy `infra/compose.yaml`, chưa lấy được đối chiếu giờ UTC container.

---

## 4. XT-03 — Brute force detection trên Keycloak

- **Expected:** Kiểm tra cấu hình *Brute force detection* trên realm `webauthn-lab`.
- **Observed:** Ảnh chụp Keycloak Admin Console (`https://auth.readiness.test:9443/admin/master/console/#/webauthn-lab/realm-settings/security-defenses`, tài khoản `lab-owner`, đồng hồ Windows `22:36` ngày `26/11/2026`) hiển thị realm `webauthn-lab` (`Enabled`), tại tab **Security defenses → Brute force detection**: **`Brute Force Mode: Disabled`**.
- **Giới hạn:** Ảnh gốc hiện nằm trong lịch sử hội thoại, chưa sao chép vào repository. Đây là bằng chứng thực tế xác nhận cụm lab hiện chưa bật tính năng chống brute-force ở tầng realm Keycloak.

---

## 5. Kết quả chấm phiếu lab thực tế (`27 / 37` — ngày 26/11/2026)

Sau khi có đủ bằng chứng thực tế cho cả 16/16 tiêu chí và nhận xác nhận từ người đánh giá (`Trần Trung Hiếu`), đã lưu phiếu chính thức tại [`evidence/lab-scorecard/phieu_cham_lab_2026-11-26.csv`](../../../evidence/lab-scorecard/phieu_cham_lab_2026-11-26.csv) và chạy CLI đánh giá:

```powershell
python -m apps.readiness.cli --scorecard evidence/lab-scorecard/phieu_cham_lab_2026-11-26.csv --evaluator "Trần Trung Hiếu" --date 2026-11-26
```

- **Kết quả:** `exit_code = 0`, trạng thái **`[✓] HOÀN THÀNH (Đủ 16/16 tiêu chí)`**, **`TỔNG ĐIỂM SẴN SÀNG: 27 / 37 điểm`**.
- **Phân bổ điểm theo 4 nhóm:**
  - `cau_hinh`: **8 / 10** (`CH-01=2/3`, `CH-02=2/2`, `CH-03=1/2`, `CH-04=3/3`)
  - `va_loi`: **7 / 9** (`VA-01=1/2`, `VA-02=3/3`, `VA-03=2/2`, `VA-04=1/2`)
  - `xac_thuc`: **6 / 10** (`XT-01=3/3`, `XT-02=2/3`, `XT-03=0/2`, `XT-04=1/2`)
  - `nhat_ky`: **6 / 8** (`NK-01=3/3`, `NK-02=2/2`, `NK-03=0/1`, `NK-04=1/2`)
- **Bằng chứng đầu ra:** [`cli-output.txt`](cli-output.txt) và [`scorecard-run.json`](scorecard-run.json).
- **Phân biệt và giới hạn:** `27/37` là điểm thực tế của cụm lab ngày `26/11/2026` (khác với điểm mẫu `29/37` của fixture trong `DU_LIEU_MAU/`). Điểm `VA-02=3/3` tính theo kết quả `0` lỗ hổng trên 18 + 7 gói Python qua `pip-audit` (chưa quét tầng OS/JAR container); `XT-03=0` và `NK-03=0` phản ánh đúng hiện trạng `Brute Force Mode: Disabled` và `W32Time` chưa chạy.
