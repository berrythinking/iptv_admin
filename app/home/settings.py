from mongoengine import EmbeddedDocument, StringField, EmbeddedDocumentListField
import app.constants as constants
from app.service.service_settings import ServiceSettings


class Settings(EmbeddedDocument):
    locale = StringField(default=constants.DEFAULT_LOCALE)
    servers = EmbeddedDocumentListField(ServiceSettings, default=[])

    def find_server(self, sid: str) -> ServiceSettings:
        return self.servers.objects(id=sid).first()


def make_servers_from_data(data: list):
    servers = []
    for server in data:
        servers.append(
            ServiceSettings(server['id'], server['name'], server['host'], server['port'], server['feedback_directory'],
                            server['timeshifts_directory'], server['hls_directory'],
                            server['playlists_directory'], server['dvb_directory'],
                            server['capture_card_directory']))

    return servers
