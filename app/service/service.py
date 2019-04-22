from bson.objectid import ObjectId

import app.constants as constants

from app.stream.stream_entry import Stream, EncodeStream, RelayStream, TimeshiftRecorderStream, CatchupStream, \
    TimeshiftPlayerStream, TestLifeStream, make_encode_stream, make_relay_stream, make_timeshift_recorder_stream, \
    make_catchup_stream, make_timeshift_player_stream, make_test_life_stream
from app.client.client_constants import Status
from app.service.service_settings import ServiceSettings
from app.service.service_client import ServiceClient

from .stream_handler import IStreamHandler


class ServiceFields:
    ID = 'id'
    CPU = 'cpu'
    GPU = 'gpu'
    LOAD_AVERAGE = 'load_average'
    MEMORY_TOTAL = 'memory_total'
    MEMORY_FREE = 'memory_free'
    MEMORY_AVAILABLE = 'memory_available'
    HDD_TOTAL = 'hdd_total'
    HDD_FREE = 'hdd_free'
    BANDWIDTH_IN = 'bandwidth_in'
    BANDWIDTH_OUT = 'bandwidth_out'
    UPTIME = 'uptime'
    TIMESTAMP = 'timestamp'
    VERSION = 'version'
    STATUS = 'status'


class Service(IStreamHandler):
    STREAM_DATA_CHANGED = 'stream_data_changed'
    SERVICE_DATA_CHANGED = 'service_data_changed'
    CALCULATE_VALUE = 'Calculate...'

    def __init__(self, socketio):
        self._init_fields()
        self._settings = None
        self._socketio = socketio
        self._client = ServiceClient(self)
        self._streams = []

    def set_settings(self, settings: ServiceSettings):
        self._settings = settings
        self._client.set_settings(settings)
        self._reload_from_db()

    def connect(self):
        return self._client.connect()

    def disconnect(self):
        return self._client.disconnect()

    def stop(self, delay: int):
        return self._client.stop_service(delay)

    def get_log_service(self):
        return self._client.get_log_service(self.id)

    def ping(self):
        return self._client.ping_service()

    def activate(self, license_key: str):
        return self._client.activate(license_key)

    def get_log_stream(self, sid: str):
        stream = self.find_stream_by_id(sid)
        if stream:
            self._client.get_log_stream(sid, stream.generate_feedback_dir())

    def start_stream(self, sid: str):
        stream = self.find_stream_by_id(sid)
        if stream:
            self._client.start_stream(stream.config())

    def stop_stream(self, sid: str):
        stream = self.find_stream_by_id(sid)
        if stream:
            self._client.stop_stream(sid)

    def restart_stream(self, sid: str):
        stream = self.find_stream_by_id(sid)
        if stream:
            self._client.restart_stream(sid)

    @property
    def id(self):
        return str(self._settings.id)

    def get_streams(self):
        return self._streams

    def find_stream_by_id(self, sid: str):
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                return stream

        return None

    def add_stream(self, stream):
        self._init_stream_runtime_fields(stream)
        self._streams.append(stream)
        self._settings.streams.append(stream)
        self._settings.save()

    def update_stream(self, stream):
        stream.save()

    def remove_stream(self, sid: str):
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                self._settings.update(pull__streams__id=stream.id)
                self._settings.save()
                self._streams.remove(stream)
                break

    def to_front(self) -> dict:
        return {ServiceFields.ID: self.id, ServiceFields.CPU: self._cpu, ServiceFields.GPU: self._gpu,
                ServiceFields.LOAD_AVERAGE: self._load_average, ServiceFields.MEMORY_TOTAL: self._memory_total,
                ServiceFields.MEMORY_FREE: self._memory_free, ServiceFields.MEMORY_AVAILABLE: self._memory_available,
                ServiceFields.HDD_TOTAL: self._hdd_total, ServiceFields.HDD_FREE: self._hdd_free,
                ServiceFields.BANDWIDTH_IN: self._bandwidth_in, ServiceFields.BANDWIDTH_OUT: self._bandwidth_out,
                ServiceFields.UPTIME: self._uptime, ServiceFields.TIMESTAMP: self._timestamp,
                ServiceFields.VERSION: self._version, ServiceFields.STATUS: self._client.status()}

    def make_relay_stream(self) -> RelayStream:
        return make_relay_stream(self._settings.feedback_directory)

    def make_encode_stream(self) -> EncodeStream:
        return make_encode_stream(self._settings.feedback_directory)

    def make_timeshift_recorder_stream(self) -> TimeshiftRecorderStream:
        return make_timeshift_recorder_stream(self._settings.feedback_directory, self._settings.timeshifts_directory)

    def make_catchup_stream(self) -> CatchupStream:
        return make_catchup_stream(self._settings.feedback_directory, self._settings.timeshifts_directory)

    def make_timeshift_player_stream(self) -> TimeshiftPlayerStream:
        return make_timeshift_player_stream(self._settings.feedback_directory)

    def make_test_life_stream(self) -> TestLifeStream:
        return make_test_life_stream(self._settings.feedback_directory)

    # handler
    def on_stream_statistic_received(self, params: dict):
        sid = params['id']
        stream = self.find_stream_by_id(sid)
        if stream:
            stream.update_runtime_fields(params)
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
            stream.reset()
            self._notify_front(Service.STREAM_DATA_CHANGED, stream.to_front())

    def on_client_state_changed(self, status: Status):
        if status == Status.ACTIVE:
            pass
        else:
            self._init_fields()

    # private
    def _notify_front(self, channel: str, params: dict):
        self._socketio.emit(channel, params)

    def _init_fields(self):
        self._node_id = Service.CALCULATE_VALUE
        self._cpu = Service.CALCULATE_VALUE
        self._gpu = Service.CALCULATE_VALUE
        self._load_average = Service.CALCULATE_VALUE
        self._memory_total = Service.CALCULATE_VALUE
        self._memory_free = Service.CALCULATE_VALUE
        self._memory_available = Service.CALCULATE_VALUE
        self._hdd_total = Service.CALCULATE_VALUE
        self._hdd_free = Service.CALCULATE_VALUE
        self._bandwidth_in = Service.CALCULATE_VALUE
        self._bandwidth_out = Service.CALCULATE_VALUE
        self._uptime = Service.CALCULATE_VALUE
        self._timestamp = Service.CALCULATE_VALUE
        self._version = Service.CALCULATE_VALUE

    def _refresh_stats(self, stats: dict):
        self._node_id = stats[ServiceFields.ID]
        self._cpu = stats[ServiceFields.CPU]
        self._gpu = stats[ServiceFields.GPU]
        self._load_average = stats[ServiceFields.LOAD_AVERAGE]
        self._memory_total = stats[ServiceFields.MEMORY_TOTAL]
        self._memory_free = stats[ServiceFields.MEMORY_FREE]
        self._memory_available = stats[ServiceFields.MEMORY_AVAILABLE]
        self._hdd_total = stats[ServiceFields.MEMORY_TOTAL]
        self._hdd_free = stats[ServiceFields.MEMORY_FREE]
        self._bandwidth_in = stats[ServiceFields.BANDWIDTH_IN]
        self._bandwidth_out = stats[ServiceFields.BANDWIDTH_OUT]
        self._uptime = stats[ServiceFields.UPTIME]
        self._timestamp = stats[ServiceFields.TIMESTAMP]
        self._version = stats[ServiceFields.VERSION]

    def _init_stream_runtime_fields(self, stream: Stream):
        type = stream.get_type()
        stream.set_feedback_dir(self._settings.feedback_directory)
        if type == constants.StreamType.TIMESHIFT_RECORDER or type == constants.StreamType.CATCHUP:
            stream.set_timeshift_dir(self._settings.timeshifts_directory)

    def _reload_from_db(self):
        self._streams = []
        streams = self._settings.streams
        for stream in streams:
            self._init_stream_runtime_fields(stream)
            self._streams.append(stream)
