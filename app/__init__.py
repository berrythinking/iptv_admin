import os

from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_socketio import SocketIO

from app.service.service_manager import ServiceManager

HOST = '127.0.0.1'
PORT = 8080


def get_app_folder():
    return os.path.dirname(__file__)


def get_runtime_folder():
    return os.path.join(get_app_folder(), 'runtime_folder')


def get_runtime_stream_folder():
    return os.path.join(get_runtime_folder(), 'stream')


def init_project(static_folder, *args):
    runtime_folder = get_runtime_folder()
    if not os.path.exists(runtime_folder):
        os.mkdir(runtime_folder)

    runtime_stream_folder = get_runtime_stream_folder()
    if not os.path.exists(runtime_stream_folder):
        os.mkdir(runtime_stream_folder)

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

    servers_manager = ServiceManager(HOST, PORT, socketio)

    return app, bootstrap, babel, db, mail, socketio, login_manager, servers_manager


app, bootstrap, babel, db, mail, socketio, login_manager, servers_manager = init_project(
    'static',
    'config/public_config.py',
    'config/config.py',
)


def get_first_user_server(user):
    if not user or not user.servers:
        return None

    server_settings = user.servers[0]
    if server_settings:
        return servers_manager.find_or_create_server(server_settings)

    return None


from app.home.view import HomeView
from app.user.view import UserView
from app.stream.view import StreamView
from app.service.view import ServiceView

HomeView.register(app)
UserView.register(app)
StreamView.register(app)
ServiceView.register(app)


# socketio
@socketio.on('connect')
def connect():
    print('Client connected')


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')
