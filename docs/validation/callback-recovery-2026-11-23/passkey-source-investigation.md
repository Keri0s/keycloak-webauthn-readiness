# Passkey retry investigation — 2026-11-23

## Scope

User reports the same native Windows Security error in Chrome as in Edge:
initial attempt fails, Try again followed by PIN succeeds. The browser switch
does not by itself isolate the passkey provider.

## Evidence collected directly

- Inspected `apps/lab/config/oidc.py` and `apps/lab/authn/views.py`.
  The application delegates authentication to Keycloak; it does not implement
  the native Windows dialog or its Try again button.
- A fresh HTTPS login from the application reached Keycloak's username form.
  Submitting only the synthetic lab username reached its passkey form (200).
  No real assertion was generated or submitted.
- The served button handler calls `authenticateByWebAuthn(input)` with
  `{ once: true }`. Inputs: identified user, UV required, RP ID
  `auth.readiness.test`, timeout **60 seconds**. Earlier inspection observed
  zero/default timeout; configuration has changed between observations.
- Downloaded the public `webauthnAuthenticate.js` served by Keycloak.
  Raw response SHA256:
  `0889bb492f6a0848f3c38e21ddb9dbf26e6f161d9cabe958767284c2fc5dfd88`.
  Saved text SHA256 (Windows newline conversion):
  `4c2e92100ad4d91dd23576521a1949e701211c3444a7501001b1e363cbec7e44`.
- `doAuthenticate()` constructs publicKey options, then returns
  `navigator.credentials.get()`. The outer async function submits the form
  only after resolution or rejection. It contains no automatic retry loop
  and does not implement the Windows Try again control.
- Source and local investigation harness are under the ignored
  `tmp/passkey-source-review/` directory. No live HTML, challenges, cookies,
  credential IDs or tokens were saved there.

## Executed check

`node tmp/passkey-source-review/check-runtime.mjs` exercised the downloaded
module with synthetic DOM, base64 adapter and mocked native credentials API:

1. Pending native request: exactly one get(), no form submission; UV required,
   RP ID, timeout 60000 ms and credential decoding checked.
2. Native success: one form submission, no second get().
3. Native rejection: one error submission, no automatic retry.

All three checks passed. This does not exercise real Windows Security,
provider-internal retry, other browser scripts or signature verification.
It does not prove the entire browser never creates overlapping requests.

## Separate callback failure

The local sanitized callback log contains an entry timestamped
`2026-11-23 13:47:06,114` with `code=expired_login_state`.
This identifies an expired application transaction on that occasion, not the
cause of the earlier native dialog failure. The 1970 timestamps and early
09:11 entries in the same file originate from the first offline test run;
they must not be counted as real login evidence. Tests now suppress runtime
log writes. The historical 09:03 screenshot is not correlated to a log entry.

## Assessment and remaining evidence

Leading hypothesis: an intermittent failure in the shared native
WebAuthn/provider path, including Microsoft Password Manager. The user's
earlier Windows log explicitly names MicrosoftCtapPluginProvider / Microsoft
Password Manager; its successful response had flags 0x1D, including UV.
No failing response has been captured that proves a missing UV bit.

Microsoft documents that its Password Manager plugin can serve browsers
other than Edge. A firsthand report on Microsoft Q&A describes provider
failures and missing UV on another Windows build. It is a similar report,
not a Microsoft-confirmed diagnosis for this machine or Keycloak version.

- Architecture: https://techcommunity.microsoft.com/blog/Windows-ITPro-blog/windows-11-expands-passkey-manager-support/4467572
- Firsthand report, not confirmed root cause: https://learn.microsoft.com/en-in/answers/questions/5906809/microsoft-edge-based-passkeys-not-always-working-w

Direct Get-WinEvent access was denied by this tool environment. The exact
native first-attempt error therefore remains unavailable. To distinguish
the provider hypothesis from browser/Keycloak interaction, the next decisive
comparison is a second passwordless credential held by a different provider
(device-local Windows storage, phone or security key), with UV still required,
on the same account and flow. Enrollment and PIN require the user's device
interaction; preserve the existing credential. Do not disable the only
usable provider first, delete credentials, lower UV or increase the OIDC TTL
as a purported fix for the native error.

No authentication source or policy was changed in this investigation.
No claim of a repaired native error or new FR acceptance PASS is made.
