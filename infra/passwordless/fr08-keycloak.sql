-- Read-only metadata/aggregate inspection, limited to the synthetic lab realm.
-- Never SELECT the raw secret_data, credential_data or key values.
\set ON_ERROR_STOP on
\set VERBOSITY terse
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public' AND table_name IN ('credential', 'event_entity')
ORDER BY table_name, ordinal_position;

SELECT c.type, count(*) AS credential_count,
       count(*) FILTER (WHERE c.secret_data IS NULL OR btrim(c.secret_data) IN ('', '{}', 'null')) AS empty_secret_data_count
FROM credential c JOIN user_entity u ON u.id=c.user_id
JOIN realm r ON r.id=u.realm_id
WHERE r.name='webauthn-lab' AND c.type IN ('webauthn','webauthn-passwordless')
GROUP BY c.type;

-- MATERIALIZED bounds JSON parsing to the selected lab credentials.
-- Non-object data is reported by type, never silently treated as clean.
-- Invalid JSON stops the transaction; do not print the failing raw value.
WITH lab AS MATERIALIZED (
    SELECT c.type, c.credential_data, c.secret_data
    FROM credential c JOIN user_entity u ON u.id=c.user_id
    JOIN realm r ON r.id=u.realm_id
    WHERE r.name='webauthn-lab' AND c.type IN ('webauthn','webauthn-passwordless')
), documents AS (
    SELECT type, 'credential_data' AS source, NULLIF(btrim(credential_data),'')::jsonb AS body FROM lab
    UNION ALL
    SELECT type, 'secret_data', NULLIF(btrim(secret_data),'')::jsonb FROM lab
)
SELECT d.type, d.source, coalesce(jsonb_typeof(d.body),'sql_null_or_empty') AS json_type,
       keys.field_name, count(*) AS occurrence_count
FROM documents d
LEFT JOIN LATERAL jsonb_object_keys(
    CASE WHEN jsonb_typeof(d.body)='object' THEN d.body ELSE '{}'::jsonb END
) AS keys(field_name) ON true
GROUP BY d.type, d.source, jsonb_typeof(d.body), keys.field_name
ORDER BY d.type, d.source, json_type, keys.field_name;

SELECT e.type, count(*) AS event_count,
       count(*) FILTER (WHERE e.details_json ~* 'PRIVATE KEY|private[_-]?key|privateKeyPkcs8') AS marker_rows,
       count(*) FILTER (WHERE nullif(btrim(e.details_json_long_value),'') IS NOT NULL) AS long_value_rows,
       count(*) FILTER (WHERE e.details_json_long_value ~* 'PRIVATE KEY|private[_-]?key|privateKeyPkcs8') AS long_marker_rows
FROM event_entity e JOIN realm r ON r.id=e.realm_id
WHERE r.name='webauthn-lab'
  AND e.type IN ('LOGIN','LOGIN_ERROR','UPDATE_CREDENTIAL','CUSTOM_REQUIRED_ACTION')
GROUP BY e.type ORDER BY e.type;
ROLLBACK;
