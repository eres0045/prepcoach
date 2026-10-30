import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prepcoach.model_client import BharatCodeProvider, StubProvider, get_provider


class TestModelClient(unittest.TestCase):
    def test_stub_returns_deterministic_replies(self):
        stub = StubProvider()
        self.assertEqual(stub.complete("INTERVIEW_QUESTION", "x"),
                         "STUB_QUESTION")
        self.assertIn("Strengths", stub.complete("INTERVIEW_DEBRIEF", "x"))

    def test_live_provider_requires_key(self):
        env = dict(os.environ)
        os.environ.pop("BHARATCODE_API_KEY", None)
        try:
            with self.assertRaises(Exception):
                BharatCodeProvider(api_key="")
        finally:
            os.environ.clear()
            os.environ.update(env)

    def test_get_provider_defaults_to_stub_without_key(self):
        env = dict(os.environ)
        os.environ.pop("BHARATCODE_API_KEY", None)
        try:
            self.assertIsInstance(get_provider(), StubProvider)
        finally:
            os.environ.clear()
            os.environ.update(env)


if __name__ == "__main__":
    unittest.main()
