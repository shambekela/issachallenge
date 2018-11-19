from flask_script import Manager, Shell
from app import create_app, scheduler , db
from flask_migrate import Migrate, MigrateCommand
from app.models import User, Challenge, Tag, Activity, ChallengeStatus
import os

app = create_app(os.environ.get('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

@manager.shell
def make_shell_context():
	return dict(app=app )#, db=db)

scheduler.start()

if __name__ == '__main__':
	manager.run()