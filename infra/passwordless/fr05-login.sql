-- Read-only, allowlisted event evidence. No raw SID, tokens or session cookies.
\set ON_ERROR_STOP on
\set VERBOSITY terse
\x on
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
WITH selected AS MATERIALIZED (
    SELECT e.id, e.event_time, e.session_id, e.user_id, e.client_id,
           e.details_json, e.details_json_long_value, u.username
    FROM event_entity e JOIN realm r ON r.id=e.realm_id
    JOIN user_entity u ON u.id=e.user_id AND u.realm_id=r.id
    WHERE r.name='webauthn-lab' AND e.client_id='app-lab' AND e.type='LOGIN'
      AND u.username='lab-user-01' AND e.error IS NULL
      AND e.event_time >= extract(epoch FROM now() - interval '30 minutes') * 1000
    ORDER BY e.event_time DESC LIMIT 20
), parsed AS (
    SELECT *, coalesce(nullif(details_json,'')::jsonb,'{}'::jsonb) AS short_data,
              coalesce(nullif(details_json_long_value,'')::jsonb,'{}'::jsonb) AS long_data
    FROM selected
), normalized AS (
    SELECT *, short_data || long_data AS detail FROM parsed
)
SELECT id AS source_event_id,
       to_char(to_timestamp(event_time/1000.0) AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"') AS login_at_utc,
       username, client_id,
       detail->>'credential_type' AS credential_type,
       detail->>'public_key_credential_id' AS credential_id,
       detail->>'web_authn_authenticator_user_verification_checked' AS uv_checked,
       detail->>'custom_required_action' AS required_action,
       CASE WHEN session_id IS NOT NULL AND session_id <> '' THEN
         encode(sha256(convert_to('https://auth.readiness.test:9443/realms/webauthn-lab'
             || E'\n' || client_id || E'\n' || session_id,'UTF8')),'hex') END AS session_ref,
       encode(sha256(convert_to('https://auth.readiness.test:9443/realms/webauthn-lab'
             || E'\n' || user_id,'UTF8')),'hex') AS subject_ref,
       EXISTS (SELECT 1 FROM jsonb_each(short_data) s JOIN jsonb_each(long_data) l USING (key)
               WHERE s.key IN ('credential_type','public_key_credential_id',
                   'web_authn_authenticator_user_verification_checked','custom_required_action')
                 AND s.value IS DISTINCT FROM l.value) AS detail_conflict
FROM normalized ORDER BY event_time DESC;
ROLLBACK;
