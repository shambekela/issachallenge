from flask import render_template, request
from app.error import error
from app import db

@error.app_errorhandler(404)
def not_found_error(error):
	return render_template('404.html', error=error), 404

@error.app_errorhandler(500)
def internal_error(error):
	return render_template('500.html', error=error), 500