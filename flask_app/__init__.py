# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# stdlib
from datetime import datetime
import os

# local
from .client import TenorClient

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
tenor_client = TenorClient()
mail = Mail()

from .posts.routes import posts
from .users.routes import users

def page_not_found(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = 'dayinthelife.cmsc388jproject@gmail.com'
    app.config['MAIL_PASSWORD'] = 'dayinthelife132'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    mail.init_app(app)
    app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app
