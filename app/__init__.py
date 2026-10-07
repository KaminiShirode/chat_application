from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_object("config.Config")

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from app.models import User, Message
    from app.routes import main

    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app