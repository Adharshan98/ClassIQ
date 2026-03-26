import streamlit as st

def apply_global_styles():
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
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

::-webkit-scrollbar { width:4px; height:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#2563eb44; border-radius:99px; }

p, span, div, li, td, th, label { color: #c9d6ea; }
h1,h2,h3,h4,h5,h6 { color: #f0f6ff !important; }

[data-testid="stMetricValue"] { color:#60a5fa !important; font-weight:700 !important; font-size:2rem !important; }
[data-testid="stMetricLabel"] { color:#94a3b8 !important; font-size:0.78rem !important; text-transform:uppercase; letter-spacing:.05em; }

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
.stSelectbox label, .stTextInput label, .stSlider label, .stTextArea label {
    color: #94a3b8 !important; font-size:.82rem !important;
    font-weight:600 !important; letter-spacing:.04em !important;
}

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

.stDownloadButton > button {
    background: linear-gradient(135deg, #059669, #10b981) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    box-shadow: 0 4px 20px rgba(16,185,129,.30) !important;
}

[data-testid="stDataFrame"] { border-radius:14px !important; overflow:hidden; }
.stDataFrame * { font-size:12.5px !important; }

.streamlit-expanderHeader { color:#94a3b8 !important; font-weight:600 !important; font-size:.88rem !important; }
details { border:1px solid rgba(255,255,255,0.07) !important; border-radius:12px !important;
          background:rgba(255,255,255,0.03) !important; padding:.4rem; margin-top: 1rem; }
.stAlert { border-radius:12px !important; }
hr { border-color:rgba(255,255,255,0.06) !important; }

/* ══ Custom Components ══ */
.hero {
    background: linear-gradient(135deg,#0f172a 0%,#1e1b4b 50%,#0f172a 100%);
    border:1px solid rgba(99,102,241,0.2); border-radius:20px;
    padding:2.4rem 3rem; position:relative; overflow:hidden;
    margin-bottom:1.6rem; box-shadow:0 8px 40px rgba(99,102,241,0.18);
}
.hero::before {
    content:""; position:absolute; top:-60px; right:-60px;
    width:280px; height:280px;
    background:radial-gradient(circle,rgba(99,102,241,0.25) 0%,transparent 70%);
    border-radius:50%;
}
.hero::after {
    content:""; position:absolute; bottom:-40px; left:20%;
    width:180px; height:180px;
    background:radial-gradient(circle,rgba(124,58,237,0.20) 0%,transparent 70%);
    border-radius:50%;
}
.hero h1 {
    font-size:2.8rem !important; font-weight:800 !important;
    background:linear-gradient(90deg,#818cf8,#c084fc,#60a5fa);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; margin:0 !important; line-height:1.15 !important;
}
.hero p   { margin:.5rem 0 0 !important; color:#94a3b8 !important; font-size:1.0rem !important; }
.hero .badge {
    display:inline-block; margin-top:.9rem;
    background:rgba(99,102,241,0.15); border:1px solid rgba(99,102,241,0.35);
    color:#a5b4fc !important; border-radius:20px;
    padding:.25rem .85rem; font-size:.75rem; font-weight:600;
    letter-spacing:.06em; text-transform:uppercase;
}

.sec-label {
    display:flex; align-items:center; gap:.6rem;
    font-size:.72rem; font-weight:700; letter-spacing:.12em;
    text-transform:uppercase; color:#6366f1 !important;
    margin:1.8rem 0 .9rem;
}
.sec-label::after { content:""; flex:1; height:1px; background:linear-gradient(90deg,rgba(99,102,241,0.4),transparent); }

.glass {
    background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08);
    border-radius:16px; padding:1.4rem 1.6rem;
    box-shadow:0 4px 24px rgba(0,0,0,0.3); backdrop-filter:blur(12px); margin-bottom:.8rem;
}

.stat-grid { display:flex; gap:.85rem; flex-wrap:wrap; margin-bottom:.5rem; }
.stat-card {
    flex:1 1 130px; background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.08); border-radius:14px;
    padding:1.2rem 1rem; text-align:center; transition:transform .15s, box-shadow .15s;
}
.stat-card:hover { transform:translateY(-3px); box-shadow:0 8px 28px rgba(0,0,0,0.4); }
.stat-card .sv { font-size:2.1rem; font-weight:800; line-height:1; }
.stat-card .sl { font-size:.68rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:#64748b !important; margin-top:.35rem; }
.sv-green  { color:#34d399 !important; }
.sv-yellow { color:#fbbf24 !important; }
.sv-red    { color:#f87171 !important; }
.sv-purple { color:#a78bfa !important; }
.sv-blue   { color:#60a5fa !important; }

.pill { display:inline-block; border-radius:20px; padding:.22rem .8rem; font-size:.72rem; font-weight:700; letter-spacing:.04em; }
.pill-g { background:rgba(52,211,153,.15);  color:#34d399 !important; border:1px solid rgba(52,211,153,.3); }
.pill-y { background:rgba(251,191,36,.12);  color:#fbbf24 !important; border:1px solid rgba(251,191,36,.3); }
.pill-r { background:rgba(248,113,113,.12); color:#f87171 !important; border:1px solid rgba(248,113,113,.3); }

.insight-box {
    background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(124,58,237,0.06));
    border:1px solid rgba(99,102,241,0.25); border-left:4px solid #6366f1;
    border-radius:14px; padding:1.2rem 1.6rem;
    font-size:.9rem; line-height:1.7; color:#c9d6ea !important;
}

.risk-card {
    background:rgba(248,113,113,0.05); border:1px solid rgba(248,113,113,0.15);
    border-left:3px solid #f87171; border-radius:12px; padding:1rem 1.2rem; margin-bottom:.6rem;
}
.scaffold-card {
    background:rgba(99,102,241,0.05); border:1px solid rgba(99,102,241,0.18);
    border-left:3px solid #818cf8; border-radius:12px; padding:1rem 1.2rem; margin-bottom:.6rem;
}
.gap-card {
    background:rgba(251,191,36,0.05); border:1px solid rgba(251,191,36,0.20);
    border-left:3px solid #fbbf24; border-radius:12px; padding:1rem 1.2rem; margin-bottom:.6rem;
}
.confusion-card {
    background:rgba(239,68,68,0.05); border:1px solid rgba(239,68,68,0.22);
    border-left:3px solid #ef4444; border-radius:12px; padding:1rem 1.2rem; margin-bottom:.6rem;
}
.card-name { font-weight:700; color:#e2e8f0 !important; font-size:.9rem; }
.card-sub  { font-size:.8rem; color:#94a3b8 !important; margin-top:.3rem; line-height:1.5; }
.info-note {
    background:rgba(96,165,250,0.06); border:1px solid rgba(96,165,250,0.2);
    border-radius:10px; padding:.7rem 1rem; font-size:.82rem; color:#93c5fd !important;
}
.q-block {
    background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.08);
    border-radius:12px; padding:1rem 1.4rem; margin-bottom:1rem;
    font-style:italic; color:#a5b4fc !important; font-size:.95rem;
}

/* Role selector landing */
.role-card {
    background: linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.10); border-radius: 20px;
    padding: 2.4rem 2rem; text-align:center; cursor:pointer;
    transition: transform .2s, box-shadow .2s, border-color .2s;
    margin-bottom: .5rem;
    text-decoration: none;
    display: block;
}
.role-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(99,102,241,0.25);
    border-color: rgba(99,102,241,0.4);
}
.role-icon { font-size:3.5rem; margin-bottom:1rem; }
.role-title { font-size:1.3rem; font-weight:800; color:#e2e8f0 !important; }
.role-desc  { font-size:.82rem; color:#64748b !important; margin-top:.4rem; line-height:1.5; }
</style>
    """, unsafe_allow_html=True)
