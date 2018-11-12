from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime

# tables stores user account data and related info.
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	uuid = db.Column(db.Integer, index=True)
	username = db.Column(db.String(255), unique=True, nullable=False)
	email = db.Column(db.String(255), unique=True)
	dateJoined = db.Column(db.Date, nullable=False, default=datetime.datetime.utcnow())
	avatar = db.Column(db.String(200))
	tokens = db.Column(db.Text)
	numOfLogins = db.Column(db.Integer, default=1)
	receiveEmail = db.Column(db.Boolean, default=True)
	users = db.relationship('Activity', backref='user', cascade="all, delete", lazy=False)

# stores all challenges.
class Challenge(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	cid = db.Column(db.BigInteger, unique=True, index=True)
	name = db.Column(db.String(255), index=True, nullable=False)
	tag = db.Column(db.Integer, db.Foreign_key('tag.id'))
	difficulty = db.Column(db.Integer, nullable=True)
	activities = db.relationship('Activity', backref='challenge', cascade="all, delete", lazy=False)

class Tag(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tagname = db.Column(db.String(100), nullable=True, unique=True)
	challenges = db.relationship('Challenge', backref='tags', lazy=True)

# store all user challenges active or not
class Activity(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	activity_id = db.Column(db.BigInteger, unique=True, index=True)
	cid = db.Column(db.BigInteger, db.Foreign_key('challenge.cid', ondelete="CASCADE"))
	user_id = db.Column(db.Integer, db.Foreign_key('user.uuid', ondelete="CASCADE"))
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	end_date = db.Column(db.DateTime, nullable=True)
	current = db.Column(db.Boolean, default=True) # stores if this is the current user challenge.
	chal_status = db.Column(db.Integer, db.Foreign_key('challenge_status.id', ondelete="CASCADE"), default=0) # status of this challenge done not today etc.


class ChallengeStatus(db.Model):
	__tablename__ = 'challenge_status'
	id = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.String(100), unique=True) # 0 - noactiontaken 1- done 3- Not today.
	activities = db.relationship('Activity', backref='c_status', cascade="all, delete", lazy=False)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))