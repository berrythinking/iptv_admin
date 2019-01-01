import socket, struct, json


class ResponseStatus:
    FAIL = 0
    OK = 1


class SeqType:
    REQUEST = 0
    RESPONSE = 1


class Command:
    ACTIVATE_COMMAND = 'activate_request'


CmdID = str


class Request:
    def __init__(self, cmd_id: CmdID, command: Command, command_args: dict):
        self.id = cmd_id
        self.command = command
        self.command_args = command_args


class Response:
    def __init__(self, cmd_id: CmdID, command: Command, status: ResponseStatus):
        self.id = cmd_id
        self.command = command
        self.status = status


def _parse_response_or_request(data: str):
    return None


class Handler:
    def ProcessUnhandledData(self, resp: Response):
        pass


class Client:
    def __init__(self, host: str, port: int, handler=None):
        self.host = host
        self.port = port
        self._handler = handler
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active = False

    def connect(self):
        self._socket.connect((self.host, self.port))

    def activate(self, id_request: str, license: str):
        command_args = {'license_key': license}
        self._send_request(id_request, Command.ACTIVATE_COMMAND, command_args)
        resp = self._read_response_by_id(id_request)
        if resp:
            self.active = True

    def _send_request(self, id_request: CmdID, command: str, command_args: dict):
        data = '0 {0} {1} {2}\r\n'.format(id_request, command, json.dumps(command_args))
        data_len = socket.ntohl(len(data))
        array = struct.pack("I", data_len)
        data_to_send_bytes = array + data.encode()
        self._socket.send(data_to_send_bytes)

    def _read_response_by_id(self, cmd_id: CmdID) -> Response:
        while True:
            resp_or_req = self._read_response_or_request()
            if not resp_or_req:
                continue

            if resp_or_req.id == cmd_id:
                return resp_or_req
            else:
                if self._handler:
                    self._handler.ProcessUnhandledData(resp_or_req)

    def _read_response_or_request(self):
        data = self._socket.recv(4096)
        if data:
            var = data[4:]
            return _parse_response_or_request(var.decode())

        return None
