from . import client


class IptvCloud:
    def __init__(self, id: str, host: str, port: int, handler=None):
        self.id = id
        self._client = client.Client(host, port, handler)
        self._client.connect()
        self._id = client.ACTIVE_SERVICE_ID + 1

    def id(self):
        return self.id

    def activate(self, license_key: str):
        return self._client.activate(license_key)

    def service_state(self, jobs_directory: str, timeshifts_directory: str, hls_directory: str,
                      playlists_directory: str, dvb_directory: str, capture_card_directory: str):
        return self._client.service_state(self._gen_request_id(), jobs_directory, timeshifts_directory, hls_directory,
                                          playlists_directory, dvb_directory, capture_card_directory)

    def stop_service(self, delay: int):
        return self._client.stop_service(self._gen_request_id(), delay)

    def start_stream(self, feedback_dir: str, log_level: int, config: dict):
        return self._client.start_stream(self._gen_request_id(), feedback_dir, log_level, config)

    def stop_stream(self, stream_id: str):
        return self._client.stop_stream(self._gen_request_id(), stream_id)

    def restart_stream(self, stream_id: str):
        return self._client.restart_stream(self._gen_request_id(), stream_id)

    # private
    def _gen_request_id(self) -> int:
        return ++self._id
