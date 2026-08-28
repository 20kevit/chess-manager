"""
User and Authentication Models.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class UserModel(db.Model, UserMixin):
    __tablename__ = "users"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)  # Global system admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship("UserRoleModel", backref="user", cascade="all, delete-orphan")
    profile = db.relationship("PlayerProfileModel", backref="user", uselist=False)

    # Phase 9F: Telegram Integration Fields
    telegram_chat_id = db.Column(db.String(50), nullable=True, index=True)
    telegram_link_token = db.Column(db.String(100), nullable=True)
    telegram_link_expires_at = db.Column(db.DateTime, nullable=True)

    # Phase 9G: Bale Integration Fields
    bale_chat_id = db.Column(db.String(50), nullable=True, index=True)
    bale_link_token = db.Column(db.String(100), nullable=True)
    bale_link_expires_at = db.Column(db.DateTime, nullable=True)

    # Password Security
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # RBAC Helper Properties
    @property
    def role_names(self):
        """Returns a list of role names for this user."""
        return [role.role for role in self.roles]

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        if self.is_admin:
            return True
        return role_name in self.role_names

    def has_any_role(self, roles: list) -> bool:
        """Check if user has any of the specified roles."""
        if self.is_admin:
            return True
        return any(role in self.role_names for role in roles)


class UserRoleModel(db.Model):
    __tablename__ = "user_roles"
    __table_args__ = (
        db.UniqueConstraint("user_id", "role", name="uq_user_role"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # System roles: 'player', 'organizer', 'arbiter'
    role = db.Column(db.String(50), nullable=False)