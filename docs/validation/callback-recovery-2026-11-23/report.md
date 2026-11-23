# Callback recovery and passkey investigation — 2026-11-23

## Scope and observations

Local Readiness Lab only, realm `webauthn-lab`, client `app-lab`.
The user reports Windows Security fails on the first attempt after logout,
then succeeds after Try again and PIN. A later breakpoint experiment ends
at the application callback with a generic rejection message.
These are two observations; a shared root cause has not been established.

Read-only inspection plus an unauthenticated login attempt for the synthetic
`lab-user-01` account reached the live passkey page. No assertion was submitted.
The page uses `webauthnAuthenticate.js`, one button click handler calling
`authenticateByWebAuthn`, `userVerification: required`,
`rpId: auth.readiness.test`, `isUserIdentified: true`, `createTimeout: 0`.
This is static page inspection, not proof that the browser never invokes twice.
No Windows PIN, credential, token or raw challenge was collected.

HTTPS certificate and discovery issuer validation passed. Live application
`/` returned 200, `/auth/login/` redirected to Keycloak with 302, and an invalid
callback returned 400. The existing callback source has a 300-second state TTL.
The old callback message groups missing/expired state, token exchange and
token validation errors together. No retained log identifies the cause of
the user's 09:03 rejection; expiration is possible, not confirmed.

## Implemented changes

- Distinguish an expired login transaction from malformed transaction data.
- Keep the same expiry limit and all state, nonce, PKCE and token checks.
- On rejection, offer a fixed link to `/auth/login/` for a new transaction.
  Do not retry the authorization code automatically or grant access.
- Store bounded callback diagnostics in an ignored rotating local log:
  time, random support reference, allowlisted reason and allowlisted claim name.
  Do not store exception descriptions, query parameters, tokens or credentials.
- Return no-store and no-referrer on the callback recovery response.

## Verification

Command from `apps/lab`:

```powershell
.\.venv\Scripts\python.exe manage.py test authn.test_oidc_recovery --verbosity 2
```

Nine offline tests passed: expired state with recovery link, missing state,
nonce/PKCE required, one-use state/replay, exchange failure with redaction,
duplicate callback parameters, successful binding/redirect, log allowlist,
and excessive future expiry rejection. Django system checks passed.
Provider/token success is mocked; these are not live passkey acceptance tests.

## Deployment and remaining limitation

A live probe after editing still received the old callback response. The
running server has not loaded these changes. This tool environment could
reach the HTTPS endpoints but could not access the host process through CIM
or the Docker named pipe (permission denied), and has no interactive Windows
Security control. No process was killed, and no duplicate server was launched.
The existing Django terminal must be restarted to load the code.

The Windows Security error remains unresolved. No passkey was deleted, no
provider was switched and no Keycloak policy was weakened. A successful retry
does not prove the first failure was a session or URL problem. No FR acceptance
status or the existing 19-case session matrix was promoted to PASS.
