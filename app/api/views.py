from . import api 
from flask import render_template, redirect, url_for, request, session
from flask_login import login_user, login_required, current_user, logout_user
from requests_oauthlib import OAuth2Session
from requests.exceptions import HTTPError
from config import Auth
from app import db
from app.models import User, Tracker
import json, uuid, sys

def get_google_auth(state=None, token=None):
	if token:
		return OAuth2Session(Auth.CLIENT_ID, token=token)
	if state:
		return OAuth2Session(Auth.CLIENT_ID, state=state, redirect_uri=Auth.REDIRECT_URI, scope=Auth.SCOPE)
	oauth = OAuth2Session(Auth.CLIENT_ID, redirect_uri=Auth.REDIRECT_URI, scope=Auth.SCOPE)
	return oauth

@api.route('/google_login', methods=['POST'])
def login():

	timezone = request.form.get('timezone')
	session['timezone'] = int(timezone)

	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	
	google = get_google_auth()
	auth_url, state = google.authorization_url(Auth.AUTH_URI, access_type='offline')
	session['oauth_state'] = state
	return redirect(auth_url)

@api.route('/logout')
@login_required
def logout():
	logout_user()
	session.clear()
	return redirect(url_for('auth.login'))

@api.route('/gCallback')
def callback():
	if current_user is not None and current_user.is_authenticated:
		return redirect(url_for('main.home'))

	if 'error' in request.args:
		if request.args.get('error') == 'access_denied':
			return 'You are denied access'

		return 'Error encountered.'

	if 'code' not in request.args and 'state' not in request.args:
		return redirect(url_for('main.home'))

	else:
		google = get_google_auth(state=session['oauth_state'])

		try:
			token = google.fetch_token(Auth.TOKEN_URI, client_secret=Auth.CLIENT_SECRET, authorization_response=request.url)
		except HTTPError:
			return 'HTTPError Occurred'

		google = get_google_auth(token=token)
		resp = google.get(Auth.USER_INFO)

		if resp.status_code==200:
			user_data = resp.json()
			email = user_data['email']
			user = User.query.filter_by(email=email).first()
			if user is None:
				uud = (uuid.uuid4().int & (1<<29)-1)
				user = User()
				user.email = email
				user.uuid = uud
				tracker = Tracker(uuid=uud)
				user.tracker.append(tracker)
			else:
				# tracks number of logins
				user.numOfLogins = user.numOfLogins + 1

			if session['timezone'] is not None:
				# update the user timezone
				user.timezoneoffset = session['timezone']
				
			user.username = user_data['family_name']
			user.tokens = json.dumps(token)
			user.avatar = user_data['picture']
			user.confirmed = True 

			db.session.add(user)
			db.session.commit()
			login_user(user, remember=True)
			return redirect(url_for('main.home'))
		return 'Could not fetch data'