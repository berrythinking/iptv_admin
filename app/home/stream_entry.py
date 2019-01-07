from app import db
from datetime import datetime
import app.constants as constants


class Stream(db.Document):
    meta = {'collection': 'streams', 'auto_create_index': False}
    name = db.StringField(default=constants.DEFAULT_STREAM_NAME, max_length=constants.MAX_STREAM_NAME_LENGHT,
                          required=True)
    type = db.IntField(default=constants.StreamType.RELAY, required=True)
    input_url = db.StringField(max_length=constants.MAX_URL_LENGHT, required=True)
    created_date = db.DateTimeField(default=datetime.now)  # for inner use
    # runtime
    status = constants.StreamStatus.NEW
