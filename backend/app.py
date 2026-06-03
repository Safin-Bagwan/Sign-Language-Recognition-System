import logging
import os
import sys
from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.config import get_config
from backend.routes.api import api_bp
from backend.utils.paths import FRONTEND_DIR
from backend.utils.responses import error


def create_app(config_name=None):
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path="",
    )
    app.config.from_object(get_config(config_name))

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": app.config["CORS_ORIGINS"],
                "methods": ["GET", "POST", "OPTIONS"],
                "allow_headers": ["Content-Type"],
            }
        },
    )

    app.register_blueprint(api_bp)

    @app.get("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.errorhandler(404)
    def not_found(_):
        return error("Resource not found.", 404, "not_found")

    @app.errorhandler(500)
    def server_error(exc):
        app.logger.exception("Unhandled server error: %s", exc)
        return error("Internal server error.", 500, "server_error")

    @app.after_request
    def add_security_headers(response):
        for header, value in app.config["SECURITY_HEADERS"].items():
            response.headers.setdefault(header, value)
        return response

    return app


def configure_logging():
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


configure_logging()
app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
