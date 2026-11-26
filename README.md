# Keycloak WebAuthn Readiness

Đồ án xây dựng bộ đánh giá mức sẵn sàng an ninh và lab kiểm chứng xác thực, quản lý phiên với Keycloak, Django và PostgreSQL. Tác giả: Trần Trung Hiếu.

## Cập nhật đối chiếu ngày 26/11/2026

Đã hoàn tất chấm điểm **phiếu đánh giá lab thực tế** tại [phieu_cham_lab_2026-11-26.csv](evidence/lab-scorecard/phieu_cham_lab_2026-11-26.csv)
sau khi thu thập bổ sung bằng chứng `pip-audit` (`VA-02`), đối chiếu EOL + `/etc/os-release` 3 container (`VA-03`), `w32tm` (`NK-03`) và cấu hình *Brute Force Mode* (`XT-03`): đạt **`27 / 37` điểm** (`HOÀN THÀNH` đủ 16/16 tiêu chí; xem [báo cáo chấm lab](docs/validation/scorecard-evidence-2026-11-26/report.md) và [cli-output.txt](docs/validation/scorecard-evidence-2026-11-26/cli-output.txt)).
Số liệu `27/37` phản ánh hiện trạng lab thực ngày `26/11/2026` (tách biệt với mẫu fixture `29/37`); phiếu trống `phieu_cham_lab_draft.csv` được giữ để chấm lại khi triển khai ở môi trường khác.

Cùng ngày, README đã được bổ sung bảng **Phiên bản công cụ và môi trường thực dùng** (tổng hợp theo phiên bản thực đo 22–26/11/2026) và mục **Hướng dẫn dựng lab từ trạng thái sạch (Clean Setup)** gồm 9 bước. Lưu ý ranh giới: quy trình dựng sạch được hoàn thiện từ cấu hình thực tế đang vận hành ngày `26/11/2026` nhưng **chưa được chạy kiểm chứng lại từ đầu trên một máy sạch độc lập**.

## Cập nhật đối chiếu ngày 23/11/2026

Đã hoàn tất kiểm chứng sổ bằng chứng live `evidence/ledger/so_bang_chung.csv`
(67 dòng từ Keycloak Admin Events qua `apps/ledger`, 13 unit test offline PASS;
xem [báo cáo sổ live](docs/validation/ledger-2026-11-23/report.md)), cập nhật cấu hình
hiệu lực mới [inspection 23/11](docs/validation/passwordless-preflight/20261123T135327930466Z/review.md)
(`app-lab` dùng `browser-passkey-uv`, `UV=required`), rà tĩnh [NFR-01/NFR-02](docs/validation/nfr01-02-2026-11-23/report.md)
và quét bổ sung [FR-08/NFR-04](docs/validation/fr08-2026-11-23/export-review.md)
(62 tệp JSON/JSONL/CSV đạt `0` marker khóa riêng). Xem tổng hợp 20 mã tại
[Ma trận 20 yêu cầu](docs/validation/requirements-review-2026-11-23/report.md) và
[docs/truy_vet.csv](docs/truy_vet.csv). Tiếp theo còn hoàn thành một lượt demo liền
mạch từ đăng ký → đăng nhập → mở dòng theo README (NFR-03) và tự điền điểm cho
phiếu chấm lab thực tại `evidence/lab-scorecard/`. Lỗi native cần Try again vẫn
tạm hoãn (`DEFERRED_OPEN`); không coi là đã sửa. Các số liệu bảng 18/11 dưới đây
là mốc lịch sử.

## Trạng thái lịch sử ngày 18/11/2026

| Thành phần | Đã làm | Phần còn lại |
| --- | --- | --- |
| Readiness engine | Nạp YAML/CSV, kiểm tra dữ liệu, tính điểm, CLI; hồ sơ 81 tests PASS ngày 13/11 | Đưa bằng chứng đo từ lab vào phiếu thay cho dữ liệu mẫu |
| Lab OIDC | Cấu hình Compose/Caddy, callback, liên kết danh tính, cookie phiên và logout | Hoàn thiện hướng dẫn dựng máy sạch; kiểm chứng thêm giao thức và vận hành |
| Quản lý phiên | Group theo issuer/client/SID, binding Django session, marker thu hồi, receipt chống xử lý lặp, transaction lock | 10 ca còn lại trong ma trận 19 ca; các quyết định thu hồi theo subject |
| Kiểm chứng phiên | 9/19 ca ghi PASS, một số fault injection đã chạy | Mở rộng coverage; concurrency và thử nghiệm Keycloak thật |
| Sổ sự kiện, bằng chứng WebAuthn | Có dữ liệu và hồ sơ mẫu | Thu thập sự kiện thực, thử hủy xác thực, kiểm chứng không lộ private key và nghiệm thu |

PASS hiện có chỉ áp dụng cho phạm vi từng bài kiểm thử. 81 tests readiness và 19 kịch bản phiên là hai bộ khác nhau. Điểm 29/37 là kết quả fixture, không phải điểm an ninh của lab. Đây là đồ án đang phát triển, chưa phải bản triển khai production đã nghiệm thu.

## Đọc repository từ đâu?

| File/thư mục | Vai trò |
| --- | --- |
| [apps/](apps/README.md) | Hai phần ứng dụng readiness và lab |
| [apps/readiness/](apps/readiness/README.md) | Models, loader, parser, evaluator và CLI tính điểm |
| [apps/ledger/](apps/ledger/README.md) | Kéo Keycloak Admin Events và xem sổ bằng chứng theo allowlist |
| [apps/lab/](apps/lab/README.md) | Django app OIDC và ánh xạ phiên; có chú thích từng module |
| [infra/](infra/README.md) | Docker Compose cho hai database, Keycloak và Caddy |
| [tests/](tests/README.md) | Tests readiness và ma trận kịch bản phiên |
| [tmp/](tmp/README.md) | Các script thực nghiệm được chọn để tái lập kết quả lab |
| [docs/](docs/README.md) | Chỉ mục bằng chứng và kế hoạch công việc tiếp theo |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Đã làm, chưa làm, ưu tiên tiếp theo và giới hạn |
| [docs/validation/](docs/validation/README.md) | Báo cáo, kết quả máy đọc được và hash nguồn tại thời điểm chạy |
| [DU_LIEU_MAU/N15_San_sang_WebAuthn/](DU_LIEU_MAU/N15_San_sang_WebAuthn/README.md) | Catalog 16 tiêu chí, CSV và realm mẫu tổng hợp |
| [evidence/](evidence/README.md) | Hồ sơ mẫu theo CH/VA/XT/NK, chưa phải nghiệm thu lab |
| requirements.txt | Dependencies cho readiness/tests; lab có requirements riêng |
| .gitignore | Loại secrets, runtime, DB, môi trường Python và tài liệu nội bộ |

## Phiên bản công cụ và môi trường thực dùng

Bảng dưới đây ghi nhận các phiên bản hệ điều hành, trình duyệt, container image, runtime và thư viện thực tế đã đối chiếu trong quá trình kiểm thử và chấm lab tính đến ngày `26/11/2026`:

| Thành phần | Phiên bản thực dùng | Ghi chú / vai trò |
| --- | --- | --- |
| Hệ điều hành máy chủ | Windows 11 Home Single Language 26H2 (`OS Build 26300.9974`, x64) | Máy chạy Docker Desktop, trình duyệt và Django lab |
| Trình duyệt & Authenticator | Microsoft Edge `158.0.4370.33` (64-bit, Official build) | Windows Hello PIN / Microsoft Password Manager |
| Docker | Docker Desktop `4.97.0` (Engine/CLI `29.9.2`, Compose `v5.6.1`, `linux/amd64`) | Chạy cụm hạ tầng trong `infra/compose.yaml` |
| Reverse proxy HTTPS | `caddy:2.11.9-alpine` (OS container: Alpine Linux `3.24.4`) | Terminate TLS nội bộ tại `127.0.0.1:9443` |
| Identity Provider (IdP) | `quay.io/keycloak/keycloak:26.8.2` (OS container: RHEL `9.9 (Plow)`) | Realm `webauthn-lab`, flow `browser-passkey-uv`, OIDC + WebAuthn |
| Cơ sở dữ liệu | `postgres:17.12-bookworm` (OS container: Debian `12 (bookworm)`) | Hai instance tách biệt: `keycloak-db` và `app-db` (host `127.0.0.1:15432`) |
| Ngôn ngữ Python | Python `3.12.10` | Dùng cho cả bộ readiness/tests ở gốc và Django lab/ledger |
| Readiness & Tests (`requirements.txt`) | `PyYAML 6.0.3` (`>=6.0.0`), `pytest 9.2.0` (`>=9.0.0`), `requests 2.34.2` | Cài ở môi trường gốc để chạy `apps/readiness` và `tests/` |
| Lab & Ledger (`apps/lab/requirements.txt`) | `Django 5.2.19` (LTS), `Authlib 1.9.6`, `requests 2.34.2`, `psycopg[binary] 3.3.9`, `python-dotenv 1.2.4` | Cài tại `apps/lab/.venv` *(phụ thuộc chính: `cryptography 50.0.2`, `joserfc 1.8.0`, `urllib3 2.8.0`)* |
| Rà lỗ hổng Python (`VA-02`, tùy chọn) | `pip-audit 2.10.1` | Dùng trong venv tạm khi đánh giá lỗ hổng thư viện và xóa sau khi xuất báo cáo |

*Lưu ý tách biệt hai môi trường Python:* môi trường gốc (`requirements.txt`) chạy `apps/readiness` và `pytest tests`; môi trường ảo `apps/lab/.venv` (`apps/lab/requirements.txt`) chạy ứng dụng Django (`apps/lab`), CLI sổ bằng chứng (`apps/ledger`) và công cụ kiểm kê Keycloak (`infra/passwordless/inspect_keycloak.py`).

## Chạy readiness

Từ thư mục gốc, dùng Python 3.12 trong môi trường ảo:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -q
python -m apps.readiness.cli --scorecard DU_LIEU_MAU/N15_San_sang_WebAuthn/phieu_cham_mau_day_du.csv --evaluator "Nguoi cham lab"
```

CLI nhận phiếu CSV và catalog YAML; ô chưa chấm khác điểm 0. Bộ mẫu có 16 tiêu chí, tổng tối đa 37. Chi tiết quy tắc nằm trong README của readiness.

## Hướng dẫn dựng lab từ trạng thái sạch (Clean Setup)

Clone repository rồi chạy `docker compose up -d` chưa đủ vì lab yêu cầu CA nội bộ của Caddy phải tồn tại trước khi Keycloak khởi động, có tài khoản quản trị Keycloak 26, role PostgreSQL `lab_app`, cấu hình realm/flow/client khớp [inspection.json](docs/validation/passwordless-preflight/20261123T135327930466Z/inspection.json) và liên kết `ExternalIdentity`. Tham khảo thêm [infra/README.md](infra/README.md) và [apps/lab/README.md](apps/lab/README.md).

### Bước 1 — Yêu cầu hệ thống & tải mã nguồn
- Máy Windows 10/11 hỗ trợ Docker Desktop (Linux containers, WSL2), Python `3.12`, Git, Microsoft Edge/Chrome và Windows Hello PIN (hoặc passkey authenticator tương thích).
- Đảm bảo trống các cổng local `9443` (Caddy), `15432` (`app-db`) và `18000` (Django lab).
- Clone repository vào thư mục làm việc local:

```powershell
git clone https://github.com/Keri0s/keycloak-webauthn-readiness.git
cd keycloak-webauthn-readiness
```

### Bước 2 — Cấu hình tên miền local (`hosts` Windows)
Mở PowerShell hoặc Notepad với quyền **Administrator**, thêm hai dòng sau vào `C:\Windows\System32\drivers\etc\hosts`:

```text
127.0.0.1 auth.readiness.test
127.0.0.1 app.readiness.test
```

Kiểm tra phân giải tên (không dùng tên miền hệ thống Trường — NFR-02):

```powershell
Resolve-DnsName auth.readiness.test
Resolve-DnsName app.readiness.test
```

### Bước 3 — Chuẩn bị biến môi trường hạ tầng (`infra/.env`)
Sao chép mẫu và tự điền hai mật khẩu ngẫu nhiên riêng cho `KEYCLOAK_DB_PASSWORD` và `LAB_DB_ADMIN_PASSWORD` (tuyệt đối không dùng lại mật khẩu hệ thống thật và không commit `.env`):

```powershell
Copy-Item infra\.env.example infra\.env
```

### Bước 4 — Khởi tạo CA nội bộ Caddy trước khi chạy Keycloak (bắt buộc đúng thứ tự)
`infra/compose.yaml` mount trực tiếp file `./.runtime/keycloak-trust/readiness-root.pem` vào container Keycloak (`KC_TRUSTSTORE_PATHS`). **Không** chạy `docker compose up -d` toàn bộ trước khi tệp này tồn tại, vì Docker sẽ tự tạo một thư mục rỗng cùng tên làm Keycloak lỗi khởi động.

1. Khởi chạy riêng dịch vụ `caddy` để Caddy tạo CA nội bộ:

   ```powershell
   docker compose -f infra/compose.yaml up -d caddy
   ```

2. Chờ vài giây rồi kiểm tra `root.crt` đã được sinh chưa (nếu chưa, mở/gửi thử 1 request bất kỳ tới `https://auth.readiness.test:9443` hoặc đợi vài giây rồi kiểm tra lại):

   ```powershell
   Test-Path infra\.runtime\caddy-data\caddy\pki\authorities\local\root.crt
   ```

3. Chỉ sao chép **chứng chỉ công khai** `root.crt` (tuyệt đối không sao chép `root.key`) để Keycloak container và các CLI Python tin cậy CA này:

   ```powershell
   New-Item -ItemType Directory -Force infra\.runtime\keycloak-trust | Out-Null
   Copy-Item infra\.runtime\caddy-data\caddy\pki\authorities\local\root.crt infra\.runtime\keycloak-trust\readiness-root.pem
   ```

4. Cài `root.crt` vào **Trusted Root Certification Authorities** của Windows (chạy PowerShell bằng **Administrator**) để Edge/Chrome không báo lỗi chứng chỉ khi gọi WebAuthn:

   ```powershell
   Import-Certificate -FilePath .\infra\.runtime\caddy-data\caddy\pki\authorities\local\root.crt -CertStoreLocation Cert:\LocalMachine\Root
   ```

*(Ghi chú: Django đọc trực tiếp `infra/.runtime/caddy-data/caddy/pki/authorities/local/root.crt` qua `OIDC_CA_BUNDLE` trong `apps/lab/config/settings.py`; Keycloak container, `apps/ledger` và `inspect_keycloak.py` đọc `infra/.runtime/keycloak-trust/readiness-root.pem`.)*

### Bước 5 — Khởi chạy DB, tạo admin Keycloak 26.8.2 rồi bật Keycloak
Keycloak 26 sử dụng cơ chế bootstrap admin cho database mới khởi tạo (thay cho biến cũ `KEYCLOAK_ADMIN`). Thực hiện theo đúng thứ tự:

1. Bật hai database PostgreSQL trước:

   ```powershell
   docker compose -f infra/compose.yaml up -d keycloak-db app-db
   ```

2. Tạo tài khoản quản trị tạm trong realm `master` trên DB trống (nhập username/password trực tiếp trong terminal, không lưu vào `compose.yaml`):

   ```powershell
   docker compose -f infra/compose.yaml run --rm keycloak bootstrap-admin user
   ```

3. Khởi động dịch vụ `keycloak` và kiểm tra trạng thái:

   ```powershell
   docker compose -f infra/compose.yaml up -d keycloak
   docker compose -f infra/compose.yaml ps
   ```

4. Mở `https://auth.readiness.test:9443/admin/master/console/`, đăng nhập bằng tài khoản bootstrap vừa tạo, tạo tài khoản quản trị cố định (ví dụ `lab-owner`, gán role `admin` của realm `master`), đăng xuất rồi đăng nhập lại bằng `lab-owner` và xóa tài khoản bootstrap tạm.

### Bước 6 — Tạo role PostgreSQL `lab_app` trên `app-db`
`infra/compose.yaml` chỉ khởi tạo role quản trị `lab_db_admin`, trong khi `apps/lab/config/settings.py` kết nối DB `readiness_lab` bằng role riêng `lab_app`. Trên PostgreSQL 17, quyền `CREATE` trên schema `public` bị thu hồi mặc định với `PUBLIC`, nên cần cấp tường minh để `manage.py migrate` chạy được.

Mở `psql` vào `app-db`:

```powershell
docker compose -f infra/compose.yaml exec app-db psql -U lab_db_admin -d readiness_lab
```

Chạy các câu lệnh SQL sau (thay `<MAT_KHAU_LAB_APP>` bằng mật khẩu mạnh tự chọn, dùng lại ở Bước 8):

```sql
CREATE ROLE lab_app WITH LOGIN PASSWORD '<MAT_KHAU_LAB_APP>';
GRANT CONNECT ON DATABASE readiness_lab TO lab_app;
GRANT USAGE, CREATE ON SCHEMA public TO lab_app;
\q
```

### Bước 7 — Cấu hình Keycloak realm `webauthn-lab`, WebAuthn Policy, Flow và Client `app-lab`
Trong Keycloak Admin Console (`https://auth.readiness.test:9443/admin/master/console/`), tạo realm `webauthn-lab` (`Enabled = ON`) với cấu hình khớp bản kiểm kê ngày `23/11/2026`:

1. **Realm settings → Login:** tắt `User registration`, `Forgot password`, `Remember me`.
2. **Realm settings → Events → User events settings:** bật `Save events = ON`, đặt `Expiration = 7 days` (`604800` giây), đảm bảo có các event `LOGIN`, `LOGIN_ERROR`, `UPDATE_CREDENTIAL`, `UPDATE_CREDENTIAL_ERROR`, `LOGOUT`, `CODE_TO_TOKEN`.
3. **Authentication → Policies → WebAuthn Passwordless Policy:**
   - `Relying Party Entity Name`: `Readiness Lab`
   - `Signature Algorithms`: `ES256`, `RS256`
   - `Relying Party ID`: `auth.readiness.test`
   - `Attestation Conveyance Preference`: `None`
   - `Authenticator Attachment`: `Platform` *(chọn `Not specified` nếu dùng khóa bảo mật rời)*
   - `User Verification Requirement`: `Required`
   - `Timeout`: `60`
4. **Authentication → Required actions:** bật `Webauthn Register Passwordless` (`webauthn-register-passwordless`, `Enabled = ON`, `Default Action = OFF`).
5. **Authentication → Flows:** tạo top-level `Basic flow` mới tên **`browser-passkey-uv`** với 2 bước ở cấp gốc (level 0):
   - `Username Form` (`auth-username-form`) — **Required**
   - `WebAuthn Passwordless Authenticator` (`webauthn-authenticator-passwordless`) — **Required**
   *(Không đặt làm Browser Flow mặc định toàn realm để tránh khóa Admin/Account Console nếu cần thao tác quản trị; gắn qua override cho riêng `app-lab`.)*
6. **Clients → Create client (`app-lab`, OpenID Connect):**
   - `Client authentication`: `ON` (confidential client); bật `Standard flow`; tắt `Direct access grants`, `Implicit flow`, `Service accounts roles`.
   - `Valid redirect URIs`: `https://app.readiness.test:9443/auth/callback/`
   - `Valid post logout redirect URIs`: `https://app.readiness.test:9443/auth/logged-out/`
   - `Web origins`: để trống
   - `Logout settings → Backchannel logout URL`: `https://app.readiness.test:9443/auth/backchannel-logout/` và bật `Backchannel logout session required = ON`
   - `Advanced → PKCE Code Challenge Method`: `S256`
   - `Advanced → Authentication flow overrides → Browser Flow`: chọn `browser-passkey-uv`
   - Vào tab **Credentials** sao chép `Client Secret` cho Bước 8.
7. **Users → Add user:** tạo tài khoản thử tổng hợp `lab-user-01` (`Enabled = ON`, không dùng thông tin tài khoản Trường — DR-04), ghi lại **User ID (UUID)** để liên kết ở Bước 8.

### Bước 8 — Cài đặt, migrate, liên kết danh tính và chạy Django (`apps/lab`)
1. Tạo virtualenv, cài dependencies đúng phiên bản và tạo `.env`:

   ```powershell
   cd apps\lab
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

2. Mở `apps\lab\.env` và điền đầy đủ giá trị:
   - `DJANGO_SECRET_KEY`: chuỗi ngẫu nhiên sinh bằng `.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(50))"`
   - `LAB_DB_PASSWORD`: mật khẩu của role `lab_app` đã tạo ở Bước 6
   - `OIDC_ISSUER=https://auth.readiness.test:9443/realms/webauthn-lab`
   - `OIDC_CLIENT_ID=app-lab`
   - `OIDC_CLIENT_SECRET`: lấy từ tab **Credentials** của client `app-lab` ở Bước 7

3. Chạy migration và kiểm tra cấu hình Django:

   ```powershell
   .\.venv\Scripts\python.exe manage.py migrate
   .\.venv\Scripts\python.exe manage.py check
   ```

4. Liên kết `ExternalIdentity` cho `lab-user-01` với tài khoản không có mật khẩu nội bộ (thay `<KEYCLOAK_USER_SUB_UUID>` bằng UUID của user `lab-user-01` lấy ở Bước 7; tham khảo [tmp/link_lab_user.py](tmp/link_lab_user.py)):

```powershell
$linkScript = @'
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from authn.models import ExternalIdentity

User = get_user_model()
subject = "<KEYCLOAK_USER_SUB_UUID>"

with transaction.atomic():
    user, _ = User.objects.get_or_create(
        username="lab-user-01",
        defaults={"password": make_password(None)},
    )
    identity, _ = ExternalIdentity.objects.get_or_create(
        issuer=settings.OIDC_ISSUER,
        subject=subject,
        defaults={"user": user},
    )
    if identity.user_id != user.pk:
        raise ValueError("Subject da lien ket voi user khac.")
    if user.has_usable_password():
        user.set_unusable_password()
        user.save(update_fields=["password"])
print("Linked:", user.username, identity.issuer, identity.subject)
'@
$linkScript | .\.venv\Scripts\python.exe manage.py shell
```

5. Khởi chạy Django dev server trên cổng `18000` (dùng `--noreload` để log/diagnostic dễ theo dõi):

   ```powershell
   .\.venv\Scripts\python.exe manage.py runserver 0.0.0.0:18000 --noreload
   ```

### Bước 9 — Kiểm tra nhanh sau khi dựng (Smoke check)
Mở terminal mới tại thư mục gốc repository:

```powershell
# 1. Kiểm tra kết nối HTTPS/OIDC discovery và đối chiếu cấu hình Keycloak hiệu lực
.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\inspect_keycloak.py --check-connectivity
.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\inspect_keycloak.py

# 2. Chạy các bộ test offline
python -m pytest tests -q
.\apps\lab\.venv\Scripts\python.exe -m unittest discover -s apps/ledger/tests -t . -v
.\apps\lab\.venv\Scripts\python.exe -m unittest discover -s infra/passwordless -p "test_*.py" -v
.\apps\lab\.venv\Scripts\python.exe apps\lab\manage.py test authn.test_oidc_recovery authn.test_login_evidence -v 2
```

Sau khi kiểm tra nhanh đạt, chuyển xuống mục **Demo nghiệm thu SRS (NFR-03)** bên dưới để đăng ký passkey, đăng nhập `/private/` và mở dòng bằng chứng trong `apps/ledger`.

> **Ranh giới trung thực (26/11/2026):** Hướng dẫn 9 bước ở trên được hoàn thiện bám sát cấu hình thực tế đang vận hành trên máy phát triển và dữ liệu `inspection.json`, nhưng quy trình dựng mới hoàn toàn này **chưa được chạy kiểm chứng lại trên một máy sạch độc lập** và chưa tự động hóa thành script cài đặt một chạm. Khi triển khai sang máy mới, nên chạy lại toàn bộ 9 bước, giữ nguyên phiếu trống `evidence/lab-scorecard/phieu_cham_lab_draft.csv` để chấm lại từ dữ liệu đo của máy mới.

## Demo nghiệm thu SRS (NFR-03)

Mục này mô tả luồng demo tại local để kiểm chứng **đăng ký passkey → đăng nhập passkey → mở một dòng bằng chứng** theo NFR-03:

### Điều kiện chuẩn bị
- Đã hoàn tất 9 bước dựng lab ở trên; hạ tầng Docker tại `infra/` (`docker compose -f infra/compose.yaml up -d`: `caddy`, `keycloak`, `keycloak-db`, `app-db`) đang chạy khỏe.
- Ứng dụng Django tại `apps/lab` đang chạy (chạy từ thư mục gốc repository hoặc vào `apps/lab` rồi gọi `manage.py`):

  ```powershell
  .\apps\lab\.venv\Scripts\python.exe apps\lab\manage.py runserver 0.0.0.0:18000 --noreload
  ```

- CA nội bộ của Caddy đã được tin cậy trên Windows/trình duyệt; file hosts trỏ `auth.readiness.test` và `app.readiness.test` về `127.0.0.1`; trình duyệt Edge/Chrome và Windows Hello PIN sẵn sàng.

### Ba bước demo chính
1. **Đăng ký passkey (FR-04 / IF-02 — có bước gán thủ công):**
   - Trong Keycloak Admin Console (`https://auth.readiness.test:9443`, realm `webauthn-lab`), gán required action `Webauthn Register Passwordless` (`webauthn-register-passwordless`) cho tài khoản thử `lab-user-01` (hoặc cấp quyền đăng ký theo quy trình admin lab).
   - Mở trình duyệt mới tới `https://app.readiness.test:9443/auth/login/`, nhập username `lab-user-01` và hoàn tất tạo passkey qua hộp thoại Windows Security / nhập PIN (thao tác thủ công của người dùng).
2. **Đăng nhập bằng passkey vừa tạo (FR-05 / IF-03):**
   - Nếu đang có phiên trước đó, bấm **Đăng xuất** tại `https://app.readiness.test:9443/private/`.
   - Mở mới `https://app.readiness.test:9443/auth/login/`, nhập `lab-user-01`, chọn **Sign in with Passkey**, xác nhận Windows Hello PIN và vào `https://app.readiness.test:9443/private/` (HTTP 200, hiển thị `Xin chào, lab-user-01`).
   - Có thể mở DevTools → Response Headers của `/private/` để xem `X-Lab-Session-Ref` và `X-Lab-Subject-Ref` dùng đối chiếu với Keycloak.
3. **Kéo và mở một dòng bằng chứng (FR-06 / IF-04 / NFR-04):**
   - Tại thư mục gốc, kéo sự kiện từ Keycloak Admin Events về sổ CSV (nhập tài khoản quản trị realm `master` trực tiếp trong terminal, không lưu mật khẩu):

     ```powershell
     .\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli pull --since 2026-11-16
     .\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show
     ```

   - Lấy một `evidence_id` trong bảng vừa in rồi mở chi tiết đúng một dòng bằng chứng (chỉ hiện các trường trong allowlist, không chứa khóa riêng):

     ```powershell
     .\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show --id <evidence_id>
     ```

   - **Phương án xem nguồn dự phòng:** mở Keycloak Admin Console → realm `webauthn-lab` → **Events** → tab **User events** để đối chiếu trực tiếp sự kiện `UPDATE_CREDENTIAL`, `LOGIN`, `LOGIN_ERROR`.

*(Lưu ý thao tác thủ công: gán required action trong Admin Console, xác nhận PIN trên hộp thoại Windows Security và nhập tài khoản quản trị trong terminal khi chạy `pull` hiện vẫn thực hiện thủ công. Hướng dẫn chi tiết thu dữ liệu kiểm thử xem tại [docs/validation/ledger-2026-11-23/runbook.md](docs/validation/ledger-2026-11-23/runbook.md).)*

Bản public không chứa `.env`, khóa riêng, CA runtime, dữ liệu PostgreSQL, cookie, token hoặc tài khoản thật. Chỉ dùng lab local với dữ liệu tổng hợp. SRS là tài liệu định hướng học thuật; phạm vi nghiệm thu cuối cùng còn cần được xác nhận. Các tài liệu bàn giao và trao đổi nội bộ không nằm trong bản public.
