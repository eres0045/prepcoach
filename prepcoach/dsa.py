"""DSA practice: a curated problem bank with a hint ladder.

Design rule: hints level 1 (nudge) and level 2 (approach) never contain
code. Level 3 is pseudocode only — never a full solution. The point is
practice, not answer-copying, so the bank ships no complete solutions
at all.

Solution review never executes user code (executing pasted code would
be unsafe). It walks the stated test cases, checks the named edge
cases against the pasted text, and returns a checklist plus a
model/stub commentary. It is practice review, not grading.
"""

PROBLEMS = [
    {
        "id": "two-sum",
        "title": "Two Sum",
        "topic": "hash maps",
        "difficulty": "easy",
        "statement": "Given an array of integers and a target, return the indices of "
                    "the two numbers that add up to the target. Assume "
                    "exactly one solution, and do not reuse an element.",
        "examples": [{"input": "nums = [2, 7, 11, 15], target = 9",
                      "output": "[0, 1]"}],
        "starter": "def two_sum(nums, target):\n    # your code here\n    pass",
        "edge_cases": ["empty array", "no solution exists",
                       "duplicate numbers"],
        "hints": [
            "Nudge: for each number, what other number would complete "
            "the target?",
            "Approach: remember numbers you have already seen and what "
            "you still need, so each lookup is fast instead of scanning "
            "the whole array again.",
            "Pseudocode: seen = empty map; for each index i and value v: "
            "need = target - v; if need in seen, return [seen[need], i]; "
            "else store v at i.",
        ],
        "keywords": ["dict", "map", "hash", "seen"],
    },
    {
        "id": "valid-parentheses",
        "title": "Valid Parentheses",
        "topic": "stacks",
        "difficulty": "easy",
        "statement": "Given a string of brackets ()[]{} , decide whether it is valid: "
                    "every opening bracket must be closed by the same type, "
                    "in the correct order.",
        "examples": [{"input": "s = \"()[]{}\"", "output": "true"},
                     {"input": "s = \"(]\"", "output": "false"}],
        "starter": "def is_valid(s):\n    # your code here\n    pass",
        "edge_cases": ["empty string", "closing bracket first",
                       "unclosed opening bracket"],
        "hints": [
            "Nudge: which bracket did you see most recently, and what "
            "must come next?",
            "Approach: track opening brackets in order, and match each "
            "closing bracket against the most recent unmatched one.",
            "Pseudocode: stack = empty; for each character: if opening, "
            "push it; else if stack empty or top does not match, return "
            "false; else pop. Valid if stack is empty at the end.",
        ],
        "keywords": ["stack", "push", "pop"],
    },
    {
        "id": "best-stock",
        "title": "Best Time to Buy and Sell Stock",
        "topic": "arrays",
        "difficulty": "easy",
        "statement": "Given daily prices, choose one day to buy and a later day to sell "
                    "to maximise profit. Return the maximum profit, or 0 "
                    "if no profit is possible.",
        "examples": [{"input": "prices = [7, 1, 5, 3, 6, 4]",
                      "output": "5"}],
        "starter": "def max_profit(prices):\n    # your code here\n    pass",
        "edge_cases": ["prices always falling", "single price",
                       "profit on the last day"],
        "hints": [
            "Nudge: you only need the lowest price seen so far, not every "
            "pair of days.",
            "Approach: walk once, remembering the cheapest buy price and "
            "the best profit available at each step.",
            "Pseudocode: min_price = infinity; best = 0; for each price: "
            "min_price = min(min_price, price); "
            "best = max(best, price - min_price).",
        ],
        "keywords": ["min", "max", "profit"],
    },
    {
        "id": "reverse-string",
        "title": "Reverse a String In Place",
        "topic": "two pointers",
        "difficulty": "easy",
        "statement": "Reverse a list of characters in place, using only constant extra "
                    "space.",
        "examples": [{"input": "s = ['h', 'e', 'l', 'l', 'o']",
                      "output": "['o', 'l', 'l', 'e', 'h']"}],
        "starter": "def reverse_string(s):\n    # your code here\n    pass",
        "edge_cases": ["empty list", "single character",
                       "even vs odd length"],
        "hints": [
            "Nudge: which two positions would you swap first?",
            "Approach: work from both ends towards the middle, swapping "
            "as you go.",
            "Pseudocode: left = 0; right = last index; while left < "
            "right: swap s[left] and s[right]; left += 1; right -= 1.",
        ],
        "keywords": ["swap", "left", "right"],
    },
    {
        "id": "anagram",
        "title": "Valid Anagram",
        "topic": "strings",
        "difficulty": "easy",
        "statement": "Given two strings, decide whether one is an anagram of the other: "
                    "same letters, same counts, possibly different order.",
        "examples": [{"input": "s = \"anagram\", t = \"nagaram\"",
                      "output": "true"},
                     {"input": "s = \"rat\", t = \"car\"",
                      "output": "false"}],
        "starter": "def is_anagram(s, t):\n    # your code here\n    pass",
        "edge_cases": ["different lengths", "empty strings",
                       "repeated letters"],
        "hints": [
            "Nudge: what has to match — the letters, or something about "
            "them?",
            "Approach: count how many times each letter appears in each "
            "string, then compare the counts.",
            "Pseudocode: if lengths differ, return false; count letters "
            "in s; subtract counts for letters in t; valid if every "
            "count is zero.",
        ],
        "keywords": ["count", "counter", "freq"],
    },
    {
        "id": "contains-duplicate",
        "title": "Contains Duplicate",
        "topic": "hash maps",
        "difficulty": "easy",
        "statement": "Given an integer array, return true if any value appears at least "
                    "twice, and false otherwise.",
        "examples": [{"input": "nums = [1, 2, 3, 1]", "output": "true"},
                     {"input": "nums = [1, 2, 3, 4]", "output": "false"}],
        "starter": "def contains_duplicate(nums):\n    # your code here\n    pass",
        "edge_cases": ["empty array", "duplicate at the end",
                       "all values identical"],
        "hints": [
            "Nudge: what do you need to remember as you scan?",
            "Approach: keep a set of values seen so far; a repeat means "
            "an immediate answer.",
            "Pseudocode: seen = empty set; for each value: if value in "
            "seen, return true; add value to seen. Return false.",
        ],
        "keywords": ["set", "seen"],
    },
    {
        "id": "move-zeroes",
        "title": "Move Zeroes",
        "topic": "two pointers",
        "difficulty": "easy",
        "statement": "Move all zeroes in an array to the end, keeping the relative order "
                    "of the non-zero elements, in place.",
        "examples": [{"input": "nums = [0, 1, 0, 3, 12]",
                      "output": "[1, 3, 12, 0, 0]"}],
        "starter": "def move_zeroes(nums):\n    # your code here\n    pass",
        "edge_cases": ["no zeroes", "all zeroes", "zeroes at the end"],
        "hints": [
            "Nudge: one pointer can mark where the next non-zero element "
            "belongs.",
            "Approach: sweep once, placing non-zeroes at the front in "
            "order, then fill the rest with zeroes.",
            "Pseudocode: place = 0; for each value: if value != 0: "
            "nums[place] = value; place += 1; then fill nums[place:] "
            "with 0.",
        ],
        "keywords": ["place", "index", "zero"],
    },
    {
        "id": "longest-substring",
        "title": "Longest Substring Without Repeating Characters",
        "topic": "strings",
        "difficulty": "medium",
        "statement": "Given a string, find the length of the longest substring without "
                    "repeating characters.",
        "examples": [{"input": "s = \"abcabcbb\"", "output": "3"},
                     {"input": "s = \"bbbbb\"", "output": "1"}],
        "starter": "def length_of_longest_substring(s):\n    # your code here\n    pass",
        "edge_cases": ["empty string", "all same character",
                       "repeat far apart"],
        "hints": [
            "Nudge: when a character repeats, what part of your current "
            "window is still usable?",
            "Approach: slide a window across the string, remembering "
            "where each character was last seen, and shrink from the "
            "left past any repeat.",
            "Pseudocode: left = 0; best = 0; last_seen = map; for "
            "right, ch in string: if ch seen at or after left, left = "
            "last_seen[ch] + 1; record ch at right; "
            "best = max(best, right - left + 1).",
        ],
        "keywords": ["window", "left", "right", "seen"],
    },
]

TOPICS = sorted({p["topic"] for p in PROBLEMS})


def get_problem(problem_id):
    for problem in PROBLEMS:
        if problem["id"] == problem_id:
            return problem
    return None


def hint(problem_id, level):
    """Return hint text for level 1-3. Levels 1-2 contain no code."""
    problem = get_problem(problem_id)
    if problem is None:
        raise ValueError("Unknown problem: %s" % problem_id)
    if level not in (1, 2, 3):
        raise ValueError("Hint level must be 1, 2, or 3")
    return {"level": level, "text": problem["hints"][level - 1],
            "is_pseudocode": level == 3}


def review_solution(problem_id, code, provider):
    """Practice review of a pasted solution. Never executes the code."""
    problem = get_problem(problem_id)
    if problem is None:
        raise ValueError("Unknown problem: %s" % problem_id)
    lowered = (code or "").lower()
    matched = [kw for kw in problem["keywords"] if kw in lowered]
    checklist = []
    for edge in problem["edge_cases"]:
        mentioned = any(word in lowered
                        for word in edge.split() if len(word) > 3)
        checklist.append({"edge_case": edge,
                          "mentioned_in_solution": bool(mentioned)})
    if provider.name != "stub":
        try:
            commentary = provider.complete(
                "DSA_REVIEW: review this practice solution against the "
                "problem statement and test cases. Point out gaps and "
                "suggest what to test next. Do not write a full solution.",
                "Problem: %s\nSolution:\n%s" % (problem["statement"], code),
            )
        except Exception:
            commentary = None
    else:
        commentary = None
    if not commentary:
        commentary = (
            "Practice review: walk your solution through each stated test "
            "case by hand. Keywords spotted: %s. Check the edge cases "
            "above — any you did not mention deserve a test of their own."
            % (", ".join(matched) if matched else "none"))
    return {
        "problem": problem["title"],
        "test_cases": problem["examples"],
        "edge_checklist": checklist,
        "keywords_spotted": matched,
        "commentary": commentary,
        "note": "Practice review only — your code was not executed and this "
                "is not a grade.",
    }
