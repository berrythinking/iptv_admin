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


PRECISION = 2

DATE_JS_FORMAT = '%m/%d/%Y %H:%M:%S'

DEFAULT_LOCALE = 'en'
AVAILABLE_LOCALES = DEFAULT_LOCALE, 'ru'
AVAILABLE_LOCALES_PAIRS = [(DEFAULT_LOCALE, 'English'), ('ru', 'Russian')]

DEFAULT_STREAM_NAME = 'Stream'
AVAILABLE_STREAM_TYPES_PAIRS = [(StreamType.RELAY, 'relay'), (StreamType.ENCODING, 'encoding'),
                                (StreamType.TIMESHIFT_PLAYER, 'timeshift_player'),
                                (StreamType.TIMESHIFT_RECORDER, 'timeshift_record'), (StreamType.CATCHUP, 'catchup')]


def round_value(value: float):
    return round(value, PRECISION)
