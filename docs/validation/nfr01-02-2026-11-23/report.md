# Báo cáo rà soát tĩnh NFR-01 và NFR-02 (23/11/2026)

Báo cáo này kiểm tra hai yêu cầu phi chức năng:
- **NFR-01 (Không quét Trường):** Công cụ không có chức năng quét địa chỉ ngoài lab.
- **NFR-02 (Tách realm):** Tệp cấu hình không chứa địa chỉ cụm Keycloak đang vận hành.

Phương pháp kiểm tra theo SRS: **Rà soát** tĩnh mã nguồn, định tuyến, CLI và cấu hình không bí mật tại thời điểm **23/11/2026**. Không thực hiện quét mạng; không đọc tệp `.env`, thư mục `.runtime/`, volume PostgreSQL/Keycloak hoặc `references/`.

---

## 1. Rà soát NFR-01: Điểm gọi mạng và đầu vào địa chỉ

Phạm vi quét: `apps/` (gồm `readiness`, `lab`, `ledger`), `infra/` (bỏ `.runtime/`, `.venv/`), `tests/`, các tệp `tmp/` trong danh sách công bố và `DU_LIEU_MAU/N15_San_sang_WebAuthn/`.

| Thành phần | Thư viện / điểm gọi mạng hoặc hệ thống | Đích cố định / nguồn cấu hình | Có nhận địa chỉ đích từ người dùng? |
| --- | --- | --- | --- |
| `apps/readiness/` (`cli.py`, `loader.py`, `parser.py`, `evaluator.py`, `models.py`) | Không import `requests`, `urllib`, `socket`, `http.client`, `subprocess`. Chỉ đọc YAML/CSV cục bộ bằng `open()` / `Path`. | Không kết nối mạng | Không |
| `apps/ledger/keycloak.py` | `requests.Session()` (`trust_env=False`, `allow_redirects=False`, `verify=CA`, `timeout=15`) | Cố định `BASE="https://auth.readiness.test:9443"`, `REALM="webauthn-lab"`, `CLIENT="app-lab"`; từ chối path không bắt đầu bằng `/` hoặc bắt đầu bằng `//` | Không; CLI `pull`/`show` chỉ nhận `--since`, `--operation`, `--outcome`, `--id`, `--ledger` (file CSV cục bộ) |
| `apps/ledger/mapping.py` | Không import `requests` (có unit test kiểm chứng) | Thuần chuyển đổi dict sự kiện thành dòng CSV | Không |
| `apps/lab/config/oidc.py`, `authn/views.py`, `authn/backchannel.py` | `Authlib` (`DjangoOAuth2App`) gọi discovery, token, userinfo, logout, JWKS | Lấy từ `settings.OIDC_ISSUER` (biến môi trường), kiểm tra khớp `issuer` trong metadata/ID Token/Logout Token và xác minh TLS qua `OIDC_CA_BUNDLE` | Không; các route ở `apps/lab/config/urls.py` chỉ gồm `/`, `/admin/`, `/auth/login/`, `/auth/callback/`, `/private/`, `/auth/logout/`, `/auth/logged-out/`, `/auth/backchannel-logout/` |
| `infra/passwordless/inspect_keycloak.py` | `requests.Session()` (`trust_env=False`, `allow_redirects=False`, `verify=CA`, `timeout=15`) | Cố định `BASE="https://auth.readiness.test:9443"`, `REALM="webauthn-lab"`, `CLIENT="app-lab"` | Không |
| `infra/passwordless/audit_fr08_logs.py` | `subprocess.run(["docker", "compose", "-f", "infra/compose.yaml", "logs", ...])` | Chỉ chạy cho 2 service cố định `"keycloak"` và `"caddy"` trong `infra/compose.yaml` | Không |
| `tests/`, `tmp/` công bố | Chỉ tạo `SimpleNamespace` / fixture giả lập `https://auth.readiness.test:9443/realms/...` hoặc `https://synthetic.test/realm` trong bộ nhớ | Không phát sinh kết nối ra ngoài | Không |

Kết quả tìm kiếm các chuỗi công cụ/module quét mạng (`nmap`, `masscan`, `scapy`, `paramiko`, `socket.`, `urllib.request`, `http.client`, `httpx`, `aiohttp`, `ipaddress`, `os.system`, `popen`) trên toàn bộ tệp `.py` trong phạm vi trên: **0 kết quả**.

---

## 2. Rà soát NFR-02: Cấu hình hiệu lực không bí mật và kiểm tra tên miền Trường

### Bảng cấu hình không bí mật đã đọc

| Nguồn | Trường / biến cấu hình | Giá trị quan sát | Ghi chú |
| --- | --- | --- | --- |
| `infra/compose.yaml` | `KC_HOSTNAME`, `KC_DB_URL`, ports | `https://auth.readiness.test:9443`; PostgreSQL nội bộ `keycloak-db:5432/keycloak_lab`; `127.0.0.1:9443`, `127.0.0.1:15432` | Mật khẩu DB nạp từ biến môi trường |
| `infra/Caddyfile` | Virtual hosts & upstream | `https://auth.readiness.test:9443 -> keycloak:8080`; `https://app.readiness.test:9443 -> host.docker.internal:18000` | Dùng `tls internal` |
| `apps/lab/config/settings.py` | `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `OIDC_REDIRECT_URI`, `OIDC_POST_LOGOUT_REDIRECT_URI`, `DATABASES.default` | `app.readiness.test`; `https://app.readiness.test:9443`; `/auth/callback/`; `/auth/logged-out/`; DB `127.0.0.1:15432/readiness_lab` | `OIDC_ISSUER`, `OIDC_CLIENT_ID`, `OIDC_CLIENT_SECRET`, `DJANGO_SECRET_KEY`, `LAB_DB_PASSWORD` đọc từ `os.environ` |
| `apps/lab/.env.example` | `OIDC_ISSUER`, `OIDC_CLIENT_ID` | `https://auth.readiness.test:9443/realms/webauthn-lab`, `app-lab` | Mẫu không chứa secret |
| `apps/ledger/schema.py`, `infra/passwordless/inspect_keycloak.py` | `LAB_BASE_URL` / `BASE`, `REALM`, `CLIENT` | `https://auth.readiness.test:9443`, `webauthn-lab`, `app-lab` | Cố định trong mã |
| `docs/validation/passwordless-preflight/20261122T071144990590Z/inspection.json` | `realm`, `clientId`, `redirectUris`, `post.logout.redirect.uris`, `backchannel.logout.url` | `webauthn-lab`, `app-lab`, `https://app.readiness.test:9443/auth/...` | Bản chụp mốc lịch sử **22/11/2026** |
| `docs/validation/passwordless-preflight/20261123T135327930466Z/inspection.json` | `effective_browser_flow`, `webAuthnPolicyPasswordless*`, `client_override`, `redirectUris` | `browser-passkey-uv` (`auth-username-form` + `webauthn-authenticator-passwordless`), `RP ID=auth.readiness.test`, `UV=required`, `app-lab` trên `https://app.readiness.test:9443` | Bản chụp hiệu lực mới lúc **23/11/2026 13:53:27Z** (SHA-256 `28764e84...`, sạch marker FR-08) |
| `DU_LIEU_MAU/N15_San_sang_WebAuthn/realm/webauthn-lab-realm.json` | `realm`, `clientId`, `redirectUris` | `webauthn-lab`, `app-lab`, `https://app.lab.local/*`, `http://localhost:3000/*` | File mẫu tổng hợp |

### Kết quả tìm kiếm tên miền Trường và URL Keycloak

Tìm kiếm regex `(stu\.edu|hutech|\.edu\.vn)` trên mã nguồn, cấu hình, fixture, mẫu và tài liệu công bố (`apps/`, `infra/` bỏ `.runtime`/`.venv`, `tests/`, `tmp/` công bố, `DU_LIEU_MAU/N15_San_sang_WebAuthn/`, `README.md`, `docs/README.md`, `docs/ROADMAP.md`, `docs/validation/`, `evidence/`, `requirements.txt`):

- **Số kết quả tên miền Trường (`stu.edu`, `hutech`, `.edu.vn`):** **0** trong tất cả mã nguồn, cấu hình, dữ liệu mẫu và tài liệu đã quét.
- **Số kết quả chuỗi `keycloak.` trong tài liệu/requirements:** **14** kết quả, toàn bộ là tên tệp/module nội bộ (`inspect_keycloak.py`, `fr08-keycloak.sql`) hoặc chữ ký/JS trong bài kiểm tra `webauthnAuthenticate.js`; không có bất kỳ địa chỉ cụm Keycloak vận hành nào bên ngoài `auth.readiness.test`.

---

## 3. Kết luận và giới hạn

- **Kết luận trong phạm vi rà soát tĩnh và kiểm kê hiệu lực:** Mã nguồn và các tệp cấu hình công bố không có chức năng quét địa chỉ ngoài lab (**NFR-01**) và không chứa địa chỉ cụm Keycloak đang vận hành (**NFR-02**, đã xác nhận thêm bản `inspection.json` lúc `2026-11-23T13:53:27Z`).
- **Giới hạn:**
  1. Đây là kiểm tra tĩnh trên repo kết hợp đầu ra `inspect_keycloak.py` theo allowlist; chưa đọc giá trị `.env` runtime trên máy người dùng (bị loại trừ theo quy tắc bảo mật) và không quét mạng.
  2. `realm.browserFlow` mặc định toàn realm vẫn là `browser-password-webauthn`, trong khi client `app-lab` gắn override sang `browser-passkey-uv` (xem chi tiết tại [review 23/11](../passwordless-preflight/20261123T135327930466Z/review.md)).
