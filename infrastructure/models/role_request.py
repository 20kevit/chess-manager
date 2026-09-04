"""
User Role Request Model (Beta).

Global (non-tournament) role elevation requests for 'arbiter' and
'organizer'. 'player' is granted automatically at registration/profile
creation and 'admin' (is_admin) can never be requested — both are
rejected server-side by RoleRequestService.

One row per (user_id, role): a rejected request is recycled back to
pending on re-request so users can retry without duplicate rows.
"""
from datetime import datetime
from app.extensions import db


class UserRoleRequestModel(db.Model):
    __tablename__ = "user_role_requests"
    __table_args__ = (
        db.UniqueConstraint("user_id", "role", name="uq_user_role_request"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    # Requestable roles: 'arbiter', 'organizer' only (enforced in service).
    role = db.Column(db.String(50), nullable=False)
    # pending | approved | rejected
    status = db.Column(db.String(20), nullable=False, default="pending", index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
