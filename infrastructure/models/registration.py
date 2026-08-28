"""
Registration and Payment Models.
"""
from datetime import datetime
from app.extensions import db


class PromoCodeModel(db.Model):
    __tablename__ = "promo_codes"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=True)  # null = global
    code = db.Column(db.String(50), nullable=False, index=True)
    discount_percent = db.Column(db.Integer, nullable=False, default=0)
    valid_until = db.Column(db.DateTime, nullable=True)
    max_uses = db.Column(db.Integer, nullable=True)  # null = unlimited
    used_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tournament = db.relationship("TournamentModel", backref="promo_codes")


class RegistrationModel(db.Model):
    __tablename__ = "registrations"
    __table_args__ = (
        db.UniqueConstraint("tournament_id", "player_profile_id", name="uq_registration_tournament_profile"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    player_profile_id = db.Column(db.Integer, db.ForeignKey("player_profiles.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Who submitted the request

    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected, withdrawn, payment_pending
    final_price = db.Column(db.Integer, default=0)
    pricing_breakdown = db.Column(db.Text, default="{}")  # JSON string of pricing details
    rejection_reason = db.Column(db.String(255), nullable=True)

    # Phase 5: Payment Method and Receipt
    payment_method = db.Column(db.String(20), default="online")  # online, transfer
    receipt_path = db.Column(db.String(255), nullable=True)

    promo_code_id = db.Column(db.Integer, db.ForeignKey("promo_codes.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Eager loading to prevent N+1 queries on registration management pages
    tournament = db.relationship("TournamentModel", backref="registrations", lazy="joined")
    profile = db.relationship("PlayerProfileModel", backref="registrations", lazy="joined")
    user = db.relationship("UserModel", backref="registrations")
    promo_code = db.relationship("PromoCodeModel", backref="registrations")
    payments = db.relationship("PaymentModel", backref="registration", cascade="all, delete-orphan")


class PaymentModel(db.Model):
    __tablename__ = "payments"
    __table_args__ = (
        db.UniqueConstraint("authority", name="uq_payment_authority"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey("registrations.id"), nullable=False, index=True)

    amount = db.Column(db.Integer, nullable=False)  # Amount in Toman
    status = db.Column(db.String(20), default="pending")  # pending, cancelled, successful, failed
    rejection_reason = db.Column(db.String(255), nullable=True)  # New Field
    gateway = db.Column(db.String(50), default="zarinpal")
    authority = db.Column(db.String(100), nullable=True, index=True)
    ref_id = db.Column(db.String(100), nullable=True, index=True)
    card_mask = db.Column(db.String(20), nullable=True)

    gateway_metadata = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)