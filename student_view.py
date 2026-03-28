"""
student_view.py
---------------
ClassIQ Student Portal — rendered inside app.py.
Handles student login, joining sessions via code, submitting responses,
and displaying individual AI evaluation (including Plagiarism/AI warnings).
"""

import re
import datetime
import streamlit as st

from core.auth            import validate_login
from core.styles          import apply_global_styles
from database.db          import get_session_by_code, save_response
from core.session_manager import evaluate_student_response


def _strip_html(text: str) -> str:
    """Remove all HTML tags from AI-generated text to prevent layout breakage."""
    return re.sub(r'<[^>]+>', '', str(text)).strip()


def _init_state():
    defaults = {
        "s_logged_in":   False,
        "s_name":        "",
        "s_email":       "",
        "s_session":     None,   # The session dict
        "s_evaluated":   False,
        "s_eval_result": None,
        "s_eval_text":   "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def render():
    _init_state()
    apply_global_styles()

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:.8rem 0 1.2rem;">
            <div style="font-size:2.2rem;margin-bottom:.4rem;">📚</div>
            <div style="font-size:1.2rem;font-weight:800;
                        background:linear-gradient(90deg,#3aaaed,#22d3ee);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                ClassIQ
            </div>
            <div style="font-size:.65rem;color:#475569;letter-spacing:.12em;text-transform:uppercase;margin-top:.2rem;">
                Student Portal
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.s_logged_in:
            st.markdown(f"""
            <div style="padding:.6rem .85rem;background:rgba(14,165,233,0.1);
                        border:1px solid rgba(14,165,233,0.25);border-radius:10px;margin-bottom:1rem;">
                👋 <strong style="color:#38bdf8;">{st.session_state.s_name}</strong><br>
                <span style="font-size:.7rem;color:#94a3b8;">{st.session_state.s_email}</span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚪 Logout", use_container_width=True):
                preserve = {"_db_ready", "role"}
                for k in list(st.session_state.keys()):
                    if k not in preserve:
                        del st.session_state[k]
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 1 — LOGIN
    # ══════════════════════════════════════════════════════════════════════════
    if not st.session_state.s_logged_in:
        st.markdown('<div class="sec-label">🔐 &nbsp; Student Login</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="info-note" style="margin-bottom:1rem;">
            📌 Please log in with your university Email ID and default credentials.<br>
            Demo Email: <code>aarav_21BCE7890@vitchennai.ac.in</code> | Password: <code>21BCE7890123</code>
        </div>
        """, unsafe_allow_html=True)

        c1, _ = st.columns([1.5, 1])
        with c1:
            with st.form("stu_login_form"):
                email = st.text_input("🎓 VIT Email",  placeholder="name_regno@vitchennai.ac.in")
                pwd   = st.text_input("🔑 Password",   placeholder="regno123", type="password")
                sub   = st.form_submit_button("Login →", use_container_width=True, type="primary")

            if sub:
                if not email.strip() or not pwd.strip():
                    st.error("⚠️ Please enter both email and password.")
                else:
                    ok, name, msg = validate_login(email.strip(), pwd.strip())
                    if ok:
                        st.session_state.s_logged_in = True
                        st.session_state.s_name      = name
                        st.session_state.s_email     = email.strip()
                        st.rerun()
                    else:
                        st.error(msg)
        return

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 2 — JOIN SESSION
    # ══════════════════════════════════════════════════════════════════════════
    if not st.session_state.s_session:
        st.markdown('<div class="sec-label">🎫 &nbsp; Join Active Session</div>', unsafe_allow_html=True)

        c1, _ = st.columns([1.5, 1])
        with c1:
            with st.form("join_form"):
                code = st.text_input("🔑 Session Code", placeholder="e.g. 7A9X2")
                sub  = st.form_submit_button("Join Session", use_container_width=True, type="primary")

            if sub:
                code_upper = code.strip().upper()
                if not code_upper:
                    st.error("⚠️ Please enter a session code.")
                else:
                    session_data = get_session_by_code(code_upper)
                    if session_data:
                        st.session_state.s_session = session_data
                        st.rerun()
                    else:
                        st.error(f"❌ Session '{code_upper}' not found. Please verify the code with your teacher.")
        return

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 3 — RESPONSE SUBMISSION
    # ══════════════════════════════════════════════════════════════════════════
    SD = st.session_state.s_session

    # Session banner
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                border-radius:12px;padding:1rem 1.6rem;margin-bottom:1.4rem;display:flex;
                justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.8rem;">
        <div>
            <div style="font-size:.65rem;color:#0ea5e9;font-weight:700;
                        letter-spacing:.12em;text-transform:uppercase;">SESSION</div>
            <div style="font-size:1.8rem;font-family:'JetBrains Mono',monospace;
                        font-weight:900;color:#e2e8f0;letter-spacing:.2em;">{SD['code']}</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:.7rem;color:#64748b;">Topic</div>
            <div style="font-size:1rem;color:#bae6fd;font-weight:600;">{SD['topic']}</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:.7rem;color:#64748b;">Teacher</div>
            <div style="font-size:1rem;color:#e2e8f0;font-weight:600;">{SD['teacher']}</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:.7rem;color:#64748b;">Section</div>
            <div style="font-size:1rem;color:#e2e8f0;font-weight:600;">{SD['section']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.s_evaluated:
        st.markdown('<div class="sec-label">📝 &nbsp; Your Question</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:#0c1322;border:1px solid #1e293b;border-radius:10px;
                    padding:1.4rem;font-size:1.1rem;color:#f0f6ff;font-style:italic;
                    border-left:4px solid #38bdf8;margin-bottom:1.5rem;">
            {SD['question']}
        </div>
        """, unsafe_allow_html=True)

        with st.form("response_form"):
            resp = st.text_area(
                "Write your answer below:",
                height=160,
                placeholder="Explain your thought process clearly..."
            )
            sub = st.form_submit_button("Submit Response", type="primary", use_container_width=True)

        if sub:
            text = resp.strip()
            if len(text) < 5:
                st.error("⚠️ Response too short. Please write a meaningful answer (at least 5 characters).")
            else:
                with st.spinner("⏳ Analysing your response through AI engines…"):
                    res = evaluate_student_response(text, SD['topic'], SD['question'])

                    save_response(
                        session_id    = SD["id"],
                        student_name  = st.session_state.s_name,
                        student_email = st.session_state.s_email,
                        response_text = text,
                        score         = res["score"],
                        label         = res["label"],
                        risk_prob     = res["risk_prob"],
                        risk_label    = res["risk_label"],
                        explanation   = res["explanation"],
                        feedback      = res["feedback"],
                        scaffolding   = res["scaffolding"],
                        timestamp     = datetime.datetime.now().isoformat(),
                        plag_score    = res["plag_score"],
                        plag_flag     = res["plag_flag"],
                    )

                st.session_state.s_eval_result = res
                st.session_state.s_eval_text   = text
                st.session_state.s_evaluated   = True
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 4 — EVALUATION DASHBOARD
    # ══════════════════════════════════════════════════════════════════════════
    else:
        res = st.session_state.s_eval_result
        if not res:
            st.error("Something went wrong — no result found. Please try again.")
            if st.button("🔄 Try Again"):
                st.session_state.s_evaluated = False
                st.rerun()
            return

        st.markdown('<div class="sec-label">📊 &nbsp; Your Engagement Result</div>', unsafe_allow_html=True)

        # Visual style mapping
        label = res.get("label", "Unknown")
        if label == "Engaged":
            c_light, c_border, bg = "#00d2ff", "rgba(0,210,255,0.4)", "linear-gradient(145deg, rgba(0,210,255,0.1), rgba(0,210,255,0.02))"
            ico = "🔥"
        elif label == "Partially Engaged":
            c_light, c_border, bg = "#a020f0", "rgba(160,32,240,0.5)", "linear-gradient(145deg, rgba(160,32,240,0.15), rgba(160,32,240,0.03))"
            ico = "⚡"
        else:
            c_light, c_border, bg = "#ff007a", "rgba(255,0,122,0.5)", "linear-gradient(145deg, rgba(255,0,122,0.15), rgba(255,0,122,0.03))"
            ico = "⚠️"

        # Safe parsing — strip ALL HTML tags from AI-generated fields
        risk_label_safe  = _strip_html(res.get("risk_label", "Unknown"))
        feedback_safe    = _strip_html(res.get("feedback", ""))
        scaffolding_safe = _strip_html(res.get("scaffolding", ""))
        score_val        = float(res.get("score", 0.0))

        # ── Result card using st.columns (avoids nested HTML closure bugs) ──────
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {c_border};border-radius:20px;
                    padding:2rem 2.5rem;margin-bottom:1.5rem;
                    box-shadow:0 8px 32px rgba(0,0,0,0.3);backdrop-filter:blur(10px);">
            &nbsp;
        </div>
        <style>
        .result-overlay {{margin-top:-5.5rem;padding:0 2rem 2rem;}}
        </style>
        """, unsafe_allow_html=True)

        col_score, col_info = st.columns([1, 2], gap="large")
        with col_score:
            st.markdown(f"""
            <div style="text-align:center;padding:1.5rem 0;">
                <div style="font-size:5.5rem;font-weight:900;color:{c_light};line-height:1;
                            text-shadow:0 0 30px {c_border};margin-bottom:.4rem;">
                    {score_val:.1f}
                </div>
                <div style="font-size:.82rem;color:#a5b4fc;font-weight:700;
                            letter-spacing:.18em;text-transform:uppercase;">
                    OUT OF 100
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_info:
            st.markdown(f"""
            <div style="padding:1.5rem 0 1rem 1.5rem;border-left:2px solid rgba(255,255,255,0.1);">
                <div style="display:inline-block;padding:.55rem 1.4rem;
                            background:rgba(255,255,255,0.06);border:1px solid {c_border};
                            border-radius:99px;font-size:1rem;color:{c_light};font-weight:800;
                            margin-bottom:1rem;letter-spacing:.05em;box-shadow:0 0 18px {c_border};">
                    {ico} {label.upper()}
                </div>
                <div style="font-size:1rem;color:#cbd5e1;font-weight:500;margin-top:.2rem;">
                    Risk Level &nbsp;<strong style="color:{c_light};font-weight:800;">{risk_label_safe}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            # Plagiarism warning as separate markdown (avoids nested injection)
            if res.get("plag_score", 0.0) >= 0.7:
                flag_text = _strip_html(res.get("plag_flag", "High AI Probability detected."))
                st.markdown(f"""
                <div style="background:rgba(255,0,122,0.15);border:1px solid rgba(255,0,122,0.4);
                            border-radius:12px;padding:.9rem;margin-top:.5rem;text-align:center;
                            box-shadow:0 4px 15px rgba(255,0,122,0.15);">
                    <span style="color:#ff007a;font-weight:800;font-size:.88rem;letter-spacing:.04em;">
                        🤖 {flag_text}
                    </span>
                </div>
                """, unsafe_allow_html=True)

        # ── Personalised Feedback ─────────────────────────────────────────────
        st.markdown('<div class="sec-label">💡 &nbsp; Personalised AI Coaching</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: linear-gradient(145deg, rgba(0,210,255,0.08), rgba(160,32,240,0.08)); 
                    border:1px solid rgba(0,210,255,0.3); border-radius:14px; padding:1.5rem; 
                    font-size:1.05rem; color:#e0f2fe; margin-bottom:1.5rem; border-left: 4px solid #00d2ff;">
            {feedback_safe}
        </div>
        """, unsafe_allow_html=True)

        # ── Scaffolding (only if present) ─────────────────────────────────────
        if scaffolding_safe:
            st.markdown('<div class="sec-label">🔧 &nbsp; Recommended Scaffolding</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:rgba(255,0,122,0.05); border:1px solid rgba(255,0,122,0.3);
                        border-radius:14px; border-left:4px solid #ff007a; padding:1.4rem;
                        font-size:1.05rem; color:#fef3c7; margin-bottom:1.5rem;">
                {scaffolding_safe}
            </div>
            """, unsafe_allow_html=True)

        # ── AI Explanation (expander, rendered as clean bullet lines) ──────────
        with st.expander("🔬 View Full AI Explanation"):
            # explanation is stored as newline-separated bullet lines
            explanation_raw = res.get("explanation", "")
            if explanation_raw:
                for line in explanation_raw.split("\n"):
                    line = line.strip()
                    if line:
                        st.markdown(f"- {line}")
            else:
                st.markdown("_No detailed explanation available._")

        st.markdown("---")
        if st.button("🔄 Join Another Session", use_container_width=True):
            st.session_state.s_session   = None
            st.session_state.s_evaluated = False
            st.session_state.s_eval_result = None
            st.session_state.s_eval_text   = ""
            st.rerun()

    st.markdown("""
    <div style="text-align:center;padding:2rem 0;color:#334155;font-size:.7rem;letter-spacing:.04em;">
        ClassIQ v3.1 &nbsp;·&nbsp; AI Engagement Intelligence
    </div>
    """, unsafe_allow_html=True)
