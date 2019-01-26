from bson.objectid import ObjectId

import app.constants as constants

from app.stream.stream_entry import Stream, EncodeStream, RelayStream, TimeshiftRecorderStream, CatchupStream, \
    TimeshiftPlayerStream, make_encode_stream, make_relay_stream, make_timeshift_recorder_stream, make_catchup_stream, \
    make_timeshift_player_stream
from app.client.client_constants import Status
from app.user.stream_handler import IStreamHandler
from app.service.service_settings import ServiceSettings


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


class Service(IStreamHandler):
    STREAM_DATA_CHANGED = 'stream_data_changed'
    SERVICE_DATA_CHANGED = 'service_data_changed'
    CALCULATE_VALUE = 'Calculate...'

    def __init__(self, socketio):
        self._init_fields()
        self._settings = ServiceSettings()
        self._socketio = socketio
        self._streams = []
        self._reload_from_db()

    @property
    def host(self):
        return self._settings.host

    @property
    def port(self):
        return self._settings.port

    @property
    def id(self):
        return self._id

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
        stream.save()

    def remove_stream(self, sid: str):
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                stream.delete()
                self._streams.remove(stream)
                break

    def to_front(self) -> dict:
        return {ServiceFields.ID: self._id, ServiceFields.CPU: self._cpu, ServiceFields.GPU: self._gpu,
                ServiceFields.LOAD_AVERAGE: self._load_average, ServiceFields.MEMORY_TOTAL: self._memory_total,
                ServiceFields.MEMORY_FREE: self._memory_free, ServiceFields.MEMORY_AVAILABLE: self._memory_available,
                ServiceFields.HDD_TOTAL: self._hdd_total, ServiceFields.HDD_FREE: self._hdd_free,
                ServiceFields.BANDWIDTH_IN: self._bandwidth_in, ServiceFields.BANDWIDTH_OUT: self._bandwidth_out,
                ServiceFields.UPTIME: self._uptime, ServiceFields.TIMESTAMP: self._timestamp,
                ServiceFields.VERSION: self._version}

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
        if status != Status.ACTIVE:
            self._init_fields()

    # private
    def _notify_front(self, channel: str, params: dict):
        self._socketio.emit(channel, params)

    def _init_fields(self):
        self._id = Service.CALCULATE_VALUE
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
        self._id = stats[ServiceFields.ID]
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
        streams = Stream.objects()
        for stream in streams:
            self._init_stream_runtime_fields(stream)
            self._streams.append(stream)
