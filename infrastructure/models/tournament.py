"""
Tournament and Competition Models.

Includes: Tournament, Round, Pairing, ByeRequest, ManualPairing
"""
from datetime import datetime
import json
from app.extensions import db


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

    # Link to organizer
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # Phase 3: Registration & Pricing Fields
    base_price = db.Column(db.Integer, default=0)
    registration_deadline = db.Column(db.DateTime, nullable=True)
    max_players = db.Column(db.Integer, nullable=True)  # null = unlimited

    # Phase 5: Bank Transfer and Rulebook
    bank_card_number = db.Column(db.String(20), nullable=True)
    bank_account_name = db.Column(db.String(100), nullable=True)
    bank_transfer_notes = db.Column(db.Text, nullable=True)
    enable_online_payment = db.Column(db.Boolean, default=True)
    rulebook_text = db.Column(db.Text, nullable=True)
    # P1-D: independent optional rulebook representations.
    # sections JSON: ordered list of {key,title,body} (domain/rulebook.py);
    # pdf_path: bare filename inside instance/uploads/rulebooks (public
    # content served through an unauthenticated endpoint — never static/).
    rulebook_sections = db.Column(db.Text, default="[]")
    rulebook_pdf_path = db.Column(db.String(255), nullable=True)

    # P1-F: per-tournament event-notification gates (JSON; absent key =
    # enabled). Semantics in application/notification_policy.py.
    notification_prefs = db.Column(db.Text, default="{}")

    # JSON fields for flexible discount rules
    early_bird_config = db.Column(db.Text, default='{"deadline": null, "percent": 0}')
    veteran_config = db.Column(db.Text, default='{"min_age": 0, "percent": 0}')
    women_discount_percent = db.Column(db.Integer, default=0)
    title_discounts = db.Column(db.Text, default='{"GM": 100, "IM": 50, "FM": 25, "WGM": 100, "WIM": 50, "WFM": 25}')

    # P0-D: organizer-configured entry requirements; JSON parsed by
    # domain.registration.parse_requirements ('{}' = no requirements).
    registration_requirements = db.Column(db.Text, default="{}")

    rounds = db.relationship("RoundModel", backref="tournament", lazy="select")


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