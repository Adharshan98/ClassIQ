"""
pages/2_Student_Portal.py
-------------------------
ClassIQ Student Portal.
"""
import sys
import os

# Ensure the core module can be imported from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from database.db import init_db

st.set_page_config(
    page_title="Student Portal | ClassIQ",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "_db_ready" not in st.session_state:
    init_db()
    st.session_state["_db_ready"] = True

import student_view
student_view.render()
