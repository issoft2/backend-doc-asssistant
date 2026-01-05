# email_service.py
import os
from typing import Optional
import mailtrap as mt

MAILTRAP_API_TOKEN = os.getenv("MAILTRAPTOKEN")  # set this in your env

client = mt.MailtrapClient(token=MAILTRAP_API_TOKEN, sandbox=True)


def send_first_login_email(
    to_email: str,
    first_name: Optional[str],
    tenant_id: Optional[str],
    login_link: str,
) -> None:
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

    mail = mt.Mail(
        sender=mt.Address(email="no-reply@lexiscope.duckdns.org", name="Lexiscope"),
        to=[mt.Address(email=to_email)],
        subject="Your first-time login link",
        html=html,  # use html=..., not text=... for HTML body
    )

    # mailtrap client is sync; FastAPI BackgroundTasks will run it off the request
    client.send(mail)


