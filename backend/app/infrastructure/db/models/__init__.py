"""Model registry for Alembic autogeneration."""

from app.infrastructure.db.models.auth_session import AuthSession
from app.infrastructure.db.models.user import User

__all__ = ["User", "AuthSession"]
