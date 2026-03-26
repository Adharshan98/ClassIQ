"""
core/insight_engine.py
-----------------------
Generates class-level teaching recommendations based on the aggregate
engagement distribution across evaluated student responses.
"""


def generate_insight(results: list[dict]) -> str:
    """
    Analyse a list of student evaluation records and return a teaching action.

    Parameters
    ----------
    results : list[dict]
        Each dict must have the key 'label' with value in:
        {"Engaged", "Partially Engaged", "Needs Attention"}.

    Returns
    -------
    str – a single actionable teaching recommendation.
    """
    if not results:
        return "No data available to generate insights."

    total   = len(results)
    engaged = sum(1 for r in results if r["label"] == "Engaged")
    partial = sum(1 for r in results if r["label"] == "Partially Engaged")
    needs   = sum(1 for r in results if r["label"] == "Needs Attention")

    engaged_pct = engaged / total
    partial_pct = partial / total
    needs_pct   = needs   / total

    if needs_pct >= 0.5:
        return (
            "🔁 **Re-explain the topic from scratch.** More than half the class shows "
            "significant comprehension gaps. Use analogies, worked examples, or visual "
            "diagrams before proceeding."
        )
    if needs_pct >= 0.3:
        return (
            "⚠️ **Pause and address misconceptions.** A significant portion is struggling. "
            "Break the topic into smaller chunks and invite clarifying questions."
        )
    if partial_pct >= 0.5:
        return (
            "📖 **Provide concrete examples and practice problems.** Most students have "
            "partial understanding. Reinforce with real-world scenarios and peer discussion."
        )
    if partial_pct >= 0.3:
        return (
            "💡 **Supplement with targeted examples.** Several students need additional "
            "clarification. Consider a quick quiz or group activity."
        )
    if engaged_pct >= 0.75:
        return (
            "🚀 **Move forward to the next concept.** The class demonstrates strong "
            "understanding. Increase complexity or introduce an advanced application."
        )
    return (
        "✅ **Continue with current pace.** Engagement is reasonable. Monitor closely and "
        "check in with partially engaged students individually."
    )
