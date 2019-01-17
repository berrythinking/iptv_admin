from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import Form

from wtforms.validators import InputRequired, Length, NumberRange
from wtforms.fields import StringField, SubmitField, SelectField, FieldList, IntegerField, FormField, BooleanField, \
    FloatField

import app.constants as constants
from app.home.settings import Settings
from app.home.stream_entry import Stream, Urls, Url, RelayStream, EncodeStream, Logo

LICENSE_KEY_LENGTH = 64


class SettingsForm(FlaskForm):
    locale = SelectField(lazy_gettext(u'Locale:'), coerce=str, validators=[InputRequired()],
                         choices=constants.AVAILABLE_LOCALES_PAIRS)
    submit = SubmitField(lazy_gettext(u'Apply'))

    def make_settings(self):
        settings = Settings()
        return self.update_settings(settings)

    def update_settings(self, settings: Settings):
        settings.locale = self.locale.data
        return settings


class ActivateForm(FlaskForm):
    license = StringField(lazy_gettext(u'License:'),
                          validators=[InputRequired(), Length(min=LICENSE_KEY_LENGTH, max=LICENSE_KEY_LENGTH)])
    submit = SubmitField(lazy_gettext(u'Activate'))


class UrlForm(Form):
    id = IntegerField(lazy_gettext(u'Id:'),
                      validators=[InputRequired()], render_kw={'readonly': 'true'})
    uri = StringField(lazy_gettext(u'Url:'),
                      validators=[InputRequired(),
                                  Length(min=constants.MIN_URL_LENGTH, max=constants.MAX_URL_LENGTH)])


class UrlsForm(Form):
    urls = FieldList(FormField(UrlForm, lazy_gettext(u'Urls:')), min_entries=1, max_entries=10)


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
                                validators=[InputRequired(), NumberRange(constants.DEFAULT_AUDIO_SELECT, 1000)])
    have_video = BooleanField(lazy_gettext(u'Have video:'), validators=[])
    have_audio = BooleanField(lazy_gettext(u'Have audio:'), validators=[])
    submit = SubmitField(lazy_gettext(u'Confirm'))

    def make_entry(self):
        entry = Stream()
        return self.update_entry(entry)

    def update_entry(self, entry: Stream):
        entry.name = self.name.data
        entry.type = self.type.data
        input_urls = Urls()
        for url in self.input.data['urls']:
            input_urls.urls.append(Url(url['id'], url['uri']))
        entry.input = input_urls

        output_urls = Urls()
        for url in self.output.data['urls']:
            output_urls.urls.append(Url(url['id'], url['uri']))
        entry.output = output_urls

        entry.audio_select = self.audio_select.data
        entry.have_video = self.have_video.data
        entry.have_audio = self.have_audio.data
        entry.log_level = self.log_level.data
        return entry


class RelayStreamEntryForm(StreamEntryForm):
    video_parser = SelectField(lazy_gettext(u'Video parser:'), validators=[],
                               choices=constants.AVAILABLE_VIDEO_PARSERS)
    audio_parser = SelectField(lazy_gettext(u'Audio parser:'), validators=[],
                               choices=constants.AVAILABLE_AUDIO_PARSERS)

    def make_entry(self):
        entry = RelayStream()
        return self.update_entry(entry)

    def update_entry(self, entry: RelayStream):
        entry.video_parser = self.video_parser.data
        entry.audio_parser = self.audio_parser.data
        return super(RelayStreamEntryForm, self).update_entry(entry)


class LogoForm(Form):
    path = StringField(lazy_gettext(u'Path:'), validators=[])
    posx = IntegerField(lazy_gettext(u'Posx:'), validators=[InputRequired()])
    posy = IntegerField(lazy_gettext(u'Posy:'), validators=[InputRequired()])
    alpha = FloatField(lazy_gettext(u'Alpha:'),
                       validators=[InputRequired(), NumberRange(constants.MIN_ALPHA, constants.MAX_ALPHA)])


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
    width = IntegerField(lazy_gettext(u'Width:'), validators=[InputRequired()])
    height = IntegerField(lazy_gettext(u'Height:'), validators=[InputRequired()])
    video_bit_rate = IntegerField(lazy_gettext(u'Video bit rate:'), validators=[InputRequired()])
    audio_bit_rate = IntegerField(lazy_gettext(u'Audio bit rate:'), validators=[InputRequired()])
    logo = FormField(LogoForm, lazy_gettext(u'Logo:'), validators=[])

    def make_entry(self):
        entry = EncodeStream()
        return self.update_entry(entry)

    def update_entry(self, entry: EncodeStream):
        entry.deinterlace = self.deinterlace.data
        entry.frame_rate = self.frame_rate.data
        entry.volume = self.volume.data
        entry.video_codec = self.video_codec.data
        entry.audio_codec = self.audio_codec.data
        entry.audio_channels_count = self.audio_channels_count.data
        entry.width = self.width.data
        entry.height = self.height.data
        entry.video_bit_rate = self.video_bit_rate.data
        entry.audio_bit_rate = self.audio_bit_rate.data

        # logo
        logo = Logo()
        logo_data = self.logo.data
        logo.path = logo_data['path']
        logo.posx = logo_data['posx']
        logo.posy = logo_data['posy']
        logo.alpha = logo_data['alpha']
        entry.logo = logo
        return super(EncodeStreamEntryForm, self).update_entry(entry)
