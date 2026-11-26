# Đối chiếu vòng đời hỗ trợ (EOL) cho tiêu chí VA-03 (26/11/2026)

Tài liệu này kiểm tra yêu cầu **VA-03:** *"Ảnh nền hệ điều hành/container còn được hỗ trợ (chưa EOL)"* đối với các thành phần được khai báo trong [`infra/compose.yaml`](../../../infra/compose.yaml), [`apps/lab/requirements.txt`](../../../apps/lab/requirements.txt) và môi trường Python hiện hành.

- **Ngày đối chiếu:** `2026-11-26` (UTC+7).
- **Phương pháp:** Đối chiếu phiên bản khai báo với tài liệu phát hành và vòng đời hỗ trợ chính thức của nhà cung cấp.

---

## Bảng đối chiếu vòng đời hỗ trợ

| Thành phần | Phiên bản khai báo / đang chạy | Chính sách & mốc EOL từ nguồn chính thức | Trạng thái tại 26/11/2026 | Nguồn tham chiếu |
| --- | --- | --- | --- | --- |
| **Keycloak** | `quay.io/keycloak/keycloak:26.8.2` | Phát hành `05/11/2026`; là bản mới nhất nhánh cộng đồng tính đến tháng 11/2026. Cộng đồng Keycloak không có LTS và chỉ duy trì bản phát hành mới nhất. | **Chưa EOL** (còn được hỗ trợ) | `keycloak.org/downloads`, `github.com/keycloak/keycloak/releases` |
| **Caddy** | `caddy:2.11.9-alpine` (`Alpine Linux v3.24`, `3.24.4`) | Caddy 2.11.9 phát hành `04–05/11/2026` (mới nhất tháng 11/2026); Alpine Linux 3.24 phát hành `09/06/2026`, hỗ trợ đến **01/06/2028**. | **Chưa EOL** | `github.com/caddyserver/caddy/releases`, `alpinelinux.org` |
| **PostgreSQL** | `postgres:17.12-bookworm` | PostgreSQL 17 phát hành `26/09/2024`, hỗ trợ 5 năm đến **08/11/2029**. | **Chưa EOL** | `postgresql.org/support/versioning/` |
| **Debian (OS ảnh `app-db`)** | `Debian GNU/Linux 12 (bookworm)` | Debian 12 kết thúc full support `12/07/2026` và chuyển sang pha LTS chính thức đến **30/06/2028**. | **Chưa EOL** (pha LTS) | `debian.org/security`, `wiki.debian.org/LTS` |
| **RHEL (OS ảnh `keycloak`)** | `Red Hat Enterprise Linux 9.9 (Plow)` (`platform:el9`) | RHEL 9 có Full Support đến **31/05/2027** và Maintenance Support đến **31/05/2032**. | **Chưa EOL** (Full Support) | `redhat.com` |
| **Python** | `3.12.10` | Python 3.12 phát hành `02/10/2023`, nhận bản vá bảo mật (security-only) đến **31/10/2028**. | **Chưa EOL** (pha security fixes) | `python.org` |
| **Django** | `5.2.19` (LTS) | Django 5.2 LTS phát hành `02/04/2025`, hỗ trợ bảo mật đến **30/04/2028**. | **Chưa EOL** (LTS) | `djangoproject.com` |

---

## Xác nhận `/etc/os-release` thực tế trong container (26/11/2026)

Người dùng đã chạy `docker compose -f .\infra\compose.yaml exec -T <service> cat /etc/os-release` lúc `22:23` ngày `26/11/2026` (ảnh terminal gửi trong hội thoại):
- `caddy`: `Alpine Linux v3.24` (`VERSION_ID=3.24.4`).
- `app-db`: `Debian GNU/Linux 12 (bookworm)` (`VERSION_ID="12"`).
- `keycloak`: `Red Hat Enterprise Linux` `VERSION="9.9 (Plow)"` (`PLATFORM_ID="platform:el9"`).

**Kết luận:** Cả 3 OS nền trong container cùng các thành phần ứng dụng/CSDL/proxy (`Keycloak 26.8.2`, `Caddy 2.11.9`, `PostgreSQL 17.12`, `Python 3.12.10`, `Django 5.2.19 LTS`) đều đang còn trong hạn hỗ trợ chính thức tại ngày `26/11/2026`.

## Giới hạn

1. Đây là đối chiếu theo phiên bản khai báo trong `infra/compose.yaml`, `apps/lab/requirements.txt`, `python --version` và kết quả `/etc/os-release` tại ngày `26/11/2026`.
2. Việc OS/phần mềm chưa EOL không thay thế quét lỗ hổng định kỳ (xem kết quả quét Python tại [report.md](report.md)).
