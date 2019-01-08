from .client import Client, IClientHandler, Request, Response, Command
import app.constants as constants


class IptvCloud(IClientHandler):
    def __init__(self, id: str, host: str, port: int):
        self.id = id
        self._client = Client(host, port, self)
        self._id = 0

    def id(self):
        return self.id

    def connect(self):
        self._client.connect()

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
        if req and req.method == Command.ACTIVATE_COMMAND and resp.is_message():
            self.prepare_service(constants.DEFAULT_FEEDBACK_DIR_PATH, constants.DEFAULT_TIMESHIFTS_DIR_PATH,
                                 constants.DEFAULT_HLS_DIR_PATH, constants.DEFAULT_PLAYLISTS_DIR_PATH,
                                 constants.DEFAULT_DVB_DIR_PATH, constants.DEFAULT_CAPTURE_DIR_PATH)

        print(resp)
        pass

    def process_request(self, req: Request):
        print(req)
        pass

    # private
    def _gen_request_id(self) -> int:
        old_val = self._id
        self._id += 1
        return old_val
