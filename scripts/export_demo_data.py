"""Export the single-source-of-truth practice banks to docs/demo-data.json.

The static demo copy of the frontend (GitHub Pages) runs from this file.
Regenerate after any change to interview.QUESTIONS or dsa.PROBLEMS:

    python3 scripts/export_demo_data.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prepcoach import dsa, interview  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "docs", "demo-data.json")


def main():
    data = {
        "interview": interview.QUESTIONS,
        "topics": dsa.TOPICS,
        "dsa": [{
            "id": p["id"], "title": p["title"], "topic": p["topic"],
            "difficulty": p["difficulty"], "statement": p["statement"],
            "examples": p["examples"], "starter": p["starter"],
            "edge_cases": p["edge_cases"], "hints": p["hints"],
            "keywords": p["keywords"],
        } for p in dsa.PROBLEMS],
    }
    with open(OUT, "w") as fh:
        json.dump(data, fh, indent=1)
    print("wrote %s (%d DSA problems, %d roles)"
          % (OUT, len(data["dsa"]), len(data["interview"])))


if __name__ == "__main__":
    main()
