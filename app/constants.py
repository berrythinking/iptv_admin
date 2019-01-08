from enum import IntEnum


class StreamType(IntEnum):
    RELAY = 0
    ENCODING = 1
    TIMESHIFT_PLAYER = 2
    TIMESHIFT_RECORDER = 3
    CATCHUP = 4

    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


class StreamStatus(IntEnum):
    NEW = 0
    NULL = 1
    STARTED = 2
    READY = 3
    PLAYING = 4
    FROZEN = 5
    WAITING = 6


class StreamLogLevel(IntEnum):
    LOG_LEVEL_EMERG = 0
    LOG_LEVEL_ALERT = 1
    LOG_LEVEL_CRIT = 2
    LOG_LEVEL_ERR = 3
    LOG_LEVEL_WARNING = 4
    LOG_LEVEL_NOTICE = 5
    LOG_LEVEL_INFO = 6
    LOG_LEVEL_DEBUG = 7

    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)


MIN_URL_LENGHT = 3
MAX_URL_LENGHT = 80
MIN_STREAM_NAME_LENGHT = 3
MAX_STREAM_NAME_LENGHT = 30
MIN_PATH_LENGHT = 1
MAX_PATH_LENGHT = 255

PRECISION = 2

DATE_JS_FORMAT = '%m/%d/%Y %H:%M:%S'

DEFAULT_LOCALE = 'en'
AVAILABLE_LOCALES = DEFAULT_LOCALE, 'ru'
AVAILABLE_LOCALES_PAIRS = [(DEFAULT_LOCALE, 'English'), ('ru', 'Russian')]

DEFAULT_STREAM_NAME = 'Stream'
AVAILABLE_STREAM_TYPES_PAIRS = [(StreamType.RELAY, 'relay'), (StreamType.ENCODING, 'encoding'),
                                (StreamType.TIMESHIFT_PLAYER, 'timeshift_player'),
                                (StreamType.TIMESHIFT_RECORDER, 'timeshift_record'), (StreamType.CATCHUP, 'catchup')]
AVAILABLE_LOG_LEVELS_PAIRS = [(StreamLogLevel.LOG_LEVEL_EMERG, 'EVERG'), (StreamLogLevel.LOG_LEVEL_ALERT, 'ALERT'),
                              (StreamLogLevel.LOG_LEVEL_CRIT, 'CRITICAL'),
                              (StreamLogLevel.LOG_LEVEL_ERR, 'ERROR'),
                              (StreamLogLevel.LOG_LEVEL_WARNING, 'WARNING'),
                              (StreamLogLevel.LOG_LEVEL_NOTICE, 'NOTICE'),
                              (StreamLogLevel.LOG_LEVEL_INFO, 'INFO'),
                              (StreamLogLevel.LOG_LEVEL_DEBUG, 'DEBUG')]

DEFAULT_SERVICE_ROOT_DIR_PATH = '~/streamer'
DEFAULT_FEEDBACK_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/feedback'
DEFAULT_TIMESHIFTS_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/timeshifts'
DEFAULT_HLS_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/hls'
DEFAULT_PLAYLISTS_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/playlists'
DEFAULT_DVB_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/dvb'
DEFAULT_CAPTURE_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/capture_card'


def round_value(value: float):
    return round(value, PRECISION)
