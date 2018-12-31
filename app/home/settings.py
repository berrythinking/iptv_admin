from app import db
import app.constants as constants


class Settings(db.EmbeddedDocument):
    locale = db.StringField(default=constants.DEFAULT_LOCALE)
