"""
core/hybrid_engine.py
---------------------
Combines ML (Logistic Regression + Naive Bayes) scoring with the symbolic
rule engine to produce a final engagement score and label.

Score breakdown:
  ML component       : 0–70  (best model probability × 70)
  Symbolic component : 0–30  (dynamic rule-based adjustment, properly bounded)
  Total              : 0–100

Engagement labels:
  ≥ 75  → Engaged
  50–74 → Partially Engaged
  < 50  → Needs Attention

Performance notes:
  * Models are loaded ONCE per Streamlit server process via @st.cache_resource.
  * Response evaluation results are cached with @st.cache_data so that the
    same (response, topic) pair is never scored twice.
"""

import pickle
import os

import streamlit as st

from core.symbolic_engine import score_response

# ── Paths ─────────────────────────────────────────────────────────────────────
_BASE      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_DIR = os.path.join(_BASE, "model")
_LR_PATH   = os.path.join(_MODEL_DIR, "ml_model.pkl")
_NB_PATH   = os.path.join(_MODEL_DIR, "nb_model.pkl")
_VEC_PATH  = os.path.join(_MODEL_DIR, "vectorizer.pkl")


# ── Model loading — cached across ALL Streamlit reruns and sessions ───────────
@st.cache_resource(show_spinner=False)
def _load_models() -> tuple:
    """
    Load and cache the ML models into Streamlit's resource cache.
    Called once on first use; result persists for the life of the server.
    Returns (lr_model, nb_model, vectorizer).
    """
    with open(_LR_PATH,  "rb") as f: lr_model   = pickle.load(f)
    with open(_NB_PATH,  "rb") as f: nb_model   = pickle.load(f)
    with open(_VEC_PATH, "rb") as f: vectorizer = pickle.load(f)
    return lr_model, nb_model, vectorizer


# ── Per-response ML score — cached so identical inputs are never re-scored ────
@st.cache_data(show_spinner=False, max_entries=512)
def _get_ml_score(response: str) -> tuple[float, str]:
    """
    Vectorise the response and return (ml_score 0-70, model_used).
    Picks whichever of LR / NB returns the higher engaged-class probability.
    Result is cached by (response,) key.
    """
    lr_model, nb_model, vectorizer = _load_models()

    vec     = vectorizer.transform([response])
    lr_prob = lr_model.predict_proba(vec)[0][1]
    nb_prob = nb_model.predict_proba(vec)[0][1]

    if lr_prob >= nb_prob:
        return round(lr_prob * 70, 2), "Logistic Regression"
    return round(nb_prob * 70, 2), "Naive Bayes"


def _classify(score: float) -> str:
    if score >= 75: return "Engaged"
    if score >= 50: return "Partially Engaged"
    return "Needs Attention"


# ── Full evaluation — cached per (response, topic) ────────────────────────────
@st.cache_data(show_spinner=False, max_entries=512)
def evaluate_response(response: str, topic: str) -> tuple[float, str, list[str]]:
    """
    Evaluate a student response using the hybrid AI engine.
    Cached: same (response, topic) pair will never be recomputed.

    Symbolic score fix:
      score_response() returns raw_sym in [-15, 30].
      We normalise it to [0, 30] by a proper proportional rescale:
        sym_score = (raw_sym + 15) / 45 * 30
      This means:
        -15 → 0/30 (worst)
          0 → 10/30 (neutral)
        +30 → 30/30 (perfect)
      This prevents the score from being artificially pinned to 30.

    Returns
    -------
    (final_score, engagement_label, explanation_list)
    """
    explanation: list[str] = []

    # ML component (0–70)
    ml_score, model_used = _get_ml_score(response)
    explanation.append(f"🤖 ML Score: {ml_score:.1f}/70 (via {model_used}).")

    # Symbolic component — fix: proper proportional rescale from [-15,30] → [0,30]
    raw_sym, sym_exp = score_response(response, topic)
    # Map [-15, 30] → [0, 30]:  (raw + 15) / 45 * 30
    sym_score = round(max(0.0, min(30.0, (raw_sym + 15) / 45.0 * 30.0)), 2)
    explanation.extend(sym_exp)
    explanation.append(f"📏 Symbolic Score: {sym_score:.1f}/30.")

    # Final total (0–100)
    final = round(min(100.0, ml_score + sym_score), 2)
    label = _classify(final)
    explanation.append(f"🎯 Final: {final:.1f}/100 → {label}.")

    return final, label, explanation
