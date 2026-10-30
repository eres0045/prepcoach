"""Pluggable model client for PrepCoach.

Two providers, one interface:

* ``StubProvider`` — deterministic, no network, no key. Powers the test
  suite and the clearly-labelled demo mode.
* ``BharatCodeProvider`` — OpenAI-compatible chat-completions HTTP client
  for BharatCode's model API. BharatCode publishes no public API docs or
  endpoint that this project could verify, so the base URL and model name
  are configuration, not hard-coded facts:

      BHARATCODE_API_KEY       - issued from the BharatCode account dashboard
      BHARATCODE_API_BASE_URL  - e.g. the API base URL shown in that dashboard
      BHARATCODE_MODEL         - the model name shown in that dashboard

  The client sends a standard chat-completions request
  (``POST {base_url}/v1/chat/completions`` with a Bearer key) and reads
  ``choices[0].message.content``. If BharatCode's real endpoint differs,
  only this module changes; the interview, resume, and DSA flows do not.

The key is never logged, never printed, and never committed: it is read
from the environment at construction time only.
"""

import os

import requests

DEFAULT_BASE_URL = "https://api.bharatcode.ai"
DEFAULT_MODEL = "bharatcode"


class ModelError(Exception):
    """Raised when a live model call fails (network, auth, bad response)."""


class StubProvider:
    """Deterministic practice coach. No network, no key, no claims."""

    name = "stub"

    def complete(self, system, user):
        """Return a canned, mode-aware response.

        The stub never pretends to be a real model: its replies are
        templates driven by the prompt's mode marker.
        """
        if "INTERVIEW_QUESTION" in system:
            return "STUB_QUESTION"
        if "INTERVIEW_DEBRIEF" in system:
            return (
                "Strengths: you gave substantive answers where you went into "
                "detail.\n"
                "Gaps: some answers stayed short — expand those topics.\n"
                "Practise next: revisit the topics you answered most briefly, "
                "and rehearse one concrete example per topic."
            )
        if "RESUME_REVIEW" in system:
            return (
                "Stub review: the deterministic rubric in resume.py is the "
                "source of truth here; a live model would rephrase its "
                "findings. No experience has been invented."
            )
        if "DSA_REVIEW" in system:
            return (
                "Stub review: walk your solution through each stated test "
                "case by hand, check the listed edge cases, and confirm the "
                "time complexity you claimed."
            )
        return "Stub reply: configure a BharatCode key for live coaching."


class BharatCodeProvider:
    """OpenAI-compatible HTTP client for BharatCode's model API."""

    name = "bharatcode"

    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or os.environ.get("BHARATCODE_API_KEY", "")
        self.base_url = (base_url or os.environ.get(
            "BHARATCODE_API_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        self.model = model or os.environ.get(
            "BHARATCODE_MODEL", DEFAULT_MODEL)
        if not self.api_key:
            raise ModelError(
                "BHARATCODE_API_KEY is not set; cannot use the live provider.")

    def complete(self, system, user, timeout=60):
        url = self.base_url + "/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.7,
        }
        try:
            resp = requests.post(
                url,
                json=payload,
                headers={"Authorization": "Bearer " + self.api_key},
                timeout=timeout,
            )
        except requests.RequestException as exc:
            raise ModelError("Model request failed: %s" % exc) from exc
        if resp.status_code != 200:
            raise ModelError(
                "Model request returned HTTP %s" % resp.status_code)
        try:
            return resp.json()["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ModelError("Unexpected model response shape") from exc


def get_provider():
    """Return the live provider when a key is configured, else the stub."""
    if os.environ.get("BHARATCODE_API_KEY"):
        try:
            return BharatCodeProvider()
        except ModelError:
            return StubProvider()
    return StubProvider()


def provider_status():
    """Public status for the /api/mode endpoint (never leaks the key)."""
    provider = get_provider()
    return {
        "provider": provider.name,
        "demo_mode": provider.name == "stub",
        "model": getattr(provider, "model", None),
    }
