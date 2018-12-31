from datetime import datetime
from enum import IntEnum

from flask_login import UserMixin

from app import db
import app.constants as constants
from .settings import Settings


class User(UserMixin, db.Document):
    class Status(IntEnum):
        NO_ACTIVE = 0
        ACTIVE = 1
        BANNED = 2

    meta = {'collection': 'users', 'auto_create_index': False}
    email = db.StringField(max_length=30, required=True)
    password = db.StringField(required=True)
    created_date = db.DateTimeField(default=datetime.now)
    status = db.IntField(default=Status.NO_ACTIVE)

    settings = db.EmbeddedDocumentField(Settings, default=Settings)
