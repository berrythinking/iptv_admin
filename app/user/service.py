import app.constants as constants
from app.client.client_constants import Status
from app.user.stream_handler import IStreamHandler
from .stream_holder import StreamsHolder


class ServiceFields:
    VERSION = 'version'
    ID = 'id'
    TIMESTAMP = 'timestamp'


class Service(IStreamHandler):
    STREAM_DATA_CHANGED = 'stream_data_changed'
    SERVICE_DATA_CHANGED = 'service_data_changed'
    CALCULATE_VALUE = 'Calculate...'

    def __init__(self, socketio):
        self._init_fields()
        self._streams_holder = StreamsHolder()
        self._socketio = socketio

    def get_streams(self):
        return self._streams_holder.get_streams()

    def find_stream_by_id(self, sid: str):
        return self._streams_holder.find_stream_by_id(sid)

    def add_stream(self, stream):
        self._streams_holder.add_stream(stream)

    def remove_stream(self, sid: str):
        self._streams_holder.remove_stream(sid)

    def to_front(self):
        return {ServiceFields.ID: self._id, ServiceFields.VERSION: self._version,
                ServiceFields.TIMESTAMP: self._timestamp}

    # handler
    def on_stream_statistic_received(self, params: dict):
        sid = params['id']
        stream = self.find_stream_by_id(sid)
        if stream:
            stream.status = constants.StreamStatus(params['status'])
            self._notify_front(Service.STREAM_DATA_CHANGED, stream.to_front())

    def on_stream_sources_changed(self, params: dict):
        pass

    def on_service_statistic_received(self, params: dict):
        # nid = params['id']
        self._refresh_stats(params)
        self._notify_front(Service.SERVICE_DATA_CHANGED, self.to_front())

    def on_quit_status_stream(self, params: dict):
        sid = params['id']
        stream = self.find_stream_by_id(sid)
        if stream:
            stream.status = constants.StreamStatus.NEW
            self._notify_front(Service.STREAM_DATA_CHANGED, stream.to_front())

    def on_client_state_changed(self, status: Status):
        if status != Status.ACTIVE:
            self._init_fields()

    # private
    def _notify_front(self, channel: str, params: dict):
        self._socketio.emit(channel, params)

    def _init_fields(self):
        self._id = Service.CALCULATE_VALUE
        self._version = Service.CALCULATE_VALUE
        self._timestamp = Service.CALCULATE_VALUE

    def _refresh_stats(self, stats: dict):
        self._id = stats[ServiceFields.ID]
        self._version = stats[ServiceFields.VERSION]
        self._timestamp = stats[ServiceFields.TIMESTAMP]
