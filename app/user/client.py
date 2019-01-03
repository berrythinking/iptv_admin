import socket
import struct
import json
import threading

from datetime import datetime
from abc import ABC, abstractmethod


def make_utc_timestamp() -> int:
    return int(datetime.utcnow().timestamp() * 1000)


class Command:
    ACTIVATE_COMMAND = 'activate_request'
    STATE_SERVICE_COMMAND = 'state_service'
    STOP_SERVICE_COMMAND = 'stop_service'
    START_STREAM_COMMAND = 'start_stream'
    STOP_STREAM_COMMAND = 'stop_stream'
    RESTART_STREAM_COMMAND = 'restart_stream'
    CLIENT_PING_COMMAND = 'ping_client'
    SERVICE_PING_COMMAND = 'ping_service'


class Request:
    def __init__(self, command_id, method: str, params: dict):
        self.id = command_id
        self.method = method
        self.params = params

    def is_valid(self):
        return self.method

    def is_notification(self):
        return not self.id

    def to_dict(self) -> dict:
        if self.id:
            return {
                "method": self.method,
                "params": self.params,
                "jsonrpc": "2.0",
                "id": self.id,
            }
        else:
            return {
                "method": self.method,
                "params": self.params,
                "jsonrpc": "2.0"
            }


class Response:
    def __init__(self, command_id: str, result=None, error=None):
        self.id = command_id
        self.result = result
        self.error = error

    def is_valid(self):
        return self.id

    def is_error(self):
        return self.error

    def is_message(self):
        return self.result

    def to_dict(self) -> dict:
        if self.is_error():
            return {
                "error": self.error,
                "jsonrpc": "2.0",
                "id": self.id,
            }

        if self.is_message():
            return {
                "result": self.result,
                "jsonrpc": "2.0",
                "id": self.id,
            }


# rpc functions
def parse_response_or_request(data: str) -> (Request, Response):
    resp_req = json.loads(data)

    if 'method' in resp_req:
        params = None
        if 'params' in resp_req:
            params = resp_req['params']

        command_id = None
        if 'params' in resp_req:
            command_id = resp_req['id']

        return Request(command_id, resp_req['method'], params), None

    if 'result' in resp_req:
        return None, Response(resp_req['id'], resp_req['result'], None)

    if 'error' in resp_req:
        return None, Response(resp_req['id'], None, resp_req['error'])

    return None, None


def generate_seq_id(command_id):  # uint64_t
    if command_id is None:
        return None

    converted_bytes = command_id.to_bytes(8, byteorder='big')
    return converted_bytes.hex()


def generate_json_rpc_responce_message(result, command_id: str) -> Response:
    return Response(command_id, result)


def generate_json_rpc_responce_error(message: str, code: int, command_id: str) -> Response:
    return Response(command_id, None, {"code": code, "message": message})


# handler for client
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
        self._request_queue = dict()

    def connect(self):
        self._socket.connect((self.host, self.port))
        self._listen_thread.start()

    def disconnect(self):
        self._stop_listen = True
        self._listen_thread.join()
        self._socket.close()

    def activate(self, command_id: int, license_key: str):
        command_args = {"license_key": license_key}
        self._send_request(command_id, Command.ACTIVATE_COMMAND, command_args)

    def is_active(self):
        return self.active

    def ping_service(self, command_id: int):
        if not self.is_active():
            return

        self._send_request(command_id, Command.SERVICE_PING_COMMAND, {"timestamp": make_utc_timestamp()})

    def state_service(self, command_id: int, jobs_directory: str, timeshifts_directory: str, hls_directory: str,
                      playlists_directory: str, dvb_directory: str, capture_card_directory: str):
        if not self.is_active():
            return

        command_args = {
            "jobs_directory": jobs_directory,
            "timeshifts_directory": timeshifts_directory,
            "hls_directory": hls_directory,
            "playlists_directory": playlists_directory,
            "dvb_directory": dvb_directory,
            "capture_card_directory": capture_card_directory
        }
        self._send_request(command_id, Command.STATE_SERVICE_COMMAND, command_args)

    def stop_service(self, command_id: int, delay: int):
        if not self.is_active():
            return

        command_args = {"delay": delay}
        self._send_request(command_id, Command.STOP_SERVICE_COMMAND, command_args)

    def start_stream(self, command_id: int, feedback_dir: str, log_level: int, config: dict):
        if not self.is_active():
            return

        command_args = {"command_line": "feedback_dir='{0}' log_level={1}".format(feedback_dir, log_level),
                        "config": config}
        self._send_request(command_id, Command.START_STREAM_COMMAND, command_args)

    def stop_stream(self, command_id: int, stream_id: str):
        if not self.is_active():
            return

        command_args = {"id": stream_id}
        self._send_request(command_id, Command.STOP_STREAM_COMMAND, command_args)

    def restart_stream(self, command_id: int, stream_id: str):
        if not self.is_active():
            return

        command_args = {"id": stream_id}
        self._send_request(command_id, Command.RESTART_STREAM_COMMAND, command_args)

    # private
    def _pong(self, command_id: str):
        if not self.is_active():
            return

        self._send_responce(command_id, {"timestamp": make_utc_timestamp()})

    def _send_request(self, command_id, method: str, params):
        cid = generate_seq_id(command_id)
        req = Request(cid, method, params)
        data = json.dumps(req.to_dict())
        data_len = socket.ntohl(len(data))
        array = struct.pack("I", data_len)
        data_to_send_bytes = array + data.encode()
        self._socket.send(data_to_send_bytes)
        if not req.is_notification():
            self._request_queue[cid] = req

    def _send_notification(self, method: str, params):
        return self._send_request(None, method, params)

    def _send_responce(self, command_id, params):
        resp = generate_json_rpc_responce_message(params, command_id)
        data = json.dumps(resp.to_dict())
        data_len = socket.ntohl(len(data))
        array = struct.pack("I", data_len)
        data_to_send_bytes = array + data.encode()
        self._socket.send(data_to_send_bytes)

    def _listen_commands(self):
        while not self._stop_listen:
            req, resp = self._read_response_or_request()
            if req:
                if req.method == Command.CLIENT_PING_COMMAND:
                    self._pong(req.id)

                if self._handler:
                    self._handler.process_request(req)
            elif resp:
                saved_req = self._request_queue.pop(resp.id, None)
                if saved_req and saved_req.method == Command.ACTIVATE_COMMAND and resp.is_message():
                    self.active = True

                if self._handler:
                    self._handler.process_response(resp)

    def _read_response_or_request(self) -> (Request, Response):
        data = self._socket.recv(8 * 1024)
        if data:
            var = data[4:]
            decoded_data = var.decode()
            # print(decoded_data)
            return parse_response_or_request(decoded_data)

        return None, None
