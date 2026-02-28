# email_service.py
import os
from typing import Optional
from dotenv import load_dotenv
import resend
import logging

load_dotenv()
logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "re_BqBKvjwD_GurzED7jtJpoGJNetV4mdst2")

resend.api_key = RESEND_API_KEY

  # Design constants
BRAND_COLOR = "#5850ec" # Modern SaaS Indigo
BG_COLOR = "#f4f7fa"
APP_NAME = os.getenv("APP_NAME", "Smart Knowledge Assistant")
FROM_EMAIL = os.getenv("EMAIL_FROM", "onboarding@resend.dev")


# ── Base Template ──────────────────────────────────────────────────────────
def _base_template(*, badge: str, title: str, body_html: str, footer_note: str = "") -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: {BG_COLOR}; margin: 0; padding: 0; }}
            .wrapper {{ padding: 40px 20px; }}
            .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
            .header {{ padding: 32px 32px 10px 32px; text-align: left; }}
            .content {{ padding: 0 32px 32px 32px; color: #374151; line-height: 1.6; }}
            .button-container {{ padding: 20px 0; text-align: center; }}
            .button {{ background-color: {BRAND_COLOR}; color: #ffffff !important; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; display: inline-block; font-size: 16px; }}
            .footer {{ padding: 24px; text-align: center; color: #9ca3af; font-size: 13px; border-top: 1px solid #f3f4f6; }}
            .badge {{ display: inline-block; background: #eef2ff; color: {BRAND_COLOR}; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; margin-bottom: 16px; }}
            @media (max-width: 600px) {{ .wrapper {{ padding: 20px 10px; }} }}
        </style>
    </head>
    <body>
        <div class="wrapper">
            <div class="container">
                <div class="header">
                    <div class="badge">{badge}</div>
                    <h1 style="margin: 0; font-size: 24px; color: #111827;">{title}</h1>
                </div>
                <div class="content">
                    {body_html}
                </div>
                <div class="footer">
                    {footer_note or f"If you didn't expect this email, you can safely ignore it."}<br/>
                    &copy; 2026 {APP_NAME}. All rights reserved.
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def _send_email(*, to_email: str, subject: str, html: str) -> None:
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html,
        })
        logger.info(f"Email sent to {to_email} | subject: {subject}")

    except Exception as e:
        logger.info(f"Failed to send email to {to_email}: {e}")
        raise

    
        
        
def send_first_login_email(
        to_email: str,
        first_name: str,
        tenant_id: str, 
        login_link: str
    ) -> None:
    body = f"""
        <p style="font-size: 16px;">You've been invited to join <strong>{tenant_id}</strong> on our {APP_NAME} Platform.
        To get started, set your password and secure your account.</p>
        <div class="button-container">
            <a href="{login_link}" class="button">Set Up Your Account</a>
        </div>
        <p style="font-size: 14px; color: #6b7280;">
            <strong>Security Note:</strong> This link expires in 24 hours.
            If it expires, request a new one from the login page.
        </p>
    """
    _send_email(
        to_email=to_email,
        subject= f"Welcome to {tenant_id} - Finish setting up your account",
        html=_base_template(
            badge=f"{tenant_id.upper()} Knowledge Space",
            title=f"Welcome, {first_name}!",
            body_html=body
        )
    )

    
    

# Email: Password Reset
def send_password_reset_email(
        to_email: str,
        first_name: str,
        reset_link: str,
) -> None:
    body = f""" 
           <p style="font-size: 16px;">We received a request to reset the password for your account.</p>
        <div class="button-container">
            <a href="{reset_link}" class="button">Reset Password</a>
        </div>
        <p style="font-size: 14px; color: #6b7280;">
            <strong>Security Note:</strong> This link expires in 1 hour.
            If you didn't request a reset, you can safely ignore this email.
        </p>
        """
    _send_email(
        to_email=to_email,
        subject="Reset your password",
        html=_base_template(
            badge="SECURITY",
            title=f"Password Reset, {first_name}",
            body_html=body,
        ),
    )


# Email: Generic Notification
def send_notification_email(
        to_email: str,
        first_name: str,
        tenant_id: str,
        subject: str,
        message: str,
        cta_label: Optional[str] = None,
        cta_link: Optional[str] = None,
) -> None:
    cta_html = f"""
        <div class="button-container">
            <a href="{cta_link}" class="button">{cta_label}</a>
        </div>
    """ if cta_label and cta_link else ""

    body = f"""
        <p style="font-size: 16px;">{message}</p>
        {cta_html}
    """
    _send_email(
        to_email=to_email,
        subject=subject,
        html=_base_template(
            badge=f"{tenant_id.upper()} {APP_NAME}",
            title=f"Hi, {first_name}!",
            body_html=body,
        ),
    )    


