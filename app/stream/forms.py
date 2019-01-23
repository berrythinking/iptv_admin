from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import Form

from wtforms.validators import InputRequired, Length, NumberRange
from wtforms.fields import StringField, SubmitField, SelectField, FieldList, IntegerField, FormField, BooleanField, \
    FloatField

import app.constants as constants
from .stream_entry import Stream, Urls, Url, RelayStream, EncodeStream, TimeshiftRecorderStream, Logo, Size, Rational


class UrlForm(Form):
    id = IntegerField(lazy_gettext(u'Id:'),
                      validators=[InputRequired()], render_kw={'readonly': 'true'})
    uri = StringField(lazy_gettext(u'Url:'),
                      validators=[InputRequired(),
                                  Length(min=constants.MIN_URL_LENGTH, max=constants.MAX_URL_LENGTH)])


class UrlsForm(Form):
    urls = FieldList(FormField(UrlForm, lazy_gettext(u'Urls:')), min_entries=1, max_entries=10)

    def get_data(self) -> Urls:
        urls = Urls()
        for url in self.data['urls']:
            urls.urls.append(Url(url['id'], url['uri']))

        return urls


class StreamEntryForm(FlaskForm):
    name = StringField(lazy_gettext(u'Name:'),
                       validators=[InputRequired(),
                                   Length(min=constants.MIN_STREAM_NAME_LENGTH, max=constants.MAX_STREAM_NAME_LENGTH)])
    type = SelectField(lazy_gettext(u'Type:'), validators=[],
                       choices=constants.AVAILABLE_STREAM_TYPES_PAIRS, coerce=constants.StreamType.coerce,
                       render_kw={'disabled': 'disabled'})
    input = FormField(UrlsForm, lazy_gettext(u'Input:'))
    output = FormField(UrlsForm, lazy_gettext(u'Output:'))
    log_level = SelectField(lazy_gettext(u'Log level:'), validators=[],
                            choices=constants.AVAILABLE_LOG_LEVELS_PAIRS, coerce=constants.StreamLogLevel.coerce)
    audio_select = IntegerField(lazy_gettext(u'Audio select:'),
                                validators=[InputRequired(), NumberRange(constants.INVALID_AUDIO_SELECT, 1000)])
    have_video = BooleanField(lazy_gettext(u'Have video:'), validators=[])
    have_audio = BooleanField(lazy_gettext(u'Have audio:'), validators=[])
    loop = BooleanField(lazy_gettext(u'Loop:'), validators=[])
    restart_attempts = IntegerField(lazy_gettext(u'Max restart attempts and frozen:'),
                                    validators=[NumberRange(1, 1000)])
    auto_exit_time = IntegerField(lazy_gettext(u'Auto exit time:'), validators=[])
    submit = SubmitField(lazy_gettext(u'Confirm'))

    def make_entry(self):
        return self.update_entry(Stream())

    def update_entry(self, entry: Stream):
        entry.name = self.name.data
        entry.type = self.type.data
        entry.input = self.input.get_data()
        entry.output = self.output.get_data()

        entry.audio_select = self.audio_select.data
        entry.have_video = self.have_video.data
        entry.have_audio = self.have_audio.data
        entry.log_level = self.log_level.data
        entry.loop = self.loop.data
        entry.restart_attempts = self.restart_attempts.data
        entry.auto_exit_time = self.auto_exit_time.data
        return entry


class RelayStreamEntryForm(StreamEntryForm):
    video_parser = SelectField(lazy_gettext(u'Video parser:'), validators=[],
                               choices=constants.AVAILABLE_VIDEO_PARSERS)
    audio_parser = SelectField(lazy_gettext(u'Audio parser:'), validators=[],
                               choices=constants.AVAILABLE_AUDIO_PARSERS)

    def make_entry(self):
        return self.update_entry(RelayStream())

    def update_entry(self, entry: RelayStream):
        entry.video_parser = self.video_parser.data
        entry.audio_parser = self.audio_parser.data
        return super(RelayStreamEntryForm, self).update_entry(entry)


class LogoForm(Form):
    path = StringField(lazy_gettext(u'Path:'), validators=[])
    x = IntegerField(lazy_gettext(u'Pos x:'), validators=[InputRequired()])
    y = IntegerField(lazy_gettext(u'Pos y:'), validators=[InputRequired()])
    alpha = FloatField(lazy_gettext(u'Alpha:'),
                       validators=[InputRequired(), NumberRange(constants.MIN_ALPHA, constants.MAX_ALPHA)])

    def get_data(self) -> Logo:
        logo = Logo()
        logo_data = self.data
        logo.path = logo_data['path']
        logo.x = logo_data['x']
        logo.y = logo_data['y']
        logo.alpha = logo_data['alpha']
        return logo


class SizeForm(Form):
    width = IntegerField(lazy_gettext(u'Width:'), validators=[InputRequired()])
    height = IntegerField(lazy_gettext(u'Height:'), validators=[InputRequired()])

    def get_data(self) -> Size:
        size = Size()
        size_data = self.data
        size.width = size_data['width']
        size.height = size_data['height']
        return size


class RationalForm(Form):
    num = IntegerField(lazy_gettext(u'Numerator:'), validators=[InputRequired()])
    den = IntegerField(lazy_gettext(u'Denominator:'), validators=[InputRequired()])

    def get_data(self) -> Rational:
        ratio = Rational()
        ratio_data = self.data
        ratio.num = ratio_data['num']
        ratio.den = ratio_data['den']
        return ratio


class EncodeStreamEntryForm(StreamEntryForm):
    deinterlace = BooleanField(lazy_gettext(u'Deinterlace:'), validators=[])
    frame_rate = IntegerField(lazy_gettext(u'Frame rate:'),
                              validators=[InputRequired(),
                                          NumberRange(constants.INVALID_FRAME_RATE, constants.MAX_FRAME_RATE)])
    volume = FloatField(lazy_gettext(u'Volume:'),
                        validators=[InputRequired(), NumberRange(constants.MIN_VOLUME, constants.MAX_VOLUME)])
    video_codec = SelectField(lazy_gettext(u'Video codec:'), validators=[],
                              choices=constants.AVAILABLE_VIDEO_CODECS)
    audio_codec = SelectField(lazy_gettext(u'Audio codec:'), validators=[],
                              choices=constants.AVAILABLE_AUDIO_CODECS)
    audio_channels_count = IntegerField(lazy_gettext(u'Audio channels count:'),
                                        validators=[InputRequired(), NumberRange(constants.INVALID_AUDIO_CHANNELS_COUNT,
                                                                                 constants.MAX_AUDIO_CHANNELS_COUNT)])
    size = FormField(SizeForm, lazy_gettext(u'Size:'), validators=[])
    video_bit_rate = IntegerField(lazy_gettext(u'Video bit rate:'), validators=[InputRequired()])
    audio_bit_rate = IntegerField(lazy_gettext(u'Audio bit rate:'), validators=[InputRequired()])
    logo = FormField(LogoForm, lazy_gettext(u'Logo:'), validators=[])
    aspect_ratio = FormField(RationalForm, lazy_gettext(u'Aspect ratio:'), validators=[])

    def make_entry(self):
        return self.update_entry(EncodeStream())

    def update_entry(self, entry: EncodeStream):
        entry.deinterlace = self.deinterlace.data
        entry.frame_rate = self.frame_rate.data
        entry.volume = self.volume.data
        entry.video_codec = self.video_codec.data
        entry.audio_codec = self.audio_codec.data
        entry.audio_channels_count = self.audio_channels_count.data
        entry.size = self.size.get_data()
        entry.video_bit_rate = self.video_bit_rate.data
        entry.audio_bit_rate = self.audio_bit_rate.data
        entry.logo = self.logo.get_data()
        entry.aspect_ratio = self.aspect_ratio.get_data()
        return super(EncodeStreamEntryForm, self).update_entry(entry)


class TimeshiftRecorderStreamEntryForm(RelayStreamEntryForm):
    timeshift_chunk_duration = IntegerField(lazy_gettext(u'Chunk duration:'),
                                            validators=[InputRequired(),
                                                        NumberRange(constants.MIN_TIMESHIFT_CHUNK_DURATION,
                                                                    constants.MAX_TIMESHIFT_CHUNK_DURATION)])
    timeshift_chunk_life_time_hours = IntegerField(lazy_gettext(u'Chunk life time hours:'),
                                                   validators=[InputRequired(),
                                                               NumberRange(
                                                                   constants.MIN_TIMESHIFT_CHUNK_LIFE_TIME_HOURS,
                                                                   constants.MAX_TIMESHIFT_CHUNK_LIFE_TIME_HOURS)])

    def make_entry(self):
        return self.update_entry(TimeshiftRecorderStream())

    def update_entry(self, entry: TimeshiftRecorderStream):
        entry.timeshift_chunk_duration = self.timeshift_chunk_duration.data
        entry.timeshift_chunk_life_time_hours = self.timeshift_chunk_life_time_hours.data
        return super(TimeshiftRecorderStreamEntryForm, self).update_entry(entry)
