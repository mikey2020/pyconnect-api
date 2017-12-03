import os
from main import create_flask_app
from api.models import User, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

environment = os.getenv("FLASK_CONFIG")
app = create_flask_app(environment)

manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests') 
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__': 
    manager.run()
