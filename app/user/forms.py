from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms import Form

from wtforms.validators import InputRequired, Length
from wtforms.fields import StringField, SubmitField, SelectField, FieldList, IntegerField, FormField

import app.constants as constants
from app.home.settings import Settings
from app.home.stream_entry import Stream, Urls, Url

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

        entry.log_level = self.log_level.data
        return entry
