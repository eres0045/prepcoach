import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prepcoach.interview import InterviewSession
from prepcoach.model_client import StubProvider


class TestInterview(unittest.TestCase):
    def _session(self):
        return InterviewSession("Backend Developer", "junior",
                                StubProvider())

    def test_start_returns_first_question(self):
        s = self._session()
        q = s.next_question()
        self.assertTrue(q)
        self.assertFalse(s.finished)

    def test_thin_answer_triggers_followup_then_continues(self):
        s = self._session()
        s.next_question()
        nxt = s.answer("idk")
        self.assertIn("go deeper", nxt)
        nxt2 = s.answer("A long enough answer that explains the concept "
                        "with an example and some detail about trade-offs.")
        self.assertTrue(nxt2)
        self.assertNotIn("go deeper", nxt2)

    def test_full_session_ends_with_debrief_and_no_score(self):
        s = self._session()
        q = s.next_question()
        while q is not None:
            q = s.answer("A substantive answer with enough detail and a "
                         "concrete example to show understanding.")
        debrief = s.debrief()
        self.assertTrue(debrief["practice_only"])
        self.assertNotIn("score", debrief["guidance"].lower())
        self.assertIn("Strengths", debrief["guidance"])

    def test_repeated_thin_answers_terminate(self):
        # Regression: a follow-up answer that is itself thin must not
        # spawn another follow-up, or short answers loop forever.
        s = self._session()
        q = s.next_question()
        steps = 0
        while q is not None and steps < 50:
            q = s.answer("idk")
            steps += 1
        self.assertIsNone(q)
        self.assertLessEqual(steps, 12)

    def test_unknown_role_rejected(self):
        with self.assertRaises(ValueError):
            InterviewSession("Astronaut", "junior", StubProvider())


if __name__ == "__main__":
    unittest.main()
