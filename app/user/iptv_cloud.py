from .client import Client, IClientHandler, Request, Response
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

    def state_service(self, jobs_directory: str, timeshifts_directory: str, hls_directory: str,
                      playlists_directory: str, dvb_directory: str, capture_card_directory: str):
        return self._client.state_service(self._gen_request_id(), jobs_directory, timeshifts_directory, hls_directory,
                                          playlists_directory, dvb_directory, capture_card_directory)

    def stop_service(self, delay: int):
        return self._client.stop_service(self._gen_request_id(), delay)

    def start_stream(self, feedback_dir: str, log_level: constants.StreamLogLevel, config: dict):
        return self._client.start_stream(self._gen_request_id(), feedback_dir, log_level, config)

    def stop_stream(self, stream_id: str):
        return self._client.stop_stream(self._gen_request_id(), stream_id)

    def restart_stream(self, stream_id: str):
        return self._client.restart_stream(self._gen_request_id(), stream_id)

    # handler
    def process_response(self, req: Request, resp: Response):
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
