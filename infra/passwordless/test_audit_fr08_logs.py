import unittest
from audit_fr08_logs import summarize


class LogSummaryTests(unittest.TestCase):
    def test_timestamped_private_jwk_returns_counts_only(self):
        result = summarize('2026-11-23T01:00:00Z {"kty":"EC","d":"synthetic-secret"}')
        self.assertEqual(result["private_jwk_objects"], 1)
        self.assertNotIn("synthetic-secret", str(result))

    def test_plain_marker_and_public_key(self):
        result = summarize('2026-11-23T01:00:00Z -----BEGIN PRIVATE KEY-----\n'
                           '2026-11-23T01:00:01Z {"credentialPublicKey":"synthetic"}')
        self.assertEqual(result["text_markers"], 1)
        self.assertEqual(result["private_named_fields"], 0)

    def test_empty_is_not_positive_evidence(self):
        self.assertEqual(summarize("")["lines"], 0)


if __name__ == "__main__":
    unittest.main()
