import app.constants as constants
from app.client.client_constants import Status
from app.user.stream_handler import IStreamHandler
from .streams_holder import StreamsHolder


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

    def to_front(self) -> dict:
        return {ServiceFields.ID: self._id, ServiceFields.CPU: self._cpu, ServiceFields.GPU: self._gpu,
                ServiceFields.LOAD_AVERAGE: self._load_average, ServiceFields.MEMORY_TOTAL: self._memory_total,
                ServiceFields.MEMORY_FREE: self._memory_free, ServiceFields.MEMORY_AVAILABLE: self._memory_available,
                ServiceFields.HDD_TOTAL: self._hdd_total, ServiceFields.HDD_FREE: self._hdd_free,
                ServiceFields.BANDWIDTH_IN: self._bandwidth_in, ServiceFields.BANDWIDTH_OUT: self._bandwidth_out,
                ServiceFields.UPTIME: self._uptime, ServiceFields.TIMESTAMP: self._timestamp,
                ServiceFields.VERSION: self._version}

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
