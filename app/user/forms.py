from flask_wtf import FlaskForm
from flask_babel import lazy_gettext

from wtforms.fields import SubmitField, SelectField
from wtforms.validators import InputRequired

import app.constants as constants
from app.home.settings import Settings


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
