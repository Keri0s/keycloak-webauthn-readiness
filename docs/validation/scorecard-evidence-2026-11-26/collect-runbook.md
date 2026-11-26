# Hướng dẫn thu thập bằng chứng bổ sung cho VA-02, VA-03, XT-03, NK-03 (26/11/2026)

Tài liệu này hướng dẫn các bước người dùng chạy trực tiếp tại thư mục gốc `D:\Projects\Do-an-thuctap-totnghiep` để thu dữ liệu thực tế cho 4 tiêu chí đang thiếu bằng chứng trước khi chốt điểm phiếu lab. Không sửa cấu hình runtime hay xuất secret.

---

## 1. VA-02 — Quét lỗ hổng phụ thuộc Python bằng `pip-audit`

> `pip-audit` chỉ tra cứu cơ sở dữ liệu lỗ hổng (PyPI/OSV) cho danh sách gói cục bộ trong dự án, **không** quét mạng ngoài lab (tuân thủ NFR-01). Thao tác bên dưới dùng venv tạm ở `tmp/audit-venv` (đã được `.gitignore` loại trừ) để không thay đổi môi trường `apps/lab/.venv`.

```powershell
# 1) Xuất danh sách phụ thuộc đầy đủ (kể cả phụ thuộc bắc cầu) của lab và readiness
.\apps\lab\.venv\Scripts\python.exe -m pip freeze > .\tmp\lab-freeze.txt
python -m pip freeze > .\tmp\root-freeze.txt

# 2) Tạo venv tạm và cài pip-audit
python -m venv .\tmp\audit-venv
.\tmp\audit-venv\Scripts\python.exe -m pip install pip-audit

# 3) Quét gói của apps/lab và gói môi trường gốc, lưu JSON kết quả
.\tmp\audit-venv\Scripts\pip-audit.exe -r .\tmp\lab-freeze.txt --format json -o .\docs\validation\scorecard-evidence-2026-11-26\va02-pip-audit.json
.\tmp\audit-venv\Scripts\pip-audit.exe -r .\tmp\lab-freeze.txt

.\tmp\audit-venv\Scripts\pip-audit.exe -r .\tmp\root-freeze.txt --format json -o .\docs\validation\scorecard-evidence-2026-11-26\va02-root-pip-audit.json
.\tmp\audit-venv\Scripts\pip-audit.exe -r .\tmp\root-freeze.txt

# 4) Dọn thư mục venv tạm sau khi đã xuất JSON (tránh làm lệch đợt quét export FR-08)
Remove-Item -Recurse -Force .\tmp\audit-venv
```

Gửi lại đầu ra terminal (hoặc báo cả 2 tệp JSON đã được ghi).

---

## 2. VA-03 — Xác nhận OS thực tế bên trong 3 container Docker

Kết hợp với bản đối chiếu EOL nguồn chính thức tại [`va03-eol-review.md`](va03-eol-review.md), chạy lệnh kiểm tra `/etc/os-release` của các container đang chạy:

```powershell
docker compose -f .\infra\compose.yaml exec -T caddy cat /etc/os-release
docker compose -f .\infra\compose.yaml exec -T app-db cat /etc/os-release
docker compose -f .\infra\compose.yaml exec -T keycloak cat /etc/os-release
```

---

## 3. XT-03 — Kiểm tra Brute-force protection trên Keycloak

1. Đăng nhập Keycloak Admin Console (`https://auth.readiness.test:9443`) bằng tài khoản quản trị (`lab-owner`).
2. Chuyển sang realm **`webauthn-lab`**.
3. Vào **Realm settings** → **Security defenses** → tab **Brute force detection**.
4. Chụp màn hình hoặc ghi lại trạng thái (**Enabled** đang `On` hay `Off`) cùng các giá trị cấu hình đang hiển thị (`Max login failures`, `Wait increment`, `Permanent lockout`, v.v.).

*(Lưu ý: Dù cấu hình hiện tại đang bật hay tắt thì vẫn là bằng chứng thực tế để chấm đúng điểm `XT-03` thay vì thiếu bằng chứng.)*

---

## 4. NK-03 — Kiểm tra đồng bộ đồng hồ NTP trên Windows và đối chiếu UTC container

1. Mở PowerShell (**Run as Administrator** nếu câu lệnh `w32tm` ở terminal thường báo *Access is denied*):

```powershell
w32tm /query /status
w32tm /query /source
```

2. Đối chiếu nhanh thời gian UTC giữa máy host Windows và các container Docker:

```powershell
[DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
docker compose -f .\infra\compose.yaml exec -T keycloak date -u +"%Y-%m-%dT%H:%M:%SZ"
docker compose -f .\infra\compose.yaml exec -T app-db date -u +"%Y-%m-%dT%H:%M:%SZ"
```
