from mongoengine import Document, StringField, DateTimeField, IntField, EmbeddedDocumentField, ListField, \
    ReferenceField, PULL
from datetime import datetime
from enum import IntEnum
from flask import session
from flask_login import UserMixin, login_user, logout_user

from app.home.settings import Settings
from app.service.service_entry import ServiceSettings
from app import servers_manager

SERVER_POSITION_SESSION_FIELD = 'server_position'


def login_user_wrap(user):
    login_user(user)
    user.set_current_server_position(0)


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
    servers = ListField(ReferenceField(ServiceSettings, reverse_delete_rule=PULL), default=[])

    def logout(self):
        session.pop(SERVER_POSITION_SESSION_FIELD)
        logout_user()

    def add_server(self, server: ServiceSettings):
        self.servers.append(server)
        self.save()

    def set_current_server_position(self, pos: int):
        session[SERVER_POSITION_SESSION_FIELD] = pos

    def get_current_server(self):
        if not self.servers:
            return None

        server_settings = self.servers[session[SERVER_POSITION_SESSION_FIELD]]
        if server_settings:
            return servers_manager.find_or_create_server(server_settings)

        return None


User.register_delete_rule(ServiceSettings, "users", PULL)
