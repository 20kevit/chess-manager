# app/cli.py
import click
from app.extensions import db
from infrastructure.db_models import UserModel

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