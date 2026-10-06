"""
Flask application factory.
"""
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import current_user
from app.extensions import db, login_manager
from config import Config
from application.notification_service import NotificationService

from infrastructure.repositories.user import UserRepository
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
    flask_app.config["SESSION_COOKIE_HTTPONLY"] = True
    flask_app.config["SESSION_COOKIE_SAMESITE"] = flask_app.config.get("SESSION_COOKIE_SAMESITE", "Lax")

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
        
        return UserRepository.get_by_id(int(user_id))

    from interfaces.web.tournament import tournament_bp
    from interfaces.web.manage_routes import manage_bp
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
    flask_app.register_blueprint(manage_bp)
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

    @flask_app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # Narrow CSP compatible with vanilla-JS/Jinja + inline shim/handlers + Vazirmatn CDN.
        # 'unsafe-inline' retained — extracting all inline handlers would be a broad refactor
        # out of scope for the release candidate phase.
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net data:; "
            "img-src 'self' data: blob:; "
            "connect-src 'self'; "
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        # Prevent caching of private/authenticated responses.
        # Public anonymous responses (e.g. tournament view) remain cacheable.
        try:
            is_private = False
            if current_user.is_authenticated:
                is_private = True
            elif request.path.startswith(("/dashboard", "/admin", "/notifications", "/api/notifications")):
                is_private = True
            if is_private:
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                response.headers["Pragma"] = "no-cache"
        except Exception:
            pass
        # HSTS only in production (HTTPS)
        if flask_app.config.get("ENV") == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

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

    # Tournament Management Workspace nav context.
    #
    # Every template rendered inside the workspace shell (manage/* and the
    # converted manager-only tool pages) needs the same capability flags and
    # the active nav key. Computing them here keeps old tool routes untouched:
    # they already pass `tournament`, and the shell derives the rest.
    _MANAGE_ACTIVE_BY_ENDPOINT = {
        "manage.overview": "overview",
        "manage.players": "players",
        "manage.rounds": "rounds",
        "manage.round_detail": "rounds",
        "manage.standings": "standings",
        "manage.crosstable": "crosstable",
        "manage.tiebreaks": "tiebreaks",
        "manage.output": "output",
        "manage.staff": "staff",
        "manage.staff_add": "staff",
        "manage.staff_remove": "staff",
        "tournament.settings": "settings",
        "tournament.rulebook_settings": "rulebook",
        "tournament.upload_rulebook_pdf": "rulebook",
        "tournament.remove_rulebook_pdf": "rulebook",
        "tournament.announcements": "announcements",
        "tournament.notification_prefs": "announcements",
        "tournament.prize_settings": "prizes",
        "tournament.prizes_recompute": "prizes",
        "registration.pricing_settings": "pricing",
        "registration.add_promo_code": "pricing",
        "registration.delete_promo_code": "pricing",
        "registration.manage_registrations": "registrations",
        "registration.approve_registration": "registrations",
        "registration.reject_registration": "registrations",
        "registration.reject_receipt": "registrations",
        "player.player_list": "players",
        "player.player_add": "players",
        "player.player_edit": "players",
        "player.player_import": "players",
        "player.csv_template": "players",
        "player.player_delete": "players",
        "player.player_withdraw": "players",
        "round.round_list": "rounds",
        "round.round_view": "rounds",
        "round.round_new": "rounds",
        "round.finish_round": "rounds",
        "round.delete_round": "rounds",
        "round.save_results": "rounds",
        "round.request_bye": "byes",
        "round.manual_pairing_add": "byes",
        "round.manual_pairing_remove": "byes",
        "round.cancel_bye": "byes",
        "round.manual_pairing": "rounds",
        "print.print_standings": "output",
        "print.print_round": "output",
        "print.print_crosstable": "output",
        "print.export_trf": "output",
        "backup.export_json": "output",
        "backup.import_json": "output",
        "backup.export_provider": "output",
        "backup.import_provider": "output",
        "dashboard.manage_tournament": "staff",
        "dashboard.add_staff": "staff",
        "dashboard.remove_staff": "staff",
    }

    @flask_app.context_processor
    def inject_manage_nav():
        try:
            view_args = request.view_args or {}
            public_id = view_args.get("public_id")
            if not public_id:
                return {}
            from interfaces.web.admin_auth import capabilities
            _t, can_manage, can_edit = capabilities(str(public_id))
            if _t is None:
                return {}
            return dict(
                mn_can_manage=can_manage,
                mn_can_edit_results=can_edit,
                mn_active=_MANAGE_ACTIVE_BY_ENDPOINT.get(
                    request.endpoint or "", ""),
            )
        except Exception:
            return {}
        
    return flask_app