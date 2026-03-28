"""
teacher_view.py
---------------
ClassIQ Teacher Dashboard — rendered inside app.py.

Flow:
  1. Login screen  (teacher_id + password via core/teacher_auth.py)
  2. Session setup (topic, section)
  3. Live dashboard showing student responses, concept gaps, confusion alerts.

Performance:
  * generate_insight() and analyse_concept_gaps() are wrapped with st.cache_data
    so they are not recomputed on every Streamlit rerun.
  * Chart figures are closed immediately after rendering to free memory.
  * DB calls go through the cached public API in database/db.py.
"""

import io
import re
import random
import string
import datetime

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

from core.teacher_auth        import validate_teacher_login
from core.question_generator  import generate_question
from core.insight_engine      import generate_insight
from core.concept_gap_engine  import analyse_concept_gaps
from core.styles              import apply_global_styles
from database.db import (
    create_session, update_session_health,
    get_responses_for_session, get_all_sessions, get_trend_data,
)

# ── Plot theme constants ───────────────────────────────────────────────────────
ENGAGE_COLOR = {
    "Engaged":           "#34d399",
    "Partially Engaged": "#fbbf24",
    "Needs Attention":   "#f87171",
}
PLOT_BG    = "#0a0e1a"
PLOT_GRID  = "#1e293b"
PLOT_TEXT  = "#94a3b8"
PLOT_SPINE = "#1e293b"


# ── Cached analytics helpers ──────────────────────────────────────────────────

@st.cache_data(ttl=10, show_spinner=False, max_entries=64)
def _cached_insight(responses_key: str, scores_key: str, labels_key: str) -> str:
    """
    generate_insight accepts a list of response dicts.
    We can't hash dicts directly so we rebuild a minimal list from the
    frozen string keys passed in.  The ttl=10 means it re-runs at most
    once every 10 seconds, which is more than sufficient.
    """
    import json
    rows = json.loads(responses_key)
    return generate_insight(rows)


@st.cache_data(ttl=10, show_spinner=False, max_entries=64)
def _cached_gaps(texts_json: str, topic: str) -> dict:
    """Cached wrapper for analyse_concept_gaps."""
    import json
    texts = json.loads(texts_json)
    return analyse_concept_gaps(texts, topic)


# ── Chart helpers ─────────────────────────────────────────────────────────────

def _mpl_dark(fig, axes=None):
    fig.patch.set_facecolor(PLOT_BG)
    for ax in (axes or fig.get_axes()):
        ax.set_facecolor(PLOT_BG)
        ax.tick_params(colors=PLOT_TEXT, labelsize=9)
        ax.xaxis.label.set_color(PLOT_TEXT)
        ax.yaxis.label.set_color(PLOT_TEXT)
        ax.title.set_color("#e2e8f0")
        for sp in ax.spines.values():
            sp.set_color(PLOT_SPINE)
        ax.grid(color=PLOT_GRID, lw=.7, ls="--", alpha=.7)


def _bar_chart(df: pd.DataFrame, threshold: int) -> plt.Figure:
    n   = max(len(df), 1)
    fig, ax = plt.subplots(figsize=(9, max(3, n * 0.65)))
    _mpl_dark(fig)
    colors = [ENGAGE_COLOR.get(l, "#64748b") for l in df["Engagement"]]
    bars   = ax.barh(df["Name"], df["Score"], color=colors, height=.55, edgecolor="none")
    ax.barh(df["Name"], df["Score"], color=colors, height=.55, edgecolor="none", alpha=.18, linewidth=8)
    ax.axvline(threshold, color="#6366f1", lw=1.5, ls="--", label=f"Threshold ({threshold})", alpha=.8)
    ax.axvline(75, color="#34d399", lw=1, ls=":", alpha=.5, label="Engaged ≥ 75")
    ax.axvline(50, color="#fbbf24", lw=1, ls=":", alpha=.5, label="Partial ≥ 50")
    ax.set_xlim(0, 110)
    ax.set_xlabel("Engagement Score (0–100)", fontsize=9, color=PLOT_TEXT)
    ax.set_title("Student Engagement Scores", fontsize=12, fontweight="bold", pad=14)
    ax.legend(fontsize=8, framealpha=0, labelcolor=PLOT_TEXT)
    ax.spines[["top", "right"]].set_visible(False)
    for bar, score in zip(bars, df["Score"]):
        ax.text(bar.get_width() + 1.2, bar.get_y() + bar.get_height() / 2,
                f"{score:.1f}", va="center", fontsize=9, color="#e2e8f0", fontweight="600")
    plt.tight_layout()
    return fig


def _donut_chart(counts: dict) -> plt.Figure:
    labels = [k for k, v in counts.items() if v > 0]
    sizes  = [v for v in counts.values() if v > 0]
    if not sizes:
        # Return empty placeholder figure
        fig, ax = plt.subplots(figsize=(5, 4.8))
        _mpl_dark(fig)
        ax.text(0.5, 0.5, "No data", ha="center", va="center", color=PLOT_TEXT, fontsize=12)
        ax.axis("off")
        return fig
    colors = [ENGAGE_COLOR.get(l, "#64748b") for l in labels]
    fig, ax = plt.subplots(figsize=(5, 4.8))
    _mpl_dark(fig)
    wedges, _, pcts = ax.pie(
        sizes, labels=None, colors=colors, autopct="%1.0f%%",
        startangle=90, pctdistance=0.72,
        wedgeprops={"edgecolor": PLOT_BG, "linewidth": 3, "width": 0.55},
    )
    for p in pcts:
        p.set_fontsize(11); p.set_fontweight("bold"); p.set_color("#f0f6ff")
    ax.legend(wedges, labels, loc="lower center", fontsize=9, framealpha=0,
              labelcolor=PLOT_TEXT, ncol=1, bbox_to_anchor=(.5, -0.08))
    ax.set_title("Engagement Share", fontsize=12, fontweight="bold", pad=10)
    plt.tight_layout()
    return fig


def _trend_chart(trend_data: list, section: str, topic: str) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 3.4))
    _mpl_dark(fig)
    dates  = [d["date"][:10] for d in trend_data]
    scores = [d["health_score"] for d in trend_data]
    ax.fill_between(dates, scores, alpha=.12, color="#818cf8")
    ax.plot(dates, scores, marker="o", color="#818cf8", lw=2.5,
            markersize=8, markerfacecolor=PLOT_BG, markeredgewidth=2.5,
            markeredgecolor="#818cf8")
    ax.axhline(75, color="#34d399", ls="--", lw=1.2, alpha=.55, label="75% target")
    for x, y in zip(dates, scores):
        ax.annotate(f"{y:.0f}%", (x, y), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9, color="#a5b4fc", fontweight="600")
    ax.set_ylim(0, 108)
    ax.set_ylabel("Health Score (%)", fontsize=9)
    ax.set_title(f"Class Health Trend — {section} / {topic}", fontsize=11, fontweight="bold", pad=12)
    ax.legend(fontsize=8, framealpha=0, labelcolor=PLOT_TEXT)
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=28, ha="right", fontsize=8)
    plt.tight_layout()
    return fig


def _gen_code(length=6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length)).upper()


# ── Pandas styler helper (compatible with pandas ≥ 2.1 which deprecated applymap)
def _style_col(col: pd.Series, mapping: dict, default: str = "") -> list[str]:
    return [mapping.get(v, default) for v in col]


# ── Session state initialisation ──────────────────────────────────────────────
def _init_state():
    defaults = {
        "t_logged_in":    False,
        "t_name":         "",
        "t_session_id":   None,
        "t_session_code": "",
        "t_topic":        "",
        "t_difficulty":   "",
        "t_section":      "",
        "t_question":     "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
def render():
    """Entry point called from app.py."""
    _init_state()
    apply_global_styles()

    # ── Sidebar brand ──────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:.6rem 0 1rem;">
            <div style="font-size:2.2rem;">🎓</div>
            <div style="font-size:1.15rem;font-weight:800;
                        background:linear-gradient(90deg,#818cf8,#c084fc);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                ClassIQ
            </div>
            <div style="font-size:.65rem;color:#475569;letter-spacing:.12em;text-transform:uppercase;">
                Teacher Portal
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.t_logged_in:
            st.markdown(f"""
            <div style="padding:.5rem .8rem;background:rgba(99,102,241,0.1);
                        border:1px solid rgba(99,102,241,0.25);border-radius:10px;
                        margin-bottom:.8rem;font-size:.8rem;">
                👤 <strong style="color:#a5b4fc;">{st.session_state.t_name}</strong>
            </div>
            """, unsafe_allow_html=True)

        # ── Session setup form (only after login) ──────────────────────────────
        if st.session_state.t_logged_in:
            st.markdown("### 📋 Session Setup")
            section   = st.text_input("🏫 Section",  value="CS-A", key="sb_section")
            topic     = st.text_input("📖 Topic", value="Artificial Intelligence", key="sb_topic")
            difficulty = st.selectbox("⭐ Difficulty Level", ["Easy", "Medium", "Hard"], index=1, key="sb_difficulty")
            threshold = st.slider("📊 Threshold", 30, 90, 50, 5, key="sb_threshold",
                                  help="Reference line on the score chart")

            st.markdown("---")
            start_btn   = st.button("🚀  Start Session",     use_container_width=True, type="primary")
            refresh_btn = st.button("🔄  Refresh Dashboard",  use_container_width=True)  # noqa: F841
            if refresh_btn:
                from database.db import _cached_get_responses
                _cached_get_responses.clear()
            
            auto_refresh = st.checkbox("🟢 Live Auto-Refresh (5s)", value=True, help="Turn off to pause auto-refresh while reading or exporting.")
            st.session_state.t_auto_refresh = auto_refresh

            st.markdown("""
            <div style="margin-top:.8rem;padding:.65rem .85rem;
                        background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.18);
                        border-radius:10px;font-size:.74rem;color:#64748b;line-height:1.6;">
                ⚠️ <strong style="color:#a5b4fc;">Decision-support only.</strong><br>
                ClassIQ does <u>not</u> mark attendance.<hr style="margin:8px 0;opacity:0.3">
                🧠 Hybrid ML · Offline AI Engine<br>
                📄 Plagiarism Detection Enabled
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            if st.button("🚪  Home / Logout", use_container_width=True):
                # Using standard multipage app routing
                st.switch_page("app.py")
        else:
            start_btn = False
            threshold = 50

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero">
        <h1>ClassIQ</h1>
        <p>AI-Powered Classroom Engagement Intelligence System</p>
        <span class="badge">🤖 Hybrid ML · Core AI · Plagiarism Analytics</span>
    </div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 1 — LOGIN
    # ══════════════════════════════════════════════════════════════════════════
    if not st.session_state.t_logged_in:
        st.markdown('<div class="sec-label">🔐 &nbsp; Teacher Login</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="info-note" style="margin-bottom:1rem;">
            🔑 Enter your <strong>Teacher ID</strong> and password
            &nbsp;(format: <code>classiq@&lt;your_id&gt;</code>).<br>
            Demo: ID = <code>teacher</code> &nbsp;·&nbsp; Password = <code>classiq@teacher</code>
        </div>
        """, unsafe_allow_html=True)

        col_f, _, col_r = st.columns([2, 1, 2])
        with col_f:
            with st.form("teacher_login_form"):
                tid  = st.text_input("👤 Teacher ID", placeholder="e.g. ananya")
                pwd  = st.text_input("🔑 Password",   placeholder="classiq@ananya", type="password")
                sub  = st.form_submit_button("Login →", use_container_width=True, type="primary")

            if sub:
                if not tid.strip() or not pwd.strip():
                    st.error("⚠️ Please enter both Teacher ID and password.")
                else:
                    ok, name, msg = validate_teacher_login(tid.strip(), pwd.strip())
                    if ok:
                        st.session_state.t_logged_in = True
                        st.session_state.t_name      = name
                        st.rerun()
                    else:
                        st.error(msg)
        return  # don't render dashboard until logged in

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 2 — START SESSION
    # ══════════════════════════════════════════════════════════════════════════
    topic      = st.session_state.get("sb_topic",      "Artificial Intelligence")
    difficulty = st.session_state.get("sb_difficulty", "Medium")
    section    = st.session_state.get("sb_section",    "CS-A")
    threshold  = st.session_state.get("sb_threshold",  50)

    if start_btn:
        with st.spinner("Generating question…"):
            question = generate_question(topic, difficulty)
            code     = _gen_code()
            now      = datetime.datetime.now().isoformat()
            sid      = create_session(code, st.session_state.t_name,
                                      topic, section, question, now)
        st.session_state.t_session_id   = sid
        st.session_state.t_session_code = code
        st.session_state.t_topic        = topic
        st.session_state.t_difficulty   = difficulty
        st.session_state.t_section      = section
        st.session_state.t_question     = question
        st.success("✅ Session created! Share the code with your students.")

    # ══════════════════════════════════════════════════════════════════════════
    # SESSION CODE + QUESTION DISPLAY
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.t_session_id:
        code = st.session_state.t_session_code
        c1, c2 = st.columns([1, 2], gap="medium")
        with c1:
            st.markdown(f"""
            <div class="glass" style="text-align:center;padding:1.6rem 1rem;">
                <div style="font-size:.65rem;color:#6366f1;font-weight:700;
                            letter-spacing:.12em;text-transform:uppercase;margin-bottom:.6rem;">
                    Session Code
                </div>
                <div style="font-size:3rem;font-weight:900;color:#a5b4fc;
                            font-family:'JetBrains Mono',monospace;letter-spacing:.25em;line-height:1;">
                    {code}
                </div>
                <div style="font-size:.73rem;color:#475569;margin-top:.6rem;">
                    Share with students →<br>
                    <code style="color:#6366f1;">localhost:8501</code>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="glass" style="padding:1.4rem 1.6rem;">
                <div style="font-size:.65rem;color:#6366f1;font-weight:700;
                            letter-spacing:.12em;text-transform:uppercase;margin-bottom:.6rem;">
                    📝 Question for This Session
                </div>
                <div style="font-size:1rem;color:#a5b4fc;font-style:italic;line-height:1.75;">
                    {st.session_state.t_question}
                </div>
                <div style="font-size:.72rem;color:#475569;margin-top:.7rem;">
                    Topic: <strong style="color:#818cf8;">{st.session_state.t_topic}</strong>
                    &nbsp;·&nbsp; Difficulty: <strong style="color:#818cf8;">{st.session_state.t_difficulty}</strong>
                    &nbsp;·&nbsp; Section: <strong style="color:#818cf8;">{st.session_state.t_section}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── LIVE DASHBOARD ─────────────────────────────────────────────────────
        responses = get_responses_for_session(st.session_state.t_session_id)

        if responses:
            R        = responses
            engaged  = sum(1 for r in R if r["label"] == "Engaged")
            partial  = sum(1 for r in R if r["label"] == "Partially Engaged")
            needs    = sum(1 for r in R if r["label"] == "Needs Attention")
            highrisk = sum(1 for r in R if r["risk_label"] == "High")
            plagged  = sum(1 for r in R if r.get("plagiarism_score", 0.0) >= 0.7)
            avg_sc   = round(sum(r["score"] for r in R) / len(R), 1)  # noqa: F841
            health   = round(engaged / len(R) * 100, 1)

            # Only write health to DB when value actually changes
            _prev_health_key = f"_last_health_{st.session_state.t_session_id}"
            if st.session_state.get(_prev_health_key) != health:
                update_session_health(st.session_state.t_session_id, health)
                st.session_state[_prev_health_key] = health

            hc = "#34d399" if health >= 70 else "#fbbf24" if health >= 45 else "#f87171"
            plag_color = '#f87171' if plagged > 0 else '#94a3b8'
            plag_border = '#f8717133' if plagged > 0 else 'rgba(255,255,255,0.08)'
            st.markdown(f"""
            <style>
            .kpi-grid {{
                display: grid;
                grid-template-columns: repeat(6, 1fr);
                gap: 1rem;
                margin: 1.2rem 0 1.6rem;
            }}
            @media (max-width: 900px) {{
                .kpi-grid {{ grid-template-columns: repeat(3, 1fr); }}
            }}
            .kpi-card {{
                position: relative;
                background: rgba(255,255,255,0.035);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 18px;
                padding: 1.4rem 1rem 1.1rem;
                text-align: center;
                overflow: hidden;
                transition: transform .18s, box-shadow .18s;
                cursor: default;
            }}
            .kpi-card:hover {{
                transform: translateY(-4px);
                box-shadow: 0 12px 36px rgba(0,0,0,0.45);
            }}
            .kpi-card::before {{
                content: "";
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 3px;
                border-radius: 18px 18px 0 0;
            }}
            .kpi-green::before  {{ background: linear-gradient(90deg, #34d399, #10b981); }}
            .kpi-yellow::before {{ background: linear-gradient(90deg, #fbbf24, #f59e0b); }}
            .kpi-red::before    {{ background: linear-gradient(90deg, #f87171, #ef4444); }}
            .kpi-purple::before {{ background: linear-gradient(90deg, #a78bfa, #8b5cf6); }}
            .kpi-orange::before {{ background: linear-gradient(90deg, #fb923c, #f97316); }}
            .kpi-health::before {{ background: linear-gradient(90deg, {hc}, {hc}aa); }}
            .kpi-icon  {{ font-size: 1.5rem; margin-bottom: .4rem; line-height: 1; }}
            .kpi-value {{ font-size: 2.4rem; font-weight: 900; line-height: 1.1; letter-spacing: -0.02em; }}
            .kpi-label {{ font-size: .65rem; font-weight: 700; letter-spacing: .1em;
                          text-transform: uppercase; color: #64748b !important; margin-top: .45rem; }}
            </style>
            <div class="kpi-grid">
                <div class="kpi-card kpi-green">
                    <div class="kpi-icon">✅</div>
                    <div class="kpi-value" style="color:#34d399;text-shadow:0 0 20px rgba(52,211,153,0.4);">{engaged}</div>
                    <div class="kpi-label">Engaged</div>
                </div>
                <div class="kpi-card kpi-yellow">
                    <div class="kpi-icon">⚡</div>
                    <div class="kpi-value" style="color:#fbbf24;text-shadow:0 0 20px rgba(251,191,36,0.4);">{partial}</div>
                    <div class="kpi-label">Partial</div>
                </div>
                <div class="kpi-card kpi-red">
                    <div class="kpi-icon">🔴</div>
                    <div class="kpi-value" style="color:#f87171;text-shadow:0 0 20px rgba(248,113,113,0.4);">{needs}</div>
                    <div class="kpi-label">Needs Help</div>
                </div>
                <div class="kpi-card kpi-purple">
                    <div class="kpi-icon">⚠️</div>
                    <div class="kpi-value" style="color:#a78bfa;text-shadow:0 0 20px rgba(167,139,250,0.4);">{highrisk}</div>
                    <div class="kpi-label">High Risk</div>
                </div>
                <div class="kpi-card kpi-orange" style="border-color:{plag_border};">
                    <div class="kpi-icon">🤖</div>
                    <div class="kpi-value" style="color:{plag_color};text-shadow:0 0 20px {plag_color}55;">{plagged}</div>
                    <div class="kpi-label">Suspected AI</div>
                </div>
                <div class="kpi-card kpi-health">
                    <div class="kpi-icon">🏥</div>
                    <div class="kpi-value" style="color:{hc};text-shadow:0 0 20px {hc}66;">{health:.0f}%</div>
                    <div class="kpi-label">Class Health</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Charts ────────────────────────────────────────────────────────
            st.markdown('<div class="sec-label">📊 &nbsp; Visual Analytics</div>', unsafe_allow_html=True)
            df_vis = pd.DataFrame([{
                "Name": r["student_name"], "Score": r["score"], "Engagement": r["label"]
            } for r in R])

            c1, c2 = st.columns([3, 2], gap="medium")
            with c1:
                fb = _bar_chart(df_vis, threshold)
                st.pyplot(fb, use_container_width=True)
                plt.close(fb)
            with c2:
                fp = _donut_chart({"Engaged": engaged, "Partially Engaged": partial, "Needs Attention": needs})
                st.pyplot(fp, use_container_width=True)
                plt.close(fp)

            # ── Student Table ─────────────────────────────────────────────────
            st.markdown('<div class="sec-label">📋 &nbsp; Student Results</div>', unsafe_allow_html=True)
            def _clean(text: str) -> str:
                """Strip markdown bold/italic markers so table cells render cleanly."""
                return re.sub(r'[*_]{1,3}', '', text).strip()

            tbl = pd.DataFrame([{
                "Name":       r["student_name"],
                "Response":   (r["response_text"][:65] + "…") if len(r["response_text"]) > 65 else r["response_text"],
                "Score":      r["score"],
                "Engagement": r["label"],
                "Risk":       r["risk_label"],
                "AI%":        f"{r.get('plagiarism_score', 0.0) * 100:.0f}%",
                "Summary":    _clean(r["explanation"].split("\n")[0])[:90] if r["explanation"] else "",
            } for r in R])

            eng_style  = {"Engaged": "background-color:#14532d;color:#86efac;",
                          "Partially Engaged": "background-color:#422006;color:#fde68a;",
                          "Needs Attention":   "background-color:#450a0a;color:#fca5a5;"}
            risk_style = {"Low":    "background-color:#14532d;color:#86efac;",
                          "Medium": "background-color:#422006;color:#fde68a;",
                          "High":   "background-color:#450a0a;color:#fca5a5;"}

            def _ai_style(v: str) -> str:
                try:    p = int(v.strip("%"))
                except: p = 0
                if p >= 70:  return "background-color:#450a0a;color:#fca5a5;"
                if p >= 30:  return "background-color:#422006;color:#fde68a;"
                return "background-color:#14532d;color:#86efac;"

            styled = (tbl.style
                      .apply(_style_col, mapping=eng_style,  axis=0, subset=["Engagement"])
                      .apply(_style_col, mapping=risk_style, axis=0, subset=["Risk"])
                      .apply(lambda col: [_ai_style(v) for v in col], axis=0, subset=["AI%"])
                      .format({"Score": "{:.1f}"})
                      .set_properties(**{"font-size": "12px", "color": "#c9d6ea",
                                         "background-color": "#0a0e1a"}))
            st.dataframe(styled, use_container_width=True, height=280)

            # ── CSV Export ────────────────────────────────────────────────────
            full_df = pd.DataFrame([{
                "Name":        r["student_name"],
                "Email":       r["student_email"],
                "Response":    r["response_text"],
                "Score":       r["score"],
                "Engagement":  r["label"],
                "Risk Level":  r["risk_label"],
                "AI Prob %":   r.get("plagiarism_score", 0.0) * 100,
                "AI Flags":    r.get("plagiarism_flag", ""),
                "Explanation": r["explanation"],
                "Scaffolding": r["scaffolding"],
            } for r in R])
            buf = io.StringIO()
            full_df.to_csv(buf, index=False)
            st.download_button(
                "📥  Export Full Report (CSV)",
                data=buf.getvalue(),
                file_name=f"classiq_{code}_{st.session_state.t_topic}.csv",
                mime="text/csv",
                use_container_width=True,
            )

            # ── AI Teaching Recommendation (cached) ───────────────────────────
            st.markdown('<div class="sec-label">🧠 &nbsp; AI Teaching Recommendation</div>', unsafe_allow_html=True)
            import json
            # Build a minimal JSON-serialisable key for caching
            insight_rows = json.dumps([{
                "score": r["score"], "label": r["label"],
                "risk_label": r["risk_label"], "response_text": r["response_text"]
            } for r in R], sort_keys=True)
            insight_text = _cached_insight(insight_rows, "", "")
            st.markdown(f'<div class="insight-box">{insight_text}</div>', unsafe_allow_html=True)

            # ── Concept Gap Analysis (cached) ─────────────────────────────────
            st.markdown('<div class="sec-label">🔎 &nbsp; Concept Gap Analysis</div>', unsafe_allow_html=True)
            texts_json = json.dumps([r["response_text"] for r in R])
            gap_data   = _cached_gaps(texts_json, st.session_state.t_topic)

            col_gap, col_conf = st.columns([3, 2], gap="medium")
            with col_gap:
                st.markdown(f"""
                <div class="gap-card">
                    <div class="card-name">📌 Biggest Concept Gap:
                        <span style="color:#fbbf24;">{gap_data['biggest_gap']}</span>
                    </div>
                    <div class="card-sub" style="margin-top:.5rem;">{gap_data['gap_message']}</div>
                </div>""", unsafe_allow_html=True)

                if gap_data.get("missing_counts"):
                    st.markdown(
                        "<div style='font-size:.72rem;color:#64748b;font-weight:600;"
                        "letter-spacing:.06em;text-transform:uppercase;margin:.8rem 0 .4rem;'>"
                        "Keyword Coverage (students who mentioned it)</div>",
                        unsafe_allow_html=True,
                    )
                    total_stu = len(R)
                    kw_rows = []
                    for kw, missed in gap_data["missing_counts"].items():
                        hit = total_stu - missed
                        kw_rows.append({
                            "Keyword":    kw,
                            "Mentioned":  hit,
                            "Missing":    missed,
                            "Coverage %": f"{hit / total_stu * 100:.0f}%" if total_stu else "0%",
                        })
                    kw_df = pd.DataFrame(kw_rows)
                    st.dataframe(
                        kw_df.style.set_properties(
                            **{"font-size": "11px", "color": "#c9d6ea",
                               "background-color": "#0a0e1a"}
                        ),
                        use_container_width=True, height=200, hide_index=True,
                    )
                else:
                    st.markdown('<div class="info-note">No keyword data for this topic.</div>',
                                unsafe_allow_html=True)

            with col_conf:
                level_color = {"High": "#f87171", "Moderate": "#fbbf24", "Low": "#34d399"}
                lc = level_color.get(gap_data.get("confusion_level", "Low"), "#94a3b8")
                st.markdown(f"""
                <div class="confusion-card">
                    <div class="card-name">🧩 Confusion Level:
                        <span style="color:{lc};">{gap_data.get('confusion_level', 'Low')}</span>
                    </div>
                    <div class="card-sub" style="margin-top:.5rem;">{gap_data.get('confusion_alert', '')}</div>
                </div>""", unsafe_allow_html=True)

                conf_signals = ["don't know", "not sure", "confused", "no idea", "not clear"]
                conf_students = [
                    r for r in R
                    if any(sig in r["response_text"].lower() for sig in conf_signals)
                ]
                if conf_students:
                    st.markdown(
                        f"<div style='font-size:.72rem;color:#64748b;font-weight:600;"
                        f"letter-spacing:.06em;text-transform:uppercase;margin:.8rem 0 .4rem;'>"
                        f"Confused Students ({len(conf_students)})</div>",
                        unsafe_allow_html=True,
                    )
                    for r in conf_students:
                        st.markdown(f"""
                        <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.18);
                                    border-radius:8px;padding:.5rem .8rem;margin-bottom:.3rem;">
                            <span style="font-size:.82rem;font-weight:600;color:#fca5a5;">{r['student_name']}</span>
                        </div>""", unsafe_allow_html=True)

            # ── Alerts & Scaffolding ──────────────────────────────────────────
            st.markdown('<div class="sec-label">⚠️ &nbsp; Alerts &amp; Scaffolding Suggestions</div>',
                        unsafe_allow_html=True)
            c_plag, c_risk, c_scaff = st.columns(3, gap="small")

            with c_plag:
                plag_list = [r for r in R if r.get("plagiarism_score", 0.0) >= 0.7]
                st.markdown(f"**🤖 Suspected AI/Copy ({len(plag_list)})**")
                for r in plag_list:
                    st.markdown(f"""
                    <div class="risk-card" style="border-left:3px solid #ef4444;margin-bottom:.4rem;">
                        <div class="card-name">{r['student_name']}</div>
                        <div class="card-sub">AI Probability: {r.get('plagiarism_score', 0) * 100:.0f}%</div>
                    </div>""", unsafe_allow_html=True)
                if not plag_list:
                    st.markdown('<div class="info-note" style="font-size:.77rem;">✅ No AI/copy flags.</div>',
                                unsafe_allow_html=True)

            with c_risk:
                risk_list = [r for r in R if r["risk_label"] == "High"]
                st.markdown(f"**🔴 High Risk ({len(risk_list)})**")
                for r in risk_list:
                    st.markdown(f"""
                    <div class="risk-card" style="margin-bottom:.4rem;">
                        <div class="card-name">{r['student_name']}</div>
                        <div class="card-sub">Risk Score: {r['risk_prob']:.2f}</div>
                    </div>""", unsafe_allow_html=True)
                if not risk_list:
                    st.markdown('<div class="info-note" style="font-size:.77rem;">✅ No high-risk students.</div>',
                                unsafe_allow_html=True)

            with c_scaff:
                weak_list = [r for r in R if r["label"] == "Needs Attention"]
                st.markdown(f"**🔧 Scaffold Required ({len(weak_list)})**")
                if weak_list:
                    st.markdown(
                        "<div style='font-size:.77rem;color:#a78bfa;margin-bottom:.4rem;'>"
                        "➡️ Ask each student to explain the concept step-by-step.</div>",
                        unsafe_allow_html=True,
                    )
                for r in weak_list:
                    scaffold_text = r.get("scaffolding", "")
                    st.markdown(f"""
                    <div class="scaffold-card" style="margin-bottom:.4rem;padding:.6rem .8rem;">
                        <div class="card-name">{r['student_name']}</div>
                        {f'<div class="card-sub">{scaffold_text}</div>' if scaffold_text else ''}
                    </div>""", unsafe_allow_html=True)
                if not weak_list:
                    st.markdown('<div class="info-note" style="font-size:.77rem;">✅ All students engaged.</div>',
                                unsafe_allow_html=True)

            # ── Students Needing Attention ──────────────────────────────────
            st.markdown(
                '<div class="sec-label">🎯 &nbsp; Students Needing Attention</div>',
                unsafe_allow_html=True,
            )
            needs_attention = [r for r in R if r["label"] != "Engaged"]
            if needs_attention:
                # Sort: Needs Attention first, then Partially Engaged; within each group by score asc
                needs_attention.sort(key=lambda r: (
                    0 if r["label"] == "Needs Attention" else 1,
                    r["score"]
                ))
                na_cols = st.columns(min(len(needs_attention), 3), gap="small")
                for idx, r in enumerate(needs_attention):
                    col = na_cols[idx % 3]
                    is_needs = r["label"] == "Needs Attention"
                    border_color = "#f87171" if is_needs else "#fbbf24"
                    bg_color     = "rgba(248,113,113,0.05)" if is_needs else "rgba(251,191,36,0.05)"
                    score_color  = "#f87171" if is_needs else "#fbbf24"
                    label_ico    = "🔴" if is_needs else "⚡"
                    with col:
                        scaffold_snippet = ""
                        if r.get("scaffolding"):
                            sc_text = r["scaffolding"][:100] + ("…" if len(r["scaffolding"]) > 100 else "")
                            scaffold_snippet = f'<div style="font-size:.77rem;color:#a78bfa;margin-top:.5rem;">💡 {sc_text}</div>'
                        st.markdown(f"""
                        <div style="background:{bg_color};border:1px solid {border_color}40;
                                    border-left:3px solid {border_color};border-radius:12px;
                                    padding:1rem 1.1rem;margin-bottom:.6rem;">
                            <div style="font-size:.82rem;font-weight:700;color:#e2e8f0;">{label_ico} {r['student_name']}</div>
                            <div style="font-size:.75rem;color:#94a3b8;margin-top:.2rem;">{r['student_email']}</div>
                            <div style="font-size:1.5rem;font-weight:800;color:{score_color};margin:.4rem 0 .1rem;">
                                {r['score']:.1f}<span style="font-size:.85rem;color:#475569;"> / 100</span>
                            </div>
                            <div style="font-size:.75rem;color:#64748b;">{r['label']} · Risk: {r['risk_label']}</div>
                            {scaffold_snippet}
                        </div>""", unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="info-note" style="text-align:center;">'
                    '🎉 All students are engaged! Great session.</div>',
                    unsafe_allow_html=True,
                )

            # ── Per-student feedback expander ─────────────────────────────────
            with st.expander("💬  Individual Student Details & Feedback", expanded=False):
                for r in R:
                    ico = "✅" if r["label"] == "Engaged" else "⚡" if r["label"] == "Partially Engaged" else "🔴"
                    plag_warn = (
                        f"&nbsp;&nbsp;&nbsp; *(⚠️ AI Probability: {r.get('plagiarism_score', 0) * 100:.0f}%)*"
                        if r.get("plagiarism_score", 0) > 0.6 else ""
                    )
                    st.markdown(f"**{ico} {r['student_name']} ({r['student_email']})** {plag_warn}")
                    st.markdown(f"<span style='font-size:.85rem;'>{r['feedback']}</span>", unsafe_allow_html=True)
                    st.markdown("---")

            # ── Trend ─────────────────────────────────────────────────────────
            st.markdown('<div class="sec-label">📉 &nbsp; Engagement Trend</div>', unsafe_allow_html=True)
            trend = get_trend_data(st.session_state.t_section, st.session_state.t_topic)
            if len(trend) >= 2:
                ft = _trend_chart(trend, st.session_state.t_section, st.session_state.t_topic)
                st.pyplot(ft, use_container_width=True)
                plt.close(ft)
            else:
                st.markdown('<div class="info-note">📊 Run 2+ sessions for the same section &amp; topic to see the trend chart.</div>',
                            unsafe_allow_html=True)
                            
            if st.session_state.get('t_auto_refresh', True):
                import time
                time.sleep(5)
                from database.db import _cached_get_responses
                _cached_get_responses.clear()
                try:
                    st.rerun()
                except AttributeError:
                    st.experimental_rerun()

        else:
            st.markdown("""
            <div class="info-note" style="text-align:center;padding:2.5rem 1rem;margin-top:1rem;">
                ⏳ <strong>Waiting for student responses…</strong><br>
                <span style="font-size:.82rem;color:#475569;margin-top:.4rem;display:block;">
                    Direct students to open<br>
                    <code style="color:#818cf8;">localhost:8501</code>
                    and enter code
                    <strong style="color:#a5b4fc;letter-spacing:.12em;">{}</strong>
                </span>
            </div>
            """.format(code), unsafe_allow_html=True)
            import time
            time.sleep(3)
            from database.db import _cached_get_responses
            _cached_get_responses.clear() # purge cache explicitly to fetch latest
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()

    # ── SESSION HISTORY ────────────────────────────────────────────────────────
    st.markdown('<div class="sec-label">🗂️ &nbsp; Session History</div>', unsafe_allow_html=True)
    history = get_all_sessions()
    if history:
        hdf = pd.DataFrame(history)
        available = [c for c in ["id", "code", "teacher", "section", "topic", "timestamp", "health_score"]
                     if c in hdf.columns]
        hdf = hdf[available]
        rename_map = {"id": "ID", "code": "Code", "teacher": "Teacher", "section": "Section",
                      "topic": "Topic", "timestamp": "Date", "health_score": "Health (%)"}
        hdf = hdf.rename(columns={k: v for k, v in rename_map.items() if k in hdf.columns})
        if "Date" in hdf.columns:
            hdf["Date"] = hdf["Date"].str[:19].str.replace("T", " ")
        if "Health (%)" in hdf.columns:
            hdf["Health (%)"] = hdf["Health (%)"].round(1)
        st.dataframe(
            hdf.style.set_properties(**{"font-size": "12px", "color": "#c9d6ea",
                                        "background-color": "#0a0e1a"}),
            use_container_width=True, height=200,
        )
    else:
        st.markdown('<div class="info-note">No sessions yet — start your first session above.</div>',
                    unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;color:#334155;font-size:.74rem;letter-spacing:.04em;">
        ClassIQ v3.1 &nbsp;·&nbsp; Hybrid AI Engagement Intelligence &nbsp;·&nbsp;
        <span style="color:#4f46e5;">Decision-support only — does not mark attendance</span>
    </div>
    """, unsafe_allow_html=True)
