from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
import json
from . import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Serializer(object):
    __public__ = None

    def to_serializable_dict(self):
        dict = {}
        for public_key in self.__public__:
            value = getattr(self, public_key)
            dict[public_key] = value
        return dict

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(64), default=None)

    @property
    def password(self):
        raise AttributeError('password is not readable attr')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def token_dict():
        to_ret = {user.username: user.token for user in User.query.all()}
        return to_ret

    def reset_token(self, new_token):
        self.token = new_token
        db.session.add(self)
        return True

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return '<User %r>' % self.username


class Photos(db.Model, Serializer):
    __tablename__ = 'photos'
    __public__ = ['id', 'name', 'completed', 'lastupdated', 'comments', 'photodate']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    completed = db.Column(db.Boolean, default=False)
    lastupdated = db.Column(db.DateTime, default=None)
    comments = db.Column(db.String(128), default=None)
    photodate = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Photo %r>' % self.id

    @property
    def last_updated(self):
        return self.lastupdated

    @last_updated.setter
    def last_updated(self, value):
        self.lastupdated= datetime.now()

    def as_json(self):
        return self.to_serializable_dict()
