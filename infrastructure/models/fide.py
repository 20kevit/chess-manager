"""
FIDE Models.
"""
from datetime import datetime
from app.extensions import db


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
    rating_type = db.Column(db.String(10), nullable=False)  # standard, rapid, blitz
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
    # P1-G: honest progress reporting.
    stage = db.Column(db.String(20), nullable=True)  # download|extract|parse|finalize
    progress_percent = db.Column(db.Integer, nullable=True)  # 0..100; NULL = indeterminate
    # Phase 2: Separate download and processing progress for two-row UI
    download_progress = db.Column(db.Integer, nullable=True)  # 0..100 for download stage
    processing_progress = db.Column(db.Integer, nullable=True)  # 0..100 for processing stage