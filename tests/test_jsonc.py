import sys
import unittest
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE_ROOT / "scripts"))

from jsonc import loads  # noqa: E402


class JsoncReaderTest(unittest.TestCase):
    def test_comments_and_trailing_commas_are_supported(self):
        value = loads(
            """
            {
              // A line comment
              "name": "https://example.test//not-a-comment",
              /* A block comment */
              "items": [1, 2,],
            }
            """
        )
        self.assertEqual(value["name"], "https://example.test//not-a-comment")
        self.assertEqual(value["items"], [1, 2])

    def test_invalid_unterminated_comment_is_rejected(self):
        with self.assertRaises(ValueError):
            loads('{"name": "value" /* missing terminator }')


if __name__ == "__main__":
    unittest.main()
