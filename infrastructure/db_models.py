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

    # ── Phase 9F: Telegram Integration Fields ──
    telegram_chat_id = db.Column(db.String(50), nullable=True, index=True)
    telegram_link_token = db.Column(db.String(100), nullable=True)
    telegram_link_expires_at = db.Column(db.DateTime, nullable=True)

    # ── Phase 9G: Bale Integration Fields ──
    bale_chat_id = db.Column(db.String(50), nullable=True, index=True)
    bale_link_token = db.Column(db.String(100), nullable=True)
    bale_link_expires_at = db.Column(db.DateTime, nullable=True)

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
    fide_verification_status = db.Column(db.String(20), default="unverified") # unverified, pending, verified, rejected
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

    # Phase 5: Bank Transfer and Rulebook
    bank_card_number = db.Column(db.String(20), nullable=True)
    bank_account_name = db.Column(db.String(100), nullable=True)
    bank_transfer_notes = db.Column(db.Text, nullable=True)
    enable_online_payment = db.Column(db.Boolean, default=True)
    rulebook_text = db.Column(db.Text, nullable=True)

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
    
    # Phase 8D: Eager load tournament data to prevent N+1 queries
    tournament = db.relationship("TournamentModel", lazy="joined")

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
        # Phase 8E: Add indexes for faster cross-tournament game history queries
        db.Index("ix_pairing_white_participant_id", "white_participant_id"),
        db.Index("ix_pairing_black_participant_id", "black_participant_id"),
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
    
    # Phase 5: Payment Method and Receipt
    payment_method = db.Column(db.String(20), default="online") # online, transfer
    receipt_path = db.Column(db.String(255), nullable=True)
    
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
    status = db.Column(db.String(20), default="pending") # pending, approved, rejected, withdrawn, payment_pending
    rejection_reason = db.Column(db.String(255), nullable=True) # New Field    
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


class TempImportDataModel(db.Model):
    __tablename__ = "temp_import_data"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    data_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FidePlayerModel(db.Model):
    """FIDE player identity data (global ready, filtered by config during import)."""
    __tablename__ = "fide_players"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    fide_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sex = db.Column(db.String(1), default="M")
    federation = db.Column(db.String(5), default="", index=True)
    title = db.Column(db.String(10), default="")
    wtitle = db.Column(db.String(10), default="")
    otitle = db.Column(db.String(10), default="")
    foatitle = db.Column(db.String(10), default="")
    birth_year = db.Column(db.String(4), default="")
    inactive = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FideRatingModel(db.Model):
    """Monthly rating history for a FIDE player."""
    __tablename__ = "fide_ratings"
    __table_args__ = (
        db.UniqueConstraint("fide_id", "period", "rating_type", name="uq_fide_rating_period_type"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    fide_id = db.Column(db.String(20), db.ForeignKey("fide_players.fide_id"), nullable=False, index=True)
    period = db.Column(db.String(7), nullable=False, index=True)  # Format: YYYY-MM
    rating_type = db.Column(db.String(10), nullable=False)       # standard, rapid, blitz
    rating = db.Column(db.Integer, default=0)
    games = db.Column(db.Integer, default=0)
    k_factor = db.Column(db.Integer, default=20)


class FideImportModel(db.Model):
    """Tracks FIDE rating list downloads and imports."""
    __tablename__ = "fide_imports"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.String(7), nullable=False, index=True)  # YYYY-MM
    source_url = db.Column(db.String(255), nullable=True)
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    imported_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default="pending")  # pending, success, failed
    records_processed = db.Column(db.Integer, default=0)
    records_imported = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text, nullable=True)


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
    player_profile = db.relationship("PlayerProfileModel", foreign_keys=[player_profile_id])
    reviewer = db.relationship("UserModel", foreign_keys=[reviewer_id])


class NotificationModel(db.Model):
    """Stores user notifications for in-app display and external delivery tracking."""
    __tablename__ = "notifications"
    __table_args__ = (
        # Composite index for fast unread count queries
        db.Index("ix_notification_user_is_read", "user_id", "is_read"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link_url = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("UserModel", backref="notifications")


class NotificationPreferenceModel(db.Model):
    """Stores user preferences for different notification types and channels."""
    __tablename__ = "notification_preferences"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    # JSON format: {"REGISTRATION_APPROVED": {"web": true, "telegram": false}, ...}
    preferences_json = db.Column(db.Text, default="{}")
    
    user = db.relationship("UserModel", backref=db.backref("notif_pref", uselist=False))

    def is_channel_enabled(self, type_str: str, channel: str = "web") -> bool:
        """Checks if a specific channel is enabled for a notification type. Defaults to True."""
        import json
        prefs = json.loads(self.preferences_json or "{}")
        type_pref = prefs.get(type_str, {})
        return type_pref.get(channel, True) # Default to True if not specified