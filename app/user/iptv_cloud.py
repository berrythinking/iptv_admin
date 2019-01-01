from . import client


class IptvCloud:
    def __init__(self, id: str, host: str, port: int, handler=None):
        self.id = id
        self._client = client.Client(host, port, handler)
        self._client.connect()
        self._id = 1

    def id(self):
        return self.id

    def activate(self, license: str):
        return self._client.activate(license)

    def _gen_request_id(self) -> str:
        return str(++self._id)
