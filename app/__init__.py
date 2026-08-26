"""
Flask application factory.
"""
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.extensions import db, login_manager
from config import Config
from application.notification_service import NotificationService

def create_app(config_class=None) -> Flask:
    flask_app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    if config_class:
        flask_app.config.from_object(config_class)
    else:
        flask_app.config.from_object(Config)

    # Session cookie hardening: Secure only where deployment is HTTPS-only.
    flask_app.config["SESSION_COOKIE_SECURE"] = (
        flask_app.config.get("ENV") == "production"
    )

    # Upload hardening (Category H): global request-size ceiling plus a
    # private, non-web-servable directory for bank-payment receipts.
    flask_app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB
    flask_app.config["RECEIPT_UPLOAD_DIR"] = os.path.join(
        flask_app.instance_path, "uploads", "receipts"
    )
    # Private profile media (P0-C): identity documents must never be
    # web-servable; access goes through authenticated endpoints only.
    flask_app.config["PROFILE_PHOTO_UPLOAD_DIR"] = os.path.join(
        flask_app.instance_path, "uploads", "profile_photos"
    )
    flask_app.config["ID_DOCUMENT_UPLOAD_DIR"] = os.path.join(
        flask_app.instance_path, "uploads", "id_documents"
    )
    # P1-D: rulebook PDFs are PUBLIC tournament content but still stored
    # privately (instance-anchored, never under static/) and served
    # through a dedicated unauthenticated endpoint.
    flask_app.config["RULEBOOK_UPLOAD_DIR"] = os.path.join(
        flask_app.instance_path, "uploads", "rulebooks"
    )

    # FIDE downloads/retention live under the instance path too (Category K):
    # never CWD-dependent.
    flask_app.config["FIDE_DATA_DIR"] = os.path.join(
        flask_app.instance_path, "data", "fide"
    )

    # P0-G: a configured webhook secret is enforced on every incoming
    # update. Remind operators at boot, because the #1 production failure
    # mode is registering the webhook WITHOUT the matching secret_token.
    for _secret_key, _bot in (
        ("TELEGRAM_WEBHOOK_SECRET", "Telegram"),
        ("BALE_WEBHOOK_SECRET", "Bale"),
    ):
        if flask_app.config.get(_secret_key):
            flask_app.logger.warning(
                "%s webhook secret is configured; the webhook MUST be "
                "registered with the matching secret_token (see "
                "docs/DEPLOYMENT.md section 11) or every update is "
                "rejected with 403.", _bot,
            )

    db.init_app(flask_app)

    from app.extensions import migrate
    migrate.init_app(flask_app, db)

    from app.extensions import csrf
    csrf.init_app(flask_app)

    login_manager.init_app(flask_app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from infrastructure.repositories import UserRepository
        return UserRepository.get_by_id(int(user_id))

    from interfaces.web.tournament_routes import tournament_bp
    from interfaces.web.player_routes import player_bp
    from interfaces.web.round_routes import round_bp
    from interfaces.web.print_routes import print_bp
    from interfaces.web.backup_routes import backup_bp
    from interfaces.web.auth_routes import auth_bp
    from interfaces.web.admin_routes import admin_bp
    from interfaces.web.dashboard_routes import dashboard_bp
    from interfaces.web.registration_routes import registration_bp
    from interfaces.web.payment_routes import payment_bp
    from interfaces.web.fide_routes import fide_bp
    from interfaces.web.player_profile_routes import player_profile_bp
    from interfaces.web.notification_routes import notification_bp

    flask_app.register_blueprint(tournament_bp)
    flask_app.register_blueprint(player_bp)
    flask_app.register_blueprint(round_bp)
    flask_app.register_blueprint(print_bp)
    flask_app.register_blueprint(backup_bp)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(admin_bp)
    flask_app.register_blueprint(dashboard_bp)
    flask_app.register_blueprint(registration_bp)
    flask_app.register_blueprint(payment_bp)
    flask_app.register_blueprint(fide_bp)
    flask_app.register_blueprint(player_profile_bp)
    flask_app.register_blueprint(notification_bp)

    from app.cli import register_cli
    register_cli(flask_app)

    # ── Phase 9E, 9F & 9G: Register Notification Providers ──
    from application.providers.web_provider import WebProvider
    from application.providers.telegram_provider import TelegramProvider
    from application.providers.bale_provider import BaleProvider
    from application.notification_dispatcher import NotificationDispatcher
    NotificationDispatcher.register_provider(WebProvider())
    NotificationDispatcher.register_provider(TelegramProvider())
    NotificationDispatcher.register_provider(BaleProvider())
    # ──────────────────────────────────────────────────────────
    
    @flask_app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @flask_app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @flask_app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    @flask_app.errorhandler(413)
    def request_entity_too_large(e):
        flash("حجم فایل ارسال‌شده بیش از حد مجاز (۸ مگابایت) است.", "error")
        return redirect(request.referrer or url_for("tournament.index")), 302

    @flask_app.template_filter('toman_formatter')
    def toman_formatter(value):
        try:
            return f"{int(value):,} تومان"
        except (ValueError, TypeError):
            return "0 تومان"
    
    @flask_app.context_processor
    def inject_unread_notifications():
        if current_user.is_authenticated:
            unread_count = NotificationService.get_unread_count(current_user.id)
        else:
            unread_count = 0
        return dict(unread_notifications_count=unread_count)
        
    return flask_app