from mongoengine import Document, ListField, EmbeddedDocumentField, ReferenceField

from app.service.server_entry import ServerSettings
from app.stream.stream_entry import Stream


class ServiceSettings(Document, ServerSettings):
    meta = {'collection': 'service', 'auto_create_index': False}

    streams = ListField(EmbeddedDocumentField(Stream), default=[])

    users = ListField(ReferenceField('User'), default=[])
