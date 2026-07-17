import unittest

from identity.repository.models import (
    OrganizationModel,
    OrgMembershipModel,
    PortfolioModel,
    SessionModel,
    UserModel,
)
from utility.db import Base


class TestOrmModelMetadata(unittest.TestCase):
    """Verifies ORM model definitions without requiring a database connection."""

    def test_organization_tablename(self) -> None:
        self.assertEqual(OrganizationModel.__tablename__, "organizations")

    def test_portfolio_tablename(self) -> None:
        self.assertEqual(PortfolioModel.__tablename__, "portfolios")

    def test_user_tablename(self) -> None:
        self.assertEqual(UserModel.__tablename__, "users")

    def test_org_membership_tablename(self) -> None:
        self.assertEqual(OrgMembershipModel.__tablename__, "org_memberships")

    def test_session_tablename(self) -> None:
        self.assertEqual(SessionModel.__tablename__, "sessions")

    def test_all_models_share_metadata(self) -> None:
        tables = Base.metadata.tables
        for name in ("organizations", "portfolios", "users", "org_memberships", "sessions"):
            self.assertIn(name, tables)

    def test_organization_columns(self) -> None:
        cols = {c.name for c in OrganizationModel.__table__.columns}
        self.assertIn("id", cols)
        self.assertIn("slug", cols)
        self.assertIn("status", cols)
        self.assertIn("subscription_tier", cols)

    def test_portfolio_unique_constraint_exists(self) -> None:
        constraints = {c.name for c in PortfolioModel.__table__.constraints}
        self.assertIn("uq_portfolio_org_name", constraints)

    def test_org_membership_unique_constraint_exists(self) -> None:
        constraints = {c.name for c in OrgMembershipModel.__table__.constraints}
        self.assertIn("uq_org_membership", constraints)

    def test_user_email_is_unique(self) -> None:
        email_col = UserModel.__table__.columns["email"]
        self.assertTrue(email_col.unique)

    def test_session_has_expires_at(self) -> None:
        cols = {c.name for c in SessionModel.__table__.columns}
        self.assertIn("expires_at", cols)


if __name__ == "__main__":
    unittest.main()
