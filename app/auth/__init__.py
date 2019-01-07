from flask import Blueprint

auth = Blueprint('auth', __name__, static_url_path='/auth/static', template_folder='templates', static_folder='static')

from . import views