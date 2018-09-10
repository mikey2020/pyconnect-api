import os

from flask import Flask, jsonify, current_app
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from celery import Celery
from flask_mail import Mail, Message
from config import Config


try:
    from config import app_configuration
    from api import models
    from api.views.users import UserResource
    from celery_worker import make_celery

except ModuleNotFoundError:
    from connect_api.config import app_configuration
    from connect_api.api import models
    from connect_api.api.views.users import UserResource
    from connect_api.celery_worker import make_celery

environment = os.getenv("FLASK_CONFIG")
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sender = 'Admin'

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_flask_app(environment):
    app = Flask(__name__, instance_relative_config=True, static_folder=None)
    app.config.from_object(app_configuration[environment])

    CORS(app)

    # Initialize Celery
    celery.conf.update(app.config)

    # initialize SQLAlchemy
    models.db.init_app(app)

    # initilize migration commands
    Migrate(app, models.db)

    # initilize api resources
    api = Api(app)

    # Landing page
    @app.route('/')
    def index():
        return "Welcome to the Connect Api"

    # create endpoints
    api = Api(app)

    # contribution endpoints
    api.add_resource(
        UserResource,
        '/api/v1/user/register',
        endpoint='users')
   
    # handle default 404 exceptions with a custom response
    @app.errorhandler(404)
    def resource_not_found(error):

        response = jsonify(dict(status=404, error='Not found', message='The '
                                'requested URL was not found on the server. If'
                                ' you entered the URL manually please check '
                                'your spelling and try again'))
        response.status_code = 404
        return response

    # handle default 500 exceptions with a custom response
    @app.errorhandler(500)
    def internal_server_error(error):
        response = jsonify(dict(status=500, error='Internal server error',
                                message="It is not you. It is me. The server "
                                "encountered an internal error and was unable "
                                "to complete your request.  Either the server "
                                "is overloaded or there is an error in the "
                                "application"))
        response.status_code = 500
        return response

    return app

# enables flask commands
app = create_flask_app(os.getenv("FLASK_CONFIG"))
celery = make_celery(app)
mail = Mail(app=app)

@celery.task()
def add_together(a, b):
    return a + b

@celery.task()
def email_notification(subject, recipients):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = "Welcome to connect Api"
    with app.app_context():
        mail.send(msg)
    return "\n\nEmail sent successfully\n\n"

if __name__ == "__main__":
    environment = os.getenv("FLASK_CONFIG")
    app = create_flask_app(environment)
    app.run()
