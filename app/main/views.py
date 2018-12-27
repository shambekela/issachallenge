from . import main
from app import scheduler, db, moment
from flask import render_template, current_app, request, redirect, url_for, jsonify, session
from flask_login import current_user, login_required, logout_user
from app.models import User, Challenge, Activity, ChallengeStatus, Quote, Tag
import os
from sparkpost import SparkPost
import sys, time, uuid, datetime, json, random
from app.main.utils import challenge_done, challenge_skip


# before request handler: redirect if not logged in .    
@main.before_request
def before_request():

	if not current_user.is_authenticated and request.endpoint != 'main.landing' and '/static/' not in request.path: 
		return redirect(url_for('main.landing'))

	if current_user.is_authenticated and request.endpoint == 'main.landing':
		return redirect(url_for('main.home'))


# landing page 
@main.route('/')
def landing():
	return render_template('landing.html')


# homepage
@main.route('/home')
@login_required
def home():

	# store the current user_id
	current_loggedin = str(current_user.uuid)

	# determined which quote to serve the user: bases on day of the week
	dayofweek = datetime.datetime.today().weekday()

	#quote to be displayed
	quote = None

	
	# scheduler handler: add job with current_user id to scheduler 
	if not current_user.get_started:
		challenge_skip(current_user)

	#get current user activity ( challenge )
	activity = db.session.query(Activity).filter(Activity.user_id==current_user.uuid, Activity.current==True).first()
	
	# set quote to be served to the user
	quote = db.session.query(Quote).all()[dayofweek]


	return render_template('home.html', activity=activity, quote=quote)


# dashboard 
@main.route('/dashboard')
@login_required
def dashboard():

	# stores all dates since joining.
	dates = []

	# stores num of inactive days
	inactive = 0

	today = datetime.datetime.now().date()
	date_joined = current_user.dateJoined.date()

	# num of days since joining
	numOfDays = today - date_joined

	# add date to dates array: from join till now 
	for n in range(0, numOfDays.days+1):
		date_range = today - datetime.timedelta(days=n)
		dates.append(date_range)

	# activity stats
	act_query = db.session.query(db.func.DATE(Activity.timestamp).label("act_date") , 
								  Activity.chal_status, 
								  db.func.count(Activity.chal_status).label("num_results")).filter(Activity.user_id == current_user.uuid, Activity.chal_status == 2).group_by(db.func.DATE(Activity.timestamp), Activity.chal_status).order_by(db.desc(db.func.DATE(Activity.timestamp)))
	# get all activities 
	activities = act_query.all()

	# date of last activity completed by user.
	last_completed = act_query.first()

	# gets the days between today and last completed activity.
	if last_completed:
		inactive = (today - last_completed.act_date).days

	return render_template('dashboard.html', activities=activities, dates=dates, inactivedays=inactive)


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
	
	# POST request handler.
	if request.method == 'POST':
		user = User.query.filter_by(uuid=current_user.uuid).first()

		if user:

			# change status of receive email for a user. 
			user.receiveEmail = not user.receiveEmail

		db.session.commit()

		return 'updated'
		
	return render_template('profile.html')


'''
	Javascripts functions
'''

# home: challenge activity options handler.
@main.route('/activity_action', methods=['POST'])
@login_required
def activity_action():
	action = request.form.get('action')

	# user cliked the skip button
	if action == 'skip':
		# function to be executed 
		challenge_skip(current_user)

	# user clicked the done button
	if action == 'done':
		# function to be executed.
		challenge_done(current_user)

	activity = db.session.query(Activity.activity_id, Activity.timestamp, Challenge.name, Tag.tagname ).filter(Activity.user_id==current_user.uuid, 
		Activity.current==True,
		Challenge.cid == Activity.cid,
		Challenge.c_tag == Tag.id).first()

	print(activity)
	sys.stdout.flush()

	return jsonify(activity)


# delete an account 
@main.route('/delete_account', methods=['POST', 'GET'])
@login_required
def delete_account():
	#user = User.query.filter_by()
	currentuser = str(current_user.uuid)

	# clear user session and logout
	session.clear()
	logout_user

	user = db.session.query(User).filter(User.uuid == int(currentuser)).first()
	db.session.delete(user)
	db.session.commit()

	return redirect(url_for('main.landing'))

@main.route('/get_started', methods=['POST'])
@login_required
def get_started():

	# set getstarted status to True
	user = db.session.query(User).filter(User.uuid == current_user.uuid).first()

	user.set_getStarted(True)

	db.session.commit()

	return 'a'