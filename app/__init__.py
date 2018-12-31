from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager, current_user
from flask_apscheduler import APScheduler
import sys, socket, os

db = SQLAlchemy(session_options={"expire_on_commit": False})
bootstrap = Bootstrap()
moment = Moment()
login_manager = LoginManager()
scheduler = APScheduler()
login_manager.session_protection = "strong"
login_manager.login_view = 'main.landing'

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)
	db.init_app(app)
	bootstrap.init_app(app)
	moment.init_app(app)
	login_manager.init_app(app)
	from app.main.utils import challenge_scheduler

	if app.config['SSL_REDIRECT']:
		from flask_sslify import SSLify
		sslify = SSLify(app)

	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.bind(("127.0.0.1", 47200))
	except socket.error:
		print('already')
		sys.stdout.flush()
	else:
		#print('Added' + str(os.getpid()))
		scheduler.init_app(app)
		scheduler.start()
		job_id = 'issa-challenge-job'
		if scheduler.get_job(id=job_id) is None:
			scheduler.add_job(id=job_id, func=challenge_scheduler, trigger='interval',  hours=1, max_instances=3, misfire_grace_time=None)
		print(scheduler.get_job(id=job_id))

	from .api import api as api_blueprint
	from .main import main as main_blueprint

	app.register_blueprint(api_blueprint)
	app.register_blueprint(main_blueprint)

	return app #app instance