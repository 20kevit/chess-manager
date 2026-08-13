from datetime import datetime
from app.extensions import db

class TournamentModel(db.Model):
    __tablename__ = "tournaments"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

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
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    players = db.relationship("PlayerModel", backref="tournament", lazy="select")
    rounds = db.relationship("RoundModel", backref="tournament", lazy="select")


class PlayerModel(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    start_number = db.Column(db.Integer, nullable=False)
    pairing_no = db.Column(db.Integer, nullable=True) # FIDE fixed ranking number
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(1), default="M")
    birth_date = db.Column(db.Date, nullable=True)
    federation = db.Column(db.String(5), default="IRI")
    fide_id = db.Column(db.String(20), default="")
    fide_title = db.Column(db.String(5), default="")
    rating_standard = db.Column(db.Integer, default=0)
    rating_rapid = db.Column(db.Integer, default=0)
    rating_blitz = db.Column(db.Integer, default=0)
    k_factor = db.Column(db.Integer, default=20)
    age_category = db.Column(db.String(10), default="")
    custom_category = db.Column(db.String(50), default="")
    status = db.Column(db.String(20), default="active")
    joined_from_round = db.Column(db.Integer, default=1)
    withdrawn_at_round = db.Column(db.Integer, default=0)
    
    # Incremental fields for FIDE compliance and performance
    points = db.Column(db.Float, default=0.0)
    color_history = db.Column(db.String(255), default="")
    float_history = db.Column(db.String(255), default="")
    received_bye = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            "tournament_id", "start_number",
            name="uq_player_tournament_startnum"
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def rating(self):
        """Rating matching tournament time control."""
        if self.tournament:
            tc = self.tournament.time_control_type
            if tc == "standard":
                return self.rating_standard or 0
            elif tc == "rapid":
                return self.rating_rapid or 0
            elif tc == "blitz":
                return self.rating_blitz or 0
        return self.rating_standard or 0
    
    @property
    def ranking_label(self):
        """نمایش شماره قرعه ثابت فیده یا شماره شروع"""
        return self.pairing_no or self.start_number


class RoundModel(db.Model):
    __tablename__ = "rounds"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    round_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)

    pairings = db.relationship(
        "PairingModel",
        backref="round",
        lazy="select",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "tournament_id", "round_number",
            name="uq_round_tournament_number"
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )
    
    @property
    def status_label(self):
        labels = {"pending": "در انتظار", "ongoing": "در جریان", "finished": "پایان یافته"}
        return labels.get(self.status, "نامشخص")


class PairingModel(db.Model):
    __tablename__ = "pairings"

    id = db.Column(db.Integer, primary_key=True)
    round_id = db.Column(db.Integer, db.ForeignKey("rounds.id"), nullable=False)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    board_number = db.Column(db.Integer, nullable=False)
    white_player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=True
    )
    black_player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=True
    )
    result = db.Column(db.String(10), default="")
    
    # Store engine float tags
    white_float = db.Column(db.String(1), default="") # 'D', 'U', or ''
    black_float = db.Column(db.String(1), default="")
    
    is_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    white_player = db.relationship(
        "PlayerModel", foreign_keys=[white_player_id], lazy="joined"
    )
    black_player = db.relationship(
        "PlayerModel", foreign_keys=[black_player_id], lazy="joined"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "round_id", "board_number",
            name="uq_pairing_round_board"
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )
    @property
    def white_player_name(self):
        return self.white_player.full_name if self.white_player else "-"

    @property
    def black_player_name(self):
        return self.black_player.full_name if self.black_player else None

    @property
    def result_display(self):
        if not self.result: return "در انتظار"
        results = {
            "1-0": "۱ - ۰", "0-1": "۰ - ۱", "1/2": "½ - ½",
            "+/-": "+ - -", "-/+": "- - +", "+/+": "- - -",
            "bye": "1 - 0 (Bye)", "half-bye": "½ - 0 (Bye)", "zero-bye": "0 - 0 (Bye)"
        }
        return results.get(self.result, self.result)


class ByeRequestModel(db.Model):
    __tablename__ = "bye_requests"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=False
    )
    bye_type = db.Column(db.String(10), default="half-bye")
    for_round = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    player = db.relationship("PlayerModel", foreign_keys=[player_id])

    __table_args__ = (
        db.UniqueConstraint(
            "tournament_id", "player_id", "for_round",
            name="uq_bye_tournament_player_round"
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )


class ManualPairingModel(db.Model):
    __tablename__ = "manual_pairings"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(
        db.Integer, db.ForeignKey("tournaments.id"), nullable=False
    )
    round_number = db.Column(db.Integer, nullable=False)
    white_player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=False
    )
    black_player_id = db.Column(
        db.Integer, db.ForeignKey("players.id"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    white_player = db.relationship(
        "PlayerModel", foreign_keys=[white_player_id], lazy="joined"
    )
    black_player = db.relationship(
        "PlayerModel", foreign_keys=[black_player_id], lazy="joined"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "tournament_id", "round_number", "white_player_id",
            name="uq_manual_pairing_white"
        ),
        db.UniqueConstraint(
            "tournament_id", "round_number", "black_player_id",
            name="uq_manual_pairing_black"
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
        },
    )