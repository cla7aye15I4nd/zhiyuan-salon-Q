from flask import Flask
from flask import render_template, request
from flask_wtf.csrf import CSRFProtect

from .users import users
from .users import db, login_manager

from .main import main
from .affair import affairs

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')

    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(affairs)

    csrf = CSRFProtect()

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    db.create_all(app=app)

    return app
