"""Mock-interview flow.

A session asks a fixed bank of questions for the chosen role/level, one
at a time, with a follow-up when an answer is thin, and ends with a
structured debrief. The debrief is labelled practice guidance: it lists
strengths, gaps, and what to practise next. It never presents a numeric
score as a real assessment, because a practice session is not one.

With a live model provider, questions and the debrief are model-written;
with the stub, they come from the bank below and a template debrief.
Either way the flow, the question count, and the debrief shape are the
same, which is what the tests pin down.
"""

QUESTIONS = {
    "Full Stack Developer": {
        "junior": [
            "Explain the difference between SQL and NoSQL databases, and when you would pick each.",
            "How does a REST API handle a POST request end to end, from the client to the database?",
            "What is the difference between authentication and authorization? Give a practical example.",
            "Walk me through how you would debug a page that loads slowly in production.",
            "What does a good pull request look like, and how do you review someone else's code?",
        ],
        "mid": [
            "Design a rate limiter for a public API. What data structure would you use, and where does it live?",
            "Your team's service goes down at peak traffic. How do you find the cause and what do you fix first?",
            "Compare server-side rendering and client-side rendering for a content-heavy product.",
            "How would you design database indexes for a query that filters by user, status, and date?",
            "Explain how you would roll out a breaking API change without breaking existing clients.",
        ],
    },
    "Frontend Developer": {
        "junior": [
            "Explain the difference between flexbox and grid, and when you would use each.",
            "What happens in the browser between typing a URL and seeing the page?",
            "How do you make a form accessible to keyboard and screen-reader users?",
            "What is the virtual DOM, and why do frameworks use it?",
            "How would you debug a layout that breaks only on small screens?",
        ],
        "mid": [
            "Design a component library for three products. How do you keep it consistent and versioned?",
            "A page re-renders far too often. How do you find the cause and fix it?",
            "Compare client-side state tools: when is local state enough, and when do you reach for a store?",
            "How would you implement infinite scroll without hurting performance or accessibility?",
            "Explain your approach to testing a checkout flow end to end.",
        ],
    },
    "Backend Developer": {
        "junior": [
            "What is an index in a database, and what does it cost you?",
            "Explain how a web server handles many requests at once.",
            "What is the difference between a 401 and a 403 response?",
            "How do you keep secrets out of source code?",
            "Walk me through designing a simple URL shortener.",
        ],
        "mid": [
            "Design a job queue for sending emails at scale. What breaks first?",
            "How do you handle a database migration on a table with millions of rows and no downtime?",
            "Compare caching strategies: what do you cache, where, and how do you invalidate it?",
            "A downstream service is slow and timing out. How do you protect your service?",
            "Explain eventual consistency with a real example from a product you know.",
        ],
    },
    "QA Engineer": {
        "junior": [
            "What is the difference between a bug report that gets fixed fast and one that bounces back?",
            "Explain the difference between unit, integration, and end-to-end tests.",
            "How do you test a login form, including the unhappy paths?",
            "What do you do when you cannot reproduce a reported bug?",
            "How do you decide what to test when time is short?",
        ],
        "mid": [
            "Design a test strategy for a payments flow. What do you automate, and what stays manual?",
            "A release introduced a regression nobody caught. What changes in your process afterwards?",
            "How do you test an API contract between two teams?",
            "Explain how you would load-test a service before a big launch.",
            "How do you measure whether your test suite is actually useful?",
        ],
    },
}

ROLES = sorted(QUESTIONS)
LEVELS = ["junior", "mid"]
QUESTIONS_PER_SESSION = 5
THIN_ANSWER_WORDS = 20


class InterviewSession:
    """One mock-interview session. All state is plain data."""

    def __init__(self, role, level, provider):
        if role not in QUESTIONS:
            raise ValueError("Unknown role: %s" % role)
        if level not in LEVELS:
            raise ValueError("Unknown level: %s" % level)
        self.role = role
        self.level = level
        self.provider = provider
        self.bank = QUESTIONS[role][level]
        self.index = 0
        self.asked = []
        self.answers = []  # list of (question, answer)
        self.pending_followup = False
        self.last_was_followup = False
        self.finished = False

    def next_question(self):
        """Return the next question, or None when the session is done."""
        if self.finished:
            return None
        if self.pending_followup:
            self.pending_followup = False
            self.last_was_followup = True
            last_q, _ = self.answers[-1]
            question = ("You kept that one brief — can you go deeper on "
                        "'%s'? Give a concrete example." % last_q)
            self.asked.append(question)
            return question
        if self.index >= len(self.bank):
            self.finished = True
            return None
        if self.provider.name != "stub":
            try:
                question = self.provider.complete(
                    "INTERVIEW_QUESTION: ask one %s-level interview question "
                    "for a %s role. Return only the question."
                    % (self.level, self.role),
                    "Previous questions: %s" % "; ".join(self.asked),
                ).strip()
                if question:
                    self.asked.append(question)
                    return question
            except Exception:
                pass  # fall through to the bank on any model failure
        question = self.bank[self.index]
        self.index += 1
        self.last_was_followup = False
        self.asked.append(question)
        return question

    def answer(self, text):
        """Record an answer; return the next question or None."""
        if self.finished or not self.asked:
            return None
        self.answers.append((self.asked[-1], text or ""))
        # At most one follow-up per question: a follow-up answer that is
        # itself thin must not spawn another follow-up, or short answers
        # loop forever.
        if len((text or "").split()) < THIN_ANSWER_WORDS \
                and not self.last_was_followup:
            self.pending_followup = True
        return self.next_question()

    def debrief(self):
        """Structured practice guidance. No numeric score is produced."""
        if self.provider.name != "stub":
            try:
                summary = "; ".join(
                    "%s => %s" % (q, a) for q, a in self.answers)
                text = self.provider.complete(
                    "INTERVIEW_DEBRIEF: write a structured debrief with "
                    "Strengths, Gaps, and Practise next sections, as practice "
                    "guidance only. No numeric score.",
                    summary,
                )
                if text:
                    return {"guidance": text, "practice_only": True}
            except Exception:
                pass
        strengths, gaps = [], []
        for question, answer in self.answers:
            topic = question.split("?")[0][:60]
            if len(answer.split()) >= THIN_ANSWER_WORDS:
                strengths.append(topic)
            else:
                gaps.append(topic)
        if not strengths:
            strengths = ["You completed the session — that itself is "
                         "practice most candidates skip."]
        if not gaps:
            gaps = ["No thin answers; next time, push for harder follow-ups."]
        text = ("Strengths: %s.\nGaps: %s.\nPractise next: revisit the gap "
                "topics above and rehearse one concrete example per topic."
                % ("; ".join(strengths), "; ".join(gaps)))
        return {"guidance": text, "practice_only": True}
