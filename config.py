import os
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class Auth:
	CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID') 
	CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
	REDIRECT_URI = 'https://www.issachallenge.fun/gCallback'
	AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
	TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
	USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
	SCOPE = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
	
class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'afafd6a5f65a6f5a65df6a5f6af65daf84df23sfa6d5fa'
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root@localhost/issa-challenge'
	SPARKPOST_KEY = os.environ.get('SPARKPOST_KEY')
	SPARKPOST_NOTIFICATION_EMAIL = os.environ.get('SPARKPOST_NOTIFICATION_EMAIL')
	SPARKPOST_CONTACT_EMAIL = os.environ.get('SPARKPOST_CONTACT_EMAIL')
	 
	SCHEDULER_JOBSTORES = {
		'default': SQLAlchemyJobStore(url=os.environ.get('DATABASE_URL') or 'postgres://euhumsfiyvvakh:1267b859f6a8499f87f7bb2bd5e5cd22b4d9f090a1dc70dcce39b5a7f9c9419b@ec2-54-228-229-10.eu-west-1.compute.amazonaws.com:5432/d1mngqi2ppvuv9')
	}

	SCHEDULER_EXECUTORS = {
		'default': {'type': 'threadpool', 'max_workers': 20}
	}
	
	SCHEDULER_API_ENABLED = True

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SSL_REDIRECT = False

class TestingConfig(Config):
	pass

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

	@classmethod
	def init_app(cls, app):
		Config.init_app(app)
	
class HerokuConfig(ProductionConfig):
	SSL_REDIRECT = True if os.environ.get('DYNO') else False

	@classmethod
	def init_app(cls, app):
		ProductionConfig.init_app(app)

		# handle reverse proxy server headers
		from werkzeug.contrib.fixers import ProxyFix
		app.wsgi_app = ProxyFix(app.wsgi_app)

		# log to stderr
		import logging
		from logging import StreamHandler
		file_handler = StreamHandler()
		file_handler.setLevel(logging.INFO)
		app.logger.addHandler(file_handler)


config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig,
	'testing': TestingConfig,
	'heroku': HerokuConfig,

	'default': DevelopmentConfig
}