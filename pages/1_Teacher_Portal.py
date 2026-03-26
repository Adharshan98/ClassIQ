"""
pages/1_Teacher_Portal.py
-------------------------
ClassIQ Teacher Dashboard.
"""
import sys
import os

# Ensure the core module can be imported from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from database.db import init_db

st.set_page_config(
    page_title="Teacher Portal | ClassIQ",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "_db_ready" not in st.session_state:
    init_db()
    st.session_state["_db_ready"] = True

import teacher_view
teacher_view.render()
