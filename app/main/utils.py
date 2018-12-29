from app import scheduler, db
from app.models import User, Challenge, Activity, ChallengeStatus, Quote, Tag, Tracker
from sparkpost import SparkPost
from flask import current_app
import sys, time, uuid, datetime, json, random, os

'''
	function runs when challenge is done
'''
def challenge_done(current_user):
	random_challenge = None
	currentuser = current_user.uuid
	# generates new random challeng
	while True:
		query = db.session.query(Challenge.cid)
		challenges = query.all()

		# random challenge
		random_challenge = random.choice(challenges)

		activity = db.session.query(Activity.cid).filter(
			Activity.user_id == int(currentuser), 
			Activity.cid == random_challenge.cid).first()
		
		if activity is None:
			break

	
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

	# update user last activity
	update_last_activity()

	print('Done execute')
	sys.stdout.flush()

''' runs when users skips a challenge'''
def challenge_skip(current_user):

	random_challenge = None
	currentuser = current_user.uuid

	# generates new random challeng
	while True:
		query = db.session.query(Challenge.cid)
		challenges = query.all()

		# random challenge
		random_challenge = random.choice(challenges)

		activity = db.session.query(Activity.cid).filter(
			Activity.user_id == int(currentuser), 
			Activity.cid == random_challenge.cid).first()
		
		if activity is None:
			break

	# generates a unique id for activity.
	activityid = (uuid.uuid4().int & (1<<29)-1)


	#delete current activity
	db.session.query(Activity).filter(Activity.chal_status != 2, Activity.user_id == currentuser).delete()

	# add a new activity for this user.
	active = Activity(activity_id=activityid, 
					  cid=random_challenge.cid,
					  user_id=int(currentuser),
					  current=True,
					  chal_status=4)

	db.session.add(active)
	db.session.commit()

	# update the user last activity.
	update_last_activity()

	print('Skip executed')
	sys.stdout.flush()		

''' function runs with apscheduler '''
def challenge_scheduler():
	app = scheduler.app
	print('Name: ' + str(app) + ' Running: ' + str(scheduler.state))
	with app.app_context():

		for user in db.session.query(User.uuid, User.username,Tracker.last_activity).filter(User.uuid == Tracker.uuid ).all():
			random_challenge = None
			print(user)
			currentuser = user.uuid

			# generates new random challenge
			while True:
				query = db.session.query(Challenge.cid)
				challenges = query.all()

				# random challenge
				random_challenge = random.choice(challenges)

				activity = db.session.query(Activity.cid).filter(
					Activity.user_id == currentuser, 
					Activity.cid == random_challenge.cid).first()
				
				if activity is None:
					break

			# generates a unique id for activity.
			activityid = (uuid.uuid4().int & (1<<29)-1)

			# email credentials
			sparkpostkey = current_app.config['SPARKPOST_KEY']
			sparkpostemail = current_app.config['SPARKPOST_EMAIL']

			#delete current activity
			db.session.query(Activity).filter(
				Activity.chal_status != 2, 
				Activity.user_id == currentuser).delete()
		

			# add a new activity for this user.
			active = Activity(activity_id=activityid, 
							  cid=random_challenge.cid,
							  user_id=int(currentuser),
							  current=True,
							  chal_status=4)

			db.session.add(active)
			db.session.commit()

			# send new activity email
			'''
			user = db.session.query(User).filter(User.uuid== int(currentuser)).first()
			email = user.email
			if email and user.receiveEmail:
				sp = SparkPost(sparkpostkey)
				response = sp.transmissions.send(
				text = 'New challenge - Issa challenge',	
				recipients=[email],
				html= render_template('email/challenge_notification.html'),
				from_email='Issa challenge {}'.format("<" + sparkpostemail + ">"),
				subject='You have a new challenge {}'.format(datetime.datetime.now().strftime('%dth %b %Y')))

				print("response: " + str(response))
				sys.stdout.flush()
			'''
	# update last activity
	update_last_activity()

	print('Scheduler Executed')
	sys.stdout.flush()

# update users last_activity timestamp
def update_last_activity():
	current_user = current_user.uuid
	tracker = db.session.query(Tracker).first()
	new_date = datetime.datetime.utcnow()

	# update the users last activity.
	if tracker is not None:
		tracker.update_last_activity(new_date)

	db.session.commit()
