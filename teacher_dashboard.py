"""
teacher_dashboard.py
--------------------
ClassIQ — AI-Powered Classroom Engagement Intelligence System
Premium dark-mode Streamlit dashboard.

Run:  streamlit run teacher_dashboard.py
"""

import os, sys, io, datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.question_generator import generate_question
from core.session_manager import run_session
from core.insight_engine import generate_insight
from database.db import init_db, save_session, get_all_sessions, get_trend_data

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClassIQ | Engagement Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — Dark Glassmorphism Theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── root reset ── */
*, html, body { font-family: 'Inter', sans-serif !important; }

/* ── full-page dark gradient ── */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1528 40%, #111c35 70%, #0a1220 100%) !important;
    min-height: 100vh;
}
[data-testid="stHeader"]              { background: transparent !important; }
[data-testid="stSidebar"]             { background: rgba(255,255,255,0.03) !important;
                                        border-right: 1px solid rgba(255,255,255,0.07) !important;
                                        backdrop-filter: blur(20px); }
[data-testid="stSidebar"] * , [data-testid="stSidebar"] label { color: #c9d6ea !important; }
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px;}
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2563eb44; border-radius: 99px; }

/* ── text defaults ── */
p, span, div, li, td, th, label { color: #c9d6ea; }
h1,h2,h3,h4,h5,h6 { color: #f0f6ff !important; }

/* ── stMetric override ── */
[data-testid="stMetricValue"]  { color: #60a5fa !important; font-weight: 700 !important; font-size: 2rem !important; }
[data-testid="stMetricLabel"]  { color: #94a3b8 !important; font-size: 0.78rem !important; text-transform: uppercase; letter-spacing: .05em; }

/* ── inputs / selects ── */
.stSelectbox > div > div, .stTextInput > div > div > input,
.stSlider > div { background: rgba(255,255,255,0.05) !important;
                  border: 1px solid rgba(255,255,255,0.10) !important;
                  border-radius: 10px !important; color: #f0f6ff !important; }
.stSelectbox label, .stTextInput label, .stSlider label { color: #94a3b8 !important; font-size: .82rem !important; font-weight: 600 !important; letter-spacing: .04em; }

/* ── primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: .95rem !important; letter-spacing: .03em !important;
    padding: .7rem 1.2rem !important;
    box-shadow: 0 4px 24px rgba(99,102,241,.40) !important;
    transition: transform .15s, box-shadow .15s !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(99,102,241,.55) !important;
}
.stButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: #c9d6ea !important; border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important; font-weight: 600 !important;
    transition: background .15s !important;
}
.stButton > button:hover { background: rgba(255,255,255,0.10) !important; }

/* ── download button ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    box-shadow: 0 4px 20px rgba(16,185,129,.30) !important;
}

/* ── dataframe ── */
[data-testid="stDataFrame"] { border-radius: 14px !important; overflow: hidden; }
.stDataFrame * { font-size: 12.5px !important; }

/* ── expander ── */
.streamlit-expanderHeader { color: #94a3b8 !important; font-weight: 600 !important; font-size: .88rem !important; }
details { border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 12px !important; background: rgba(255,255,255,0.03) !important; padding: .4rem; }

/* ── info / success / warning boxes ── */
.stAlert { border-radius: 12px !important; }

/* ── divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; }


/* ══════════════ CUSTOM COMPONENTS ══════════════ */

/* ── hero banner ── */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 20px;
    padding: 2.4rem 3rem;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.6rem;
    box-shadow: 0 8px 40px rgba(99,102,241,0.18);
}
.hero::before {
    content: "";
    position: absolute; top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: "";
    position: absolute; bottom: -40px; left: 20%;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(124,58,237,0.20) 0%, transparent 70%);
    border-radius: 50%;
}
.hero h1 {
    font-size: 2.8rem !important; font-weight: 800 !important;
    background: linear-gradient(90deg, #818cf8, #c084fc, #60a5fa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0 !important; line-height: 1.15 !important;
}
.hero p { margin: .5rem 0 0 !important; color: #94a3b8 !important; font-size: 1.0rem !important; }
.hero .badge {
    display: inline-block; margin-top: .9rem;
    background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.35);
    color: #a5b4fc !important; border-radius: 20px;
    padding: .25rem .85rem; font-size: .75rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase;
}

/* ── section label ── */
.sec-label {
    display: flex; align-items: center; gap: .6rem;
    font-size: .72rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: #6366f1 !important;
    margin: 1.8rem 0 .9rem;
}
.sec-label::after {
    content: ""; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(99,102,241,0.4), transparent);
}

/* ── glass card ── */
.glass {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    backdrop-filter: blur(12px);
    margin-bottom: .8rem;
}

/* ── stat cards ── */
.stat-grid { display: flex; gap: .85rem; flex-wrap: wrap; margin-bottom: .5rem; }
.stat-card {
    flex: 1 1 130px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: transform .15s, box-shadow .15s;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 8px 28px rgba(0,0,0,0.4); }
.stat-card .sv { font-size: 2.1rem; font-weight: 800; line-height: 1; }
.stat-card .sl { font-size: .68rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: #64748b !important; margin-top: .35rem; }

.sv-green  { color: #34d399 !important; }
.sv-yellow { color: #fbbf24 !important; }
.sv-red    { color: #f87171 !important; }
.sv-purple { color: #a78bfa !important; }
.sv-blue   { color: #60a5fa !important; }

/* ── engagement pill ── */
.pill {
    display: inline-block; border-radius: 20px;
    padding: .22rem .8rem; font-size: .72rem; font-weight: 700; letter-spacing: .04em;
}
.pill-g  { background: rgba(52,211,153,.15); color: #34d399 !important; border: 1px solid rgba(52,211,153,.3); }
.pill-y  { background: rgba(251,191,36,.12); color: #fbbf24 !important; border: 1px solid rgba(251,191,36,.3); }
.pill-r  { background: rgba(248,113,113,.12); color: #f87171 !important; border: 1px solid rgba(248,113,113,.3); }

/* ── risk badge ── */
.rbadge { display:inline-block; border-radius:6px; padding:.18rem .6rem; font-size:.7rem; font-weight:700; }
.rbadge-low  { background:rgba(52,211,153,.12); color:#34d399 !important; }
.rbadge-mid  { background:rgba(251,191,36,.12); color:#fbbf24 !important; }
.rbadge-high { background:rgba(248,113,113,.12); color:#f87171 !important; }

/* ── insight box ── */
.insight-box {
    background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(124,58,237,0.06));
    border: 1px solid rgba(99,102,241,0.25);
    border-left: 4px solid #6366f1;
    border-radius: 14px;
    padding: 1.2rem 1.6rem;
    font-size: .9rem;
    line-height: 1.7;
    color: #c9d6ea !important;
}

/* ── risk / scaffold card ── */
.risk-card {
    background: rgba(248,113,113,0.05);
    border: 1px solid rgba(248,113,113,0.15);
    border-left: 3px solid #f87171;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: .6rem;
}
.scaffold-card {
    background: rgba(99,102,241,0.05);
    border: 1px solid rgba(99,102,241,0.18);
    border-left: 3px solid #818cf8;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: .6rem;
}
.card-name { font-weight: 700; color: #e2e8f0 !important; font-size: .9rem; }
.card-sub  { font-size: .8rem; color: #94a3b8 !important; margin-top: .3rem; line-height: 1.5; }

/* ── info note ── */
.info-note {
    background: rgba(96,165,250,0.06); border: 1px solid rgba(96,165,250,0.2);
    border-radius: 10px; padding: .7rem 1rem;
    font-size: .82rem; color: #93c5fd !important;
}

/* ── question block ── */
.q-block {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 1rem;
    font-style: italic;
    color: #a5b4fc !important;
    font-size: .95rem;
}

/* ── session pill ── */
.sess-meta { font-size: .75rem; color: #64748b !important; font-weight: 500; }

/* ── matplotlib plot bg ── */
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
ENGAGE_COLOR = {"Engaged": "#34d399", "Partially Engaged": "#fbbf24", "Needs Attention": "#f87171"}
RISK_EMOJI   = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}

PLOT_BG    = "#0d1528"
PLOT_GRID  = "#1e293b"
PLOT_TEXT  = "#94a3b8"
PLOT_SPINE = "#1e293b"

def _mpl_dark(fig, ax_list=None):
    """Apply dark theme to any matplotlib figure."""
    fig.patch.set_facecolor(PLOT_BG)
    axes = ax_list if ax_list else fig.get_axes()
    for ax in axes:
        ax.set_facecolor(PLOT_BG)
        ax.tick_params(colors=PLOT_TEXT, labelsize=9)
        ax.xaxis.label.set_color(PLOT_TEXT)
        ax.yaxis.label.set_color(PLOT_TEXT)
        ax.title.set_color("#e2e8f0")
        for spine in ax.spines.values():
            spine.set_color(PLOT_SPINE)
        ax.grid(color=PLOT_GRID, linewidth=.7, linestyle="--", alpha=.7)


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────────────────────────────────────
def _bar_chart(df: pd.DataFrame, threshold: int) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    _mpl_dark(fig)

    scores = df["Score"].values
    names  = df["Name"].values
    labels = df["Engagement"].values
    colors = [ENGAGE_COLOR.get(l, "#64748b") for l in labels]

    bars = ax.barh(names, scores, color=colors, height=.55,
                   edgecolor="none")
    # glow effect — duplicate with alpha
    ax.barh(names, scores, color=colors, height=.55, edgecolor="none", alpha=.18, linewidth=8)

    ax.axvline(threshold, color="#6366f1", lw=1.5, ls="--", label=f"Threshold ({threshold})", alpha=.8)
    ax.axvline(75, color="#34d399", lw=1, ls=":", alpha=.5, label="Engaged ≥ 75")
    ax.axvline(50, color="#fbbf24", lw=1, ls=":", alpha=.5, label="Partial ≥ 50")

    ax.set_xlim(0, 108)
    ax.set_xlabel("Engagement Score  (0 – 100)", fontsize=9, color=PLOT_TEXT)
    ax.set_title("Student Engagement Scores", fontsize=12, fontweight="bold", pad=14)
    ax.legend(fontsize=8, framealpha=0, labelcolor=PLOT_TEXT)
    ax.spines[["top","right"]].set_visible(False)

    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 1.2, bar.get_y() + bar.get_height() / 2,
                f"{score:.1f}", va="center", fontsize=9, color="#e2e8f0", fontweight="600")

    plt.tight_layout()
    return fig


def _donut_chart(counts: dict) -> plt.Figure:
    labels = [k for k, v in counts.items() if v > 0]
    sizes  = [v for v in counts.values() if v > 0]
    colors = [ENGAGE_COLOR.get(l, "#64748b") for l in labels]

    fig, ax = plt.subplots(figsize=(5, 4.8))
    _mpl_dark(fig)

    wedges, texts, pcts = ax.pie(
        sizes, labels=None, colors=colors, autopct="%1.0f%%",
        startangle=90, pctdistance=0.72,
        wedgeprops={"edgecolor": PLOT_BG, "linewidth": 3, "width": 0.55},
    )
    for p in pcts:
        p.set_fontsize(11); p.set_fontweight("bold"); p.set_color("#f0f6ff")

    ax.legend(wedges, labels, loc="lower center", fontsize=9,
              framealpha=0, labelcolor=PLOT_TEXT, ncol=1,
              bbox_to_anchor=(.5, -0.08))
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
                    xytext=(0, 10), ha="center", fontsize=9,
                    color="#a5b4fc", fontweight="600")

    ax.set_ylim(0, 108)
    ax.set_ylabel("Health Score (%)", fontsize=9)
    ax.set_title(f"Class Health Trend — {section}  /  {topic}", fontsize=11, fontweight="bold", pad=12)
    ax.legend(fontsize=8, framealpha=0, labelcolor=PLOT_TEXT)
    ax.spines[["top","right"]].set_visible(False)
    plt.xticks(rotation=28, ha="right", fontsize=8)
    plt.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:.6rem 0 1.2rem;">
        <div style="font-size:2.6rem; margin-bottom:.3rem;">🎓</div>
        <div style="font-size:1.3rem; font-weight:800; background:linear-gradient(90deg,#818cf8,#c084fc);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;">ClassIQ</div>
        <div style="font-size:.7rem; color:#475569; letter-spacing:.1em; text-transform:uppercase; margin-top:.2rem;">
            Engagement Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Session Setup")
    teacher_name = st.text_input("👤  Teacher Name",   value="Dr. Ananya Sharma")
    section      = st.text_input("🏫  Section / Class", value="CS-A")
    topic        = st.text_input("📖  Topic", value="Artificial Intelligence")
    difficulty   = st.selectbox("⭐ Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
    threshold = st.slider("📊  Engagement Threshold", 30, 90, 50, 5,
                          help="Reference line shown on the score chart")

    st.markdown("---")
    run_btn = st.button("🚀  Analyse Class", use_container_width=True, type="primary")

    st.markdown("""
    <div style="margin-top:1.4rem; padding:.75rem 1rem;
                background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2);
                border-radius:10px; font-size:.77rem; color:#64748b; line-height:1.6;">
        ⚠️ <strong style="color:#a5b4fc;">Decision-support only.</strong><br>
        ClassIQ does <u>not</u> mark attendance.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
if "results"  not in st.session_state: st.session_state.results  = None
if "meta"     not in st.session_state: st.session_state.meta     = {}


# ─────────────────────────────────────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>ClassIQ</h1>
    <p>AI-Powered Classroom Engagement Intelligence System</p>
    <span class="badge">🤖 Hybrid ML · Symbolic AI · Real-time Analytics</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RUN SESSION
# ─────────────────────────────────────────────────────────────────────────────
if run_btn:
    with st.spinner("Running hybrid AI pipeline…"):
        results  = run_session(topic, threshold)
        question = generate_question(topic, difficulty)
        now      = datetime.datetime.now().isoformat()

        engaged_n = sum(1 for r in results if r["label"] == "Engaged")
        health    = round(engaged_n / len(results) * 100, 1)

        sid = save_session(teacher_name, section, topic, question, now, health, results)
        st.session_state.results = results
        st.session_state.meta    = dict(teacher=teacher_name, section=section,
                                        topic=topic, difficulty=difficulty, question=question,
                                        date=now, health=health)

    st.toast(f"✅ Session #{sid} saved — {health:.0f}% class health", icon="🎉")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.results:
    R    = st.session_state.results
    meta = st.session_state.meta

    # ── session question ────────────────────────────────────────────────────
    st.markdown(f'<div class="q-block">📝 &nbsp; {meta["question"]}</div>', unsafe_allow_html=True)

    # ── KPI grid ────────────────────────────────────────────────────────────
    engaged  = sum(1 for r in R if r["label"] == "Engaged")
    partial  = sum(1 for r in R if r["label"] == "Partially Engaged")
    needs    = sum(1 for r in R if r["label"] == "Needs Attention")
    highrisk = sum(1 for r in R if r["risk_label"] == "High")
    avg_sc   = round(sum(r["score"] for r in R) / len(R), 1)
    health   = meta["health"]

    st.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="sv sv-green">{engaged}</div>
            <div class="sl">✅ Engaged</div>
        </div>
        <div class="stat-card">
            <div class="sv sv-yellow">{partial}</div>
            <div class="sl">⚡ Partial</div>
        </div>
        <div class="stat-card">
            <div class="sv sv-red">{needs}</div>
            <div class="sl">🔴 Needs Help</div>
        </div>
        <div class="stat-card">
            <div class="sv sv-purple">{highrisk}</div>
            <div class="sl">⚠️ High Risk</div>
        </div>
        <div class="stat-card">
            <div class="sv sv-blue">{avg_sc}</div>
            <div class="sl">📈 Avg Score</div>
        </div>
        <div class="stat-card">
            <div class="sv" style="color:{'#34d399' if health>=70 else '#fbbf24' if health>=45 else '#f87171'} !important;">{health:.0f}%</div>
            <div class="sl">🏥 Class Health</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── charts ──────────────────────────────────────────────────────────────
    st.markdown('<div class="sec-label">📊 &nbsp; Visual Analytics</div>', unsafe_allow_html=True)

    df_vis = pd.DataFrame([{"Name": r["name"], "Score": r["score"],
                             "Engagement": r["label"]} for r in R])

    col_bar, col_pie = st.columns([3, 2], gap="medium")
    with col_bar:
        fig_b = _bar_chart(df_vis, threshold)
        st.pyplot(fig_b, use_container_width=True)
        plt.close(fig_b)
    with col_pie:
        fig_p = _donut_chart({"Engaged": engaged, "Partially Engaged": partial,
                               "Needs Attention": needs})
        st.pyplot(fig_p, use_container_width=True)
        plt.close(fig_p)

    # ── student table ────────────────────────────────────────────────────────
    st.markdown('<div class="sec-label">📋 &nbsp; Student Results</div>', unsafe_allow_html=True)

    tbl = pd.DataFrame([{
        "Roll":       r["roll"],
        "Name":       r["name"],
        "Response":   r["response"][:72] + "…" if len(r["response"]) > 72 else r["response"],
        "Score":      r["score"],
        "Engagement": r["label"],
        "Risk":       r["risk_label"],
        "Explanation":r["explanation"][:110] + "…",
        "Feedback":   r["feedback"],
    } for r in R])

    def _ce(v):
        m = {"Engaged":"background-color:#14532d;color:#86efac;",
             "Partially Engaged":"background-color:#422006;color:#fde68a;",
             "Needs Attention":"background-color:#450a0a;color:#fca5a5;"}
        return m.get(v,"")
    def _cr(v):
        m = {"Low":"background-color:#14532d;color:#86efac;",
             "Medium":"background-color:#422006;color:#fde68a;",
             "High":"background-color:#450a0a;color:#fca5a5;"}
        return m.get(v,"")

    styled = (tbl.style
              .applymap(_ce, subset=["Engagement"])
              .applymap(_cr, subset=["Risk"])
              .format({"Score": "{:.1f}"})
              .set_properties(**{"font-size":"12px","color":"#c9d6ea",
                                 "background-color":"#0d1528"}))
    st.dataframe(styled, use_container_width=True, height=300)

    # ── CSV export ───────────────────────────────────────────────────────────
    full_df = pd.DataFrame([{
        "Roll No": r["roll"], "Name": r["name"], "Response": r["response"],
        "Score": r["score"],  "Engagement": r["label"],
        "Risk Probability": r["risk_prob"], "Risk Level": r["risk_label"],
        "Explanation": r["explanation"], "Feedback": r["feedback"],
        "Scaffolding Question": r["scaffolding"],
    } for r in R])
    buf = io.StringIO(); full_df.to_csv(buf, index=False)
    st.download_button("📥  Export Full Report as CSV", data=buf.getvalue(),
                       file_name=f"classiq_{meta['section']}_{meta['topic']}_{meta['date'][:10]}.csv",
                       mime="text/csv", use_container_width=True)

    # ── AI recommendation ────────────────────────────────────────────────────
    st.markdown('<div class="sec-label">🧠 &nbsp; AI Teaching Recommendation</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-box">{generate_insight(R)}</div>', unsafe_allow_html=True)

    # ── risk + scaffolding — side by side ────────────────────────────────────
    risk_col, scaffold_col = st.columns(2, gap="medium")

    with risk_col:
        at_risk = [r for r in R if r["risk_label"] == "High"]
        st.markdown(f'<div class="sec-label">⚠️ &nbsp; High-Risk Students ({len(at_risk)})</div>',
                    unsafe_allow_html=True)
        if at_risk:
            for r in at_risk:
                st.markdown(f"""
                <div class="risk-card">
                    <div class="card-name">🔴 {r['name']} <span style="color:#475569;font-size:.75rem;">({r['roll']})</span></div>
                    <div class="card-sub">Risk probability: <strong style="color:#f87171;">{r['risk_prob']:.2f}</strong><br>{r['feedback']}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-note">🎉 No high-risk students this session.</div>',
                        unsafe_allow_html=True)

    with scaffold_col:
        weak = [r for r in R if r["label"] == "Needs Attention"]
        st.markdown(f'<div class="sec-label">🔧 &nbsp; Scaffolding ({len(weak)} students)</div>',
                    unsafe_allow_html=True)
        if weak:
            for r in weak:
                st.markdown(f"""
                <div class="scaffold-card">
                    <div class="card-name">📌 {r['name']} <span style="color:#475569;font-size:.75rem;">({r['roll']})</span></div>
                    <div class="card-sub">❓ {r['scaffolding']}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-note">✅ No scaffolding needed.</div>',
                        unsafe_allow_html=True)

    # ── individual feedback ──────────────────────────────────────────────────
    with st.expander("💬  Individual Student Feedback", expanded=False):
        for r in R:
            ico = "✅" if r["label"]=="Engaged" else "⚡" if r["label"]=="Partially Engaged" else "🔴"
            st.markdown(f"**{ico} {r['name']} ({r['roll']})**  \n{r['feedback']}")
            st.markdown("---")

    # ── trend ────────────────────────────────────────────────────────────────
    st.markdown('<div class="sec-label">📉 &nbsp; Engagement Trend</div>', unsafe_allow_html=True)
    trend = get_trend_data(meta["section"], meta["topic"])
    if len(trend) >= 2:
        fig_t = _trend_chart(trend, meta["section"], meta["topic"])
        st.pyplot(fig_t, use_container_width=True)
        plt.close(fig_t)
    else:
        st.markdown('<div class="info-note">📊 Run 2+ sessions on the same section & topic to see the trend chart.</div>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION HISTORY (always visible)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">🗂️ &nbsp; Session History</div>', unsafe_allow_html=True)
history = get_all_sessions()
if history:
    hdf = pd.DataFrame(history)[["id","teacher","section","topic","date","health_score"]]
    hdf.columns = ["ID","Teacher","Section","Topic","Date","Health (%)"]
    hdf["Date"]       = hdf["Date"].str[:19].str.replace("T"," ")
    hdf["Health (%)"] = hdf["Health (%)"].round(1)
    st.dataframe(
        hdf.style.set_properties(**{"font-size":"12px","color":"#c9d6ea",
                                    "background-color":"#0d1528"}),
        use_container_width=True, height=210,
    )
else:
    st.markdown('<div class="info-note">No sessions yet — run your first analysis above.</div>',
                unsafe_allow_html=True)

# ── footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:2rem 0 1rem; color:#334155; font-size:.75rem; letter-spacing:.04em;">
    ClassIQ v2.0 &nbsp;·&nbsp; Hybrid AI Engagement Intelligence &nbsp;·&nbsp;
    <span style="color:#4f46e5;">Decision-support only — does not mark attendance</span>
</div>
""", unsafe_allow_html=True)
