import os

from datetime import datetime
from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import event, desc
from sqlalchemy.exc import SQLAlchemyError
# from walrus import (Model, TextField, Database, DateField, IntegerField)


def to_camel_case(snake_str):
    """Format string to camel case."""
    title_str = snake_str.title().replace("_", "")
    return title_str[0].lower() + title_str[1:]


db = SQLAlchemy()


class ModelOpsMixin(db.Model):
    """Base models.

    - Contains the serialize method to convert objects to a dictionary
    - Save and Delete utilities
    - Common field atrributes in the models
    """

    __abstract__ = True

    id = db.Column(db.String, primary_key=True)

    def serialize(self):
        """Map model objects to dict representation."""
        return {to_camel_case(column.name): getattr(self, column.name)
                for column in self.__table__.columns}

    def save(self):
        """Save an instance of the model to the database."""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    def __repr__(self):
        """REPL representation of model instance."""
        string_representation = self.__str__().replace("{", "(").replace(
            "}", ")").replace(":", "=")
        return f"{type(self).__name__}{string_representation}"

    def __str__(self):
        """String representation of model."""
        return str(self.serialize())

    def delete(self):
        """Delete an instance of the model from the database."""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            return False

    @classmethod
    def fetch_all(cls):
        """Return all the data in the model."""
        return cls.query.all()

    @classmethod
    def get(cls, *args):
        """Return data by the Id."""
        return cls.query.get(*args)

    @classmethod
    def count(cls):
        """Return the count of all the data in the model."""
        return cls.query.count()

    @classmethod
    def get_first_item(cls):
        """Return the first data in the model."""
        return cls.query.first()

    @classmethod
    def order_by(cls, *args):
        """Query and order the data of the model."""
        return cls.query.order_by(*args)

    @classmethod
    def filter_all(cls, **kwargs):
        """Query and filter the data of the model."""
        return cls.query.filter(**kwargs).all()

    @classmethod
    def filter_by(cls, **kwargs):
        """Query and filter the data of the model."""
        return cls.query.filter_by(**kwargs)

    @classmethod
    def find_first(cls, **kwargs):
        """Query and filter the data of a model, returning the first result."""
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def filter_and_count(cls, **kwargs):
        """Query, filter and counts all the data of a model."""
        return cls.query.filter_by(**kwargs).count()

    @classmethod
    def filter_and_order(cls, *args, **kwargs):
        """Query, filter and orders all the data of a model."""
        return cls.query.filter_by(**kwargs).order_by(*args)

class User(ModelOpsMixin):
    """This class represents the User's table."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(255))
    password_hash = db.Column(db.String(128))

    def __init__(self, username, password, email):
        """initialize with name."""
        self.username = username
        self.password = password
        self.email = email
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=86400):
        # generate an auth token that lasts for a day.
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        # check token to ascertain validity
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            raise ValueError  # invalid token
        return User.query.get(data['id'])

    # def save(self):
    #     db.session.add(self)
    #     db.session.commit()

    # def __repr__(self):
    #     return "<User: {}>".format(self.username)
