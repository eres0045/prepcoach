import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prepcoach import resume

GOOD = """Ronit Shrimankar
ronit@example.com | +91 90000 00000 | github.com/example
Summary
Full-stack developer.
Experience
- Built a dashboard that reduced report time by 30%.
- Shipped an API used by 200 users.
Education
B.Tech, Example University, 2025.
Skills
Python, JavaScript, React.
Projects
- OpenTube: video streaming platform.
"""

THIN = "John Doe\nLikes coding."


class TestResume(unittest.TestCase):
    def test_good_resume_passes_sections_and_impact(self):
        result = resume.analyse(GOOD)
        by_criterion = {f["criterion"]: f for f in result["findings"]}
        self.assertEqual(by_criterion["Experience section"]["status"], "pass")
        self.assertEqual(by_criterion["Impact wording"]["status"], "pass")
        self.assertEqual(by_criterion["Quantified outcomes"]["status"],
                         "pass")

    def test_thin_resume_flags_gaps_without_inventing(self):
        result = resume.analyse(THIN)
        statuses = {f["criterion"]: f["status"] for f in result["findings"]}
        self.assertEqual(statuses["Experience section"], "attention")
        self.assertEqual(statuses["Quantified outcomes"], "attention")
        blob = str(result)
        self.assertNotIn("Google", blob)
        self.assertNotIn("Microsoft", blob)

    def test_suggestions_are_templates_not_claims(self):
        result = resume.analyse("- Worked on stuff.\n- Did things.")
        self.assertTrue(any("<" in s and ">" in s
                            for s in result["suggestions"]))

    def test_empty_input_handled(self):
        result = resume.analyse("")
        self.assertEqual(result["words"], 0)


if __name__ == "__main__":
    unittest.main()
