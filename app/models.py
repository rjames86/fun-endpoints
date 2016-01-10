import datetime
import hashlib
from BeautifulSoup import BeautifulSoup as Soup
import urllib
import calendar
from collections import defaultdict, Counter

from stravalib.client import BatchedResultsIterator, Client as StravaClient
from stravalib.model import BaseEntity, Athlete
from stravalib import unithelper


from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for, session, g
from . import db, login_manager
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


class MyAthlete(Athlete):
    def __init__(self, **kwargs):
        self.attrsdict = {}
        super(Athlete, self).__init__(**kwargs)

    def _asdict(self):
        return self.attrsdict

    def from_dict(self, d):
        """
        Populates this object from specified dict.
        Only defined attributes will be set; warnings will be logged for invalid attributes.
        """
        for (k, v) in d.items():
            # Only set defined attributes.
            if hasattr(self.__class__, k):
                self.log.debug("Setting attribute `{0}` [{1}] on entity {2} with value {3!r}".format(k, getattr(self.__class__, k).__class__.__name__, self, v))
                try:
                    setattr(self, k, v)
                    self.attrsdict[k] = v
                except AttributeError as x:
                    raise AttributeError("Could not find attribute `{0}` on entity {1}, value: {2!r}.  (Original: {3!r})".format(k, self, v, x))
            else:
                self.log.warning("No such attribute {0} on entity {1}".format(k, self))


class RideCounter(object):
    def __init__(self, activities):
        self.rides = activities.rides
        self.activities = activities
        self._counter_dict = None
        # CalendarInfo().month_names.index(month_abbrev)

    @property
    def rides_count_by_month(self):
        if not self._counter_dict:
            year = defaultdict(dict)
            for ride in self.rides:
                ride_year = year[ride.start_date_local.year] or defaultdict(int)
                ride_year[ride.start_date_local.month] += 1
                year[ride.start_date_local.year] = ride_year
            self._counter_dict = year
        return self._counter_dict

    def by_year(self, year):
        return sum(self.rides_count_by_month[year].viewvalues())

    def by_month(self, month):
        to_ret = 0
        for year, values in self.rides_count_by_month.iteritems():
            for month_value, count in values.iteritems():
                if month_value == month:
                    to_ret += count

        return to_ret

    def by_month_year(self, month, year):
        return self.rides_count_by_month[year][month]


class DistanceCounter(object):
    UNIT = 'miles'

    def __init__(self, activities):
        self.rides = activities.rides
        self.activities = activities
        self.unit_name = getattr(unithelper, self.UNIT).name

    def get_distance(self, distance):
        return getattr(unithelper, self.UNIT)(distance).num

    def formatted_distance(self, distance):
        return "%0.2f" % distance

    def by_year(self, year):
        return self._calculate_distance(lambda ride: ride.start_date_local.year == year)

    def by_month(self, month):
        return self._calculate_distance(lambda ride: ride.start_date_local.month == month)

    def by_month_year(self, month, year):
        return self._calculate_distance(
            lambda ride: (ride.start_date_local.year, ride.start_date_local.month) == (year, month))

    def by_day_month_year(self, day, month, year):
        # TODO probably should memoize this at some point so its faster.
        return self._calculate_distance(
            lambda ride: (ride.start_date_local.year, ride.start_date_local.month, ride.start_date_local.day) == (year, month, day))

    def by_calendar_week(self, cal_week):
        return self._calculate_distance(
            lambda ride: (ride.start_date_local.date() > cal_week[0]) and (ride.start_date_local.date() <= cal_week[-1]))

    def best_month(self, month):
        all_years = set([ride.start_date_local.year for ride in self.rides])
        return max(
            [(year, month, self.by_month_year(month, year), self.activities.ride_counts.by_month_year(month, year)) for year in all_years],
            key=lambda y: y[2]
            )

    def _calculate_distance(self, comparator):
        to_ret = 0
        for ride in self.rides:
            if comparator(ride):
                to_ret += self.get_distance(ride.distance)
        return to_ret

class Activities(object):
    def __init__(self, activities):
        self.activities = activities
        self._rides = None

    @property
    def rides(self):
        if not self._rides:
            self._rides = [a for a in self.activities if a.type == 'Ride']
        return self._rides

    @property
    def ride_counts(self):
        return RideCounter(self)

    @property
    def ride_distances(self):
        return DistanceCounter(self)


class Strava(object):
    def __init__(self):
        self.client_id = current_app.config['STRAVA_CLIENT_ID']
        self.client_secret = current_app.config['STRAVA_CLIENT_SECRET']
        self.redirect_uri = url_for('strava.confirm_auth', _external=True)

        self.client = StravaClient()

    @property
    def athlete(self):
        return self.client.get_athlete()

    @property
    def activities(self):
        return Activities(self.client.get_activities())

    @classmethod
    def authorization_url(cls):
        self = cls()
        return self.client.authorization_url(client_id=self.client_id,
                                             redirect_uri=self.redirect_uri)

    def get_access_token(self, code):
        return self.client.exchange_code_for_token(client_id=self.client_id,
                                                   client_secret=self.client_secret,
                                                   code=code)

    @classmethod
    def athlete_by_code(cls, code):
        self = cls()
        self.client.access_token = self.get_access_token(code)
        return self.athlete

    @classmethod
    def athlete_by_token(cls, token):
        self = cls()
        self.client.access_token = token
        return self.athlete

    @classmethod
    def activities_by_token(cls, token):
        self = cls()
        self.client.access_token = token
        return self.activities


class CalendarInfo(object):
    @property
    def short_month_names(self):
        return list(calendar.month_abbr)

    @property
    def full_month_names(self):
        return list(calendar.month_name)

    @classmethod
    def by_activities(cls, activities):
        self = cls()
        self.activities = activities
        return self

    def ride_calendar(self):
        calendars = {}

        cal = calendar.Calendar()
        # Render weeks beginning on Sunday
        cal.setfirstweekday(6)

        for year in [2016]:
            if year not in calendars:
                calendars[year] = {}
            for month in range(1, 13):

                calendars[year][month] = []

                for week in cal.monthdatescalendar(year, month):
                    week_list = []
                    for date in week:
                        date_info = {}
                        date_ride_distance = self.activities.ride_distances.by_day_month_year(date.day, date.month, date.year)
                        if date_ride_distance:
                            date_info["ride_distance"] = date_ride_distance

                        date_info["day_of_month"] = date.day
                        date_info["week_total_distance"] = self.activities.ride_distances.by_calendar_week(week)

                        if date.month == month:
                            date_info["style_class"] = "cur_month_date"
                        else:
                            date_info["style_class"] = "adjacent_month_date"

                        week_list.append(date_info)

                    calendars[year][month].append(week_list)
        return calendars

class AverageMileageChart(object):
    @classmethod
    def by_activities(cls, activities):
        self = cls()
        self.activities = activities
        return self

    @property
    def weeks_in_year(self):
        cal = calendar.Calendar()
        cal.setfirstweekday(6)
        all_weeks = [item for sublist in [cal.monthdatescalendar(2016, month) for month in range(1,13)] for item in sublist]
        # Get the unique list of weeks
        return sorted([list(w) for w in set(tuple(w) for w in all_weeks)], key=lambda i: i[0])

    @property
    def weekly_average(self):
        to_ret = []
        for week_num in self.range:
            to_ret.append(
                sum([self.activities.ride_distances.by_calendar_week(self.weeks_in_year[w-1]) for w in range(1, week_num + 1)]) / week_num
            )
            if datetime.date.today() in self.weeks_in_year[week_num]:
                return to_ret


    @property
    def range(self):
        return range(1, len(self.weeks_in_year) + 1)


