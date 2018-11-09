from flask import Blueprint

main = Blueprint('main', __name__, static_url_path='/main/static', template_folder='templates', static_folder='static')

from . import views, errors