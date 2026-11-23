-- Follow-up for the long event column observed in the user's schema output.
-- Outputs aggregates only; never event payloads.
\set ON_ERROR_STOP on
\set VERBOSITY terse
BEGIN READ ONLY;
SET LOCAL statement_timeout = '10s';
SELECT e.type, count(*) AS event_count,
       count(*) FILTER (WHERE nullif(btrim(e.details_json_long_value),'') IS NOT NULL) AS long_value_rows,
       count(*) FILTER (WHERE e.details_json ~* 'PRIVATE KEY|private[_-]?key|privateKeyPkcs8') AS marker_rows,
       count(*) FILTER (WHERE e.details_json_long_value ~* 'PRIVATE KEY|private[_-]?key|privateKeyPkcs8') AS long_marker_rows
FROM event_entity e JOIN realm r ON r.id=e.realm_id
WHERE r.name='webauthn-lab'
  AND e.type IN ('LOGIN','LOGIN_ERROR','UPDATE_CREDENTIAL','CUSTOM_REQUIRED_ACTION')
GROUP BY e.type ORDER BY e.type;
ROLLBACK;
