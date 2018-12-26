from flask_script import Manager, Shell
from app import create_app, scheduler , db
from flask_migrate import Migrate, MigrateCommand
from app.models import *
import os, socket, sys

app = create_app(os.environ.get('ENVIRONMENT') or 'development')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.shell
def make_shell_context():
	return dict(app=app )#, db=db)

try:
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((socket.gethostname(), 12345))
except socket.error as e:
	print(e)
	sys.stdout.flush()
else:
	if scheduler.state != 1:
		scheduler.start()
		scheduler.delete_all_jobs()
	
	print(str(scheduler.state))
		

if __name__ == '__main__':
	manager.run()