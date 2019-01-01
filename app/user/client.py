import socket
import struct
import json
import threading

from abc import ABC, abstractmethod

ACTIVE_SERVICE_ID = "0"


class SeqType:
    REQUEST = 0
    RESPONSE = 1


class Command:
    ACTIVATE_COMMAND = 'activate_request'
    CLIENT_PING_COMMAND = 'client_ping'


class Request:
    def __init__(self, command_id: int, command: Command, params: dict):
        self.id = command_id
        self.command = command
        self.params = params


class Response:
    def __init__(self, command_id: int, result=None, error=None):
        self.id = command_id
        self.result = result
        self.error = error

    def is_error(self):
        return not self.is_message()

    def is_message(self):
        return self.result


def parse_response_or_request(data: str) -> (Request, Response):
    resp_req = json.loads(data)
    if 'id' not in resp_req:
        return None, None

    if 'method' in resp_req:
        params = None
        if 'params' in resp_req:
            params = resp_req['params']

        return Request(resp_req['id'], resp_req['method'], params), None

    if 'result' in resp_req:
        return None, Response(resp_req['id'], resp_req['result'], None)

    if 'error' in resp_req:
        return None, Response(resp_req['id'], None, resp_req['error'])

    return None, None


def generate_json_rpc_request(method: str, params, command_id: str) -> dict:
    return {
        "method": method,
        "params": params,
        "jsonrpc": "2.0",
        "id": command_id,
    }


def generate_json_rpc_responce_message(result, command_id: str) -> dict:
    return {
        "result": result,
        "jsonrpc": "2.0",
        "id": command_id,
    }


def generate_json_rpc_responce_error(message: str, code: int, command_id: str) -> dict:
    return {
        "error": {"code": code, "message": message},
        "jsonrpc": "2.0",
        "id": command_id,
    }


class IClientHandler(ABC):
    @abstractmethod
    def process_response(self, resp: Response):
        pass

    @abstractmethod
    def process_request(self, req: Request):
        pass


class Client:
    def __init__(self, host: str, port: int, handler: IClientHandler):
        self.host = host
        self.port = port
        self._handler = handler
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.active = False
        self._listen_thread = threading.Thread(target=self._listen_commands)
        self._listen_thread.daemon = True
        self._stop_listen = False

    def connect(self):
        self._socket.connect((self.host, self.port))
        self._listen_thread.start()

    def disconnect(self):
        self._stop_listen = True
        self._listen_thread.join()
        self._socket.close()

    def activate(self, license_key: str):
        command_args = {'license_key': license_key}
        self._send_request(Command.ACTIVATE_COMMAND, command_args, ACTIVE_SERVICE_ID)

    def is_active(self):
        return self.active

    def _pong(self, command_id: str):
        if not self.is_active():
            return

        self._send_responce({}, command_id)

    def _send_request(self, method: str, params, command_id: str):
        data = json.dumps(generate_json_rpc_request(method, params, command_id))
        data_len = socket.ntohl(len(data))
        array = struct.pack("I", data_len)
        data_to_send_bytes = array + data.encode()
        self._socket.send(data_to_send_bytes)

    def _send_responce(self, params, command_id: str):
        data = json.dumps(generate_json_rpc_responce_message(params, command_id))
        data_len = socket.ntohl(len(data))
        array = struct.pack("I", data_len)
        data_to_send_bytes = array + data.encode()
        self._socket.send(data_to_send_bytes)

    def _listen_commands(self):
        while not self._stop_listen:
            req, resp = self._read_response_or_request()
            if req:
                if req.command == Command.CLIENT_PING_COMMAND:
                    self._pong(req.id)

                if self._handler:
                    self._handler.process_request(req)
            elif resp:
                if resp.id == ACTIVE_SERVICE_ID and resp.is_message():
                    self.active = True

                if self._handler:
                    self._handler.process_response(resp)

    def _read_response_or_request(self) -> (Request, Response):
        data = self._socket.recv(4096)
        if data:
            var = data[4:]
            return parse_response_or_request(var.decode())

        return None, None
