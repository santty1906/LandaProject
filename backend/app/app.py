import os

from flask import Flask

from .config import Config
from .models import db


def create_app(config_class=Config, overrides=None):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if overrides:
        app.config.update(overrides)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)

    from .auth import auth_bp
    from .routes import routes_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(routes_bp)

    with app.app_context():
        db.create_all()

    return app
