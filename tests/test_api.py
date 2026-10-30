import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

app.config["TESTING"] = True


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_mode_reports_stub_without_key(self):
        env = dict(os.environ)
        os.environ.pop("BHARATCODE_API_KEY", None)
        try:
            resp = self.client.get("/api/mode")
            self.assertEqual(resp.json["provider"], "stub")
            self.assertTrue(resp.json["demo_mode"])
        finally:
            os.environ.clear()
            os.environ.update(env)

    def test_interview_end_to_end(self):
        start = self.client.post("/api/interview/start",
                                 json={"role": "QA Engineer",
                                       "level": "junior"})
        self.assertEqual(start.status_code, 200)
        sid = start.json["session_id"]
        question = start.json["question"]
        while question:
            resp = self.client.post("/api/interview/answer",
                                    json={"session_id": sid,
                                          "answer": "A detailed answer "
                                          "with a concrete example and "
                                          "trade-offs explained."})
            if resp.json.get("finished"):
                self.assertIn("Strengths",
                              resp.json["debrief"]["guidance"])
                self.assertTrue(resp.json["debrief"]["practice_only"])
                break
            question = resp.json["question"]
        else:
            self.fail("Interview never finished")

    def test_resume_end_to_end(self):
        resp = self.client.post(
            "/api/resume",
            json={"resume_text": "Asha Verma\nasha@example.com | "
                  "+91 90000 00000 | github.com/asha\nExperience\n"
                  "- Built a portal that cut onboarding time by 40%.\n"
                  "Education\nB.Tech, 2025.\nSkills\nPython.\n"})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json["findings"])

    def test_dsa_end_to_end(self):
        problems = self.client.get("/api/dsa/problems").json["problems"]
        self.assertGreaterEqual(len(problems), 8)
        pid = problems[0]["id"]
        hint = self.client.post("/api/dsa/hint",
                                json={"problem_id": pid, "level": 1}).json
        self.assertNotIn("def ", hint["text"])
        review = self.client.post(
            "/api/dsa/review",
            json={"problem_id": pid,
                  "code": "def f(x):\n    seen = {}\n    return seen"}).json
        self.assertIn("not executed", review["note"])

    def test_bad_inputs_rejected(self):
        self.assertEqual(self.client.post(
            "/api/interview/start",
            json={"role": "Astronaut", "level": "junior"}).status_code, 400)
        self.assertEqual(self.client.post(
            "/api/resume", json={"resume_text": "  "}).status_code, 400)


if __name__ == "__main__":
    unittest.main()
