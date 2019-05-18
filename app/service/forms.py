from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms.fields import StringField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length
from flask_mongoengine.wtf import model_form

from app.service.service_entry import ServiceSettings

ServiceSettingsForm = model_form(ServiceSettings)


class ActivateForm(FlaskForm):
    LICENSE_KEY_LENGTH = 64

    license = StringField(lazy_gettext(u'License:'),
                          validators=[InputRequired(), Length(min=LICENSE_KEY_LENGTH, max=LICENSE_KEY_LENGTH)])
    submit = SubmitField(lazy_gettext(u'Activate'))
