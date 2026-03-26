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
    <div style="background: linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));
                border: 1px solid rgba(255,255,255,0.10); border-radius: 20px;
                padding: 2.4rem 2rem; text-align:center;
                margin-bottom: .5rem;">
        <div class="role-icon">🎓</div>
        <div class="role-title" style="margin-bottom:1rem;">Teacher</div>
        <div class="role-desc">
            Start sessions, monitor live engagement,<br>
            view concept gaps, and get AI teaching recommendations.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Teacher_Portal.py", label="Open Teacher Portal →", icon="🎓", use_container_width=True)

with c2:
    st.markdown("""
    <div style="background: linear-gradient(135deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02));
                border: 1px solid rgba(255,255,255,0.10); border-radius: 20px;
                padding: 2.4rem 2rem; text-align:center;
                margin-bottom: .5rem;">
        <div class="role-icon">📚</div>
        <div class="role-title" style="margin-bottom:1rem;">Student</div>
        <div class="role-desc">
            Join a session with your session code,<br>
            answer the question, and receive instant AI feedback.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Student_Portal.py", label="Open Student Portal →", icon="📚", use_container_width=True)

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
