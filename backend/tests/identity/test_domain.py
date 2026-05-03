import unittest
from datetime import UTC, datetime
from uuid import uuid4

from identity.domain.organization import Organization, Portfolio
from identity.domain.roles import (
    AuthMethod,
    OrgRole,
    OrgStatus,
    PortfolioRole,
    PropertyRole,
    SubscriptionTier,
    TenantRole,
)
from identity.domain.user import OrgMembership, Session, User


def _now() -> datetime:
    return datetime.now(tz=UTC)


class TestRoles(unittest.TestCase):
    def test_org_role_values(self) -> None:
        self.assertEqual(OrgRole.OWNER.value, "OWNER")
        self.assertEqual(OrgRole.ORG_ADMIN.value, "ORG_ADMIN")
        self.assertEqual(OrgRole.BILLING.value, "BILLING")

    def test_portfolio_role_values(self) -> None:
        roles = {r.value for r in PortfolioRole}
        self.assertIn("PORTFOLIO_ADMIN", roles)
        self.assertIn("PORTFOLIO_VIEWER", roles)

    def test_property_role_values(self) -> None:
        roles = {r.value for r in PropertyRole}
        self.assertIn("PROPERTY_MANAGER", roles)
        self.assertIn("CONTRACTOR", roles)

    def test_tenant_role_values(self) -> None:
        self.assertEqual(TenantRole.PRIMARY_TENANT.value, "PRIMARY_TENANT")
        self.assertEqual(TenantRole.CO_TENANT.value, "CO_TENANT")

    def test_auth_method_values(self) -> None:
        methods = {m.value for m in AuthMethod}
        self.assertIn("PASSWORD", methods)
        self.assertIn("MAGIC_LINK", methods)
        self.assertIn("GOOGLE_SSO", methods)
        self.assertIn("APPLE_SSO", methods)

    def test_org_status_values(self) -> None:
        statuses = {s.value for s in OrgStatus}
        self.assertIn("ACTIVE", statuses)
        self.assertIn("SUSPENDED", statuses)
        self.assertIn("CANCELLED", statuses)

    def test_subscription_tier_values(self) -> None:
        tiers = {t.value for t in SubscriptionTier}
        self.assertIn("STARTER", tiers)
        self.assertIn("PROFESSIONAL", tiers)
        self.assertIn("ENTERPRISE", tiers)

    def test_roles_are_str_enums(self) -> None:
        self.assertIsInstance(OrgRole.OWNER, str)
        self.assertIsInstance(AuthMethod.PASSWORD, str)


class TestOrganization(unittest.TestCase):
    def _make_org(self) -> Organization:
        return Organization(
            id=uuid4(),
            name="Acme Property Group",
            slug="acme-property",
            legal_name="Acme Property Group Ltd",
            status=OrgStatus.ACTIVE,
            subscription_tier=SubscriptionTier.PROFESSIONAL,
            created_at=_now(),
        )

    def test_create_organization(self) -> None:
        org = self._make_org()
        self.assertEqual(org.name, "Acme Property Group")
        self.assertEqual(org.status, OrgStatus.ACTIVE)
        self.assertEqual(org.subscription_tier, SubscriptionTier.PROFESSIONAL)

    def test_organization_slug(self) -> None:
        org = self._make_org()
        self.assertEqual(org.slug, "acme-property")


class TestPortfolio(unittest.TestCase):
    def test_create_portfolio_with_defaults(self) -> None:
        portfolio = Portfolio(
            id=uuid4(),
            organization_id=uuid4(),
            name="Downtown Properties",
            description="City centre portfolio",
            is_default=True,
            created_at=_now(),
        )
        self.assertIsNone(portfolio.archived_at)
        self.assertTrue(portfolio.is_default)

    def test_create_archived_portfolio(self) -> None:
        portfolio = Portfolio(
            id=uuid4(),
            organization_id=uuid4(),
            name="Legacy Portfolio",
            description="Retired properties",
            is_default=False,
            created_at=_now(),
            archived_at=_now(),
        )
        self.assertIsNotNone(portfolio.archived_at)


class TestUser(unittest.TestCase):
    def _make_user(self) -> User:
        return User(
            id=uuid4(),
            email="alice@example.com",
            full_name="Alice Smith",
            password_hash="$argon2id$hashed",
            auth_method=AuthMethod.PASSWORD,
        )

    def test_create_user_defaults(self) -> None:
        user = self._make_user()
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_tenant_only)
        self.assertIsNone(user.last_login_at)

    def test_user_can_raises(self) -> None:
        user = self._make_user()
        with self.assertRaises(NotImplementedError):
            user.can("read", object())


class TestOrgMembership(unittest.TestCase):
    def test_create_membership(self) -> None:
        membership = OrgMembership(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=uuid4(),
            org_role=OrgRole.ORG_ADMIN,
            joined_at=_now(),
        )
        self.assertIsNone(membership.invited_by)
        self.assertEqual(membership.org_role, OrgRole.ORG_ADMIN)

    def test_membership_with_inviter(self) -> None:
        inviter_id = uuid4()
        membership = OrgMembership(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=uuid4(),
            org_role=OrgRole.BILLING,
            joined_at=_now(),
            invited_by=inviter_id,
        )
        self.assertEqual(membership.invited_by, inviter_id)


class TestSession(unittest.TestCase):
    def test_create_session(self) -> None:
        now = _now()
        session = Session(
            id=uuid4(),
            user_id=uuid4(),
            active_organization_id=uuid4(),
            auth_method=AuthMethod.MAGIC_LINK,
            issued_at=now,
            expires_at=now,
        )
        self.assertEqual(session.auth_method, AuthMethod.MAGIC_LINK)


if __name__ == "__main__":
    unittest.main()
