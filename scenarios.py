"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of JSON request bodies, sent exactly as written. Use this
              when the malformed request IS the point — an array instead of an
              object, empty text, a missing field, or something enormous.
"""

import json
from pathlib import Path


ROOT = Path(__file__).parent
# The supplied personal pieces are frozen in filename order. The first five
# are deliberately plain. They were supplied for this criterion before its
# first run; authorship is the student's attestation, not a detector finding.
HUMAN_TEXTS = [path.read_text(encoding="utf-8").strip()
               for path in sorted((ROOT / "samples/evaluation_samples").glob("personal_*.txt"))]
# A text-generation assistant produced these ten samples before the first
# criterion run. They are separate from the staff attack set.
AI_TEXTS = [row["text"] for row in json.loads(
    (ROOT / "samples/ai_generated.json").read_text(encoding="utf-8"))]

REPETITIVE_AI = "The system works well. " * 8
CARROLL_HUMAN = (
    "’Twas brillig, and the slithy toves did gyre and gimble in the wabe; "
    "all mimsy were the borogoves, and the mome raths outgrabe."
)

SCENARIOS = [
    {
        "name": "human writing false accusations",
        "criterion": 1,
        "texts": HUMAN_TEXTS,
    },
    {
        "name": "known AI versus human score medians",
        "criterion": 2,
        # The first ten are AI, and the last ten are user-supplied human pieces.
        "texts": AI_TEXTS + HUMAN_TEXTS[10:20],
    },
    {
        "name": "three labels and hundredth grid",
        "criterion": 3,
        # Five known human and seven known AI texts, including the two edge
        # examples documented in Unit 7 before these measurements.
        "texts": [HUMAN_TEXTS[i] for i in (0, 5, 10, 15)] +
                 [CARROLL_HUMAN] + AI_TEXTS[:6] + [REPETITIVE_AI],
        "score_grid": True,
    },
    {
        "name": "ten valid appeals and one unknown id",
        "criterion": 4,
        "kind": "appeal",
        "texts": AI_TEXTS,
        "reasoning": "I wrote this passage and request a human review.",
    },
    {
        "name": "six malformed or oversized submissions",
        "criterion": 5,
        "kind": "rejection",
        "bodies": [
            [],
            {"creator_id": "eval_missing_text"},
            {"text": "   ", "creator_id": "eval_blank_text"},
            {"text": 42, "creator_id": "eval_nonstring_text"},
            {"text": "This body has no creator ID."},
            {"text": "x" * 10001, "creator_id": "eval_oversized_text"},
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the text check — an empty
    string or a non-object JSON value can be the whole point of a bad-input case.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                try:
                    json.dumps(body)
                except (TypeError, ValueError):
                    problems.append(
                        f"scenario {i}, body {j} is not JSON-serializable"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
