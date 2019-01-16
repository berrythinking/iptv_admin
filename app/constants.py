from enum import IntEnum


class StreamType(IntEnum):
    RELAY = 0
    ENCODE = 1
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
    INIT = 1
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


MIN_URL_LENGTH = 3
MAX_URL_LENGTH = 80
MIN_STREAM_NAME_LENGTH = 3
MAX_STREAM_NAME_LENGTH = 30
MIN_PATH_LENGTH = 1
MAX_PATH_LENGTH = 255

PRECISION = 2

DATE_JS_FORMAT = '%m/%d/%Y %H:%M:%S'

DEFAULT_LOCALE = 'en'
AVAILABLE_LOCALES = DEFAULT_LOCALE, 'ru'
AVAILABLE_LOCALES_PAIRS = [(DEFAULT_LOCALE, 'English'), ('ru', 'Russian')]

DEFAULT_STREAM_NAME = 'Stream'
AVAILABLE_STREAM_TYPES_PAIRS = [(StreamType.RELAY, 'relay'), (StreamType.ENCODE, 'encode'),
                                (StreamType.TIMESHIFT_PLAYER, 'timeshift_player'),
                                (StreamType.TIMESHIFT_RECORDER, 'timeshift_record'), (StreamType.CATCHUP, 'catchup')]
AVAILABLE_LOG_LEVELS_PAIRS = [(StreamLogLevel.LOG_LEVEL_EMERG, 'EVERG'), (StreamLogLevel.LOG_LEVEL_ALERT, 'ALERT'),
                              (StreamLogLevel.LOG_LEVEL_CRIT, 'CRITICAL'),
                              (StreamLogLevel.LOG_LEVEL_ERR, 'ERROR'),
                              (StreamLogLevel.LOG_LEVEL_WARNING, 'WARNING'),
                              (StreamLogLevel.LOG_LEVEL_NOTICE, 'NOTICE'),
                              (StreamLogLevel.LOG_LEVEL_INFO, 'INFO'),
                              (StreamLogLevel.LOG_LEVEL_DEBUG, 'DEBUG')]

DEFAULT_AUDIO_SELECT = -1
DEFAULT_HAVE_VIDEO = True
DEFAULT_HAVE_AUDIO = True
DEFAULT_DEINTERLACE = False
MIN_FRAME_RATE = 1
INVALID_FRAME_RATE = 0
MAX_FRAME_RATE = 100
MIN_VOLUME = 0
DEFAULT_VOLUME = 1
MAX_VOLUME = 10
MIN_AUDIO_CHANNELS_COUNT = 1
INVALID_AUDIO_CHANNELS_COUNT = 0
MAX_AUDIO_CHANNELS_COUNT = 8

TS_VIDEO_PARSER = 'tsparse'
H264_VIDEO_PARSER = 'h264parse'
H265_VIDEO_PARSER = 'h265parse'
DEFAULT_VIDEO_PARSER = H264_VIDEO_PARSER

AAC_AUDIO_PARSER = 'aacparse'
AC3_AUDIO_PARSER = 'ac3parse'
MPEG_AUDIO_PARSER = 'mpegaudioparse'
DEFAULT_AUDIO_PARSER = AAC_AUDIO_PARSER

AVAILABLE_VIDEO_PARSERS = [(TS_VIDEO_PARSER, 'ts'), (H264_VIDEO_PARSER, 'h264'), (H265_VIDEO_PARSER, 'h265')]
AVAILABLE_AUDIO_PARSERS = [(MPEG_AUDIO_PARSER, 'mpeg'), (AAC_AUDIO_PARSER, 'aac'), (AC3_AUDIO_PARSER, 'ac3')]

EAVC_ENC = 'eavcenc'
OPEN_H264_ENC = 'openh264enc'
X264_ENC = 'x264enc'
NV_H264_ENC = 'nvh264enc'
VAAPI_H264_ENC = 'vaapih264enc'
VAAPI_MPEG2_ENC = 'vaapimpeg2enc'
MFX_H264_ENC = 'mfxh264enc'
X265_ENC = 'x265enc'
MSDK_H264_ENC = 'msdkh264enc'
DEFAULT_VIDEO_CODEC = X264_ENC

LAME_MP3_ENC = 'lamemp3enc'
FAAC = 'faac'
VOAAC_ENC = 'voaacenc'
DEFAULT_AUDIO_CODEC = FAAC

AVAILABLE_VIDEO_CODECS = [(EAVC_ENC, 'eav'), (OPEN_H264_ENC, 'openh264'), (X264_ENC, 'x264'), (NV_H264_ENC, 'nvh264'),
                          (VAAPI_H264_ENC, 'vaapih264'), (VAAPI_MPEG2_ENC, 'vaapimpeg2'), (MFX_H264_ENC, 'mfxh264'),
                          (X265_ENC, 'x265'), (MSDK_H264_ENC, 'msdkh264')]
AVAILABLE_AUDIO_CODECS = [(LAME_MP3_ENC, 'mpe'), (FAAC, 'aac'), (VOAAC_ENC, 'voaac')]

DEFAULT_SERVICE_ROOT_DIR_PATH = '~/streamer'
DEFAULT_FEEDBACK_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/feedback'
DEFAULT_TIMESHIFTS_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/timeshifts'
DEFAULT_HLS_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/hls'
DEFAULT_PLAYLISTS_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/playlists'
DEFAULT_DVB_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/dvb'
DEFAULT_CAPTURE_DIR_PATH = DEFAULT_SERVICE_ROOT_DIR_PATH + '/capture_card'


def round_value(value: float):
    return round(value, PRECISION)
