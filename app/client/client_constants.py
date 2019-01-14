from enum import IntEnum


class Commands:
    # stream
    START_STREAM_COMMAND = 'start_stream'
    STOP_STREAM_COMMAND = 'stop_stream'
    RESTART_STREAM_COMMAND = 'restart_stream'
    CHANGED_STREAM_COMMAND = 'changed_source_stream'
    STATISTIC_STREAM_COMMAND = 'statistic_stream'
    STATUS_STREAM_COMMAND = 'status_stream'

    # service
    ACTIVATE_COMMAND = 'activate_request'
    PREPARE_SERVICE_COMMAND = 'prepare_service'
    STOP_SERVICE_COMMAND = 'stop_service'
    SERVICE_PING_COMMAND = 'ping_service'
    STATISTIC_SERVICE_COMMAND = 'statistic_service'
    CLIENT_PING_COMMAND = 'ping_client'  # ping from service


class Status(IntEnum):
    INIT = 0
    CONNECTED = 1
    ACTIVE = 2
