"""Identity & Access enumerations.

Stored as plain strings in the database (no native Postgres enum types) to keep
migrations and Row-Level Security policies simple. Membership records carry a
role drawn from these closed sets.
"""

from __future__ import annotations

from enum import StrEnum


class OrgRole(StrEnum):
    OWNER = "OWNER"
    ORG_ADMIN = "ORG_ADMIN"
    BILLING = "BILLING"


class PortfolioRole(StrEnum):
    PORTFOLIO_ADMIN = "PORTFOLIO_ADMIN"
    PORTFOLIO_MANAGER = "PORTFOLIO_MANAGER"
    PORTFOLIO_MEMBER = "PORTFOLIO_MEMBER"
    PORTFOLIO_VIEWER = "PORTFOLIO_VIEWER"


class PropertyRole(StrEnum):
    PROPERTY_MANAGER = "PROPERTY_MANAGER"
    OPERATOR = "OPERATOR"
    CONTRACTOR = "CONTRACTOR"
    PROPERTY_VIEWER = "PROPERTY_VIEWER"


class AuthMethod(StrEnum):
    PASSWORD = "PASSWORD"
    MAGIC_LINK = "MAGIC_LINK"
    GOOGLE_SSO = "GOOGLE_SSO"
    APPLE_SSO = "APPLE_SSO"
