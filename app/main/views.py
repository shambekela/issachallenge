from . import main
from app import scheduler, db, moment
from flask import render_template, current_app, request, redirect, url_for, jsonify, session
from flask_login import current_user, login_required, logout_user
from app.models import User, Challenge, Activity, ChallengeStatus, Quote
import os
from sparkpost import SparkPost
import sys, time, uuid, datetime, json

#function that runs every 24 hours
def challenge_done(currentuser):

	# generates new random challeng
	random_challenge = db.session.query(Challenge.cid).order_by(db.func.random()).limit(1).first()
	
	# generates unique id for activity.
	activityid = (uuid.uuid4().int & (1<<29)-1)
	
	#get current activity.
	for a in Activity.query.filter_by(user_id = currentuser, chal_status = 4).all():
		a.set_status(2) # set current activity to done
		a.set_point(3) # 3 points for each activity completed
		a.set_current(False) # not current anymore
	

	# add a new activity for this user.
	active = Activity(activity_id=activityid, 
					  cid=random_challenge.cid,
					  user_id=int(currentuser),
					  current=True,
					  chal_status=4)

	db.session.add(active)
	db.session.commit()

	""" re-add job """
	next_run = scheduler.get_job(currentuser).next_run_time
	scheduler.modify_job(currentuser, next_run_time= next_run + datetime.timedelta(minutes = 2))
	print("Next run: " + str(scheduler.get_job(currentuser).next_run_time))
	sys.stdout.flush()


# function that runs every 24 hours or on skip
def issa_challenge(currentuser, job):
	app = scheduler.app
	with app.app_context():

		#generates a new random challenge
		random_challenge = db.session.query(Challenge.cid).order_by(db.func.random()).limit(1).first()
		
		# generates a unique id for activity.
		activityid = (uuid.uuid4().int & (1<<29)-1)

		# email credentials
		sparkpostkey = current_app.config['SPARKPOST_KEY']
		sparkpostemail = current_app.config['SPARKPOST_EMAIL']

		#delete current activity
		db.session.query(Activity).filter(Activity.user_id == currentuser).filter(Activity.chal_status != 2).delete()
	

		# add a new activity for this user.
		active = Activity(activity_id=activityid, 
						  cid=random_challenge.cid,
						  user_id=int(currentuser),
						  current=True,
						  chal_status=4)

		db.session.add(active)
		db.session.commit()

		# send new activity email

		if job:

			'''
			email = db.session.query(User.email).filter(User.uuid== int(currentuser)).first()
			if email:
				sp = SparkPost(sparkpostkey)
				response = sp.transmissions.send(
				text = 'New challenge - Issa challenge',	
				recipients=[email.email],
				html= render_template('email/challenge_notification.html'),
				from_email='Issa challenge {}'.format("<" + sparkpostemail + ">"),
				subject='You have a new challenge {}'.format(datetime.datetime.now().strftime('%dth %b %Y')))

			print(response)
			'''
		
		if not job:
			next_run = scheduler.get_job(currentuser).next_run_time
			scheduler.modify_job(currentuser, next_run_time= next_run + datetime.timedelta(minutes = 2))
	
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

	print(current_user.uuid)

	# scheduler handler: add job with current_user id to scheduler 
	if scheduler.get_job(current_loggedin) is None:
		scheduler.add_job(id=(current_loggedin), func=issa_challenge, args=(current_loggedin, True), trigger='interval',  minutes=2, max_instances=3, misfire_grace_time=None)
		issa_challenge(current_loggedin, False)



	#get current user activity ( challenge )
	activity = db.session.query(Activity).filter(Activity.user_id==current_user.uuid, Activity.current==True).first()
	
	# set quote to be served to the user
	quote = db.session.query(Quote).all()[dayofweek]

	print("User Jobs: " + str(scheduler.get_jobs()))
	sys.stdout.flush()

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
	date_joined = current_user.dateJoined

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
	currentuser = str(current_user.uuid)

	# user cliked the skip button
	if action == 'skip':
		# function to be executed 
		issa_challenge(currentuser, False)

	# user clicked the done button
	if action == 'done':

		# function to be executed.
		challenge_done(currentuser)

	return jsonify(action)

# delete an account 
@main.route('/delete_account', methods=['POST', 'GET'])
@login_required
def delete_account():
	#user = User.query.filter_by()
	currentuser = str(current_user.uuid)

	# remove users job from scheduler
	if scheduler.get_job(currentuser):
		scheduler.remove_job(id=currentuser)

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

@main.route('/new_activity', methods=['POST'])
@login_required
def new_activity():
	# get specific activities  
	activity = db.session.query(Activity.activity_id, Activity.timestamp, Challenge.name).filter(Activity.user_id==current_user.uuid, Activity.current==True,Challenge.cid == Activity.cid).first()
	return jsonify(activity)