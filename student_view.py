"""
student_view.py
---------------
ClassIQ Student Portal — rendered inside app.py.
Handles student login, joining sessions via code, submitting responses,
and displaying individual AI evaluation (including Plagiarism/AI warnings).
"""

import datetime
import streamlit as st

from core.auth            import validate_login
from database.db          import get_session_by_code, save_response
from core.session_manager import evaluate_student_response


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
        label = res["label"]
        if label == "Engaged":
            c_light, c_border, bg = "#34d399", "rgba(52,211,153,0.3)", "rgba(52,211,153,0.06)"
            ico = "✅"
        elif label == "Partially Engaged":
            c_light, c_border, bg = "#fbbf24", "rgba(251,191,36,0.3)", "rgba(251,191,36,0.06)"
            ico = "⚡"
        else:
            c_light, c_border, bg = "#f87171", "rgba(248,113,113,0.3)", "rgba(248,113,113,0.06)"
            ico = "🔴"

        # AI / plagiarism warning (only if flagged)
        plag_html = ""
        if res.get("plag_score", 0.0) >= 0.7:
            flag_text = res.get("plag_flag", "High AI Probability detected. This response has been flagged.")
            plag_html = f"""
            <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.5);
                        border-radius:6px;padding:.5rem;margin-top:.8rem;text-align:center;">
                <span style="color:#ef4444;font-weight:bold;font-size:.8rem;">⚠️ {flag_text}</span>
            </div>"""

        st.markdown(f"""
        <div style="background:{bg};border:1px solid {c_border};border-radius:12px;
                    padding:2.5rem;text-align:center;margin-bottom:1.5rem;display:flex;
                    align-items:center;justify-content:center;gap:3rem;flex-wrap:wrap;">
            <div>
                <div style="font-size:4.2rem;font-weight:900;color:{c_light};line-height:1;margin-bottom:.4rem;">
                    {res['score']:.1f}
                </div>
                <div style="font-size:.85rem;color:#64748b;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;">
                    Out of 100
                </div>
            </div>
            <div style="text-align:left;min-width:200px;border-left:1px solid rgba(255,255,255,0.1);padding-left:3rem;">
                <div style="display:inline-block;padding:.4rem 1.2rem;
                            background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);
                            border-radius:99px;font-size:.85rem;color:{c_light};font-weight:700;
                            margin-bottom:.8rem;letter-spacing:0.02em;">
                    {ico} {label}
                </div>
                <div style="font-size:.85rem;color:#94a3b8;margin-left:.25rem;">
                    Risk Level: <strong style="color:{c_light};">{res['risk_label']}</strong>
                </div>
                {plag_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Personalised Feedback ─────────────────────────────────────────────
        st.markdown('<div class="sec-label">💡 &nbsp; Personalised Feedback</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(14,165,233,0.05);border:1px solid rgba(14,165,233,0.2);
                    border-radius:10px;padding:1.2rem;font-size:.95rem;color:#e0f2fe;margin-bottom:1.2rem;">
            {res['feedback']}
        </div>
        """, unsafe_allow_html=True)

        # ── Scaffolding (only if present) ─────────────────────────────────────
        if res.get("scaffolding"):
            st.markdown('<div class="sec-label">🔧 &nbsp; Hint &amp; Scaffolding</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:rgba(251,191,36,0.05);border:1px solid rgba(251,191,36,0.3);
                        border-radius:10px;border-left:4px solid #fbbf24;padding:1rem 1.4rem;
                        font-size:.95rem;color:#fef3c7;margin-bottom:1.5rem;">
                {res['scaffolding']}
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
