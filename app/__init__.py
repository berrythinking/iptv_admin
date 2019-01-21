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
from app.user.iptv_cloud import IptvCloud
from .stream_holder import StreamsHolder


class ServiceFields:
    VERSION = 'version'
    ID = 'id'
    TIMESTAMP = 'timestamp'


class Service(IStreamHandler):
    STREAM_DATA_CHANGED = 'stream_data_changed'
    SERVICE_DATA_CHANGED = 'service_data_changed'
    CALCULATE_VALUE = 'Calculate...'

    def __init__(self, status):
        self._init_fields()

    def on_stream_statistic_received(self, params: dict):
        sid = params['id']
        stream = streams_holder.find_stream_by_id(sid)
        if stream:
            stream.status = constants.StreamStatus(params['status'])
            socketio.emit(Service.STREAM_DATA_CHANGED, stream.to_front())

    def on_stream_sources_changed(self, params: dict):
        # sid = params['id']
        socketio.emit(Commands.CHANGED_STREAM_COMMAND, params)

    def on_service_statistic_received(self, params: dict):
        # nid = params['id']
        self._refresh_stats(params)
        socketio.emit(Service.SERVICE_DATA_CHANGED, self.to_front())

    def on_quit_status_stream(self, params: dict):
        sid = params['id']
        stream = streams_holder.find_stream_by_id(sid)
        if stream:
            stream.status = constants.StreamStatus.NEW
            socketio.emit(Service.STREAM_DATA_CHANGED, stream.to_front())

    def on_client_state_changed(self, status: Status):
        if status != Status.ACTIVE:
            self._init_fields()

    def to_front(self):
        return {ServiceFields.ID: self._id, ServiceFields.VERSION: self._version,
                ServiceFields.TIMESTAMP: self._timestamp}

    # private
    def _init_fields(self):
        self._id = Service.CALCULATE_VALUE
        self._version = Service.CALCULATE_VALUE
        self._timestamp = Service.CALCULATE_VALUE

    def _refresh_stats(self, stats: dict):
        self._id = stats[ServiceFields.ID]
        self._version = stats[ServiceFields.VERSION]
        self._timestamp = stats[ServiceFields.TIMESTAMP]


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

    login_manager.login_view = "HomeView:login"

    cloud_id = app.config['CLOUD_SETTINGS']['id']
    cloud_host = app.config['CLOUD_SETTINGS']['host']
    cloud_port = app.config['CLOUD_SETTINGS']['port']

    cloud = IptvCloud(cloud_id, cloud_host, cloud_port)

    streams_holder = StreamsHolder()
    service = Service(cloud.status())
    cloud.set_handler(service)

    return app, bootstrap, babel, db, mail, socketio, login_manager, streams_holder, cloud, service


app, bootstrap, babel, db, mail, socketio, login_manager, streams_holder, cloud, service = init_project(
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
def socketio_connect():
    print('Client connected')


@socketio.on('disconnect')
def socketio_disconnect():
    print('Client disconnected')
