"""
student_app.py
--------------
ClassIQ — STUDENT-ONLY Application.
Completely independent from the teacher app (app.py).

Run on a SEPARATE port:
    streamlit run student_app.py --server.port 8502

Students open:  http://localhost:8502
Teachers open:  http://localhost:8501

Shares the same SQLite database file so teachers see student responses in real time.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from database.db import init_db

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ClassIQ | Student Portal",
    page_icon="📚",
    layout="centered",           # centered is cleaner for students
    initial_sidebar_state="auto",
)

init_db()

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, html, body { font-family: 'Inter', sans-serif !important; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1528 40%, #111c35 70%, #0a1220 100%) !important;
    min-height: 100vh;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.03) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] *, [data-testid="stSidebar"] label { color: #c9d6ea !important; }

::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#2563eb44; border-radius:99px; }

p, span, div, li, td, th, label { color: #c9d6ea; }
h1,h2,h3,h4,h5,h6 { color: #f0f6ff !important; }

.stSelectbox > div > div, .stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important; color: #f0f6ff !important;
}
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important; color: #f0f6ff !important;
    font-family: 'Inter', sans-serif !important;
}
.stSelectbox label, .stTextInput label, .stTextArea label {
    color: #94a3b8 !important; font-size: .82rem !important;
    font-weight: 600 !important; letter-spacing: .04em;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #7c3aed) !important;
    color: #fff !important; border: none !important;
    border-radius: 12px !important; font-weight: 700 !important;
    font-size: .95rem !important; padding: .7rem 1.2rem !important;
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

.stAlert { border-radius: 12px !important; }
hr { border-color: rgba(255,255,255,0.06) !important; }

/* ── Custom Components ── */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid rgba(99,102,241,0.2); border-radius: 20px;
    padding: 2rem 2.5rem; position: relative; overflow: hidden;
    margin-bottom: 1.6rem; box-shadow: 0 8px 40px rgba(99,102,241,0.18);
}
.hero::before {
    content:""; position:absolute; top:-40px; right:-40px;
    width:200px; height:200px;
    background: radial-gradient(circle, rgba(99,102,241,0.25) 0%, transparent 70%);
    border-radius:50%;
}
.hero h1 {
    font-size: 2.4rem !important; font-weight: 800 !important;
    background: linear-gradient(90deg,#818cf8,#c084fc,#60a5fa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; margin:0 !important; line-height:1.15 !important;
}
.hero p { margin:.5rem 0 0 !important; color:#94a3b8 !important; font-size:.95rem !important; }
.hero .badge {
    display:inline-block; margin-top:.8rem;
    background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.35);
    color:#a5b4fc !important; border-radius:20px;
    padding:.22rem .8rem; font-size:.72rem; font-weight:600;
    letter-spacing:.06em; text-transform:uppercase;
}

.sec-label {
    display:flex; align-items:center; gap:.6rem;
    font-size:.72rem; font-weight:700; letter-spacing:.12em;
    text-transform:uppercase; color:#6366f1 !important;
    margin:1.6rem 0 .8rem;
}
.sec-label::after {
    content:""; flex:1; height:1px;
    background:linear-gradient(90deg, rgba(99,102,241,0.4), transparent);
}

.glass {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px; padding: 1.6rem 2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    backdrop-filter: blur(12px); margin-bottom: .8rem;
}

.info-note {
    background:rgba(96,165,250,0.06); border:1px solid rgba(96,165,250,0.2);
    border-radius:10px; padding:1.2rem 1.4rem;
    font-size:.85rem; color:#93c5fd !important;
    text-align: center;
}

.q-block {
    background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08);
    border-radius:12px; padding:1.2rem 1.6rem; margin-bottom:1rem;
    font-style:italic; color:#a5b4fc !important; font-size:1rem; line-height:1.75;
}

.pill { display:inline-block; border-radius:20px; padding:.22rem .8rem;
        font-size:.72rem; font-weight:700; letter-spacing:.04em; }
.pill-g { background:rgba(52,211,153,.15);  color:#34d399 !important; border:1px solid rgba(52,211,153,.3); }
.pill-y { background:rgba(251,191,36,.12);  color:#fbbf24 !important; border:1px solid rgba(251,191,36,.3); }
.pill-r { background:rgba(248,113,113,.12); color:#f87171 !important; border:1px solid rgba(248,113,113,.3); }

.insight-box {
    background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(124,58,237,0.06));
    border:1px solid rgba(99,102,241,0.25); border-left:4px solid #6366f1;
    border-radius:14px; padding:1.2rem 1.6rem;
    font-size:.9rem; line-height:1.7; color:#c9d6ea !important;
}

.scaffold-card {
    background:rgba(99,102,241,0.05); border:1px solid rgba(99,102,241,0.18);
    border-left:3px solid #818cf8; border-radius:12px;
    padding:1rem 1.2rem; margin-bottom:.6rem;
}
.card-name { font-weight:700; color:#e2e8f0 !important; font-size:.9rem; }
.card-sub  { font-size:.8rem; color:#94a3b8 !important; margin-top:.3rem; line-height:1.5; }

.score-big { font-size:3rem; font-weight:900; color:#60a5fa; line-height:1; }

.streamlit-expanderHeader { padding-left: 0.2rem !important; padding-right: 0.5rem !important; }
.streamlit-expanderHeader svg { margin-right: 0.8rem; transform: scale(1.1); }
.streamlit-expanderHeader p { margin-left: 0.5rem !important; }

div[data-testid="stSpinner"] > div { margin: 2rem auto; }
</style>
""", unsafe_allow_html=True)

# ── Delegate to student_view ───────────────────────────────────────────────────
import student_view
student_view.render()
