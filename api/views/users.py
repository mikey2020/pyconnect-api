from flask import request, jsonify
from flask_restful import Resource

from api.helpers import response_json
from api.models import User
from main import email_notification

class UserResource(Resource):
    def post(self):
        """ signs up a user """
        try:
            username = request.json.get('username').strip(' ')
            email = request.json.get('email').strip(' ')
            password = request.json.get('password').strip(' ')
            already_user = User.query.filter_by(username=username).first()
            email_already_exists = User.query.filter_by(email=email).first()

            if already_user or email_already_exists:
                message = {
                    'message': 'user already exists'
                }
                return response_json(409, message)


            elif username is not None and password is not None:
                user = User(email=email,
                            username=username,
                            password=password)
                user.save()
                token = user.generate_auth_token()
                email_notification('Welcome', [email])
                user_data = {
                    'user': {
                        'username': username,
                        'email': email
                    },
                    'userToken': token.decode('ascii')
                }
                return response_json(201, user_data)
            
        except AttributeError:
            error_message = {
                'errors': {
                    'message': 'Invalid signup details'
                }
            }
            return response_json(400, error_message)

        except:
            error_message = {
                'errors': {
                    'message': 'Something went wrong'
                }
            }
            return response_json(500, error_message)

