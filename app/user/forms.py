from flask_wtf import FlaskForm
from flask_babel import lazy_gettext

from wtforms.validators import InputRequired, Length
from wtforms.fields import StringField, SubmitField, SelectField, IntegerField

import app.constants as constants
from app.home.settings import Settings
from app.home.stream_entry import StreamEntry

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


class StreamEntryForm(FlaskForm):
    name = StringField(lazy_gettext(u'Name:'), validators=[InputRequired()], default=constants.DEFAULT_STREAM_NAME)
    type = SelectField(lazy_gettext(u'Type:'), validators=[], default=constants.StreamType.RELAY,
                       choices=constants.AVAILABLE_STREAM_TYPES_PAIRS, coerce=constants.StreamType.coerce)
    submit = SubmitField(lazy_gettext(u'Confirm'))

    def __init__(self, **kwargs):
        super(StreamEntryForm, self).__init__(**kwargs)

    def make_entry(self):
        entry = StreamEntry()
        return self.update_entry(entry)

    def update_entry(self, entry: StreamEntry):
        entry.name = self.name.data
        entry.type = self.type.data
        return entry
