import datetime
import hashlib
from BeautifulSoup import BeautifulSoup as Soup
import urllib
import calendar
from collections import defaultdict, Counter
import json
import math

from stravalib.client import BatchedResultsIterator, Client as StravaClient
from stravalib.model import BaseEntity, Athlete
from stravalib import unithelper


from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for, session, g
from app import db, login_manager
import requests


import time

def timer(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print '%r (%r, %r) %2.2f sec' % \
              (method.__name__, args, kw, te-ts)
        return result

    return timed

def clean_keys(key):
    return key.replace(' ', '_').lower()


def lower(rider_list):
    return [rider.lower() for rider in rider_list]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    VIEW = 0x01
    VIEWALL = 0x02
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.VIEW, True),
            'AdvancedUser': (Permission.VIEW |
                             Permission.VIEWALL, False),
            'Admin': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class ApartmentUnits(db.Model):
    __tablename__ = 'apartmentunits'
    id = db.Column(db.Integer, primary_key=True)
    unit_number = db.Column(db.Integer)
    users = db.relationship('User', backref='apartment_unit', lazy='dynamic')

    def __repr__(self):
        return '<Apartment Unit %r>' % self.unit_number

    @staticmethod
    def insert_apartments():
        for i in range(1, 5):
            apartment = ApartmentUnits.query.filter_by(unit_number=i).first()
            if apartment is None:
                apartment = ApartmentUnits(unit_number=i)
            db.session.add(apartment)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    apartmentunit_id = db.Column(db.Integer, db.ForeignKey('apartmentunits.id'))
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    member_since = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    token = db.Column(db.String(64), default=None)

    confirmed = db.Column(db.Boolean, default=False)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

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

    def ping(self):
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)

    def reset_token(self, new_token):
        self.token = new_token
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


class Rider(object):
    VALID_CLUBS = [
        'CA-San Francisco Randonneurs',
        'CA-Santa Cruz Randonneurs'
    ]

    def __init__(self, headers, row_item):
        self.rider = dict(zip(headers, [row.text for row in row_item.findAll('td')]))

    def _asdict(self):
        self.rider['local_rider'] = self.local_rider
        self.rider['first'] = self.rider['first'].title()
        self.rider['last'] = self.rider['last'].title()
        self.rider['full_name'] = self.full_name
        return self.rider

    @property
    def full_name(self):
        return "{first} {last}".format(**self.rider)

    @property
    def local_rider(self):
        if (self.rider.get('club_name') in Rider.VALID_CLUBS or
                self.is_valid_name()):
            return True
        return False

    def is_valid_name(self):
        # return self.full_name.lower() in Rider.VALID_NAMES
        return self.full_name.lower() in [i[0] for i in ValidRider.query.with_entities(ValidRider.name).all()]


class Riders(list):
    @classmethod
    def get_all_riders(cls):
        self = cls()
        headers, rows = self._pull_riders()
        headers = map(clean_keys, headers)
        self.extend(map(lambda r: Rider(headers, r), rows))
        return self

    @classmethod
    def get_local_riders(cls):
        self = cls()
        local_riders = self.get_all_riders()
        return [rider for rider in local_riders if rider.local_rider]

    def _pull_riders(self):
        resp = urllib.urlopen('http://www.rusa.org/pbp-2015-entries.html')
        soup = Soup(resp.read())
        table = soup.find('table', {'class': 'entries'})
        rows = table.findAll('tr')
        headers = [row.text for row in rows.pop(0).findAll('th')]
        return headers, rows


class RiderStatus(object):
    def __init__(self, fram, resp, message):
        self.fram = fram
        self.message = message
        self.resp = resp

    def _asdict(self):
        return dict(
            message=self.message,
            resp=self.resp,
            fram=self.fram,
        )

    @classmethod
    def get_by_fram(cls, fram):
        resp = requests.get('http://suivi.paris-brest-paris.org/data/' + fram + '.txt')
        if resp.status_code == 404:
            return cls(fram, None, "Nothing found")
        if resp.status_code == 200:
            return cls(fram, resp.text, "Success")


class ValidRider(db.Model):
    __tablename__ = 'valid_riders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    VALID_NAMES = lower([
        "craig robertson",
        "paul vlasveld",
        "james allison",
        "greg kline",
        "stacy kline",
    ])

    def __repr__(self):
        return '<Rider %r>' % self.name

    @staticmethod
    def insert_riders():
        for rider in ValidRider.VALID_NAMES:
            rider = ValidRider(name=rider)
            db.session.add(rider)
        db.session.commit()
