from sparkpost import SparkPost
from flask import current_app, render_template

''' send email to user '''
def send_email(**kwags):

	user = kwags.get('user')

	# email credentials
	sparkpostkey = current_app.config['SPARKPOST_KEY']
	sparkpostemail = current_app.config['SPARKPOST_CONTACT_EMAIL']


	sp = SparkPost(sparkpostkey)
	response = sp.transmissions.send(
	text = 'Confirm your account - Issa challenge',	
	recipients=[user.email],
	html= render_template('email/confirm_email.html', **kwags),
	from_email='Issa challenge {}'.format("<" + sparkpostemail + ">"),
	subject='Please confirm your email address')


def send_reset_email(**kwags):

	user = kwags.get('user')

	# email credentials
	sparkpostkey = current_app.config['SPARKPOST_KEY'] 
	sparkpostemail = current_app.config['SPARKPOST_CONTACT_EMAIL']


	sp = SparkPost(sparkpostkey)
	response = sp.transmissions.send(
	text = 'Reset your password - Issa challenge',	
	recipients=[user.email],
	html= render_template('email/reset_email.html', **kwags),
	from_email='Issa challenge {}'.format("<" + sparkpostemail + ">"),
	subject='Password Reset')

	print(response)