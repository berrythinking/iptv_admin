from app import db
from datetime import datetime
import app.constants as constants

ID_FIELD = "id"
TYPE_FIELD = "type"
FEEDBACK_DIR_FIELD = "feedback_dir"
LOG_LEVEL_FIELD = "log_level"
INPUT_FIELD = "input"
OUTPUT_FIELD = "output"
AUDIO_SELECT_FIELD = "audio_select"
HAVE_VIDEO_FIELD = "have_video"
HAVE_AUDIO_FIELD = "have_audio"
LOOP_FIELD = "loop"
AUTO_EXIT_TIME_FIELD = "auto_exit_time"
RESTART_ATTEMPTS_FIELD = "restart_attempts"

# encode
DEINTERLACE_FIELD = "deinterlace"
FRAME_RATE_FIELD = "frame_rate"
VOLUME_FIELD = "volume"
VIDEO_CODEC_FIELD = "video_codec"
AUDIO_CODEC_FIELD = "audio_codec"
AUDIO_CHANNELS_COUNT_FIELD = "audio_channels"
SIZE_FIELD = "size"
VIDEO_BIT_RATE_FIELD = "video_bitrate"
AUDIO_BIT_RATE_FIELD = "audio_bitrate"
LOGO_FIELD = "logo"
ASPCET_RATIO_FIELD = "aspect_ratio"
# relay
VIDEO_PARSER_FIELD = "video_parser"
AUDIO_PARSER_FIELD = "audio_parser"


# {"urls": [{"id": 81,"uri": "tcp://localhost:1935"}]}
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

    input = db.EmbeddedDocumentField(Urls, default=Urls())
    output = db.EmbeddedDocumentField(Urls, default=Urls())
    have_video = db.BooleanField(default=constants.DEFAULT_HAVE_VIDEO, required=True)
    have_audio = db.BooleanField(default=constants.DEFAULT_HAVE_AUDIO, required=True)
    audio_select = db.IntField(default=constants.INVALID_AUDIO_SELECT, required=True)
    loop = db.BooleanField(default=constants.DEFAULT_LOOP, required=True)
    restart_attempts = db.IntField(default=constants.DEFAULT_RESTART_ATTEMPTS, required=True)
    auto_exit_time = db.IntField(default=constants.DEFAULT_AUTO_EXIT_TIME, required=True)

    # runtime
    status = constants.StreamStatus.NEW

    def config(self) -> dict:
        conf = {
            ID_FIELD: self.get_id(),  # required
            TYPE_FIELD: self.get_type(),  # required
            FEEDBACK_DIR_FIELD: self.generate_feedback_dir(),  # required
            LOG_LEVEL_FIELD: self.get_log_level(),
            AUTO_EXIT_TIME_FIELD: self.get_auto_exit_time(),
            LOOP_FIELD: self.get_loop(),
            HAVE_VIDEO_FIELD: self.get_have_video(),  # required
            HAVE_AUDIO_FIELD: self.get_have_audio(),  # required
            RESTART_ATTEMPTS_FIELD: self.get_restart_attempts(),
            INPUT_FIELD: self.input.to_mongo(),  # required empty in timeshift_player
            OUTPUT_FIELD: self.output.to_mongo()  # required empty in timeshift_record
        }

        audio_select = self.get_audio_select()
        if audio_select != constants.INVALID_AUDIO_SELECT:
            conf[AUDIO_SELECT_FIELD] = audio_select
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

    def get_loop(self):
        return self.loop

    def get_restart_attempts(self):
        return self.restart_attempts

    def get_auto_exit_time(self):
        return self.auto_exit_time


class RelayStream(Stream):
    def __init__(self, *args, **kwargs):
        super(RelayStream, self).__init__(*args, **kwargs)
        # super(RelayStream, self).type = constants.StreamType.RELAY

    video_parser = db.StringField(default=constants.DEFAULT_VIDEO_PARSER, required=True)
    audio_parser = db.StringField(default=constants.DEFAULT_AUDIO_PARSER, required=True)

    def config(self) -> dict:
        conf = super(RelayStream, self).config()
        conf[VIDEO_PARSER_FIELD] = self.get_video_parser()
        conf[AUDIO_PARSER_FIELD] = self.get_audio_parser()
        return conf

    def get_video_parser(self):
        return self.video_parser

    def get_audio_parser(self):
        return self.audio_parser


class Logo(db.EmbeddedDocument):
    path = db.StringField(default=constants.INVALID_LOGO_PATH, required=True)
    x = db.IntField(default=constants.DEFAULT_LOGO_X, required=True)
    y = db.IntField(default=constants.DEFAULT_LOGO_Y, required=True)
    alpha = db.FloatField(default=constants.DEFAULT_LOGO_ALPHA, required=True)

    def is_valid(self):
        return self.path != constants.INVALID_LOGO_PATH

    def to_dict(self) -> dict:
        return {'path': self.path, 'position': '{0},{1}'.format(self.x, self.y), 'alpha': self.alpha}


class Size(db.EmbeddedDocument):
    width = db.IntField(default=constants.INVALID_WIDTH, required=True)
    height = db.IntField(default=constants.INVALID_HEIGHT, required=True)

    def is_valid(self):
        return self.width != constants.INVALID_WIDTH and self.height != constants.INVALID_HEIGHT

    def __str__(self):
        return '{0}x{1}'.format(self.width, self.height)


class Rational(db.EmbeddedDocument):
    num = db.IntField(default=constants.INVALID_RATIO_NUM, required=True)
    den = db.IntField(default=constants.INVALID_RATIO_DEN, required=True)

    def is_valid(self):
        return self.num != constants.INVALID_RATIO_NUM and self.den != constants.INVALID_RATIO_DEN

    def __str__(self):
        return '{0}:{1}'.format(self.num, self.den)


class EncodeStream(Stream):
    def __init__(self, *args, **kwargs):
        super(EncodeStream, self).__init__(*args, **kwargs)

    deinterlace = db.BooleanField(default=constants.DEFAULT_DEINTERLACE, required=True)
    frame_rate = db.IntField(default=constants.INVALID_FRAME_RATE, required=True)
    volume = db.FloatField(default=constants.DEFAULT_VOLUME, required=True)
    video_codec = db.StringField(default=constants.DEFAULT_VIDEO_CODEC, required=True)
    audio_codec = db.StringField(default=constants.DEFAULT_AUDIO_CODEC, required=True)
    audio_channels_count = db.IntField(default=constants.INVALID_AUDIO_CHANNELS_COUNT, required=True)
    size = db.EmbeddedDocumentField(Size, default=Size())
    video_bit_rate = db.IntField(default=constants.INVALID_VIDEO_BIT_RATE, required=True)
    audio_bit_rate = db.IntField(default=constants.INVALID_AUDIO_BIT_RATE, required=True)
    logo = db.EmbeddedDocumentField(Logo, default=Logo())
    aspect_ratio = db.EmbeddedDocumentField(Rational, default=Rational())

    def config(self) -> dict:
        conf = super(EncodeStream, self).config()
        conf[DEINTERLACE_FIELD] = self.get_deinterlace()
        frame_rate = self.get_frame_rate()
        if frame_rate != constants.INVALID_FRAME_RATE:
            conf[FRAME_RATE_FIELD] = frame_rate
        conf[VOLUME_FIELD] = self.get_volume()
        conf[VIDEO_CODEC_FIELD] = self.get_video_codec()
        conf[AUDIO_CODEC_FIELD] = self.get_audio_codec()
        audio_channels = self.get_audio_channels_count()
        if audio_channels != constants.INVALID_AUDIO_CHANNELS_COUNT:
            conf[AUDIO_CHANNELS_COUNT_FIELD] = audio_channels

        if self.size.is_valid():
            conf[SIZE_FIELD] = str(self.size)

        vid_rate = self.get_video_bit_rate()
        if vid_rate != constants.INVALID_VIDEO_BIT_RATE:
            conf[VIDEO_BIT_RATE_FIELD] = vid_rate
        audio_rate = self.get_audio_bit_rate()
        if audio_rate != constants.INVALID_AUDIO_BIT_RATE:
            conf[AUDIO_BIT_RATE_FIELD] = self.get_audio_bit_rate()
        if self.logo.is_valid():
            conf[LOGO_FIELD] = self.logo.to_dict()
        if self.aspect_ratio.is_valid():
            conf[ASPCET_RATIO_FIELD] = str(self.aspect_ratio)
        return conf

    def get_deinterlace(self):
        return self.deinterlace

    def get_frame_rate(self):
        return self.frame_rate

    def get_volume(self):
        return self.volume

    def get_video_codec(self):
        return self.video_codec

    def get_audio_codec(self):
        return self.audio_codec

    def get_audio_channels_count(self):
        return self.audio_channels_count

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_video_bit_rate(self):
        return self.video_bit_rate

    def get_audio_bit_rate(self):
        return self.audio_bit_rate


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
