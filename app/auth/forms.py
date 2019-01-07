from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from app.models import User 

class LoginForm(FlaskForm):
	timezone = HiddenField('timezone')
	email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Log in')
	
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('Email does not exist.')

		if 'gmail' in email.data:
			raise ValidationError('For Google accounts. Please use log in with google.')

	def validate_password(self, password):
		user = User.query.filter_by(email=self.email.data).first()
		if user and 'gmail' not in user.email and not user.check_password(password.data):
			raise ValidationError('Password is incorrect.')

class RegisterForm(FlaskForm):
	timezone = HiddenField('timezone')
	email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
	username = StringField('Username', validators=[Length(1, 200)])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
	submit = SubmitField('Sign up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Username already exists.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Email already exists.')

		if 'gmail' in email.data:
			raise ValidationError('For Google accounts. Please use sign up with google.')

class PasswordResetRequestForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
	submit = SubmitField('Send me a reset link')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('Email does not exists. Go to sign up page to register this email.')
		
		if 'gmail' in email.data:
			raise ValidationError('For Google accounts. Please use sign up with google.')
		

class PasswordResetForm(FlaskForm):
	password = PasswordField('New Password', validators=[DataRequired(), Length(min=6),  EqualTo('password2', message='Passwords must match')])
	password2 = PasswordField('Confirm password', validators=[DataRequired(), Length(min=6)])
	submit = SubmitField('Reset Password')