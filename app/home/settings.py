from mongoengine import EmbeddedDocument, StringField, ListField, ReferenceField
import app.constants as constants
from app.service.service_settings import ServiceSettings


class Settings(EmbeddedDocument):
    locale = StringField(default=constants.DEFAULT_LOCALE)
    servers = ListField(ReferenceField(ServiceSettings), default=[])
