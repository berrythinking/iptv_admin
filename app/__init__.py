from flask import Flask, render_template
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_socketio import SocketIO
from app.home.view import HomeView
from app.user.view import UserView


def init_project(static_folder, *args):
    app = Flask(__name__, static_folder=static_folder)

    for file in args:
        app.config.from_pyfile(file, silent=False)

    bootstrap = Bootstrap(app)
    babel = Babel(app)
    db = MongoEngine(app)
    mail = Mail(app)
    socketio = SocketIO(app)
    login_manager = LoginManager(app)

    HomeView.register(app)
    UserView.register(app)

    login_manager.login_view = "HomeView:login"

    return app, bootstrap, babel, db, mail, socketio, login_manager


app, bootstrap, babel, db, mail, socketio, login_manager = init_project(
    'static',
    'config/public_config.py',
    'config/config.py',
)


def page_not_found(e):
    return render_template('404.html'), 404


app.register_error_handler(404, page_not_found)
