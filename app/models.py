from . import db, login_manager
from flask_login import UserMixin
import datetime

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	u_id = db.Column(db.Integer, index=True)
	username = db.Column(db.String(255), unique=True, nullable=False)
	email = db.Column(db.String(255), unique=True)
	date_joined = db.Column(db.Date, nullable=False, default=datetime.datetime.utcnow())
	avatar = db.Column(db.String(200))
	tokens = db.Column(db.Text)
	postlike = db.relationship('PostLike', backref='user_', cascade="all, delete", lazy=True)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))