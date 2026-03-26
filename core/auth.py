"""
core/auth.py
------------
Simulated authentication for ClassIQ students.

Email format:  name_regno@vitchennai.ac.in
Password rule: regno123  (regno extracted from the email)
"""

import re


# ── Regex pattern ─────────────────────────────────────────────────────────────
# Matches:  anythingletters_REGNO@vitchennai.ac.in
#           regno is the part after the last underscore before @
_EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z]+_([a-zA-Z0-9]+)@vitchennai\.ac\.in$"
)


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate student email format.

    Returns
    -------
    (valid: bool, regno: str)
        If valid, regno is the extracted registration number.
        If invalid, regno is an empty string.
    """
    m = _EMAIL_PATTERN.match(email.strip())
    if m:
        return True, m.group(1)
    return False, ""


def validate_login(email: str, password: str) -> tuple[bool, str, str]:
    """
    Validate student credentials.

    Expected password: <regno>123

    Returns
    -------
    (success: bool, student_name: str, message: str)
    """
    ok, regno = validate_email(email)
    if not ok:
        return (
            False, "",
            "❌ Invalid email format. Use name_regno@vitchennai.ac.in"
        )

    expected_password = f"{regno}123"
    if password.strip() != expected_password:
        return (
            False, "",
            f"❌ Incorrect password. Expected format: <regno>123"
        )

    # Derive a display name from the part before the underscore
    display_name = email.split("_")[0].capitalize()
    return True, display_name, "✅ Login successful"
