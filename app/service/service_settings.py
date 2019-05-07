from mongoengine import EmbeddedDocument, StringField, IntField, ListField, EmbeddedDocumentField, ObjectIdField
import app.constants as constants
from app.stream.stream_entry import Stream
from bson.objectid import ObjectId


class ServiceSettings(EmbeddedDocument):
    DEFAULT_SERVICE_NAME = 'Service'
    MIN_SERVICE_NAME_LENGTH = 3
    MAX_SERVICE_NAME_LENGTH = 30

    DEFAULT_FEEDBACK_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/feedback'
    DEFAULT_TIMESHIFTS_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/timeshifts'
    DEFAULT_HLS_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/hls'
    DEFAULT_PLAYLISTS_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/playlists'
    DEFAULT_DVB_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/dvb'
    DEFAULT_CAPTURE_DIR_PATH = constants.DEFAULT_SERVICE_ROOT_DIR_PATH + '/capture_card'
    DEFAULT_SERVICE_HOST = 'localhost'
    DEFAULT_SERVICE_PORT = 6317

    meta = {'collection': 'service', 'auto_create_index': False}
    id = ObjectIdField(required=True, default=ObjectId,
                       unique=True, primary_key=True)

    name = StringField(unique=True, default=DEFAULT_SERVICE_NAME, max_length=MAX_SERVICE_NAME_LENGTH,
                       min_length=MIN_SERVICE_NAME_LENGTH)
    host = StringField(default=DEFAULT_SERVICE_HOST)
    port = IntField(default=DEFAULT_SERVICE_PORT)

    feedback_directory = StringField(default=DEFAULT_FEEDBACK_DIR_PATH)
    timeshifts_directory = StringField(default=DEFAULT_TIMESHIFTS_DIR_PATH)
    hls_directory = StringField(default=DEFAULT_HLS_DIR_PATH)
    playlists_directory = StringField(default=DEFAULT_PLAYLISTS_DIR_PATH)
    dvb_directory = StringField(default=DEFAULT_DVB_DIR_PATH)
    capture_card_directory = StringField(default=DEFAULT_CAPTURE_DIR_PATH)

    streams = ListField(EmbeddedDocumentField(Stream), default=[])
