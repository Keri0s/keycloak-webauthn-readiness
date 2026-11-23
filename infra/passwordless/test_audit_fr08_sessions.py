import base64
import json
import unittest
import zlib
from audit_fr08_sessions import inspect_untrusted_payload


def envelope(value, compressed=False):
    data = json.dumps(value).encode()
    if compressed:
        data = zlib.compress(data)
    return ("." if compressed else "") + base64.urlsafe_b64encode(data).decode().rstrip("=") + ":timestamp:invalid-signature"


class ForensicTests(unittest.TestCase):
    def test_decoding_does_not_claim_valid_signature_or_emit_values(self):
        result = inspect_untrusted_payload(envelope({"_auth_user_id": "synthetic-secret"}))
        self.assertEqual(result["status"], "JSON_DECODED_SIGNATURE_STILL_INVALID")
        self.assertTrue(result["has_auth_fields"])
        self.assertNotIn("synthetic-secret", str(result))

    def test_compressed_private_material_detected(self):
        result = inspect_untrusted_payload(envelope({"key": {"kty": "EC", "d": "synthetic"}}, True))
        self.assertEqual(result["signals"]["private_jwk_objects"], 1)

    def test_decompression_bounded(self):
        with self.assertRaises(ValueError):
            inspect_untrusted_payload(envelope({"large": "x" * 70000}, True))

    def test_non_json_rejected(self):
        with self.assertRaises(ValueError):
            inspect_untrusted_payload("invalid!data:timestamp:signature")


if __name__ == "__main__":
    unittest.main()
