# app/cli.py
import click
from app.extensions import db

from infrastructure.models.user import UserModel


def register_cli(app):
    @app.cli.command("create-admin")
    @click.argument("email")
    def create_admin(email):
        """Promote a user to System Admin by email."""
        user = UserModel.query.filter_by(email=email.lower()).first()
        if not user:
            click.echo(f"Error: User with email '{email}' not found. Please register first.")
            return
        
        if user.is_admin:
            click.echo(f"User '{email}' is already a System Admin.")
            return
            
        user.is_admin = True
        db.session.commit()
        click.echo(f"Success: User '{email}' is now a System Admin.")

    @app.cli.command("init-db")
    def init_db():
        """Create database tables from current SQLAlchemy models.

        Fresh installations only (empty database). Never run against an
        existing database — use `flask db upgrade` for those.
        """
        from infrastructure.models import (  # noqa: F401
            UserModel,
            UserRoleModel,
            UserRoleRequestModel,
            SystemSettingModel,
            PlayerProfileModel,
            TournamentModel,
            RoundModel,
            PairingModel,
            ByeRequestModel,
            ManualPairingModel,
            TournamentParticipantModel,
            RegistrationModel,
            PaymentModel,
            PromoCodeModel,
            TournamentStaffModel,
            FidePlayerModel,
            FideRatingModel,
            FideImportModel,
            PlayerVerificationModel,
            NotificationModel,
            NotificationPreferenceModel,
            TournamentPrizeModel,
            PrizeAllocationModel,
            TempImportDataModel,
        )
        
        db.create_all()
        click.echo("Database tables created successfully.")