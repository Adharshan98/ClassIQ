"""
core/risk_engine.py
-------------------
Lightweight probabilistic risk engine.
Estimates the likelihood that a student needs immediate teacher intervention.

Signals:
  Response very short   → weight 0.35
  No topic keywords     → weight 0.35
  Confusion phrases     → weight 0.30 (capped per phrase count)
"""

from core.symbolic_engine import TOPIC_KEYWORDS, CONFUSION_PHRASES


def assess_risk(response: str, topic: str) -> tuple[float, str]:
    """
    Compute risk probability for a student response.

    Returns
    -------
    (risk_probability: float 0–1, risk_label: str ∈ {Low, Medium, High})
    """
    text       = response.lower().strip()
    word_count = len(text.split())

    # Signal 1: response length
    if word_count < 5:
        length_risk = 0.35
    elif word_count < 15:
        length_risk = 0.18
    else:
        length_risk = 0.0

    # Signal 2: keyword absence
    topic_key   = topic.lower().strip()
    keywords    = TOPIC_KEYWORDS.get(topic_key, TOPIC_KEYWORDS["default"])
    matched     = [kw for kw in keywords if kw in text]
    keyword_risk = 0.35 if not matched else (0.15 if len(matched) < 2 else 0.0)

    # Signal 3: confusion phrases
    conf_count   = sum(1 for ph in CONFUSION_PHRASES if ph in text)
    conf_risk    = min(conf_count * 0.10, 0.30)

    # Aggregate
    risk_prob = round(min(1.0, length_risk + keyword_risk + conf_risk), 3)

    if   risk_prob >= 0.65: label = "High"
    elif risk_prob >= 0.35: label = "Medium"
    else:                   label = "Low"

    return risk_prob, label
