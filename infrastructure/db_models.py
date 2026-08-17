# infrastructure/db_models.py
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
    is_admin = db.Column(db.Boolean, default=False) # Global system admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    roles = db.relationship("UserRoleModel", backref="user", cascade="all, delete-orphan")
    profile = db.relationship("PlayerProfileModel", backref="user", uselist=False)

    # ── Password Security ──
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # ── RBAC Helper Properties ──
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


class FidePlayerModel(db.Model):
    __tablename__ = "fide_players"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    fide_id = db.Column(db.String(20), primary_key=True)
    first_name = db.Column(db.String(100), default="")
    last_name = db.Column(db.String(100), nullable=False, index=True)
    gender = db.Column(db.String(1), default="M")
    federation = db.Column(db.String(5), default="")
    fide_title = db.Column(db.String(5), default="")
    rating_standard = db.Column(db.Integer, default=0)
    rating_rapid = db.Column(db.Integer, default=0)
    rating_blitz = db.Column(db.Integer, default=0)
    birth_year = db.Column(db.String(4), default="")
    k_factor = db.Column(db.Integer, default=20)
    # To track which monthly dataset this data belongs to
    dataset_date = db.Column(db.Date, nullable=True)


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    national_id = db.Column(db.String(10), nullable=True)
    bank_card_number = db.Column(db.String(20), nullable=True)
    bank_account_name = db.Column(db.String(100), nullable=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class PromoCodeModel(db.Model):
    __tablename__ = "promo_codes"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=True) # null = global
    code = db.Column(db.String(50), nullable=False, index=True)
    discount_percent = db.Column(db.Integer, nullable=False, default=0)
    valid_until = db.Column(db.DateTime, nullable=True)
    max_uses = db.Column(db.Integer, nullable=True) # null = unlimited
    used_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tournament = db.relationship("TournamentModel", backref="promo_codes")

class TournamentModel(db.Model):
    __tablename__ = "tournaments"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(8), unique=True, nullable=False, index=True)
    admin_code = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), default="")
    federation = db.Column(db.String(5), default="IRI")
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    time_control_type = db.Column(db.String(20), default="standard")
    time_control_description = db.Column(db.String(100), default="")
    total_rounds = db.Column(db.Integer, default=5)
    current_round = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default="setup")
    chief_arbiter = db.Column(db.String(100), default="")
    arbiter = db.Column(db.String(100), default="")
    tiebreak_rules = db.Column(
        db.Text,
        default='["buchholz_cut1","buchholz","sonneborn_berger","progressive"]'
    )
    cumulative_age_category = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # New: Link to organizer
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # ── Phase 3: Registration & Pricing Fields ──
    base_price = db.Column(db.Integer, default=0)
    registration_deadline = db.Column(db.DateTime, nullable=True)
    max_players = db.Column(db.Integer, nullable=True) # null = unlimited
    
    # JSON fields for flexible discount rules
    early_bird_config = db.Column(db.Text, default='{"deadline": null, "percent": 0}')
    veteran_config = db.Column(db.Text, default='{"min_age": 0, "percent": 0}')
    women_discount_percent = db.Column(db.Integer, default=0)
    title_discounts = db.Column(db.Text, default='{"GM": 100, "IM": 50, "FM": 25, "WGM": 100, "WIM": 50, "WFM": 25}')

    rounds = db.relationship("RoundModel", backref="tournament", lazy="select")


class TournamentParticipantModel(db.Model):
    __tablename__ = "tournament_participants"
    __table_args__ = (
        db.UniqueConstraint("tournament_id", "player_profile_id", name="uq_participant_tournament_profile"),
        db.UniqueConstraint("tournament_id", "start_number", name="uq_participant_tournament_startnum"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    player_profile_id = db.Column(db.Integer, db.ForeignKey("player_profiles.id"), nullable=False)
    
    start_number = db.Column(db.Integer, nullable=False)
    pairing_no = db.Column(db.Integer, nullable=True) # FIDE fixed ranking number
    
    # Historical Snapshots (Preserved at time of entry)
    rating_snapshot = db.Column(db.Integer, default=0)
    fide_title_snapshot = db.Column(db.String(5), default="")
    k_factor = db.Column(db.Integer, default=20)
    age_category = db.Column(db.String(10), default="")
    custom_category = db.Column(db.String(50), default="")
    
    # State
    status = db.Column(db.String(20), default="active") # active, withdrawn
    joined_from_round = db.Column(db.Integer, default=1)
    withdrawn_at_round = db.Column(db.Integer, default=0)
    
    # Incremental fields for pairing engine
    points = db.Column(db.Float, default=0.0)
    color_history = db.Column(db.String(255), default="")
    float_history = db.Column(db.String(255), default="")
    received_bye = db.Column(db.Boolean, default=False)
    
    profile = db.relationship("PlayerProfileModel", lazy="joined")
    
    @property
    def full_name(self):
        return self.profile.full_name if self.profile else "Unknown"

    @property
    def rating(self):
        return self.rating_snapshot

    @property
    def ranking_label(self):
        return self.pairing_no or self.start_number


class RoundModel(db.Model):
    __tablename__ = "rounds"
    __table_args__ = (
        db.UniqueConstraint("tournament_id", "round_number", name="uq_round_tournament_number"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)

    pairings = db.relationship("PairingModel", backref="round", lazy="select", cascade="all, delete-orphan")


class PairingModel(db.Model):
    __tablename__ = "pairings"
    __table_args__ = (
        db.UniqueConstraint("round_id", "board_number", name="uq_pairing_round_board"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey("rounds.id"), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    board_number = db.Column(db.Integer, nullable=False)
    
    white_participant_id = db.Column(db.Integer, db.ForeignKey("tournament_participants.id"), nullable=True)
    black_participant_id = db.Column(db.Integer, db.ForeignKey("tournament_participants.id"), nullable=True)
    
    result = db.Column(db.String(10), default="")
    white_float = db.Column(db.String(1), default="")
    black_float = db.Column(db.String(1), default="")
    is_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    white_participant = db.relationship("TournamentParticipantModel", foreign_keys=[white_participant_id], lazy="joined")
    black_participant = db.relationship("TournamentParticipantModel", foreign_keys=[black_participant_id], lazy="joined")

    @property
    def white_player_name(self):
        return self.white_participant.full_name if self.white_participant else "-"

    @property
    def black_player_name(self):
        return self.black_participant.full_name if self.black_participant else None


class ByeRequestModel(db.Model):
    __tablename__ = "bye_requests"
    __table_args__ = (
        db.UniqueConstraint("tournament_id", "participant_id", "for_round", name="uq_bye_tournament_participant_round"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey("tournament_participants.id"), nullable=False)
    bye_type = db.Column(db.String(10), default="half-bye")
    for_round = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    participant = db.relationship("TournamentParticipantModel", foreign_keys=[participant_id])


class ManualPairingModel(db.Model):
    __tablename__ = "manual_pairings"
    __table_args__ = (
        db.UniqueConstraint("tournament_id", "round_number", "white_participant_id", name="uq_manual_pairing_white"),
        db.UniqueConstraint("tournament_id", "round_number", "black_participant_id", name="uq_manual_pairing_black"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    round_number = db.Column(db.Integer, nullable=False)
    white_participant_id = db.Column(db.Integer, db.ForeignKey("tournament_participants.id"), nullable=False)
    black_participant_id = db.Column(db.Integer, db.ForeignKey("tournament_participants.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    white_participant = db.relationship("TournamentParticipantModel", foreign_keys=[white_participant_id], lazy="joined")
    black_participant = db.relationship("TournamentParticipantModel", foreign_keys=[black_participant_id], lazy="joined")


class RegistrationModel(db.Model):
    __tablename__ = "registrations"
    __table_args__ = (
        db.UniqueConstraint("tournament_id", "player_profile_id", name="uq_registration_tournament_profile"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    player_profile_id = db.Column(db.Integer, db.ForeignKey("player_profiles.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True) # Who submitted the request
    
    status = db.Column(db.String(20), default="pending") # pending, approved, rejected, withdrawn, payment_pending
    final_price = db.Column(db.Integer, default=0)
    pricing_breakdown = db.Column(db.Text, default="{}") # JSON string of pricing details
    
    promo_code_id = db.Column(db.Integer, db.ForeignKey("promo_codes.id"), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tournament = db.relationship("TournamentModel", backref="registrations")
    profile = db.relationship("PlayerProfileModel", backref="registrations")
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
    
    amount = db.Column(db.Integer, nullable=False)  # مبلغ به تومان
    status = db.Column(db.String(20), default="pending") # pending, successful, failed, cancelled
    
    gateway = db.Column(db.String(50), default="zarinpal")
    authority = db.Column(db.String(100), nullable=True, index=True)
    ref_id = db.Column(db.String(100), nullable=True, index=True)
    card_mask = db.Column(db.String(20), nullable=True) 
    
    gateway_metadata = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)


class TournamentStaffModel(db.Model):
    __tablename__ = "tournament_staff"
    __table_args__ = (
        db.UniqueConstraint("tournament_id", "user_id", name="uq_tournament_staff"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(20), default="arbiter")
    
    # New Fields for Invitation System
    status = db.Column(db.String(20), default="pending") # pending, accepted, rejected
    invited_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    tournament = db.relationship("TournamentModel", backref="staff_members")
    user = db.relationship("UserModel", foreign_keys=[user_id], backref="staff_assignments")
    inviter = db.relationship("UserModel", foreign_keys=[invited_by], backref="sent_invitations")