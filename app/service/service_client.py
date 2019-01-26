from app.client.client import Client
from app.client.client_handler import IClientHandler
from app.client.json_rpc import Request, Response
from app.client.client_constants import Commands, Status
from app.service.service_settings import ServiceSettings

import app.constants as constants

from .stream_handler import IStreamHandler


class ServiceClientFields:
    STATUS = 'status'


class ServiceClient(IClientHandler):
    def __init__(self, settings: ServiceSettings, handler: IStreamHandler):
        self._request_id = 0
        self._handler = handler
        self._service_settings = settings
        self._client = Client(settings.host, settings.port, self)

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

    def stop_service(self, delay: int):
        return self._client.stop_service(self._gen_request_id(), delay)

    def get_log_service(self, sid: str):
        return self._client.get_log_service(self._gen_request_id(),
                                            constants.DEFAULT_SERVICE_LOG_PATH_TEMPLATE_1S.format(sid))

    def start_stream(self, config: dict):
        return self._client.start_stream(self._gen_request_id(), config)

    def stop_stream(self, stream_id: str):
        return self._client.stop_stream(self._gen_request_id(), stream_id)

    def restart_stream(self, stream_id: str):
        return self._client.restart_stream(self._gen_request_id(), stream_id)

    def get_log_stream(self, stream_id: str, feedback_directory: str):
        return self._client.get_log_stream(self._gen_request_id(), stream_id, feedback_directory,
                                           constants.DEFAULT_STREAM_LOG_PATH_TEMPLATE_1S.format(stream_id))

    # handler
    def process_response(self, req: Request, resp: Response):
        if not req:
            return

        if req.method == Commands.ACTIVATE_COMMAND and resp.is_message():
            self._prepare_service()
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

    def to_front(self) -> dict:
        return {ServiceClientFields.STATUS: self.status()}

    # private
    def _prepare_service(self):
        return self._client.prepare_service(self._gen_request_id(), self._service_settings.feedback_directory,
                                            self._service_settings.timeshifts_directory,
                                            self._service_settings.hls_directory,
                                            self._service_settings.playlists_directory,
                                            self._service_settings.dvb_directory,
                                            self._service_settings.capture_card_directory)

    def _gen_request_id(self) -> int:
        current_value = self._request_id
        self._request_id += 1
        return current_value
