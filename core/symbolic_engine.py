"""
core/symbolic_engine.py
-----------------------
Rule-based scoring engine that augments ML predictions with linguistic analysis.
Evaluates student responses based on keyword presence, response length,
confusion phrases, and logical connectors.
"""

# ── Topic-specific conceptual keywords ───────────────────────────────────────
TOPIC_KEYWORDS: dict[str, list[str]] = {
    "recursion":            ["base case", "recursive", "call stack", "terminate", "sub-problem", "depth", "infinite"],
    "oop":                  ["class", "object", "inheritance", "polymorphism", "encapsulation", "method", "attribute", "instance"],
    "linked list":          ["node", "pointer", "next", "head", "tail", "traversal", "singly", "doubly"],
    "binary search":        ["divide", "sorted", "mid", "logarithm", "half", "O(log n)", "pivot"],
    "sorting":              ["compare", "swap", "partition", "merge", "pivot", "O(n log n)", "bubble", "quick", "insertion"],
    "hashing":              ["hash function", "collision", "bucket", "key", "value", "O(1)", "chaining", "load factor"],
    "dynamic programming":  ["memoization", "sub-problem", "optimal", "cache", "bottom-up", "top-down", "tabulation"],
    "graph":                ["node", "edge", "BFS", "DFS", "path", "cycle", "vertex", "adjacency", "traversal"],
    "stack":                ["LIFO", "push", "pop", "top", "overflow", "call stack"],
    "queue":                ["FIFO", "enqueue", "dequeue", "front", "rear", "circular"],
    "default":              ["understand", "concept", "because", "therefore", "example", "means", "works", "when", "how"],
}

# ── Confusion / disengagement signals ────────────────────────────────────────
CONFUSION_PHRASES: list[str] = [
    "don't know", "not sure", "i don't", "no idea", "i can't", "confused",
    "not clear", "i forget", "i forgot", "i don't understand", "lost",
    "wasn't paying", "didn't attend", "no clue", "vaguely", "maybe",
]

# ── Logical connectors that indicate reasoning ability ────────────────────────
LOGICAL_CONNECTORS: list[str] = [
    "because", "therefore", "hence", "thus", "which means",
    "as a result", "since", "this ensures", "so that", "this allows",
]


def score_response(response: str, topic: str) -> tuple[float, list[str]]:
    """
    Apply rule-based scoring to a student response.

    Returns
    -------
    tuple[float, list[str]]
        (score_adjustment, explanation_list)
        score_adjustment is in range [-15, 30]
    """
    explanation: list[str] = []
    score = 0.0
    text  = response.lower().strip()

    # ── 1. Response length ────────────────────────────────────────────────────
    word_count = len(text.split())
    if word_count >= 30:
        score += 10
        explanation.append("✅ Detailed response (30+ words) — shows effort.")
    elif word_count >= 15:
        score += 6
        explanation.append("🟡 Moderate response length (15–29 words).")
    elif word_count >= 5:
        score += 2
        explanation.append("🟠 Short response (5–14 words) — consider elaborating.")
    else:
        score -= 5
        explanation.append("❌ Very short response (<5 words) — insufficient detail.")

    # ── 2. Keyword detection ──────────────────────────────────────────────────
    topic_key = topic.lower().strip()
    keywords  = TOPIC_KEYWORDS.get(topic_key, TOPIC_KEYWORDS["default"])
    matched   = [kw for kw in keywords if kw in text]

    if len(matched) >= 3:
        score += 12
        explanation.append(f"✅ Strong keyword usage: {', '.join(matched)}.")
    elif matched:
        score += 6
        explanation.append(f"🟡 Some keywords found: {', '.join(matched)}.")
    else:
        explanation.append("❌ No topic-specific keywords detected.")

    # ── 3. Confusion phrase penalty ───────────────────────────────────────────
    found_confusion = [ph for ph in CONFUSION_PHRASES if ph in text]
    if found_confusion:
        penalty = min(len(found_confusion) * 4, 12)
        score  -= penalty
        explanation.append(
            f"⚠️ Confusion detected ('{found_confusion[0]}') — score −{penalty}."
        )

    # ── 4. Logical connector bonus ────────────────────────────────────────────
    found_connectors = [lc for lc in LOGICAL_CONNECTORS if lc in text]
    if found_connectors:
        score += 8
        explanation.append(
            f"✅ Logical reasoning detected ('{found_connectors[0]}')."
        )

    return round(max(-15.0, min(30.0, score)), 2), explanation
