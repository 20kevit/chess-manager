"""
Tournament Staff Model.
"""
from app.extensions import db


class TournamentStaffModel(db.Model):
    __tablename__ = "tournament_staff"
    __table_args__ = (
        db.UniqueConstraint("tournament_id", "user_id", name="uq_tournament_staff"),
        # NOTE: The single chief arbiter invariant is enforced at the application layer
        # (see dashboard_routes.add_staff). For production MySQL 8.0+, a database-level
        # enforcement can be added via a generated column + unique index:
        #   ALTER TABLE tournament_staff
        #     ADD COLUMN chief_arbiter_user_id INT GENERATED ALWAYS AS (
        #         CASE WHEN role = 'chief_arbiter' THEN user_id ELSE NULL END
        #     ) VIRTUAL,
        #     ADD UNIQUE INDEX uq_tournament_chief_arbiter (chief_arbiter_user_id);
        # This leverages MySQL's unique index treating NULL as distinct, allowing only
        # one non-NULL (chief_arbiter) per tournament.
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"},
    )

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role = db.Column(db.String(20), default="arbiter")

    # New Fields for Invitation System
    status = db.Column(db.String(20), default="pending")  # pending, accepted, rejected
    invited_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    tournament = db.relationship("TournamentModel", backref="staff_members")
    user = db.relationship("UserModel", foreign_keys=[user_id], backref="staff_assignments")
    inviter = db.relationship("UserModel", foreign_keys=[invited_by], backref="sent_invitations")