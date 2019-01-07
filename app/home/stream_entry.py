from app import db
from datetime import datetime
import app.constants as constants
from bson.objectid import ObjectId


class Stream(db.Document):
    meta = {'collection': 'streams', 'auto_create_index': False}
    name = db.StringField(default=constants.DEFAULT_STREAM_NAME, max_length=constants.MAX_STREAM_NAME_LENGHT,
                          required=True)
    type = db.IntField(default=constants.StreamType.RELAY, required=True)
    input_url = db.StringField(max_length=constants.MAX_URL_LENGHT, required=True)
    created_date = db.DateTimeField(default=datetime.now)  # for inner use

    # runtime
    status = constants.StreamStatus.NEW


class StreamsHolder:
    def __init__(self):
        self._streams = []
        self._reload_from_db()

    def add_stream(self, stream: Stream):
        self._streams.append(stream)
        stream.save()

    def remove_stream(self, sid: str):
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                stream.delete()
                self._streams.remove(stream)
                break

    def get_streams(self):
        return self._streams

    def find_stream_by_id(self, sid: str) -> Stream:
        for stream in self._streams:
            if stream.id == ObjectId(sid):
                return stream

        return None

    # private
    def _reload_from_db(self):
        self._streams = []
        streams = Stream.objects()
        for stream in streams:
            self._streams.append(stream)
