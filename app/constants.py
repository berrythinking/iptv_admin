PRECISION = 2

DATE_JS_FORMAT = '%m/%d/%Y %H:%M:%S'

DEFAULT_LOCALE = 'en'
AVAILABLE_LOCALES = DEFAULT_LOCALE, 'ru'
AVAILABLE_LOCALES_PAIRS = [(DEFAULT_LOCALE, 'English'), ('ru', 'Russian')]


def round_value(value: float):
    return round(value, PRECISION)
