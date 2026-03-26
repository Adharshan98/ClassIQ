"""
app.py
------
ClassIQ — Unified Entry Point Landing Page.
(Using Streamlit Multipage format. See pages/ directory).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from database.db import init_db
from core.styles import apply_global_styles

st.set_page_config(
    page_title="ClassIQ | AI Engagement System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "_db_ready" not in st.session_state:
    init_db()
    st.session_state["_db_ready"] = True

# Apply global CSS
apply_global_styles()


# ── Landing page ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>ClassIQ</h1>
    <p>AI-Powered Classroom Engagement Intelligence System</p>
    <span class="badge">🤖 Hybrid ML · Concept Gap · Confusion Detection</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="sec-label">🚀 &nbsp; Select Your Portal</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("""
    <style>
    .portal-card-hover:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(255,255,255,0.3) !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
    }
    </style>
    <a href="Teacher_Portal" target="_self" style="text-decoration:none; color:inherit; display:block;">
        <div class="portal-card-hover" style="background: linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));
                    border: 1px solid rgba(255,255,255,0.10); border-radius: 20px;
                    padding: 2.4rem 2rem; text-align:center;
                    margin-bottom: .5rem; transition: all 0.2s ease;">
            <div class="role-icon" style="font-size:3rem;margin-bottom:1rem;">🎓</div>
            <div class="role-title" style="margin-bottom:1rem;font-size:1.5rem;font-weight:600;">Teacher</div>
            <div class="role-desc" style="opacity:0.8;font-size:0.95rem;line-height:1.5;">
                Start sessions, monitor live engagement,<br>
                view concept gaps, and get AI teaching recommendations.
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <a href="Student_Portal" target="_self" style="text-decoration:none; color:inherit; display:block;">
        <div class="portal-card-hover" style="background: linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));
                    border: 1px solid rgba(255,255,255,0.10); border-radius: 20px;
                    padding: 2.4rem 2rem; text-align:center;
                    margin-bottom: .5rem; transition: all 0.2s ease;">
            <div class="role-icon" style="font-size:3rem;margin-bottom:1rem;">📚</div>
            <div class="role-title" style="margin-bottom:1rem;font-size:1.5rem;font-weight:600;">Student</div>
            <div class="role-desc" style="opacity:0.8;font-size:0.95rem;line-height:1.5;">
                Join a session with your session code,<br>
                answer the question, and receive instant AI feedback.
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="info-note" style="margin-top:1.5rem;text-align:center;">
    👈 &nbsp; You can also use the sidebar to navigate between pages at any time.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;color:#334155;font-size:.74rem;letter-spacing:.04em;">
    ClassIQ v3.1 &nbsp;·&nbsp; Fully Offline · Decision-support only — does not mark attendance
</div>
""", unsafe_allow_html=True)
