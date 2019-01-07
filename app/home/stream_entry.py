from app import db
from datetime import datetime
import app.constants as constants


class StreamEntry(db.Document):
    meta = {'collection': 'streams', 'auto_create_index': False}
    name = db.StringField(default=constants.DEFAULT_STREAM_NAME, max_length=30, required=True)
    type = db.IntField(default=constants.StreamType.RELAY)
    created_date = db.DateTimeField(default=datetime.now)  # for inner use
