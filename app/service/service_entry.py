from mongoengine import Document, ListField, EmbeddedDocumentField, ReferenceField

import app.constants as constants

from app.service.server_entry import ServerSettings
from app.stream.stream_entry import Stream


# #EXTM3U
# #EXTINF:-1 tvg-id="" tvg-name="" tvg-logo="https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Amptv.png/330px-Amptv.png" group-title="Armenia(Հայաստան)",1TV
# http://amtv1.livestreamingcdn.com/am2abr/tracks-v1a1/index.m3u8

class ServiceSettings(Document, ServerSettings):
    meta = {'collection': 'service', 'auto_create_index': False}

    streams = ListField(EmbeddedDocumentField(Stream), default=[])

    users = ListField(ReferenceField('User'), default=[])

    def generate_playlist(self) -> str:
        result = '#EXTM3U\n'
        for stream in self.streams:
            type = stream.get_type()
            if type == constants.StreamType.RELAY or type == constants.StreamType.ENCODE or type == constants.StreamType.TIMESHIFT_PLAYER:
                for idx, out in enumerate(stream.output.urls):
                    result += '#EXTINF:{0},{1}\n{2}\n'.format(idx, stream.name, out.uri)

        return result
