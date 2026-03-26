"""
core/concept_gap_engine.py
--------------------------
Analyses a batch of student responses for a given topic and identifies:
  • Which expected conceptual keywords are most commonly missing
  • The single biggest concept gap across the class
  • The overall confusion level (count of confusion phrases)

All logic is purely local — no external APIs required.
"""

# ── Expected keywords per topic ───────────────────────────────────────────────
# These represent the core concepts a student *should* mention when explaining
# the topic.  Missing keywords reveal concept gaps.

EXPECTED_KEYWORDS: dict[str, list[str]] = {
    "recursion": [
        "base case", "recursive call", "termination", "call stack",
        "sub-problem", "depth", "infinite loop",
    ],
    "oop": [
        "class", "object", "inheritance", "polymorphism",
        "encapsulation", "method", "attribute", "instance",
    ],
    "linked list": [
        "node", "pointer", "head", "traversal",
        "next", "singly", "doubly", "tail",
    ],
    "binary search": [
        "sorted", "divide", "mid", "O(log n)",
        "half", "logarithm", "pivot",
    ],
    "sorting": [
        "compare", "swap", "merge", "partition",
        "O(n log n)", "pivot", "bubble", "insertion",
    ],
    "hashing": [
        "hash function", "collision", "bucket",
        "key", "O(1)", "chaining", "load factor",
    ],
    "dynamic programming": [
        "memoization", "sub-problem", "optimal",
        "cache", "tabulation", "bottom-up", "top-down",
    ],
    "graph": [
        "node", "edge", "BFS", "DFS",
        "path", "cycle", "adjacency", "vertex",
    ],
    "stack": [
        "LIFO", "push", "pop", "top",
        "overflow", "call stack",
    ],
    "queue": [
        "FIFO", "enqueue", "dequeue", "front",
        "rear", "circular",
    ],
}

# ── Confusion signals ─────────────────────────────────────────────────────────
CONFUSION_SIGNALS: list[str] = [
    "don't know", "not sure", "confused", "i can't",
    "no idea", "not clear", "i forget", "i forgot",
    "lost", "wasn't paying", "couldn't understand",
    "vaguely", "no clue", "didn't understand",
]


def analyse_concept_gaps(responses: list[str], topic: str) -> dict:
    """
    Analyse a list of student response texts for concept gaps.

    Parameters
    ----------
    responses : list[str]
        Raw response strings from all students for this session.
    topic : str
        The lesson topic (matched against EXPECTED_KEYWORDS).

    Returns
    -------
    dict with keys:
        "topic"             – normalised topic string
        "expected_keywords" – list of all expected keywords for the topic
        "keyword_hit_rate"  – dict {keyword: hit_count} for each expected keyword
        "missing_counts"    – dict {keyword: missing_count} sorted worst-first
        "biggest_gap"       – str  – the most-missed keyword
        "gap_message"       – str  – human-readable teacher recommendation
        "confusion_count"   – int  – total confusion-phrase occurrences
        "confusion_alert"   – str  – human-readable confusion-level message
        "confusion_level"   – str  – "High" | "Moderate" | "Low"
    """
    if not responses:
        return {
            "topic":             topic,
            "expected_keywords": [],
            "keyword_hit_rate":  {},
            "missing_counts":    {},
            "biggest_gap":       "N/A",
            "gap_message":       "No responses submitted yet.",
            "confusion_count":   0,
            "confusion_alert":   "No data available.",
            "confusion_level":   "Low",
        }

    topic_key = topic.lower().strip()
    keywords  = EXPECTED_KEYWORDS.get(topic_key, [])

    # ── Keyword hit / miss analysis ───────────────────────────────────────────
    hit_rate     : dict[str, int] = {kw: 0 for kw in keywords}
    missing_count: dict[str, int] = {kw: 0 for kw in keywords}

    n = len(responses)
    for resp in responses:
        text = resp.lower()
        for kw in keywords:
            if kw in text:
                hit_rate[kw] += 1
            else:
                missing_count[kw] += 1

    # Sort by most-missed descending
    missing_sorted = dict(
        sorted(missing_count.items(), key=lambda x: x[1], reverse=True)
    )

    # Biggest single gap
    biggest_gap = next(iter(missing_sorted), "N/A") if missing_sorted else "N/A"

    if biggest_gap != "N/A":
        missed_by = missing_sorted[biggest_gap]
        pct       = round(missed_by / n * 100)
        gap_message = (
            f"📌 Students are weak in understanding "
            f"**'{biggest_gap}'** — missed by {missed_by}/{n} students ({pct}%). "
            f"Re-explain the '{biggest_gap}' concept with a concrete example "
            f"before moving forward."
        )
    else:
        gap_message = (
            f"✅ No keyword data available for topic '{topic}'. "
            "Consider adding it to the concept bank."
        )

    # ── Confusion detection ───────────────────────────────────────────────────
    total_confusion = 0
    for resp in responses:
        text = resp.lower()
        for signal in CONFUSION_SIGNALS:
            if signal in text:
                total_confusion += 1

    confusion_ratio = total_confusion / n

    if confusion_ratio >= 0.5:
        confusion_level = "High"
        confusion_alert = (
            "🚨 **High confusion detected** across the class "
            f"({total_confusion} confusion signals from {n} students). "
            "Stop and simplify your explanation. Use analogies or a live demo."
        )
    elif confusion_ratio >= 0.2:
        confusion_level = "Moderate"
        confusion_alert = (
            f"⚠️ **Moderate confusion detected** "
            f"({total_confusion} confusion signals from {n} students). "
            "Address common misconceptions before proceeding."
        )
    else:
        confusion_level = "Low"
        confusion_alert = (
            f"✅ Low confusion level "
            f"({total_confusion} confusion signals from {n} students). "
            "Class appears to be following the material."
        )

    return {
        "topic":             topic,
        "expected_keywords": keywords,
        "keyword_hit_rate":  hit_rate,
        "missing_counts":    missing_sorted,
        "biggest_gap":       biggest_gap,
        "gap_message":       gap_message,
        "confusion_count":   total_confusion,
        "confusion_alert":   confusion_alert,
        "confusion_level":   confusion_level,
    }
