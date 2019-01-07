from app import db, login_manager, scheduler
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


# tables stores user account data and related info.
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, unique=True, primary_key=True)
	uuid = db.Column(db.Integer, unique=True ,index=True)
	username = db.Column(db.String(255), unique=True, nullable=False)
	email = db.Column(db.String(255), unique=True)
	dateJoined = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	avatar = db.Column(db.String(200))
	tokens = db.Column(db.Text)
	numOfLogins = db.Column(db.Integer, default=1)
	receiveEmail = db.Column(db.Boolean, default=True)
	users = db.relationship('Activity', backref='user', cascade="all, delete", lazy=False)
	tracker = db.relationship('Tracker', backref='user_tracker', cascade="all, delete", lazy=False)
	get_started = db.Column(db.Boolean, default=False)
	timezoneoffset = db.Column(db.Numeric(12,2), default=0)
	password_hash = db.Column(db.String(255), nullable=True)
	confirmed = db.Column(db.Boolean, default=False)    

	# set getstarted modal seen
	def set_getStarted(self, seen):
		self.get_started = seen

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.uuid}).decode('utf-8')

	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except Exception as e:
			return False

		if data.get('confirm') != self.uuid:
			return False

		self.confirmed = True
		db.session.add(self)
		return True

	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.uuid}).decode('utf-8')

	@staticmethod
	def reset_password(token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False
		user = db.session.query(User).filter(User.uuid==data.get('reset')).first()
		print(user)
		if user is None:
			return False
		user.set_password(new_password)
		db.session.add(user)
		db.session.commit()
		return True

	# get completed activities per user
	def challenge_completed(self):
		stats_total = 0
		activities = db.session.query(Activity.chal_status, db.func.count(Activity.chal_status).label("num_results")).filter(Activity.user_id == self.uuid, Activity.chal_status == 2).group_by(Activity.chal_status).first()

		if activities:
			stats_total = activities.num_results

		return stats_total

	# get number of points for this user.
	def number_of_points(self):
		point_total = 0
		activities = Activity.query.filter(Activity.user_id == self.uuid, Activity.chal_status == 2).all()

		if activities:
			for activity in activities:
				point_total = point_total + activity.point

		return point_total

	# get this users done activities
	def user_done_challenge(self):
		activities = db.session.query(Activity).filter(Activity.user_id == self.uuid, Activity.chal_status == 2).order_by(db.desc(Activity.timestamp)).all()

		return activities

	def user_done_challenges_today(self):
		offset = int(self.timezoneoffset) * -1
		today_date = (datetime.utcnow() + timedelta(minutes=offset)).date()

		activities = db.session.query(Activity).filter(
			Activity.user_id == self.uuid, 
			Activity.chal_status == 2, 
			db.func.DATE(Activity.timestamp + timedelta(minutes=offset)) == today_date).order_by(db.desc(Activity.timestamp)).all()
		print(activities)
		return activities

# stores all challenges.
class Challenge(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cid = db.Column(db.BigInteger, unique=True, index=True)
	name = db.Column(db.String(255), index=True, nullable=False)
	c_tag = db.Column(db.Integer, db.ForeignKey('tag.id'))
	activities = db.relationship('Activity', backref='challenge', cascade="all, delete", lazy=False)

class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tagname = db.Column(db.String(200), nullable=False, unique=True)
	challenges = db.relationship('Challenge', backref='tags', lazy=True)

# store all user challenges active or not
class Activity(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	activity_id = db.Column(db.BigInteger, unique=True, index=True)
	cid = db.Column(db.BigInteger, db.ForeignKey('challenge.cid', ondelete="CASCADE"))
	user_id = db.Column(db.Integer, db.ForeignKey('user.uuid', ondelete="CASCADE"))
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)
	end_date = db.Column(db.DateTime, nullable=True)
	current = db.Column(db.Boolean, default=True) # stores if this is the current user challenge.
	chal_status = db.Column(db.Integer, db.ForeignKey('challenge_status.id', ondelete="CASCADE"), default=0) # status of this challenge done not today etc.
	point = db.Column(db.Integer, default=0)

	def set_status(self, status):
		self.chal_status = status

	def set_point(self, point):
		self.point = point

	def set_current(self, current):
		self.current = current

	def get_challenge_name(self):
		return self.challenge.name

class ChallengeStatus(db.Model):
	__tablename__ = 'challenge_status'
	id = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.String(100), unique=True) # 0 - noactiontaken 1- done 3- Not today.
	activities = db.relationship('Activity', backref='c_status', cascade="all, delete", lazy=False)

class Quote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(250), unique=True)
	author = db.Column(db.String(250), nullable=False)

class Tracker(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	uuid = db.Column(db.BigInteger,db.ForeignKey('user.uuid', ondelete="CASCADE"), unique=True, index=True)
	last_activity = db.Column(db.DateTime, default=datetime.utcnow)

	def update_last_activity(self, new_date):
		self.last_activity = new_date

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))