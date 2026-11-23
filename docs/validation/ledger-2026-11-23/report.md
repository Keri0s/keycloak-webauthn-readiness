# Báo cáo kiểm chứng sổ bằng chứng live `apps/ledger` (23/11/2026)

Báo cáo này ghi nhận kết quả thực thi trực tiếp trên lab local (`https://auth.readiness.test:9443` và `https://app.readiness.test:9443`) theo [runbook ngày 23/11/2026](runbook.md).

- **Người thực hiện live:** Trần Trung Hiếu (tài khoản quản trị Keycloak `lab-owner` thuộc realm `master`, tài khoản thử `lab-user-01` thuộc realm `webauthn-lab`).
- **Trình duyệt & thiết bị:** Microsoft Edge + Windows Hello PIN trên Windows 11.
- **Công cụ kéo sổ:** `.\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli` (`pull` và `show`).
- **Tệp dữ liệu thu được:**
  - [`evidence/ledger/so_bang_chung.csv`](../../../evidence/ledger/so_bang_chung.csv): 67 dòng, 20.054 byte, SHA-256 `fca424aaf19fd59fc2ad9a759aaac685c103c0687fb5dd9c2d19a58192bae80f`.
  - [`evidence/ledger/pull-log.jsonl`](../../../evidence/ledger/pull-log.jsonl): 5 bản ghi, 3.175 byte, SHA-256 `34ae201fbd352b0a3d71256b43756392c5efaa1b3e2d8f968041d5d9b28b2448`.
- **Ghi chú nguồn vào:** 12 ảnh chụp màn hình người dùng gửi trong hội thoại (nằm ở lịch sử hội thoại, chưa sao chép tệp ảnh vào repo) cùng dữ liệu sổ trực tiếp trên đĩa; tệp `Mục_A.txt` tải lên có kích thước 0 byte nên số liệu Mục A được đối chiếu trực tiếp từ ảnh 1, `pull-log.jsonl` và `so_bang_chung.csv`. Không sao chép query string phiên, độ dài PIN, `code_id`, địa chỉ IP hoặc user UUID từ ảnh vào báo cáo.

---

## 1. Nhật ký các lần kéo (`pull-log.jsonl`)

| Lần | Thời điểm UTC | Cửa sổ `--since` | Fetched | Mapped | Added | Duplicates | Tổng sau pull | Ghi chú bước |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `2026-11-23T13:36:18.716Z` | `2026-11-16` | 65 | 65 | 65 | 0 | 65 | Mục A: kéo sự kiện lịch sử 7 ngày |
| 2 | `2026-11-23T13:39:14.266Z` | `2026-11-23` | 42 | 42 | 0 | 42 | 65 | Baseline trước lượt đăng nhập Mục B |
| 3 | `2026-11-23T13:42:05.983Z` | `2026-11-23` | 43 | 43 | 1 | 42 | 66 | Mục B: sau đăng nhập `20:40:42+07:00` |
| 4 | `2026-11-23T13:45:29.578Z` | `2026-11-23` | 43 | 43 | 0 | 43 | 66 | Mục B: kéo lặp kiểm tra chống trùng |
| 5 | `2026-11-23T13:49:01.136Z` | `2026-11-23` | 44 | 44 | 1 | 43 | 67 | Mục C: sau ca hủy `20:47:34+07:00` |

---

## 2. Mục A — Kéo sự kiện lịch sử 22–23/11 trước khi hết hạn 7 ngày

- **Expected:** Kéo đủ sự kiện đăng ký và đăng nhập/hủy hiện có trong cửa sổ 7 ngày trên `webauthn-lab` (`client=app-lab`) về `so_bang_chung.csv`.
- **Observed:** Tổng 65 dòng ban đầu (tăng lên **67 dòng** sau Mục B và Mục C), trải từ `2026-11-16T14:17:13.881Z` đến `2026-11-23T13:47:34.554Z`. Phân loại toàn bộ 67 dòng cuối cùng:
  - **2 dòng đăng ký (`UPDATE_CREDENTIAL`, `operation=registration`, `outcome=success`, `credential_type=webauthn-passwordless`, `registration_context=yes`):**
    1. `52a3a562-b588-4713-8352-bedadb8929ff` (`2026-11-22T12:47:14.258Z`, `lab-user-01`, `credential_id=dndRW6XS6qIJg61vLgTUVw`, nhãn `Passkey (Default Label)`).
    2. `165052bf-adf9-4cac-b04f-f73fd25a480e` (`2026-11-23T02:47:00.875Z`, `lab-user-01`, `credential_id=gGCUOjoWoGQwWgLe3SMDow`, nhãn `Edge-Passkey`).
  - **43 dòng `LOGIN` (`operation=authentication`, `outcome=success`):**
    - 35 dòng `webauthn-passwordless` (trong đó **2 dòng** có `registration_context=yes` đi kèm giao dịch đăng ký, **33 dòng** có `registration_context=no` là đăng nhập độc lập; gồm 19 dòng `dndRW6XS6qIJg61vLgTUVw` và 16 dòng `gGCUOjoWoGQwWgLe3SMDow` nếu tính cả lượt đăng ký 09:47).
    - 7 dòng `webauthn` lịch sử từ `16/11` đến `19/11/2026` (`credential_id=RB1PYh3LHn79OqdBGT1tABCzRBfn7XmqOjIuJjugV0w`, thuộc luồng 2FA cũ trước khi chuyển sang passwordless).
    - 1 dòng `LOGIN` (`64584066-4729-4b64-8e00-6ea64cd1d47a`, `2026-11-23T02:47:50.625Z`, `lab-user-01`, `registration_context=no`) có `credential_type` và `credential_id` rỗng (sự kiện cũ không ghi chi tiết WebAuthn).
  - **22 dòng `LOGIN_ERROR` (`operation=authentication`, `outcome=failure`):** 14 dòng `webauthn-passwordless` và 8 dòng `credential_type` rỗng; tất cả 22 dòng đều có `credential_id` rỗng (`""`).

---

## 3. Mục B (FR-06 / IF-04 / DR-03) — Đăng nhập passkey mới sinh đúng 1 dòng và không trùng khi kéo lại

| Bước | Expected | Observed | Kết luận |
| --- | --- | --- | --- |
| 1. Baseline pull | Ghi nhận tổng trước khi thử | `fetched=42, added=0, duplicates=42, total=65` | Đạt |
| 2. Đăng nhập mới `lab-user-01` | Giao diện Passkey login → Windows Security PIN → `/private/` trả `X-Lab-*` | Ảnh 2–4 cho thấy đăng nhập `lab-user-01` qua `auth.readiness.test` lúc `20:40` (UTC+7); header `/private/` có `X-Lab-Binding-Created: 2026-11-23T13:40:42.834758+00:00` | Đạt có giới hạn ảnh |
| 3. Pull sau đăng nhập | `added=1` | `fetched=43, mapped=43, added=1, duplicates=42, total=66` (lúc `13:42:05.983Z`) | Đạt |
| 4. Lọc & đối chiếu `show --since 2026-11-23T13:40:42` | Đúng 1 dòng `LOGIN` `success`, cùng `credential_id` và `session_ref`/`subject_ref` khớp `/private/` | Dòng `5efcdcf3-8031-49c6-be2a-8ccd8f04e425` (`2026-11-23T13:40:42.491Z` / `20:40:42+07:00`), `lab_account=lab-user-01`, `operation=authentication`, `outcome=success`, `credential_type=webauthn-passwordless`, `credential_id=gGCUOjoWoGQwWgLe3SMDow`, `uv_checked=true`, `registration_context=no` | Đạt |
| 5. Đối chiếu `session_ref` & `subject_ref` | Khớp 100% giữa sổ CSV và header ứng dụng | `session_ref = 6f1ca140848faa67bec0cf8e8647712fd9ddc1537dcc25f617f8418c46181637`, `subject_ref = 2401d8295d0a54f76cfed1b892ecc4e94e112cbbeffdd7cd50a7b69862d2a8e3` khớp hoàn toàn; `SessionBinding` tạo sau `LOGIN` khoảng `344 ms` | Đạt |
| 6. Kéo lặp lại ngay sau đó | `added=0`, không trùng dòng | `fetched=43, mapped=43, added=0, duplicates=43, total=66` (lúc `13:45:29.578Z`) | Đạt |

**Giới hạn của Mục B:** Ảnh 4 trong bộ ảnh người dùng gửi chỉ chụp khung Response Headers (`X-Lab-Binding-Created`, `X-Lab-Session-Ref`, `X-Lab-Subject-Ref`) của `/private/`, chưa chụp lại giao diện HTML trang `/private/` ở lượt `20:40` (giao diện `/private/` HTTP 200 chào `lab-user-01` đã có ở ca đối chiếu `18:59:55` trước đó trong [fr05-observed-185955.md](../requirements-review-2026-11-23/fr05-observed-185955.md)).

---

## 4. Mục C (FR-07 / NFR-04) — Ca hủy sinh dòng thất bại sạch dữ liệu nhạy cảm và `/private/` bị từ chối

| Bước | Expected | Observed | Kết luận |
| --- | --- | --- | --- |
| 1. Hủy hộp thoại passkey | Keycloak ghi `LOGIN_ERROR`, không tạo phiên hợp lệ | Ảnh 8 (Keycloak Events) hiển thị `LOGIN_ERROR` lúc `November 23, 2026 at 8:47 PM` (`No user details`, `client=app-lab`, `error=not_allowed`, `web_authn_authentication_error=webauthn-error-api-not-allowed`) sau sự kiện `LOGOUT` lúc `8:46 PM` | Đạt |
| 2. Pull về sổ CSV | `added=1` | `fetched=44, mapped=44, added=1, duplicates=43, total=67` (lúc `13:49:01.136Z`) | Đạt |
| 3. Lọc `show --outcome failure --since 2026-11-23T20:47:34+07:00` | Đúng 1 dòng thất bại, không lộ IP/`code_id`/mô tả dài/private key | Dòng `0bf7d697-a7c6-4d95-9e22-f60c2402dd31` (`2026-11-23T13:47:34.554Z` / `20:47:34+07:00`), `lab_account=unknown`, `operation=authentication`, `outcome=failure`, `credential_type=webauthn-passwordless`, `credential_id` rỗng, `error_code=not_allowed`, `webauthn_error=webauthn-error-api-not-allowed`; toàn bộ IP, `code_id`, `redirect_uri` và chuỗi mô tả dài đều bị loại bỏ | Đạt |
| 4. Mở `/private/` sau khi hủy | Bị từ chối truy cập (`403`) | Ảnh 11 hiển thị `https://app.readiness.test:9443/private/` trả `403 Forbidden` (đồng hồ `8:52 CH 23/11/2026`) | Đạt |

---

## 5. Mở chi tiết dòng bằng chứng (`show --id`) & rà soát FR-08 bổ sung

- Đã chạy `.\apps\lab\.venv\Scripts\python.exe -m apps.ledger.cli show --id 5efcdcf3-8031-49c6-be2a-8ccd8f04e425` và `--id 0bf7d697-a7c6-4d95-9e22-f60c2402dd31`: hiển thị đầy đủ 18 trường allowlist + `occurred_at_vn`, không có trường ngoài danh sách cho phép (**NFR-03 / IF-04 / NFR-04**).
- Đã chạy lại `.\apps\lab\.venv\Scripts\python.exe .\infra\passwordless\audit_fr08_exports.py` sau khi hoàn tất Mục A–D: `evidence/ledger/so_bang_chung.csv` và `evidence/ledger/pull-log.jsonl` đều có `private_named_fields=0`, `private_jwk_objects=0`, `text_markers=0` (`flagged_paths = []`). Xem chi tiết tại [export-review.md](../fr08-2026-11-23/export-review.md) và [nfr04-review.md](nfr04-review.md).

## Giới hạn cần giữ

- Lỗi Windows Security xuất hiện phải bấm *Try again* tiếp tục giữ trạng thái **DEFERRED_OPEN**.
- Kết quả trên chưa thay thế phiếu chấm lab thực (người đánh giá tự điền cột `diem` tại `evidence/lab-scorecard/`) và chưa chứng minh các kịch bản session còn lại trong bộ 19 ca (`SESSION_MAPPING_A`).
