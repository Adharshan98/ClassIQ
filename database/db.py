"""
database/db.py
--------------
SQLite database logic for ClassIQ.
Stores sessions, teacher info, and student responses with AI/Plagiarism analytics.

Performance notes:
  * Write operations (create_session, save_response, update_session_health) are
    NOT cached — they must always hit the DB.
  * Heavy read queries use @st.cache_data with short TTLs.
  * Cache is cleared explicitly after any write so the dashboard stays consistent.

Fix: save_response now clears only the correct session cache key by calling
     _cached_get_responses.clear() which clears all entries — acceptable since
     responses are keyed per session and the TTL is only 8s anyway.
"""

import sqlite3
import os
from contextlib import contextmanager

import streamlit as st

_BASE   = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BASE, "classiq.db")


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # better concurrency
    conn.execute("PRAGMA synchronous=NORMAL") # faster writes without data loss
    try:
        yield conn
    finally:
        conn.close()


# ── Schema Init ───────────────────────────────────────────────────────────────
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                teacher TEXT NOT NULL,
                topic TEXT NOT NULL,
                section TEXT NOT NULL,
                question TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                health_score REAL DEFAULT 0.0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                student_email TEXT NOT NULL,
                response_text TEXT NOT NULL,
                score REAL,
                label TEXT,
                risk_prob REAL,
                risk_label TEXT,
                explanation TEXT,
                feedback TEXT,
                scaffolding TEXT,
                plagiarism_score REAL DEFAULT 0.0,
                plagiarism_flag TEXT DEFAULT '',
                timestamp TEXT NOT NULL,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        ''')
        # Create indexes for common queries
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_responses_session '
            'ON responses(session_id)'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_sessions_section_topic '
            'ON sessions(section, topic)'
        )
        conn.commit()


# ── Write operations (never cached) ───────────────────────────────────────────

def create_session(code: str, teacher: str, topic: str, section: str,
                   question: str, timestamp: str) -> int:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO sessions (code, teacher, topic, section, question, timestamp)'
            ' VALUES (?, ?, ?, ?, ?, ?)',
            (code, teacher, topic, section, question, timestamp)
        )
        conn.commit()
        sid = cursor.lastrowid
    # Clear cached reads so the new session appears immediately
    _cached_get_all_sessions.clear()
    if sid is None:
        raise RuntimeError("Failed to create session — no row ID returned.")
    return int(sid)


def update_session_health(session_id: int, health_score: float):
    with get_db_connection() as conn:
        conn.execute(
            'UPDATE sessions SET health_score = ? WHERE id = ?',
            (health_score, session_id)
        )
        conn.commit()
    # Invalidate session history cache
    _cached_get_all_sessions.clear()


def get_session_by_code(code: str) -> dict | None:
    """Uncached — only called once when a student joins."""
    with get_db_connection() as conn:
        row = conn.execute(
            'SELECT * FROM sessions WHERE code = ?', (code,)
        ).fetchone()
    return dict(row) if row else None


def save_response(
    session_id: int, student_name: str, student_email: str, response_text: str,
    score: float, label: str, risk_prob: float, risk_label: str,
    explanation: str, feedback: str, scaffolding: str, timestamp: str,
    plag_score: float = 0.0, plag_flag: str = ""
):
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO responses (
                session_id, student_name, student_email, response_text,
                score, label, risk_prob, risk_label, explanation,
                feedback, scaffolding, plagiarism_score, plagiarism_flag, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, student_name, student_email, response_text,
            score, label, risk_prob, risk_label, explanation,
            feedback, scaffolding, plag_score, plag_flag, timestamp
        ))
        conn.commit()
    # Invalidate response cache for this session so teacher sees new data immediately
    _cached_get_responses.clear()


# ── Cached read operations ────────────────────────────────────────────────────

@st.cache_data(ttl=5, show_spinner=False)
def _cached_get_responses(session_id: int) -> list[dict]:
    """Internal cached read — invalidated after every save_response(). TTL=5s."""
    with get_db_connection() as conn:
        rows = conn.execute(
            'SELECT * FROM responses WHERE session_id = ? ORDER BY timestamp DESC',
            (session_id,)
        ).fetchall()
    return [dict(row) for row in rows]


@st.cache_data(ttl=15, show_spinner=False)
def _cached_get_all_sessions() -> list[dict]:
    """Internal cached read — invalidated after create_session() / update_session_health()."""
    with get_db_connection() as conn:
        rows = conn.execute(
            'SELECT * FROM sessions ORDER BY timestamp DESC'
        ).fetchall()
    return [dict(row) for row in rows]


@st.cache_data(ttl=30, show_spinner=False)
def _cached_get_trend(section: str, topic: str) -> list[dict]:
    with get_db_connection() as conn:
        rows = conn.execute(
            'SELECT timestamp as date, health_score FROM sessions'
            ' WHERE section = ? AND topic = ? ORDER BY timestamp ASC',
            (section, topic)
        ).fetchall()
    return [dict(row) for row in rows]


# ── Public read API (delegates to cached versions) ────────────────────────────

def get_responses_for_session(session_id: int) -> list[dict]:
    return _cached_get_responses(session_id)


def get_all_sessions() -> list[dict]:
    return _cached_get_all_sessions()


def get_trend_data(section: str, topic: str) -> list[dict]:
    return _cached_get_trend(section, topic)
