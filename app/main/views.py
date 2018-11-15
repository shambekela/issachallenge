from . import main
from app import scheduler
from flask import render_template, current_app
import os
from sparkpost import SparkPost
import sys

@scheduler.scheduled_job('interval', seconds=2)
def show_users(var):
	app = scheduler.app
	with app.app_context():
		print('running user' + str(var))
		sys.stdout.flush()
	
@main.route('/')
def landing():
	sparkpostkey = current_app.config['SPARKPOST_KEY']
	sparkpostemail = current_app.config['SPARKPOST_EMAIL']

	'''
	sp = SparkPost(sparkpostkey)
	response = sp.transmissions.send(
	recipients=['toivo1996@gmail.com'],
	html='<p>Welcome to issa challenge</p>',
	from_email=sparkpostemail,
	subject='Welcome to Issa challenge')

	print(response)
	sys.stdout.flush()
	'''
	return render_template('landing.html')

@main.route('/test')
def test():
	var = os.urandom(1)
	job = scheduler.add_job(id=str(var), func=show_users, args=(var) , trigger='interval', seconds=3)
	return job.id

@main.route('/home')
def home():
	scheduler.shutdown()
	return render_template('home.html')

@main.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@main.route('/profile')
def profile():
	return render_template('profile.html')