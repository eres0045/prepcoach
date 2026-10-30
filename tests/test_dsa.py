import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prepcoach import dsa
from prepcoach.model_client import StubProvider


class TestDSA(unittest.TestCase):
    def test_bank_covers_five_topics(self):
        self.assertGreaterEqual(len(dsa.TOPICS), 5)
        self.assertGreaterEqual(len(dsa.PROBLEMS), 8)

    def test_hints_never_hand_over_full_solutions(self):
        for problem in dsa.PROBLEMS:
            for level in (1, 2):
                text = dsa.hint(problem["id"], level)["text"]
                self.assertNotIn("def ", text)
                self.assertNotIn("return [", text)
            level3 = dsa.hint(problem["id"], 3)
            self.assertTrue(level3["is_pseudocode"])
            self.assertNotIn("def ", level3["text"])

    def test_hint_levels_validated(self):
        with self.assertRaises(ValueError):
            dsa.hint("two-sum", 4)
        with self.assertRaises(ValueError):
            dsa.hint("nope", 1)

    def test_review_does_not_execute_code(self):
        result = dsa.review_solution(
            "two-sum", "import os; os.system('rm -rf /')", StubProvider())
        self.assertIn("not executed", result["note"])
        self.assertEqual(result["problem"], "Two Sum")
        self.assertTrue(result["test_cases"])


if __name__ == "__main__":
    unittest.main()
