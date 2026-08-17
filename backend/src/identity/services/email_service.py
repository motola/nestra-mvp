from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Mail, To

from config import get_settings


def _load_template(template_name: str) -> str:
    """Load HTML email template from backend/src/email_templates/"""
    template_path = (
        Path(__file__).parent.parent.parent / "email_templates" / f"{template_name}.html"
    )
    return template_path.read_text()


def _replace_template_vars(
    content: str,
    first_name: str = "there",
    app_url: str = "",
    verify_url: str = "",
    reset_url: str = "",
    code: str = "",
    expiry_minutes: int = 24,
    support_email: str = "support@alphacon.io",
    company_address: str = "London, UK",
    docs_url: str = "",
    preferences_url: str = "",
    request_time: str = "",
    request_device: str = "Unknown",
    request_ip: str = "Unknown",
) -> str:
    """Replace template variables with actual values."""
    replacements = {
        "{{ first_name }}": first_name,
        "{{ app_url }}": app_url,
        "{{ verify_url }}": verify_url,
        "{{ reset_url }}": reset_url,
        "{{ code }}": code,
        "{{ expiry_minutes }}": str(expiry_minutes),
        "{{ support_email }}": support_email,
        "{{ company_address }}": company_address,
        "{{ docs_url }}": docs_url,
        "{{ preferences_url }}": preferences_url,
        "{{ request_time }}": request_time,
        "{{ request_device }}": request_device,
        "{{ request_ip }}": request_ip,
        "{{ year }}": str(datetime.now().year),
    }

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    return content


class EmailService:
    def __init__(self) -> None:
        settings = get_settings()
        self.sendgrid_client = SendGridAPIClient(settings.sendgrid_api_key)
        self.frontend_url = settings.frontend_url
        self.from_email = Email("founders@alphacon.ai", "Alphacon AI")

    async def send_welcome_email(
        self,
        user_email: str,
        first_name: str,
    ) -> None:
        """Send welcome email after successful signup."""
        html_content = _load_template("welcome")
        app_url = f"{self.frontend_url}/properties"
        docs_url = f"{self.frontend_url}/docs"
        preferences_url = f"{self.frontend_url}/settings/preferences"

        html_content = _replace_template_vars(
            html_content,
            first_name=first_name,
            app_url=app_url,
            docs_url=docs_url,
            preferences_url=preferences_url,
        )

        message = Mail(
            from_email=self.from_email,
            to_emails=To(user_email),
            subject=f"Welcome to Alphacon AI, {first_name}",
            html_content=html_content,
        )

        try:
            self.sendgrid_client.send(message)
        except Exception as e:
            raise ValueError(f"Failed to send welcome email: {e}") from e

    async def send_verification_email(
        self,
        user_email: str,
        first_name: str,
        verify_token: str,
        expiry_minutes: int = 24,
    ) -> None:
        """Send email verification with token link and code."""
        html_content = _load_template("verify_email")
        verify_url = f"{self.frontend_url}/verify-email?token={verify_token}"

        html_content = _replace_template_vars(
            html_content,
            first_name=first_name,
            verify_url=verify_url,
            code=verify_token[:6].upper(),
            expiry_minutes=expiry_minutes,
        )

        message = Mail(
            from_email=self.from_email,
            to_emails=To(user_email),
            subject="Verify Your Alphacon AI Email",
            html_content=html_content,
        )

        try:
            self.sendgrid_client.send(message)
        except Exception as e:
            raise ValueError(f"Failed to send verification email: {e}") from e

    async def send_password_reset_email(
        self,
        user_email: str,
        first_name: str,
        reset_token: str,
        expiry_minutes: int = 60,
        request_ip: str = "Unknown",
        request_device: str = "Unknown",
    ) -> None:
        """Send password reset email with token link and request details."""
        html_content = _load_template("reset_password")
        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
        request_time = datetime.now().strftime("%Y-%m-%d %H:%M %Z")

        html_content = _replace_template_vars(
            html_content,
            first_name=first_name,
            reset_url=reset_url,
            expiry_minutes=expiry_minutes,
            request_time=request_time,
            request_device=request_device,
            request_ip=request_ip,
        )

        message = Mail(
            from_email=self.from_email,
            to_emails=To(user_email),
            subject="Reset Your Alphacon AI Password",
            html_content=html_content,
        )

        try:
            self.sendgrid_client.send(message)
        except Exception as e:
            raise ValueError(f"Failed to send password reset email: {e}") from e

    async def send_password_reset_confirmation_email(
        self,
        user_email: str,
        first_name: str,
    ) -> None:
        """Send password reset confirmation email."""
        subject = "Password Reset Confirmed"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Hi {first_name},</h2>
                    <p>Your password has been successfully reset.</p>
                    <p>If you did not request this change, please contact support immediately.</p>
                    <p>You can now sign in with your new password.</p>
                    <p>Best regards,<br/>Alphacon AI Team</p>
                </div>
            </body>
        </html>
        """

        message = Mail(
            from_email=self.from_email,
            to_emails=To(user_email),
            subject=subject,
            html_content=html_content,
        )

        try:
            self.sendgrid_client.send(message)
        except Exception as e:
            raise ValueError(f"Failed to send password reset confirmation email: {e}") from e


def get_email_service() -> EmailService:
    """Dependency injection for EmailService."""
    return EmailService()
