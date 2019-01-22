from app.client.client import Client
from app.client.client_handler import IClientHandler
from app.client.json_rpc import Request, Response
from app.client.client_constants import Commands, Status

import app.constants as constants

from .stream_handler import IStreamHandler


class ServiceClientFields:
    STATUS = 'status'


class ServiceClient(IClientHandler):
    def __init__(self, host: str, port: int, handler: IStreamHandler):
        self._request_id = 0
        self._handler = handler
        self._client = Client(host, port, self)

    def connect(self):
        self._client.connect()

    def status(self) -> Status:
        return self._client.status

    def disconnect(self):
        self._client.disconnect()

    def activate(self, license_key: str):
        return self._client.activate(self._gen_request_id(), license_key)

    def ping_service(self):
        return self._client.ping_service(self._gen_request_id())

    def prepare_service(self, feedback_directory: str, timeshifts_directory: str, hls_directory: str,
                        playlists_directory: str, dvb_directory: str, capture_card_directory: str):
        return self._client.prepare_service(self._gen_request_id(), feedback_directory, timeshifts_directory,
                                            hls_directory,
                                            playlists_directory, dvb_directory, capture_card_directory)

    def stop_service(self, delay: int):
        return self._client.stop_service(self._gen_request_id(), delay)

    def start_stream(self, config: dict):
        return self._client.start_stream(self._gen_request_id(), config)

    def stop_stream(self, stream_id: str):
        return self._client.stop_stream(self._gen_request_id(), stream_id)

    def restart_stream(self, stream_id: str):
        return self._client.restart_stream(self._gen_request_id(), stream_id)

    # handler
    def process_response(self, req: Request, resp: Response):
        if req and req.method == Commands.ACTIVATE_COMMAND and resp.is_message():
            self.prepare_service(constants.DEFAULT_FEEDBACK_DIR_PATH, constants.DEFAULT_TIMESHIFTS_DIR_PATH,
                                 constants.DEFAULT_HLS_DIR_PATH, constants.DEFAULT_PLAYLISTS_DIR_PATH,
                                 constants.DEFAULT_DVB_DIR_PATH, constants.DEFAULT_CAPTURE_DIR_PATH)
            if self._handler:
                self._handler.on_service_statistic_received(resp.result)

    def process_request(self, req: Request):
        if not req:
            return
        if not self._handler:
            return

        if req.method == Commands.STATISTIC_STREAM_COMMAND:
            self._handler.on_stream_statistic_received(req.params)
        elif req.method == Commands.CHANGED_STREAM_COMMAND:
            self._handler.on_stream_sources_changed(req.params)
        elif req.method == Commands.STATISTIC_SERVICE_COMMAND:
            self._handler.on_service_statistic_received(req.params)
        elif req.method == Commands.QUIT_STATUS_STREAM_COMMAND:
            self._handler.on_quit_status_stream(req.params)

    def on_client_state_changed(self, status: Status):
        if self._handler:
            self._handler.on_client_state_changed(status)

    def to_front(self):
        return {ServiceClientFields.STATUS: self.status()}

    # private
    def _gen_request_id(self) -> int:
        current_value = self._request_id
        self._request_id += 1
        return current_value
