"""
Player Verification Model.
"""
from datetime import datetime
from app.extensions import db


class PlayerVerificationModel(db.Model):
    """Handles player requests to link their profile to a FIDE ID."""
    __tablename__ = "player_verifications"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = db.Column(db.Integer, primary_key=True)
    player_profile_id = db.Column(db.Integer, db.ForeignKey("player_profiles.id"), nullable=False, index=True)
    requested_fide_id = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    # Phase 5: Per-aspect manual verification tracking
    fide_id_verified = db.Column(db.Boolean, nullable=True)  # True=verified, False=rejected, None=not reviewed
    fide_id_notes = db.Column(db.Text, nullable=True)
    fide_id_reviewed_at = db.Column(db.DateTime, nullable=True)
    fide_id_reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    dob_verified = db.Column(db.Boolean, nullable=True)
    dob_notes = db.Column(db.Text, nullable=True)
    dob_reviewed_at = db.Column(db.DateTime, nullable=True)
    dob_reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    photo_verified = db.Column(db.Boolean, nullable=True)
    photo_notes = db.Column(db.Text, nullable=True)
    photo_reviewed_at = db.Column(db.DateTime, nullable=True)
    photo_reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    player_profile = db.relationship("PlayerProfileModel", foreign_keys=[player_profile_id])
    reviewer = db.relationship("UserModel", foreign_keys=[reviewer_id])
    fide_id_reviewer = db.relationship("UserModel", foreign_keys=[fide_id_reviewer_id])
    dob_reviewer = db.relationship("UserModel", foreign_keys=[dob_reviewer_id])
    photo_reviewer = db.relationship("UserModel", foreign_keys=[photo_reviewer_id])