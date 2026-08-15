from __future__ import annotations

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


class EmailService:
    def __init__(self) -> None:
        settings = get_settings()
        self.sendgrid_client = SendGridAPIClient(settings.sendgrid_api_key)
        self.frontend_url = settings.frontend_url
        self.from_email = Email("noreply@nestra-mvp.com", "Nestra MVP")

    async def send_password_reset_email(self, user_email: str, reset_token: str) -> None:
        """Send password reset email with token link."""
        html_content = _load_template("reset_password")
        reset_link = f"{self.frontend_url}/auth/reset?token={reset_token}"
        html_content = html_content.replace("{{ reset_link }}", reset_link)

        message = Mail(
            from_email=self.from_email,
            to_emails=To(user_email),
            subject="Reset Your Nestra Password",
            html_content=html_content,
        )

        try:
            self.sendgrid_client.send(message)
        except Exception as e:
            raise ValueError(f"Failed to send password reset email: {e}") from e

    async def send_verification_email(self, user_email: str, verify_token: str) -> None:
        """Send email verification email with token link."""
        html_content = _load_template("verify_email")
        verify_link = f"{self.frontend_url}/auth/verify?token={verify_token}"
        html_content = html_content.replace("{{ verify_link }}", verify_link)

        message = Mail(
            from_email=self.from_email,
            to_emails=To(user_email),
            subject="Verify Your Nestra Email",
            html_content=html_content,
        )

        try:
            self.sendgrid_client.send(message)
        except Exception as e:
            raise ValueError(f"Failed to send verification email: {e}") from e


def get_email_service() -> EmailService:
    """Dependency injection for EmailService."""
    return EmailService()
