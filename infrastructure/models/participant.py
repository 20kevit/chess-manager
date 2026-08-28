"""
Tournament Participant Model.
"""
from datetime import datetime
from app.extensions import db


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
    pairing_no = db.Column(db.Integer, nullable=True)  # FIDE fixed ranking number

    # Historical Snapshots (Preserved at time of entry)
    rating_snapshot = db.Column(db.Integer, default=0)
    fide_title_snapshot = db.Column(db.String(5), default="")
    k_factor = db.Column(db.Integer, default=20)
    age_category = db.Column(db.String(10), default="")
    custom_category = db.Column(db.String(50), default="")

    # State
    status = db.Column(db.String(20), default="active")  # active, withdrawn
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