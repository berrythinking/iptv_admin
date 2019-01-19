import json

from flask import Flask, render_template, session, request
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_socketio import SocketIO
from app.home.view import HomeView
from app.user.view import UserView
from itsdangerous import URLSafeTimedSerializer
from app.user.iptv_cloud import IptvCloud
from app.home.stream_holder import StreamsHolder
from app.home.user_loging_manager import User

from app.user.stream_handler import IStreamHandler
from app.client.client_constants import Commands, Status
import app.constants as constants


class StreamHandler(IStreamHandler):
    def __init__(self):
        pass

    def on_stream_statistic_received(self, params: dict):
        sid = params['id']
        stream = streams_holder.find_stream_by_id(sid)
        if stream:
            stream.status = constants.StreamStatus(params['status'])

        params_str = json.dumps(params)
        socketio.emit(Commands.STATISTIC_STREAM_COMMAND, params_str)

    def on_stream_sources_changed(self, params: dict):
        # sid = params['id']
        params_str = json.dumps(params)
        socketio.emit(Commands.CHANGED_STREAM_COMMAND, params_str)

    def on_service_statistic_received(self, params: dict):
        # nid = params['id']
        params_str = json.dumps(params)
        socketio.emit(Commands.STATISTIC_SERVICE_COMMAND, params_str)

    def on_quit_status_stream(self, params: dict):
        # sid = params['id']
        # stream = streams_holder.find_stream_by_id(sid)

        params_str = json.dumps(params)
        socketio.emit(Commands.QUIT_STATUS_STREAM_COMMAND, params_str)

    def on_client_state_changed(self, status: Status):
        pass


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
    confirm_link_generator = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    HomeView.register(app)
    UserView.register(app)

    login_manager.login_view = "HomeView:login"

    cloud_id = app.config['CLOUD_SETTINGS']['id']
    cloud_host = app.config['CLOUD_SETTINGS']['host']
    cloud_port = app.config['CLOUD_SETTINGS']['port']

    cloud = IptvCloud(cloud_id, cloud_host, cloud_port)

    streams_holder = StreamsHolder()
    cloud.set_handler(StreamHandler())

    return app, bootstrap, babel, db, mail, socketio, login_manager, confirm_link_generator, streams_holder, cloud


app, bootstrap, babel, db, mail, socketio, login_manager, confirm_link_generator, streams_holder, cloud = init_project(
    'static',
    'config/public_config.py',
    'config/config.py',
)


def page_not_found(e):
    return render_template('404.html'), 404


app.register_error_handler(404, page_not_found)


# socketio
@socketio.on('connect')
def socketio_connect():
    print('Client connected')


@socketio.on('disconnect')
def socketio_disconnect():
    print('Client disconnected')


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()


@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    if current_user and current_user.is_authenticated:
        lc = current_user.settings.locale
        return lc

    if session.get('language'):
        lang = session['language']
        return lang

    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(constants.AVAILABLE_LOCALES)
