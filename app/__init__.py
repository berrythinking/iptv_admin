from flask import Flask, render_template
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel
from flask_socketio import SocketIO

app = Flask(__name__)

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

from app.home.view import HomeView
HomeView.register(app)

from app.user.view import UserView
UserView.register(app)

login_manager.login_view = "HomeView:login"


def page_not_found(e):
    return render_template('404.html'), 404


app.register_error_handler(404, page_not_found)
