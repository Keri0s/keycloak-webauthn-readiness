# Passwordless enrollment — bằng chứng giao diện ngày 22/11/2026

## Nguồn và phạm vi

Nguồn: hai ảnh chụp màn hình thực tế do người dùng gửi trong hội thoại, kèm xác nhận “đã thành công”. Trợ lý quan sát ảnh, không trực tiếp thực hiện thao tác đăng ký. Thời gian dưới đây lấy từ đồng hồ Windows trong ảnh (UTC+7), không phải timestamp sự kiện Keycloak. Bản ghi này chưa chứa bản sao ảnh trong repository; ảnh gốc vẫn ở hội thoại. Không tạo ảnh mô phỏng thay thế.

Môi trường quan sát: Microsoft Edge trên Windows; realm `webauthn-lab`, client `app-lab`, tài khoản lab `lab-user-01`; IdP `https://auth.readiness.test:9443`, ứng dụng `https://app.readiness.test:9443`. Phiên bản trình duyệt/OS không được xác định từ hai ảnh này.

## Danh mục ảnh

| Mã | Thời gian hiển thị | Quan sát trực tiếp | Ý nghĩa |
| --- | --- | --- | --- |
| PL-REG-01 | 22/11/2026 19:46 UTC+7 | Trang Keycloak “Passkey Registration”, required action `webauthn-register-passwordless`; hộp thoại “Create a passkey” cho `lab-user-01`, RP `auth.readiness.test`; thông báo sẽ lưu vào Microsoft Password Manager và truy cập trên các thiết bị | Đã đến giao diện tạo credential passwordless; riêng ảnh này chưa chứng minh tạo xong |
| PL-REG-02 | 22/11/2026 19:47 UTC+7 | Edge thông báo “Passkey saved”, liên kết Microsoft Password Manager; ứng dụng đang ở `/private/` và chào `lab-user-01` | Bằng chứng giao diện hỗ trợ đăng ký thành công và trở lại ứng dụng với đúng tên tài khoản lab |

Không sao chép query string của URL required-action vào báo cáo vì chứa dữ liệu phiên. Khi đưa ảnh vào báo cáo công khai/GitHub, che query string và cắt các tab/bookmark cá nhân; giữ phần giao diện cần chứng minh. Chưa thực hiện chỉnh sửa hay sao chép ảnh trong lượt ghi nhận này.

## Đối chiếu SRS

Nguồn yêu cầu: `docs/source/srs-extracted.md`, mục FR-04 đến FR-08. Không sửa yêu cầu gốc và không cộng ảnh này vào bộ 19 ca SESSION_MAPPING_A.

| Yêu cầu | Kết quả ghi nhận | Giới hạn / bằng chứng còn cần |
| --- | --- | --- |
| FR-04 — đăng ký passkey trên realm lab | UI_OBSERVED: có hai ảnh hỗ trợ demo đăng ký thành công | Đối chiếu credential mới của tài khoản trong Keycloak (loại passwordless, nhãn, thời điểm/mã credential) để liên kết đầy đủ; chưa đánh dấu nghiệm thu toàn bộ |
| FR-05 — cùng tài khoản dùng passkey đó đăng nhập ứng dụng | Chưa chứng minh | `/private/` ngay sau enrollment không phải một lần đăng nhập mới bằng credential vừa tạo; cần kết thúc phiên, đăng nhập lại qua flow passwordless và đối chiếu credential |
| FR-06 — dòng thành công có thời điểm/kết quả/credential ID | Chưa chứng minh | Đồng hồ ảnh và popup không thay thế sổ bằng chứng; cần dòng sự kiện thực tế cho đăng ký và đăng nhập |
| FR-07 — hủy đăng nhập có dòng thất bại | Chưa kiểm thử trong lần này | Cần lần hủy riêng và dòng thất bại tương ứng |
| FR-08 — DB/log không lưu private key passkey | Chưa kiểm tra trong lần này | Cần rà schema/storage/log; ảnh UI không chứng minh thuộc tính này |

## Giới hạn về bảo mật và luồng

- Provider thể hiện trong ảnh là **Microsoft Password Manager**. Không được mô tả bằng chứng này thành “khóa chỉ nằm trong TPM” hoặc “Windows Hello device-bound”. Ảnh có thông báo khả năng dùng qua các thiết bị, nhưng không chứng minh đã đồng bộ thực tế.
- Không thấy bước PIN/sinh trắc học hoặc authenticator data trong ảnh: chưa chứng minh UV đã được thực thi. Cấu hình UV Required và kiểm thử từ chối khi thiếu UV cần bằng chứng riêng.
- Lần kiểm kê runtime trước đó cho thấy ứng dụng dùng `browser-password-webauthn`; ảnh flow mới trước đó là `Not in use`. Hai ảnh enrollment này không chứng minh đã bind `browser-passkey-uv` hay loại bỏ password fallback.
- Đây là enrollment bổ sung cho tài khoản lab hiện có; chưa chứng minh quy trình xác minh danh tính/cấp tài khoản ban đầu hay recovery.

## Việc tiếp theo

1. Xác nhận credential mới trong Keycloak, giữ credential cũ khi chưa hoàn tất thử nghiệm.
2. Kiểm tra lại policy và binding của client thử nghiệm trước khi kiểm thử đăng nhập mới bằng passkey.
3. Thu bằng chứng FR-05 và FR-06 liên kết cùng credential; kiểm thử UV và hủy riêng.

Trạng thái: **ENROLLMENT_UI_OBSERVED — chưa nghiệm thu trọn luồng passwordless**.

## Bổ sung PL-REG-03 — xác nhận credential trong Admin Console

Nguồn: ảnh tab Users → lab-user-01 → Credentials do người dùng cung cấp tiếp theo. Ảnh cho thấy tài khoản Enabled và ba credential:

| Type hiển thị | User label | Created at hiển thị |
| --- | --- | --- |
| Password | My password | 11/15/2026, 10:01:14 AM |
| Webauthn | Lab-user01-passkey | 11/15/2026, 10:13:58 AM |
| Webauthn-passwordless | Passkey (Default Label) | 11/22/2026, 7:47:14 PM |

Đã xác nhận qua UI credential passwordless tồn tại cho đúng tài khoản; thời điểm hiển thị phù hợp hai ảnh enrollment trước. Múi giờ không được ghi trực tiếp trong bảng; không tự quy đổi timestamp này sang UTC. Ảnh được cắt, không hiện tên realm; realm được liên hệ từ chuỗi thao tác trước đó, chưa xác minh độc lập bằng API.

FR-04: bộ ảnh đã hỗ trợ cả thao tác đăng ký và credential được lưu trong Keycloak. Chưa đọc Show data, chưa lấy credential ID, chưa đối chiếu event. FR-05/FR-06 và kiểm chứng UV vẫn chưa hoàn tất. Password và Webauthn cũ còn tồn tại không tự chứng minh một đường fallback đang được bật; điều đó phụ thuộc flow/binding và các đường xác thực khác.

Bước tiếp theo: đối chiếu WebAuthn Passwordless Policy (RP ID, UV, Discoverable Credential), sau đó chuẩn bị binding client thử nghiệm và lần đăng nhập mới. Không xóa credential cũ trong bước xác nhận này. Ảnh PL-REG-03 hiện ở hội thoại, chưa được sao chép vào repository.

## Bổ sung PL-POL-01 — ảnh policy lúc 19:56 ngày 22/11/2026

Ảnh người dùng gửi sau hướng dẫn mở WebAuthn Passwordless Policy hiển thị realm webauthn-lab trong URL và các giá trị: RP entity Readiness Lab; ES256, RS256; RP ID auth.readiness.test; Attestation None; Authenticator Attachment Not specified; Discoverable credential Required; Require discoverable credential Not specified; User verification requirement Required; Timeout 0 seconds.

Giới hạn: ảnh đang cuộn xuống nên không thấy tiêu đề tab policy và không thấy thông báo Save; liên hệ với policy passwordless dựa trên chuỗi thao tác của người dùng. Đây là quan sát cấu hình UI, chưa phải xuất lại runtime hay kiểm thử thực thi UV. Không diễn giải Timeout 0 thành challenge không hết hạn. Hai trường Discoverable credential và Require discoverable credential được ghi tách biệt, không suy giá trị trường mới từ trường cũ.

Bước tiếp theo: xem cấu hình Browser Flow override của client app-lab để chuẩn bị thử nghiệm có phạm vi; chưa có bằng chứng binding mới hoặc lần đăng nhập passwordless. Không thay Browser Flow toàn realm trong bước này.

## PL-LOGIN-01 / PL-ERR-01 — đăng nhập và lỗi cần điều tra

Ảnh người dùng lúc khoảng 19:59–20:00 ngày 22/11 (đồng hồ UI, UTC+7 theo bối cảnh) cho thấy Username Form, Passkey login rồi /private/ chào lab-user-01 trong Edge InPrivate. Chưa có event/credential ID để liên kết chính xác credential dùng trong lần này.

Người dùng giải thích lần thử đầu hiện Windows Security: Something went wrong / There was a problem signing in with your passkey; Try again mới hiện hộp PIN. Ảnh tiếp theo lúc 20:04 cho thấy cùng lỗi trong Edge cửa sổ thường. Vì vậy InPrivate không phải điều kiện duy nhất gây lỗi. Không gọi hiện tượng này là xác thực hai yếu tố hay hai lần UV bình thường. Chưa xác định nguyên nhân; chưa kết luận Keycloak từ chối assertion, PIN sai, khóa hỏng hoặc lỗi TPM. Thành công sau retry và thành công lần đầu phải ghi riêng; kết quả retry của lần 20:04 chưa được xác nhận.

Trạng thái: LOGIN_UI_OBSERVED_WITH_UNRESOLVED_RETRY_ERROR. Chưa nâng FR-05 thành nghiệm thu hoàn chỉnh. Cần đối chiếu Keycloak event và thông tin phiên bản Edge/Windows; giữ policy UV Required và credential hiện có trong quá trình chẩn đoán. Ảnh gốc ở hội thoại; không ghi query URL phiên hoặc nội dung PIN vào báo cáo.

## PL-EVT-01 / PL-EVT-02 — ảnh event do người dùng cung cấp

Ngày hiển thị 22/11/2026; giờ giao diện, chưa xuất timestamp API.

- 20:03 LOGIN, client app-lab, username lab-user-01, credential_type webauthn-passwordless; có public_key_credential_id. Dòng web_authn_authenticator_user_verification_checked bị chồng chữ giữa tên và giá trị trong ảnh; cần bản chữ/export để xác nhận chính xác giá trị trước khi ghi UV=true. Không chép credential ID từ ảnh khi chưa đối chiếu chính xác.
- Danh sách có CODE_TO_TOKEN cùng phút 20:03; đây là bằng chứng thêm về OIDC, chưa tự tương quan từng giao dịch bằng ảnh danh sách.
- 20:05 LOGIN_ERROR, No user details, client app-lab, credential_type webauthn-passwordless, error not_allowed, web_authn_authentication_error webauthn-error-api-not-allowed; chi tiết NotAllowedError: The operation either timed out or was not allowed.
- 19:47 có UPDATE_CREDENTIAL và CUSTOM_REQUIRED_ACTION trong danh sách; chưa mở chi tiết để liên kết credential đăng ký với credential đăng nhập.

Kết luận cập nhật: Keycloak đã có LOGIN thành công bằng loại credential passwordless; lỗi không xảy ra ở tất cả các lần đăng nhập. Chưa liên kết event lỗi 20:05 với đúng thời điểm lỗi native ban đầu hoặc thao tác Cancel/timeout sau đó. NotAllowedError không tự xác định nguyên nhân gốc, không tự chứng minh sai PIN/UV/RP ID, và không đủ để đánh dấu ca hủy chủ động FR-07. FR-06 có bằng chứng một login success có trường credential ID, nhưng chưa chứng minh đầy đủ mọi đăng ký/đăng nhập đều có dòng và cùng credential. Không lưu code_id hoặc dữ liệu phiên trong bản ghi này.

Chẩn đoán tiếp: xác nhận người dùng có bấm Cancel ở lần 20:05 không; thu phiên bản Edge/Windows để điều tra lỗi provider/browser; giữ flow, UV và credential hiện có. Nguồn chuẩn cho ngữ nghĩa lỗi: https://www.w3.org/TR/webauthn-2/ .

## PL-ENV-01 — phiên bản và xác nhận thao tác Cancel

Người dùng xác nhận có bấm Cancel trong lần 20:05. Vì vậy LOGIN_ERROR/NotAllowedError của lần đó được ghi là lỗi sau thao tác hủy theo lời người thực hiện; không dùng event này để quy nguyên nhân cho lỗi Windows xuất hiện trước Cancel. Đây là bằng chứng hỗ trợ ca hủy, chưa tự hoàn tất FR-07 vì chưa đối chiếu toàn bộ sổ bằng chứng.

Ảnh About Microsoft Edge: 158.0.4370.33, Official build, 64-bit, giao diện báo up to date. Ảnh winver: Windows 11 Home Single Language, Version 26H2, OS Build 26300.9974. Không sao chép thông tin người được cấp phép/email trong ảnh.

Tra cứu tài liệu Microsoft ở lượt này chưa xác định được bản công bố lỗi khớp chính xác cả phiên bản và hiện tượng. Không kết luận đây là known bug hoặc yêu cầu downgrade/reset PIN/xóa credential. Tiếp theo phân biệt lời gọi WebAuthn tự động khi tải trang với thao tác bấm Sign in with Passkey, giữ nguyên provider/flow/policy để kiểm tra từng yếu tố.

## PL-LOGIN-02 — thành công không cần retry, khoảng 20:15–20:16

Nguồn: ba ảnh và lời người dùng ngày 22/11/2026. Edge cửa sổ thường hiển thị Windows Security chọn passkey lab-user-01 cho auth.readiness.test, sau đó hộp nhập PIN, cuối cùng /private/ chào lab-user-01. Người dùng xác nhận lần này không hiện lỗi. Không sao chép PIN, độ dài PIN hoặc query URL phiên. Ảnh gốc hiện ở hội thoại.

Bổ sung lời người dùng trước lần thử này: hộp lỗi chỉ xuất hiện sau khi bấm Sign in with Passkey, không tự bật khi tải trang.

Kết quả: một lần đăng nhập có tương tác passkey/PIN và vào ứng dụng, không cần Try again theo người thực hiện. Lỗi trước đó là không liên tục trong các lần quan sát; chưa có bản sửa được thực hiện hoặc nguyên nhân gốc xác định. Giả thuyết session do người dùng đề xuất chưa được kiểm chứng. Cần phân biệt phiên xác thực Keycloak/challenge với session Django sau callback; chưa có bằng chứng quy lỗi native Windows cho session mapping Django. Event 20:05 có thao tác Cancel nên không dùng để suy ra phiên hết hạn.

FR-05: bổ sung bằng chứng UI thành công; còn đối chiếu event LOGIN 20:16 và public_key_credential_id với credential đăng ký để hoàn tất liên kết. Lỗi retry tiếp tục OPEN, không đóng chỉ vì một lần thành công. Phép thử tiếp theo nếu cần tái hiện: ba lượt đăng xuất hoàn tất rồi mở mới /auth/login/, cùng profile/credential/policy, không tái dùng URL login-actions cũ; ghi giờ và số lần retry. Không tự suy nguyên nhân nếu cả ba lượt thành công.

## PL-NET-01 — đối chiếu Network trước/trong lỗi và sau đăng nhập

Nguồn: ba ảnh Edge InPrivate do người dùng gửi, đồng hồ 20:22–20:23 ngày 22/11/2026.

- Trước khi gọi passkey: Network All, ô filter trống, 14 requests; document authenticate trả 200 và các tài nguyên trang đã tải.
- Khi Windows Security hiện Something went wrong: vẫn 14 requests, không thấy request authenticate mới trong danh sách; không có HTTP lỗi mới hiển thị.
- Ảnh cuối: authenticate 302 → callback 302 → private 200, trang chào lab-user-01. Keep log không bật nên danh sách sau navigation không phải toàn bộ lịch sử. Không tự khẳng định thao tác trung gian từ ảnh; cần lời người dùng nếu muốn ghi chính xác đã bấm Try again trong lần này.

Suy luận có giới hạn: lỗi native xuất hiện trước khi quan sát thấy trang gửi kết quả WebAuthn mới về Keycloak; chưa có căn cứ coi lỗi là phản hồi từ Django/session mapping hoặc Keycloak từ chối assertion trong bước đó. Điều này không loại trừ tham số WebAuthn do server tạo ảnh hưởng đến hành vi client. Chưa xác định nguyên nhân giữa Edge, Windows và provider; chưa coi URL/query là nguyên nhân. DevTools của trang không quan sát đầy đủ hoạt động mạng bên trong provider.

Bằng chứng bổ sung: luồng HTTP về ứng dụng hoàn tất thành công trong ảnh cuối. Lỗi native vẫn OPEN. Bước chẩn đoán tiếp: xác định provider được chọn ở lần gọi đầu và sau retry (qua Choose a different passkey nếu giao diện cho phép), giữ nguyên credential/policy. Không reset PIN, xóa passkey hay hạ UV để thử sửa.

## PL-RETRY-02 — xác nhận chọn thủ công vẫn lỗi

Ngày ghi nhận 23/11/2026, theo lời người dùng (không xác định lại thời điểm thao tác): chọn dòng lab-user-01 trong danh sách ba lựa chọn ngay lần đầu vẫn lỗi. Chỉ sau Try again, chọn lại dòng lab-user-01 rồi nhập PIN mới vào được ứng dụng. Không coi lựa chọn thủ công là cách sửa; giả thuyết chỉ chọn nhầm dòng mặc định chưa được hỗ trợ. Tên tài khoản giống nhau chưa chứng minh provider/credential ID giống nhau ở hai lần.

Lỗi vẫn OPEN; workaround quan sát được là retry. Chưa xác định nguyên nhân session, URL, Edge, Windows hoặc provider. Trợ lý thử liệt kê metadata các kênh Windows Event Log WebAuth/HelloForBusiness để chuẩn bị chẩn đoán nhưng Get-WinEvent trả Attempted to perform an unauthorized operation; không đọc được event và không thay quyền/cấu hình logging.

## PL-WIN-01 — provider và cờ xác thực của giao dịch thành công

Ảnh Windows WebAuthN/Operational do người dùng gửi: TimeCreated 11/23/2026 8:16:50 AM, các event cùng TransactionId (không chép lại định danh giao dịch): 2102 Ctap WebAuthN completed (Success); 2104 Ctap device info, ProviderName MicrosoftCtapPluginProvider, Product Microsoft Password Manager, AAGuid toàn zero, U2fProtocol false; 1104 Cbor decode GetAssertion response, Flags 0x1D, SignCount 0x0; 2106 authenticationResponseJSON; 1004 WebAuthN Ctap GetAssertion completed (Success).

Theo bitmap WebAuthn, 0x1D & 0x01 != 0 và 0x1D & 0x04 != 0: response được log có UP=1 và UV=1. Đây là bằng chứng cờ trong response của giao dịch này, chưa phải kiểm thử âm chứng minh server từ chối UV=0. Nguồn: https://www.w3.org/TR/webauthn-2/#sctn-authenticator-data . Không suy AAGUID zero hoặc platform thành khóa device-bound/TPM-only.

Các ảnh này xác nhận provider cho giao dịch thành công; chưa có event lỗi của lần gọi đầu, chưa xác định provider lần thất bại. Không lưu raw response, signature, clientDataJSON hoặc userHandle vào báo cáo. Cần bảng metadata các event lân cận trước 08:16:50 để tìm lần lỗi thay vì yêu cầu toàn bộ Message chứa payload.

Bổ sung lời người dùng: sau restart lần đăng nhập đầu không lỗi, đăng xuất và đăng nhập lại ngay thì lỗi. Đây là quan sát do người dùng báo, chưa có phép thử kiểm soát xác định nguyên nhân trạng thái/thời gian. Lỗi retry vẫn OPEN.

## PL-WAIT-01 — chờ sau logout vẫn lỗi

Ngày 23/11/2026: người dùng báo vẫn lỗi sau hướng dẫn chờ 60 giây từ khi đăng xuất rồi mở mới /auth/login/. Không coi chờ 60 giây là workaround. Chưa xác định nguyên nhân. Dừng lặp lại thử nghiệm cùng provider không bổ sung dữ liệu; bước đối chứng tiếp nên tách provider/credential trong phạm vi tài khoản lab, giữ UV Required và credential cũ, hoặc kiểm tra mã JS runtime trước khi sửa.
