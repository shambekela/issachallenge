from . import main
from app import scheduler
from flask import render_template
import os
from sparkpost import SparkPost

def show_users(var):
	app = scheduler.app
	with app.app_context():
		print('running user' + str(var))
	
@main.route('/')
def landing():
	sp = SparkPost('fa2334fcfd642dd97c4af50e322182d906913fbf')
	response = sp.transmissions.send(
	recipients=['toivo1996@gmail.com'],
	html='<p>Welcome to issa challenge</p>',
	from_email='daily@issachallenge.fun',
	subject='Welcome to Issa challenge')

	print(response)
	
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