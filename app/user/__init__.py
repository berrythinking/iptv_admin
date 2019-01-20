import json
import app.constants as constants

from app import app, socketio
from app.client.client_constants import Commands, Status
from app.stream.stream_holder import StreamsHolder

from .iptv_cloud import IptvCloud
from .stream_handler import IStreamHandler


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


cloud_id = app.config['CLOUD_SETTINGS']['id']
cloud_host = app.config['CLOUD_SETTINGS']['host']
cloud_port = app.config['CLOUD_SETTINGS']['port']

cloud = IptvCloud(cloud_id, cloud_host, cloud_port)

streams_holder = StreamsHolder()
cloud.set_handler(StreamHandler())


# socketio
@socketio.on('connect')
def socketio_connect():
    print('Client connected')


@socketio.on('disconnect')
def socketio_disconnect():
    print('Client disconnected')
