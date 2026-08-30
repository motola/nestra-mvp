"""Intelligence and AI endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from db import SessionLocal
from dependencies import UserDep
from identity.api.schemas import (
    AiActionResponse,
    AiChatRequest,
    AiChatResponse,
    AiReportResponse,
    UserConsentRequest,
    UserConsentResponse,
)
from identity.repository.models import (
    AiActionLogModel,
    AiConversationModel,
    AiGeneratedReportModel,
    UserConsentModel,
    UserModel,
)

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.post("/consent", response_model=UserConsentResponse)
async def set_user_consent(
    body: UserConsentRequest,
    user_id: UserDep,
) -> UserConsentResponse:
    """Set user consent for AI data access."""
    now = datetime.now(tz=UTC)

    async with SessionLocal() as session:
        # Check if consent already exists
        result = await session.execute(
            select(UserConsentModel).where(UserConsentModel.user_id == user_id)
        )
        consent = result.scalar_one_or_none()

        if consent:
            # Update existing consent
            consent.portfolio_access = body.portfolio_access
            consent.device_access = body.device_access
            consent.historical_data_access = body.historical_data_access
            consent.updated_at = now
        else:
            # Create new consent
            consent = UserConsentModel(
                user_id=user_id,
                portfolio_access=body.portfolio_access,
                device_access=body.device_access,
                historical_data_access=body.historical_data_access,
                consented_at=now,
                updated_at=now,
            )
            session.add(consent)

        await session.commit()

        return UserConsentResponse(
            portfolio_access=consent.portfolio_access,
            device_access=consent.device_access,
            historical_data_access=consent.historical_data_access,
        )


@router.get("/consent", response_model=UserConsentResponse)
async def get_user_consent(
    user_id: UserDep,
) -> UserConsentResponse:
    """Get user consent status for AI data access."""
    async with SessionLocal() as session:
        result = await session.execute(
            select(UserConsentModel).where(UserConsentModel.user_id == user_id)
        )
        consent = result.scalar_one_or_none()

        if not consent:
            # Return default (no access granted)
            return UserConsentResponse(
                portfolio_access=False,
                device_access=False,
                historical_data_access=False,
            )

        return UserConsentResponse(
            portfolio_access=consent.portfolio_access,
            device_access=consent.device_access,
            historical_data_access=consent.historical_data_access,
        )


@router.post("/chat", response_model=AiChatResponse)
async def chat_with_ai(
    body: AiChatRequest,
    user_id: UserDep,
) -> AiChatResponse:
    """Chat with Claude AI.

    Claude can:
    - Provide conversational responses
    - Analyze portfolio data (if user consents)
    - Make recommendations (if user consents)
    - Create reports (if user consents)
    - Send notifications (if requested)

    Actions are reflected across the dashboard.
    """
    now = datetime.now(tz=UTC)

    async with SessionLocal() as session:
        # Check user consent
        consent_result = await session.execute(
            select(UserConsentModel).where(UserConsentModel.user_id == user_id)
        )
        consent = consent_result.scalar_one_or_none()

        # Get user's organization
        user_result = await session.execute(select(UserModel).where(UserModel.id == user_id))
        db_user = user_result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # For now, return mock response
        # In production, this would call Claude API with Anthropic SDK
        ai_response = (
            "I'm Claude, your AI assistant. "
            "I can help you with portfolio analysis, recommendations, and more. "
            f"Message received: '{body.message}'"
        )

        actions: list[AiActionResponse] = []

        # If user mentioned "report" or "analyze", create an action
        if "report" in body.message.lower() or "analyze" in body.message.lower():
            if consent and consent.portfolio_access:
                action = AiActionResponse(
                    action_type="create_report",
                    status="pending",
                    details="Generating portfolio analysis report...",
                )
                actions.append(action)

                # Log the action
                action_log = AiActionLogModel(
                    user_id=user_id,
                    action_type="create_report",
                    action_status="pending",
                    details="Portfolio analysis report requested",
                    created_at=now,
                )
                session.add(action_log)
            else:
                ai_response += (
                    "\n\nI noticed you asked for a report, but I need your consent to access "
                    "your portfolio data. Please enable portfolio access in settings."
                )

        # If user mentioned "notify", create a notification action
        if "notify" in body.message.lower() or "notification" in body.message.lower():
            action = AiActionResponse(
                action_type="send_notification",
                status="pending",
                details="Preparing notification...",
            )
            actions.append(action)

            # Log the action
            action_log = AiActionLogModel(
                user_id=user_id,
                action_type="send_notification",
                action_status="pending",
                details="Notification action triggered",
                created_at=now,
            )
            session.add(action_log)

        # Store conversation
        conversation = AiConversationModel(
            user_id=user_id,
            organization_id=user_id,  # Using user_id as placeholder for org_id
            user_message=body.message,
            ai_response=ai_response,
            created_at=now,
        )
        session.add(conversation)

        await session.commit()

        return AiChatResponse(
            response=ai_response,
            actions=actions,
        )


@router.get("/reports", response_model=list[AiReportResponse])
async def get_ai_reports(
    user_id: UserDep,
) -> list[AiReportResponse]:
    """Get all AI-generated reports for the user."""
    async with SessionLocal() as session:
        result = await session.execute(
            select(AiGeneratedReportModel)
            .where(AiGeneratedReportModel.user_id == user_id)
            .order_by(AiGeneratedReportModel.created_at.desc())
        )
        reports = result.scalars().all()

        return [
            AiReportResponse(
                id=report.id,
                title=report.title,
                content=report.content,
                report_type=report.report_type,
                created_at=report.created_at.isoformat(),
            )
            for report in reports
        ]
