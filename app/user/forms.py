from flask_wtf import FlaskForm
from flask_babel import lazy_gettext

from wtforms.validators import InputRequired, Length
from wtforms.fields import StringField, SubmitField, SelectField

import app.constants as constants
from app.home.settings import Settings


class SettingsForm(FlaskForm):
    locale = SelectField(lazy_gettext(u'Locale:'), coerce=str, validators=[InputRequired()],
                         choices=constants.AVAILABLE_LOCALES_PAIRS)
    submit = SubmitField(lazy_gettext(u'Apply'))

    def make_settings(self):
        return self.update_settings(Settings())

    def update_settings(self, settings: Settings):
        settings.locale = self.locale.data
        return settings


class ActivateForm(FlaskForm):
    LICENSE_KEY_LENGTH = 64

    license = StringField(lazy_gettext(u'License:'),
                          validators=[InputRequired(), Length(min=LICENSE_KEY_LENGTH, max=LICENSE_KEY_LENGTH)])
    submit = SubmitField(lazy_gettext(u'Activate'))
