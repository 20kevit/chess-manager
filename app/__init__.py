"""
Flask application factory.
"""
from flask import Flask, render_template
from app.extensions import db
from config import Config


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

    db.init_app(flask_app)

    from app.extensions import migrate
    migrate.init_app(flask_app, db)

    from app.extensions import csrf
    csrf.init_app(flask_app)

    from interfaces.web.tournament_routes import tournament_bp
    from interfaces.web.player_routes import player_bp
    from interfaces.web.round_routes import round_bp
    from interfaces.web.print_routes import print_bp
    from interfaces.web.admin_auth import admin_auth_bp
    from interfaces.web.backup_routes import backup_bp

    flask_app.register_blueprint(tournament_bp)
    flask_app.register_blueprint(player_bp)
    flask_app.register_blueprint(round_bp)
    flask_app.register_blueprint(print_bp)
    flask_app.register_blueprint(admin_auth_bp)
    flask_app.register_blueprint(backup_bp)

    @flask_app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @flask_app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @flask_app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    return flask_app