import random
import unittest
from decimal import Decimal, getcontext, localcontext

from MathEncode import ALPHABET, build_numeric_code, decode_secret, encode_secret


class CodecTests(unittest.TestCase):
    def test_roundtrip_and_decimal_serialization(self):
        generator = random.Random(7)
        messages = ["a", "i", "A", "?", " ", "abc", "Hello how are you I am fine?", "a" * 49]
        messages += ["".join(generator.choices(ALPHABET, k=size)) for size in (1, 5, 20, 49)]
        for message in messages:
            with self.subTest(message=message):
                _, metadata, root = encode_secret(message)
                self.assertEqual(decode_secret(Decimal(str(root)), Decimal(str(metadata))), message)

    def test_all_supported_characters(self):
        for character in ALPHABET:
            _, metadata, root = encode_secret(character)
            self.assertEqual(decode_secret(root, metadata), character)

    def test_input_rejection(self):
        for message in ("", "a" * 50, "Hello!", "Grüße", "\0"):
            with self.subTest(message=message), self.assertRaises(ValueError):
                build_numeric_code(message)

    def test_rounded_preview_is_not_the_transport(self):
        preview, metadata, _ = encode_secret("Hello how are you I am fine?")
        with self.assertRaises(ValueError):
            decode_secret(preview, metadata)

    def test_context_is_local(self):
        with localcontext() as context:
            context.prec = 6
            _, metadata, root = encode_secret("abc")
            self.assertEqual(decode_secret(root, metadata), "abc")
            self.assertEqual(getcontext().prec, 6)

    def test_invalid_metadata_and_thresholds(self):
        for metadata in ("NaN", "Infinity", "-1", "101", "103", "102.5", "409799"):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                decode_secret(Decimal(2), Decimal(metadata))
        for threshold in ("NaN", "Infinity", "0", "1", "1.000000000001"):
            with self.subTest(threshold=threshold), self.assertRaises(ValueError):
                encode_secret("abc", Decimal(threshold))
        for root in ("NaN", "Infinity", "-1", "0", "1E10000"):
            with self.subTest(root=root), self.assertRaises(ValueError):
                decode_secret(Decimal(root), Decimal(302))

    def test_custom_threshold(self):
        for threshold in (Decimal(2), Decimal(100), Decimal("1E30")):
            _, metadata, root = encode_secret("abc", threshold)
            self.assertLess(root, threshold)
            self.assertEqual(decode_secret(root, metadata), "abc")


if __name__ == "__main__":
    unittest.main()
