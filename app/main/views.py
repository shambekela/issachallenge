from . import main
from flask import render_template

@main.route('/')
def landing():
	return render_template('landing.html')

@main.route('/home')
def home():
	return render_template('home.html')

@main.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@main.route('/profile')
def profile():
	return render_template('profile.html')