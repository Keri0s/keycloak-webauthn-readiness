"""Synthetic controls for the audit detector; no real credentials."""
import unittest
from audit_fr08 import signals


class SignalsTests(unittest.TestCase):
    def test_public_credential_is_not_private(self):
        self.assertEqual(sum(signals({"credentialPublicKey": "synthetic",
                                      "credentialId": "synthetic",
                                      "kty": "EC", "x": "synthetic"}).values()), 0)

    def test_nested_private_jwk(self):
        result = signals({"nested": [{"kty": "EC", "d": "synthetic"}]})
        self.assertEqual(result["private_jwk_objects"], 1)
        self.assertNotIn("synthetic", str(result))

    def test_private_named_property(self):
        self.assertEqual(signals({"privateKeyPkcs8": "synthetic"})["private_named_fields"], 1)

    def test_log_markers(self):
        self.assertEqual(signals('-----BEGIN PRIVATE KEY-----')["text_markers"], 1)
        self.assertEqual(signals('{"private_key": "synthetic"}')["text_markers"], 1)

    def test_single_letter_d_is_not_enough(self):
        self.assertEqual(signals({"d": 1})["private_jwk_objects"], 0)


if __name__ == "__main__":
    unittest.main()
