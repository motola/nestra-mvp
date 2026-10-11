"""Exercise the authenticated Bluetooth integration flow against a real database."""

from __future__ import annotations

import asyncio
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import httpx
import jwt
from sqlalchemy import func, select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT / "src"))

from config import get_settings  # noqa: E402
from db import SessionLocal  # noqa: E402
from identity.domain.roles import OrgStatus, SubscriptionTier  # noqa: E402
from identity.repository.models import OrganizationModel, PortfolioModel  # noqa: E402
from integrations.models import IntegrationModel  # noqa: E402
from main import app  # noqa: E402
from property.repository.models import (  # noqa: E402
    AuditEventModel,
    DeviceIntegrationModel,
    DeviceModel,
    DevicePlacementModel,
    PropertyModel,
)


def _raise_for_status(response: httpx.Response) -> None:
    if not response.is_success:
        raise RuntimeError(
            f"{response.request.method} {response.request.url.path} returned "
            f"{response.status_code}: {response.text}"
        )


async def main() -> int:
    settings = get_settings()
    now = datetime.now(UTC)
    organization_id = uuid4()
    portfolio_id = uuid4()
    property_id = uuid4()
    user_id = uuid4()

    async with SessionLocal() as session:
        session.add(
            OrganizationModel(
                id=organization_id,
                name="Contract Test Organization",
                slug=f"contract-{organization_id}",
                legal_name="Contract Test Organization",
                status=OrgStatus.ACTIVE,
                subscription_tier=SubscriptionTier.STARTER,
                created_at=now,
            )
        )
        await session.flush()
        session.add(
            PortfolioModel(
                id=portfolio_id,
                organization_id=organization_id,
                name="Contract Test Portfolio",
                description="",
                is_default=True,
                created_at=now,
            )
        )
        await session.flush()
        session.add(
            PropertyModel(
                id=property_id,
                portfolio_id=portfolio_id,
                organization_id=organization_id,
                name="Contract Test Property",
                address="1 Contract Street",
                property_type="residential",
                units=1,
                timezone="UTC",
                created_at=now,
                updated_at=now,
            )
        )
        await session.commit()

    token = jwt.encode(
        {
            "sub": str(user_id),
            "org": str(organization_id),
            "iat": now.timestamp(),
            "exp": (now + timedelta(minutes=10)).timestamp(),
        },
        settings.secret_key,
        algorithm="HS256",
    )
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://contract.test"
    ) as client:
        integration_response = await client.post(
            "/integrations",
            headers=headers,
            json={
                "provider_id": "bluetooth",
                "connection_identifier": "local",
                "display_name": "Local Bluetooth",
            },
        )
        _raise_for_status(integration_response)
        integration_id = integration_response.json()["id"]

        list_response = await client.get("/integrations", headers=headers)
        _raise_for_status(list_response)
        if integration_id not in {item["id"] for item in list_response.json()}:
            raise RuntimeError("created integration was not returned by GET /integrations")

        device_payload = {
            "property_id": str(property_id),
            "name": "Contract Test Bluetooth Device",
            "connection_identifier": "browser-device-contract-test",
        }
        device_url = f"/integrations/{integration_id}/devices/bluetooth"
        device_response = await client.post(device_url, headers=headers, json=device_payload)
        _raise_for_status(device_response)
        device_id = device_response.json()[0]["id"]

        retry_response = await client.post(device_url, headers=headers, json=device_payload)
        _raise_for_status(retry_response)
        if retry_response.json()[0]["id"] != device_id:
            raise RuntimeError("retrying the same Bluetooth device created a duplicate device")

        property_devices_response = await client.get(
            f"/properties/{property_id}/devices", headers=headers
        )
        _raise_for_status(property_devices_response)
        if device_id not in {item["id"] for item in property_devices_response.json()}:
            raise RuntimeError("created device was not returned by the property device endpoint")

    async with SessionLocal() as session:
        checks = {
            "integration": select(func.count())
            .select_from(IntegrationModel)
            .where(IntegrationModel.id == integration_id),
            "device": select(func.count())
            .select_from(DeviceModel)
            .where(DeviceModel.id == device_id),
            "placement": select(func.count())
            .select_from(DevicePlacementModel)
            .where(DevicePlacementModel.device_id == device_id),
            "device integration": select(func.count())
            .select_from(DeviceIntegrationModel)
            .where(DeviceIntegrationModel.device_id == device_id),
        }
        for label, statement in checks.items():
            count = (await session.execute(statement)).scalar_one()
            if count != 1:
                raise RuntimeError(f"expected one {label} row, found {count}")

        audit_count = (
            await session.execute(
                select(func.count())
                .select_from(AuditEventModel)
                .where(AuditEventModel.resource_id == device_id)
            )
        ).scalar_one()
        if audit_count < 1:
            raise RuntimeError("device creation did not persist an audit event")

    print("Bluetooth integration contract passed end to end")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
