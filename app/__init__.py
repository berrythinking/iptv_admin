from flask import Flask, request, send_from_directory
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_socketio import SocketIO

app = Flask(__name__, static_folder='static')

# load configs
app.config.from_pyfile('config/public_config.py', silent=False)
app.config.from_pyfile('config/config.py', silent=True)

# modules
bootstrap = Bootstrap(app)
babel = Babel(app)
db = MongoEngine(app)
mail = Mail(app)
socketio = SocketIO(app)

login_manager = LoginManager(app)

# blueprints
from app.home import home as home_blueprint

app.register_blueprint(home_blueprint)

from app.user import user as user_blueprint

app.register_blueprint(user_blueprint, url_prefix='/user')

login_manager.login_view = "home.login"


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])
