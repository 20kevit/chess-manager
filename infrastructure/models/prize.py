"""
Prize Models.
"""
from datetime import datetime
from app.extensions import db


class TournamentPrizeModel(db.Model):
    """P1-C: organizer-defined prize (category + rank + amount), ordered by priority."""
    __tablename__ = "tournament_prizes"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False, index=True
    )
    category_type = db.Column(db.String(20), default="open")  # domain.prizes.CATEGORY_TYPES
    category_params = db.Column(db.Text, default="{}")  # e.g. {"min_age":14,"max_age":18}
    rank = db.Column(db.Integer, default=1)
    amount = db.Column(db.Integer, default=0)  # Toman
    description = db.Column(db.String(255), default="")
    priority = db.Column(db.Integer, default=0)  # lower evaluated first

    tournament = db.relationship(
        "TournamentModel", backref=db.backref("prizes", cascade="all, delete-orphan")
    )


class PrizeAllocationModel(db.Model):
    """P1-C: recomputed report cache of prize winners (never authoritative)."""
    __tablename__ = "prize_allocations"
    __table_args__ = (
        db.UniqueConstraint("prize_id", "participant_id",
                            name="uq_prize_allocation_prize_participant"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False, index=True
    )
    prize_id = db.Column(
        db.Integer, db.ForeignKey("tournament_prizes.id"), nullable=False
    )
    participant_id = db.Column(
        db.Integer, db.ForeignKey("tournament_participants.id"), nullable=False
    )
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

    prize = db.relationship("TournamentPrizeModel", backref=db.backref(
        "allocations", cascade="all, delete-orphan"))
    participant = db.relationship("TournamentParticipantModel")