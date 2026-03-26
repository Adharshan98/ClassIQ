"""
core/session_manager.py
-----------------------
Orchestrates the AI evaluation pipeline for a single student response
submitted in real time.

Now includes Plagiarism/AI Detection alongside Engagement Risk & Scaffolding.
"""

from core.hybrid_engine      import evaluate_response
from core.risk_engine        import assess_risk
from core.scaffolding_engine import get_scaffolding_question
from core.plagiarism_engine  import detect_plagiarism
from difflib import SequenceMatcher


def evaluate_student_response(
    response: str,
    topic:    str,
    question: str = "",
    student_index: int = 0,
) -> dict:
    """
    Run the full AI pipeline on a single student response.

    Returns dict with keys:
        score, label, risk_prob, risk_label, explanation (HTML-safe str),
        feedback, scaffolding, plag_score, plag_flag
    """
    # 0. Question Copy-Paste Trap
    if question and len(response.strip()) > 5:
        r_low = response.lower().strip()
        q_low = question.lower().strip()
        ratio = SequenceMatcher(None, r_low, q_low).ratio()

        if ratio > 0.85 or r_low in q_low or q_low in r_low:
            return {
                "score":       2.0,
                "label":       "Needs Attention",
                "risk_prob":   1.0,
                "risk_label":  "High",
                "explanation": "❌ Response precisely matches the question text. Zero engagement effort detected.",
                "feedback":    "Did you just copy and paste the question? 🤨 Please provide your own actual thought process.",
                "scaffolding": "Start by explaining what keywords in the question mean in your own words.",
                "plag_score":  1.0,
                "plag_flag":   "High AI/Plagiarism: Re-submitted the Question exactly.",
            }

    # 1. AI/Plagiarism Detection
    plag_score, plag_flag = detect_plagiarism(response)

    # 2. Hybrid Engagement Engine
    score, label, explanation_parts = evaluate_response(response, topic)

    # If it's highly flagged as AI, append a warning
    if plag_score >= 0.7:
        explanation_parts = list(explanation_parts)  # unfreeze tuple if cached
        explanation_parts.append(
            f"⚠️ High probability of AI generation or copy-pasting ({plag_score * 100:.0f}%)"
        )

    # 3. Risk Engine
    risk_prob, risk_label = assess_risk(response, topic)

    # 4. Feedback Generation
    if label == "Engaged":
        feedback = "🌟 Excellent! Keep exploring advanced aspects of this topic."
    elif label == "Partially Engaged":
        feedback = (
            "📚 You are partially engaged. Try using more technical keywords "
            "and explain the 'why' with connectors like 'because' or 'therefore'."
        )
    else:
        feedback = (
            "💡 Your response needs more depth. Review the core concept, use "
            "specific technical terms, and explain the reasoning behind your answer."
        )

    # 5. Scaffolding (only for Needs Attention)
    scaffolding = (
        get_scaffolding_question(topic, student_index)
        if label == "Needs Attention" else ""
    )

    # Join explanation as clean bullet lines (not pipe-separated)
    explanation_str = "\n".join(explanation_parts)

    return {
        "score":       score,
        "label":       label,
        "risk_prob":   risk_prob,
        "risk_label":  risk_label,
        "explanation": explanation_str,
        "feedback":    feedback,
        "scaffolding": scaffolding,
        "plag_score":  plag_score,
        "plag_flag":   plag_flag,
    }
