from flask_wtf import FlaskForm
from flask_babel import lazy_gettext

from wtforms.validators import InputRequired, Length
from wtforms.fields import StringField, SubmitField


class ActivateForm(FlaskForm):
    LICENSE_KEY_LENGTH = 64

    license = StringField(lazy_gettext(u'License:'),
                          validators=[InputRequired(), Length(min=LICENSE_KEY_LENGTH, max=LICENSE_KEY_LENGTH)])
    submit = SubmitField(lazy_gettext(u'Activate'))
