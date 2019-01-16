from app import db
from datetime import datetime
import app.constants as constants
from bson.objectid import ObjectId

ID_FIELD = "id"
TYPE_FIELD = "type"
FEEDBACK_DIR_FIELD = "feedback_dir"
LOG_LEVEL_FIELD = "log_level"
INPUT_FIELD = "input"
OUTPUT_FIELD = "output"
AUDIO_SELECT_FIELD = "audio_select"
HAVE_VIDEO_FIELD = "have_video"
HAVE_AUDIO_FIELD = "have_audio"

# relay
VIDEO_PARSER_FIELD = "video_parser"
AUDIO_PARSER_FIELD = "audio_parser"


class Url(db.EmbeddedDocument):
    _next_url_id = 0

    id = db.IntField(default=lambda: Url.generate_id(), required=True)
    uri = db.StringField(default='test', max_length=constants.MAX_URL_LENGTH, required=True)

    @staticmethod
    def generate_id():
        current_value = Url._next_url_id
        Url._next_url_id += 1
        return current_value


class Urls(db.EmbeddedDocument):
    urls = db.ListField(db.EmbeddedDocumentField(Url))


class Stream(db.Document):
    meta = {'collection': 'streams', 'auto_create_index': False, 'allow_inheritance': True}
    name = db.StringField(default=constants.DEFAULT_STREAM_NAME, max_length=constants.MAX_STREAM_NAME_LENGTH,
                          required=True)
    type = db.IntField(default=constants.StreamType.RELAY, required=True)
    created_date = db.DateTimeField(default=datetime.now)  # for inner use
    log_level = db.IntField(default=constants.StreamLogLevel.LOG_LEVEL_INFO, required=True)

    input = db.EmbeddedDocumentField(Urls,
                                     default=Urls())  # "input": {"urls": [{"id": 80,"uri": "tcp://localhost:1935"}]}
    output = db.EmbeddedDocumentField(Urls,
                                      default=Urls())  # "output": {"urls": [{"id": 81,"uri": "tcp://localhost:1935"}]}
    have_video = db.BooleanField(default=constants.DEFAULT_HAVE_VIDEO, required=True)
    have_audio = db.BooleanField(default=constants.DEFAULT_HAVE_AUDIO, required=True)
    audio_select = db.IntField(default=constants.DEFAULT_AUDIO_SELECT, required=True)

    # runtime
    status = constants.StreamStatus.NEW

    def config(self) -> dict:
        conf = {ID_FIELD: self.get_id(), TYPE_FIELD: self.get_type(), FEEDBACK_DIR_FIELD: self.generate_feedback_dir(),
                LOG_LEVEL_FIELD: self.get_log_level(), AUDIO_SELECT_FIELD: self.get_audio_select(),
                HAVE_VIDEO_FIELD: self.get_have_video(), HAVE_AUDIO_FIELD: self.get_have_audio(),
                INPUT_FIELD: self.input.to_mongo(),
                OUTPUT_FIELD: self.output.to_mongo()}
        return conf

    def generate_feedback_dir(self):
        return '{0}/{1}/{2}'.format(constants.DEFAULT_FEEDBACK_DIR_PATH,
                                    self.get_type(), self.get_id())

    def get_log_level(self):
        return self.log_level

    def get_audio_select(self):
        return self.audio_select

    def get_have_video(self):
        return self.have_video

    def get_have_audio(self):
        return self.have_audio

    def get_id(self):
        return str(self.id)

    def get_type(self):
        return self.type


class RelayStream(Stream):
    def __init__(self, *args, **kwargs):
        super(RelayStream, self).__init__(*args, **kwargs)
        # super(RelayStream, self).type = constants.StreamType.RELAY

    video_parser = db.StringField(default=constants.DEFAULT_RELAY_VIDEO_PARSER, required=True)
    audio_parser = db.StringField(default=constants.DEFAULT_RELAY_AUDIO_PARSER, required=True)

    def config(self) -> dict:
        conf = super(RelayStream, self).config()
        conf[VIDEO_PARSER_FIELD] = self.get_video_parser()
        conf[AUDIO_PARSER_FIELD] = self.get_audio_parser()
        return conf

    def get_video_parser(self):
        return self.video_parser

    def get_audio_parser(self):
        return self.audio_parser


class EncodeStream(Stream):
    def __init__(self, *args, **kwargs):
        super(EncodeStream, self).__init__(*args, **kwargs)


def make_relay_stream() -> Stream:
    stream = RelayStream(type=constants.StreamType.RELAY)
    stream.input = Urls(urls=[Url(id=Url.generate_id())])
    stream.output = Urls(urls=[Url(id=Url.generate_id())])
    return stream


def make_encode_stream() -> Stream:
    stream = EncodeStream(type=constants.StreamType.ENCODE)
    stream.input = Urls(urls=[Url(id=Url.generate_id())])
    stream.output = Urls(urls=[Url(id=Url.generate_id())])
    return stream


class StreamsHolder:
    def __init__(self):
        self._streams = []
        self._reload_from_db()

    def add_stream(self, stream: Stream):
        self._streams.append(stream)
        stream.save()

    def remove_stream(self, sid: str):
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                stream.delete()
                self._streams.remove(stream)
                break

    def get_streams(self):
        return self._streams

    def find_stream_by_id(self, sid: str):
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                return stream

        return None

    # private
    def _reload_from_db(self):
        self._streams = []
        streams = Stream.objects()
        for stream in streams:
            self._streams.append(stream)
