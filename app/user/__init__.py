from flask import Blueprint
from app import app
from .iptv_cloud import IptvCloud

user = Blueprint('user', __name__)

cloud_id = app.config['CLOUD_SETTINGS']['id']
cloud_host = app.config['CLOUD_SETTINGS']['host']
cloud_port = app.config['CLOUD_SETTINGS']['port']

cloud = IptvCloud(cloud_id, cloud_host, cloud_port)
streams = []

from app.user import routes
