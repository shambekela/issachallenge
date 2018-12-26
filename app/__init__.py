from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_apscheduler import APScheduler
from flask_sslify import SSLify

db = SQLAlchemy(session_options={"expire_on_commit": False})
bootstrap = Bootstrap()
moment = Moment()
login_manager = LoginManager()
scheduler = APScheduler()
login_manager.session_protection = "strong"
sslify = SSLify()

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)
	db.init_app(app)
	bootstrap.init_app(app)
	moment.init_app(app)
	login_manager.init_app(app)
	scheduler.init_app(app)
	if app.config['SSL_REDIRECT']:
		sslify.init_app(app)
	from .api import api as api_blueprint
	from .main import main as main_blueprint

	app.register_blueprint(api_blueprint)
	app.register_blueprint(main_blueprint)

	return app #app instance