from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_socketio import SocketIO

import app.constants as constants
from app.client.client_constants import Commands, Status
from app.user.stream_handler import IStreamHandler

from app.user.service_client import ServiceClient
from app.user.service import Service


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

    login_manager.login_view = "HomeView:signin"

    service = Service(socketio)
    client = ServiceClient(app.config['SERVICE']['host'], app.config['SERVICE']['port'], service)

    return app, bootstrap, babel, db, mail, socketio, login_manager, client, service


app, bootstrap, babel, db, mail, socketio, login_manager, client, service = init_project(
    'static',
    'config/public_config.py',
    'config/config.py',
)

from app.home.view import HomeView
from app.user.view import UserView
from app.stream.view import StreamView

HomeView.register(app)
UserView.register(app)
StreamView.register(app)


# socketio
@socketio.on('connect')
def connect():
    print('Client connected')


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')
