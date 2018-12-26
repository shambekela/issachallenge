from flask_script import Manager, Shell
from app import create_app, scheduler , db
from flask_migrate import Migrate, MigrateCommand
from app.models import *
import os

app = create_app(os.environ.get('ENVIRONMENT'))
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.shell
def make_shell_context():
	return dict(app=app )#, db=db)

if scheduler.state == 1:
	scheduler.shutdown()
	scheduler.delete_all_jobs()

scheduler.start()

if __name__ == '__main__':
	manager.run()