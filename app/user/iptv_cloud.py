from . import client


class IptvCloud:
    def __init__(self, id: str, host: str, port: int):
        self.id = id
        self._client = client.Client(host, port)
        self._client.connect()
        self._id = 0

    def id(self):
        return self.id

    def activate(self, license: str):
        return self._client.activate(self._gen_request_id(), license)

    def _gen_request_id(self) -> client.CmdID:
        return str(++self._id)
