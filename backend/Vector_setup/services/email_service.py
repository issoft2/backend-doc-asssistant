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
    subject = f"Welcome to {tenant_id} – Finish setting up your account"
    
    # Design constants
    brand_color = "#5850ec" # Modern SaaS Indigo
    bg_color = "#f4f7fa"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: {bg_color}; margin: 0; padding: 0; }}
            .wrapper {{ padding: 40px 20px; }}
            .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .header {{ padding: 32px 32px 10px 32px; text-align: left; }}
            .content {{ padding: 0 32px 32px 32px; color: #374151; line-height: 1.6; }}
            .button-container {{ padding: 20px 0; text-align: center; }}
            .button {{ background-color: {brand_color}; color: #ffffff !important; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; font-size: 16px; }}
            .footer {{ padding: 24px; text-align: center; color: #9ca3af; font-size: 13px; border-top: 1px solid #f3f4f6; }}
            .workspace-tag {{ display: inline-block; background: #eef2ff; color: {brand_color}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 16px; }}
            @media (max-width: 600px) {{ .wrapper {{ padding: 20px 10px; }} }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="container">
                <div class="header">
                    <div class="workspace-tag">{tenant_id.upper()} WORKSPACE</div>
                    <h1 style="margin: 0; font-size: 24px; color: #111827;">Welcome, {first_name or 'there'}!</h1>
                </div>
                <div class="content">
                    <p style="font-size: 16px;">You’ve been invited to join <strong>{tenant_id}</strong> on our AI Platform. To get started, you’ll need to set your password and secure your account.</p>
                    
                    <div class="button-container">
                        <a href="{login_link}" class="button">Set Up Your Account</a>
                    </div>
                    
                    <p style="font-size: 14px; color: #6b7280;">
                        <strong>Security Note:</strong> This link will expire in 24 hours. If it expires, you can request a new one at the login page.
                    </p>
                </div>
                <div class="footer">
                    If you didn’t expect this invitation, you can safely ignore this email.<br/>
                    &copy; 2026 CG Assistant AI. All rights reserved.
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    _send_email(to_email, subject, html)

