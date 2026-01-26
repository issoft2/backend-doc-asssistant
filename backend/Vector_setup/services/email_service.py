# email_service.py
import os
from typing import Optional
import mailtrap as mt

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "issoft")
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "true").lower() in ("true", "1", "yes")


def _send_email(to_email: str, subject: str, html_body: str) -> None:
    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("SMTP_USER/SMTP_PASSWORD not configured")

    msg = MIMEText(html_body, "html")
    msg["Subject"] = subject
    msg["From"] = formataddr((SMTP_FROM_NAME, SMTP_USER))
    msg["To"] = to_email

    if SMTP_USE_SSL:
        server_cls = smtplib.SMTP_SSL
    else:
        server_cls = smtplib.SMTP

    with server_cls(SMTP_HOST, SMTP_PORT) as server:
        if not SMTP_USE_SSL:
            server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [to_email], msg.as_string())
        
def send_first_login_email(to_email: str, first_name: str, tenant_id: str, login_link: str) -> None:
    subject = "Welcome – Your first login details"
    html = f"""
    <p>Hi {first_name or ''},</p>
    <p>
      You have been added to the company <b>{tenant_id or ''}</b>.
      Click the link below to set your password and log in for the first time:
    </p>
    <p>
      <a href="{login_link}">Click here to set your password</a>
    </p>
    <p>If you did not expect this email, you can ignore it.</p>
    """
    _send_email(to_email, subject, html)        


