from mongoengine import Document, StringField, DateTimeField, IntField, EmbeddedDocumentField
from datetime import datetime
from enum import IntEnum
from flask_login import UserMixin

from .settings import Settings
from app.service.service_settings import ServiceSettings


class User(UserMixin, Document):
    class Status(IntEnum):
        NO_ACTIVE = 0
        ACTIVE = 1
        BANNED = 2

    meta = {'collection': 'users', 'auto_create_index': False}
    email = StringField(max_length=30, required=True)
    password = StringField(required=True)
    created_date = DateTimeField(default=datetime.now)
    status = IntField(default=Status.NO_ACTIVE)

    settings = EmbeddedDocumentField(Settings, default=Settings)

    def add_server(self, server: ServiceSettings):
        self.settings.servers.append(server)
        self.settings.save()
