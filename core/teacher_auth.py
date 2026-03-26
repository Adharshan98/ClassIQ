"""
core/teacher_auth.py
--------------------
Simulated teacher authentication for ClassIQ.

Credentials (predefined teacher accounts):
  teacher ID: staff name (lowercase, no spaces)
  password  : classiq@<id>

Example:
  ID       → "ananya"
  Password → "classiq@ananya"
"""

# ── Predefined teacher accounts ───────────────────────────────────────────────
# key = teacher_id (login username), value = (display_name, password)
TEACHER_ACCOUNTS: dict[str, tuple[str, str]] = {
    "ananya":   ("Dr. Ananya Sharma",    "classiq@ananya"),
    "rajan":    ("Prof. Rajan Mehta",    "classiq@rajan"),
    "priya":    ("Dr. Priya Nair",       "classiq@priya"),
    "suresh":   ("Prof. Suresh Kumar",   "classiq@suresh"),
    "divya":    ("Dr. Divya Krishnan",   "classiq@divya"),
    "arun":     ("Prof. Arun Patel",     "classiq@arun"),
    # Generic demo account
    "teacher":  ("Demo Teacher",         "classiq@teacher"),
}


def validate_teacher_login(teacher_id: str, password: str) -> tuple[bool, str, str]:
    """
    Validate teacher credentials.

    Parameters
    ----------
    teacher_id : str – the teacher's login ID (username)
    password   : str – the entered password

    Returns
    -------
    (success: bool, display_name: str, message: str)
    """
    tid = teacher_id.strip().lower()
    if tid not in TEACHER_ACCOUNTS:
        return (
            False, "",
            f"❌ Unknown teacher ID '{teacher_id}'. Contact your administrator."
        )

    display_name, expected_pw = TEACHER_ACCOUNTS[tid]
    if password.strip() != expected_pw:
        return (
            False, "",
            "❌ Incorrect password. Format: classiq@<your_id>"
        )

    return True, display_name, "✅ Login successful"


def get_all_teachers() -> list[str]:
    """Return a list of all registered teacher IDs."""
    return list(TEACHER_ACCOUNTS.keys())
