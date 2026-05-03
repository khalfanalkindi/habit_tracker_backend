"""Optional SMTP for password-reset emails (stdlib only)."""

from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger(__name__)


def send_password_reset_email(to_addr: str, reset_link: str) -> bool:
    """Return True if the message was handed to SMTP; False if SMTP is not configured."""
    host = (os.getenv("SMTP_HOST") or "").strip()
    if not host:
        return False
    port = int((os.getenv("SMTP_PORT") or "587").strip() or "587")
    user = (os.getenv("SMTP_USER") or "").strip()
    password = (os.getenv("SMTP_PASSWORD") or "").strip()
    from_addr = (os.getenv("SMTP_FROM") or user or "noreply@localhost").strip()

    subject = (os.getenv("SMTP_PASSWORD_RESET_SUBJECT") or "Password reset").strip()
    body = (
        "You requested a password reset.\n\n"
        f"Open this link (valid for a limited time):\n{reset_link}\n\n"
        "If you did not request this, ignore this email.\n"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.starttls()
            if user and password:
                smtp.login(user, password)
            smtp.send_message(msg)
        return True
    except OSError as e:
        logger.warning("SMTP send failed: %s", e)
        return False
