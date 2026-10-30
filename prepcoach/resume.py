"""Resume teardown: a deterministic, rubric-based analysis.

The rubric only analyses what the user actually pasted. It never invents
experience, employers, metrics, or degrees. Rewrite suggestions are
phrasing templates with explicit placeholders (``<what>``, ``<number>``)
that the user must fill with their own real numbers — a template is not
a claim.

Criteria: contact info, summary, experience section, education section,
skills section, projects section, impact wording (action verbs and
quantified outcomes), and overall length.
"""

import re

IMPACT_VERBS = [
    "built", "shipped", "designed", "led", "improved", "reduced",
    "increased", "automated", "launched", "delivered", "created",
    "developed", "optimised", "optimized", "scaled", "fixed", "owned",
]

SECTION_PATTERNS = {
    "experience": r"experience|work history|employment",
    "education": r"education|degree|university|college|b\.?tech",
    "skills": r"skills|technologies|tech stack|tools",
    "projects": r"projects|portfolio",
    "summary": r"summary|profile|objective",
}

CONTACT_PATTERNS = {
    "email": r"[\w.+-]+@[\w-]+\.[\w.-]+",
    "phone": r"\+?\d[\d\s-]{7,}\d",
    "link": r"(github\.com|linkedin\.com|https?://)",
}


def _find_sections(text):
    lowered = text.lower()
    return {name: bool(re.search(pat, lowered))
            for name, pat in SECTION_PATTERNS.items()}


def _bullet_lines(text):
    return [ln.strip() for ln in text.splitlines()
            if ln.strip().startswith(("-", "*", "•")) or
            re.match(r"^\d+[.)]\s", ln.strip())]


def analyse(text):
    """Analyse pasted resume text. Returns rubric findings + suggestions."""
    text = text or ""
    sections = _find_sections(text)
    bullets = _bullet_lines(text)
    words = len(text.split())
    findings = []

    def add(criterion, status, evidence, suggestion):
        findings.append({
            "criterion": criterion, "status": status,
            "evidence": evidence, "suggestion": suggestion,
        })

    contacts = {k: bool(re.search(p, text)) for k, p in
                CONTACT_PATTERNS.items()}
    if all(contacts.values()):
        add("Contact info", "pass", "Email, phone, and a link all present.",
            "Keep it to one line at the top so parsers read it first.")
    else:
        missing = ", ".join(k for k, v in contacts.items() if not v)
        add("Contact info", "attention", "Missing: %s." % missing,
            "Add the missing contact detail(s) at the top: %s." % missing)

    for name in ("experience", "education", "skills", "projects"):
        if sections[name]:
            add("%s section" % name.capitalize(), "pass",
                "Section detected.", "Keep entries newest-first with dates.")
        else:
            add("%s section" % name.capitalize(), "attention",
                "No %s section detected." % name,
                "Add a %s section — recruiters and ATS parsers look for it "
                "explicitly." % name)

    if not bullets:
        add("Impact wording", "attention",
            "No bullet points found.",
            "Rewrite achievements as bullets starting with an action verb, "
            "e.g. 'Built <what>, improving <metric> by <number>%' — fill "
            "the placeholders with your real numbers only.")
        add("Quantified outcomes", "attention",
            "No bullets to quantify.",
            "Once bullets exist, add a real figure where true: users, "
            "latency, revenue, or time saved. Never invent one.")
    else:
        with_verb = [b for b in bullets
                     if any(v in b.lower() for v in IMPACT_VERBS)]
        with_number = [b for b in bullets if re.search(r"\d", b)]
        if len(with_verb) >= len(bullets) / 2:
            add("Impact wording", "pass",
                "%d of %d bullets start with or contain an action verb."
                % (len(with_verb), len(bullets)),
                "Keep verbs specific: 'shipped' beats 'worked on'.")
        else:
            add("Impact wording", "attention",
                "Only %d of %d bullets contain an action verb."
                % (len(with_verb), len(bullets)),
                "Start each bullet with a verb like built, shipped, or "
                "reduced, and name what changed.")
        if with_number:
            add("Quantified outcomes", "pass",
                "%d bullet(s) include a number." % len(with_number),
                "Numbers are good — keep them truthful and checkable.")
        else:
            add("Quantified outcomes", "attention",
                "No bullet contains a number.",
                "Where true, add a real figure: users, latency, revenue, "
                "or time saved. Never invent one — leave it out if unsure.")

    if words < 150:
        add("Length", "attention", "%d words — very short." % words,
            "A one-page resume is usually 300–600 words; add the missing "
            "sections above before padding anything.")
    elif words > 900:
        add("Length", "attention", "%d words — long for one page." % words,
            "Trim to one page: cut older or less relevant bullets first.")
    else:
        add("Length", "pass", "%d words." % words,
            "Length is in a sensible range for one page.")

    weak_bullets = [b for b in bullets
                    if not any(v in b.lower() for v in IMPACT_VERBS)]
    suggestions = []
    for bullet in weak_bullets[:3]:
        suggestions.append(
            "Rewrite (template — fill with real facts only): '" +
            bullet[:80] + "' -> '<Action verb> <what you changed>, "
            "improving <metric> by <number>%'")
    if not suggestions:
        suggestions.append("No weak bullets found — keep the verb-first "
                           "style throughout.")
    return {
        "words": words,
        "bullets": len(bullets),
        "sections": sections,
        "findings": findings,
        "suggestions": suggestions,
        "note": "Analysis of the text you pasted only. Nothing here was "
                "invented about your background.",
    }
