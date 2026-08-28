"""
Player Profile Model.
"""
from datetime import datetime
from app.extensions import db


class PlayerProfileModel(db.Model):
    __tablename__ = "player_profiles"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    fide_id = db.Column(db.String(20), nullable=True, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(1), default="M")
    birth_date = db.Column(db.Date, nullable=True)
    federation = db.Column(db.String(5), default="IRI")
    fide_title = db.Column(db.String(5), default="")
    # Phase 7: FIDE Verification Status
    fide_verification_status = db.Column(db.String(20), default="unverified")  # unverified, pending, verified, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    national_id = db.Column(db.String(10), nullable=True)
    bank_card_number = db.Column(db.String(20), nullable=True)
    bank_account_name = db.Column(db.String(100), nullable=True)
    # Canonical Iranian mobile number, normalized to 09xxxxxxxxx by
    # domain.registration.normalize_phone.
    phone = db.Column(db.String(20), nullable=True)

    # Private media (P0-C): bare filenames inside app-owned instance dirs,
    # served only through authenticated endpoints — never static/.
    photo_path = db.Column(db.String(255), nullable=True)
    id_document_path = db.Column(db.String(255), nullable=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"