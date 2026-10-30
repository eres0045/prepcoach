# PrepCoach — Placement-prep AI coach

Built for the **BharatCode Build League**: an AI-powered placement-prep
coach that uses BharatCode's model API for live coaching, with a
built-in practice mode when no key is configured. Solo entry, team
**Fortec**.

## The three modes

1. **Mock interviews** — pick a role (Full Stack, Frontend, Backend, QA)
   and level (junior/mid). The coach asks questions one at a time,
   follows up when an answer is thin, and ends with a structured
   debrief: strengths, gaps, what to practise next. The debrief is
   labelled practice guidance — there is no numeric score, because a
   practice session is not a real assessment.
2. **Resume teardown** — paste resume text and get rubric-based feedback
   (contact info, sections, impact wording, quantified outcomes,
   length) with concrete rewrite suggestions. It only analyses what was
   pasted: it never invents experience, employers, or numbers, and
   rewrite templates carry explicit placeholders for real figures.
3. **DSA practice** — a curated bank (arrays, strings, hash maps, two
   pointers, stacks) with a hint ladder: level 1 is a nudge, level 2 an
   approach, level 3 pseudocode only. No full solutions are shipped.
   Solution review walks the stated test cases and edge cases; it
   never executes pasted code, and it is practice review, not a grade.

## Run locally

```bash
pip install -r requirements.txt
python3 app.py          # http://localhost:5000
python3 -m unittest discover -s tests
```

## Model client and the one open gate: the BharatCode key

`prepcoach/model_client.py` is the only place that talks to a model.
BharatCode publishes no public model-API documentation, endpoint, or
key-issuance flow that could be verified from public sources, so the
client is a pluggable OpenAI-compatible chat-completions client driven
entirely by environment configuration:

```bash
export BHARATCODE_API_KEY="..."        # from the BharatCode account dashboard
export BHARATCODE_API_BASE_URL="..."   # API base URL shown in that dashboard
export BHARATCODE_MODEL="..."          # model name shown in that dashboard
```

Without a key, the app runs in **demo mode** on the built-in stub
provider (question bank, deterministic rubric, hint ladder), and the
banner says so. With a key, the same three flows are model-driven and
the banner switches to live mode. The key stays server-side, is read
from the environment only, and is never logged, printed, or committed.

**To go live:** sign in to the BharatCode account dashboard, copy the
API key (and base URL / model name if shown) into the environment
above, restart the server, and confirm the banner reads live mode. If
BharatCode's real endpoint shape differs from chat-completions, only
`model_client.py` needs to change.

## Live demo

The static copy in `docs/` is served by GitHub Pages in **demo mode**
(the same three flows run in-browser from `docs/demo-data.json`,
regenerated from the Python banks by
`python3 scripts/export_demo_data.py`). For live coaching, run the
Flask backend with a key as above.

## Honest limits

- Demo mode is not a live model: its interview questions come from a
  fixed bank and its resume/DSA feedback is rule-based.
- Feedback is practice guidance only. No placement is guaranteed, no
  score is a real assessment, and no reviewed solution is executed.
- The live BharatCode endpoint is unverified (see above): the client
  assumes the standard chat-completions shape until the dashboard
  confirms otherwise.
- No user accounts, no payments, no data stored server-side beyond
  in-memory interview sessions.
