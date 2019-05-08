from flask_wtf import FlaskForm
from flask_babel import lazy_gettext
from wtforms.fields import StringField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length

from app.service.service_entry import ServiceSettings


class ServiceSettingsForm(FlaskForm):
    name = StringField(lazy_gettext(u'Name:'), validators=[InputRequired()])
    host = StringField(lazy_gettext(u'Host:'), validators=[InputRequired()])
    port = IntegerField(lazy_gettext(u'Port:'), validators=[InputRequired()])

    feedback_directory = StringField(lazy_gettext(u'Feedback directory:'), validators=[InputRequired()])
    timeshifts_directory = StringField(lazy_gettext(u'Timeshifts directory:'), validators=[InputRequired()])
    hls_directory = StringField(lazy_gettext(u'Hls directory:'), validators=[InputRequired()])
    playlists_directory = StringField(lazy_gettext(u'Playlist directory:'), validators=[InputRequired()])
    dvb_directory = StringField(lazy_gettext(u'DVB directory:'), validators=[InputRequired()])
    capture_card_directory = StringField(lazy_gettext(u'Capture card directory:'), validators=[InputRequired()])
    apply = SubmitField(lazy_gettext(u'Apply'))

    def make_entry(self):
        return self.update_entry(ServiceSettings())

    def update_entry(self, settings: ServiceSettings):
        settings.name = self.name.data
        settings.host = self.host.data
        settings.port = self.port.data

        settings.feedback_directory = self.feedback_directory.data
        settings.timeshifts_directory = self.timeshifts_directory.data
        settings.hls_directory = self.hls_directory.data
        settings.playlists_directory = self.playlists_directory.data
        settings.dvb_directory = self.dvb_directory.data
        settings.capture_card_directory = self.capture_card_directory.data
        return settings


class ActivateForm(FlaskForm):
    LICENSE_KEY_LENGTH = 64

    license = StringField(lazy_gettext(u'License:'),
                          validators=[InputRequired(), Length(min=LICENSE_KEY_LENGTH, max=LICENSE_KEY_LENGTH)])
    submit = SubmitField(lazy_gettext(u'Activate'))
