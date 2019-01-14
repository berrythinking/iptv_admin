import socket
import struct
import json
import threading
import select

from datetime import datetime
from app.client.client_constants import Commands, Status
from app.client.client_handler import IClientHandler
from app.client.json_rpc import Request, Response, parse_response_or_request


def make_utc_timestamp() -> int:
    return int(datetime.utcnow().timestamp() * 1000)


def generate_seq_id(command_id):  # uint64_t
    if command_id is None:
        return None

    converted_bytes = command_id.to_bytes(8, byteorder='big')
    return converted_bytes.hex()


def generate_json_rpc_responce_message(result, command_id: str) -> Response:
    return Response(command_id, result)


def generate_json_rpc_responce_error(message: str, code: int, command_id: str) -> Response:
    return Response(command_id, None, {"code": code, "message": message})


class Client:
    def __init__(self, host: str, port: int, handler: IClientHandler):
        self.host = host
        self.port = port
        self._handler = handler
        self._socket = None
        self._listen_thread = None
        self._stop_listen = False
        self._request_queue = dict()
        self._state = Status.INIT

    def status(self) -> Status:
        return self._state

    def connect(self):
        if self.is_connected():
            return

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
        except socket.error as exc:
            print('Caught exception socket.error : {0}'.format(exc))
            return

        self._socket = sock
        thread = threading.Thread(target=self._listen_commands, daemon=True)
        thread.start()
        self._listen_thread = thread
        self._set_state(Status.CONNECTED)

    def is_connected(self):
        return self._state != Status.INIT

    def disconnect(self):
        if not self.is_connected():
            return

        self._stop_listen = True
        self._listen_thread.join()
        self._listen_thread = None
        self._socket.close()
        self._socket = None
        self._set_state(Status.INIT)
        self._stop_listen = False

    def activate(self, command_id: int, license_key: str):
        command_args = {"license_key": license_key}
        self._send_request(command_id, Commands.ACTIVATE_COMMAND, command_args)

    def is_active(self):
        return self._state == Status.ACTIVE

    def ping_service(self, command_id: int):
        if not self.is_active():
            return

        self._send_request(command_id, Commands.SERVICE_PING_COMMAND, {"timestamp": make_utc_timestamp()})

    def prepare_service(self, command_id: int, feedback_directory: str, timeshifts_directory: str, hls_directory: str,
                        playlists_directory: str, dvb_directory: str, capture_card_directory: str):
        if not self.is_active():
            return

        command_args = {
            "feedback_directory": feedback_directory,
            "timeshifts_directory": timeshifts_directory,
            "hls_directory": hls_directory,
            "playlists_directory": playlists_directory,
            "dvb_directory": dvb_directory,
            "capture_card_directory": capture_card_directory
        }
        self._send_request(command_id, Commands.PREPARE_SERVICE_COMMAND, command_args)

    def stop_service(self, command_id: int, delay: int):
        if not self.is_active():
            return

        command_args = {"delay": delay}
        self._send_request(command_id, Commands.STOP_SERVICE_COMMAND, command_args)

    def start_stream(self, command_id: int, config: dict):
        if not self.is_active():
            return

        command_args = {"config": config}
        self._send_request(command_id, Commands.START_STREAM_COMMAND, command_args)

    def stop_stream(self, command_id: int, stream_id: str):
        if not self.is_active():
            return

        command_args = {"id": stream_id}
        self._send_request(command_id, Commands.STOP_STREAM_COMMAND, command_args)

    def restart_stream(self, command_id: int, stream_id: str):
        if not self.is_active():
            return

        command_args = {"id": stream_id}
        self._send_request(command_id, Commands.RESTART_STREAM_COMMAND, command_args)

    # private
    def _set_state(self, status: Status):
        self._state = status
        if self._handler:
            self._handler.on_state_changed(status)

    def _pong(self, command_id: str):
        if not self.is_active():
            return

        self._send_responce(command_id, {"timestamp": make_utc_timestamp()})

    def _send_request(self, command_id, method: str, params):
        if not self.is_connected():
            return

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
                if req.method == Commands.CLIENT_PING_COMMAND:
                    self._pong(req.id)

                if self._handler:
                    self._handler.process_request(req)
            elif resp:
                saved_req = self._request_queue.pop(resp.id, None)
                if saved_req and saved_req.method == Commands.ACTIVATE_COMMAND and resp.is_message():
                    self._set_state(Status.ACTIVE)

                if self._handler:
                    self._handler.process_response(saved_req, resp)

    def _read_response_or_request(self, timeout=1) -> (Request, Response):
        ready = select.select([self._socket], [], [], timeout)
        if ready[0]:
            data_size_bytes = self._socket.recv(4)
            if data_size_bytes:
                unp = struct.unpack("I", data_size_bytes)
                data_size = socket.ntohl(unp[0])
                if data_size < 8 * 1024:
                    data = self._socket.recv(data_size)
                    if data:
                        decoded_data = data.decode()
                        return parse_response_or_request(decoded_data)

        return None, None
