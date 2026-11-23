# Hồ sơ bằng chứng NFR-01 — Không quét Trường

- **Yêu cầu (SRS 3.4, NFR-01):** *"Công cụ không có chức năng quét địa chỉ ngoài lab."*
- **Phương thức kiểm tra theo SRS:** `Rà soát`
- **Trạng thái hiện tại:** `Đã rà có giới hạn` (rà soát tĩnh ngày 23/11/2026)

## Bằng chứng hiện có
- Báo cáo rà soát tĩnh mã nguồn, CLI, định tuyến và cấu hình mạng: [`docs/validation/nfr01-02-2026-11-23/report.md`](../../docs/validation/nfr01-02-2026-11-23/report.md).
- Các điểm gọi ngoài duy nhất đều cố định đích lab local hoặc biến môi trường `OIDC_ISSUER`:
  - `apps/readiness/`: thuần đọc file YAML/CSV cục bộ.
  - `apps/ledger/keycloak.py` & `infra/passwordless/inspect_keycloak.py`: cố định `BASE="https://auth.readiness.test:9443"`, `REALM="webauthn-lab"`, `CLIENT="app-lab"`, `trust_env=False`, `allow_redirects=False`, kiểm tra path guard (`apps/ledger/tests/test_keycloak_guard.py`, `infra/passwordless/test_inspect_keycloak.py`).
  - `apps/lab/config/urls.py`: chỉ phục vụ các endpoint xác thực/trang lab cục bộ.
  - 0 kết quả khớp `nmap`, `masscan`, `scapy`, `socket.`, `urllib.request`, `http.client` trên toàn bộ mã nguồn Python công bố.

## Giới hạn
- Rà soát tĩnh mã nguồn tại thời điểm 23/11/2026; không tự quét mạng để chứng minh (vì bản thân việc quét mạng ngoài lab bị cấm).

## Tệp/ảnh bổ sung
- Báo cáo tĩnh đã có sẵn trong repo; không bắt buộc ảnh chụp thêm.
