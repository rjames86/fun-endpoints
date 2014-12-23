from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from . import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

    def reset_token(self, new_token):
        print "setting token to", new_token
        self.token = new_token
        db.session.add(self)
        print self.token
        return True

    def __repr__(self):
        return '<User %r>' % self.username
