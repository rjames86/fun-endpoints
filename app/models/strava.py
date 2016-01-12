import calendar
from collections import defaultdict, Counter
import json
import math
import datetime

from flask import current_app, request, url_for, session, g

from stravalib.client import BatchedResultsIterator, Client as StravaClient
from stravalib.model import BaseEntity, Athlete
from stravalib import unithelper


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


class ActivityCounter(object):
    def __init__(self, activities):
        self.chosen_activities = activities.chosen_activities
        self.activities = activities
        self._counter_dict = None
        # CalendarInfo().month_names.index(month_abbrev)

    @property
    def activity_count_by_month(self):
        if not self._counter_dict:
            year = defaultdict(dict)
            for chosen_activity in self.chosen_activities:
                if chosen_activity.start_date_local.year not in year.keys():
                    activity_year = defaultdict(int)
                else:
                    activity_year = year[chosen_activity.start_date_local.year]
                activity_year[chosen_activity.start_date_local.month] += 1
                year[chosen_activity.start_date_local.year] = activity_year
            self._counter_dict = year
        return self._counter_dict

    def by_year(self, year):
        return sum(self.activity_count_by_month[year].viewvalues())

    def by_month(self, month):
        to_ret = 0
        for year, values in self.activity_count_by_month.iteritems():
            for month_value, count in values.iteritems():
                if month_value == month:
                    to_ret += count

        return to_ret

    def by_month_year(self, month, year):
        return self.activity_count_by_month[year].get(month, 0)


class DistanceCounter(object):
    UNIT = 'miles'

    def __init__(self, activities):
        self.chosen_activities = activities.chosen_activities
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
        # TODO(ryan) probably should memoize this at some point so its faster.
        return self._calculate_distance(
            lambda ride: (ride.start_date_local.year, ride.start_date_local.month, ride.start_date_local.day) == (year, month, day))

    def by_calendar_week(self, cal_week):
        return self._calculate_distance(
            lambda ride: (ride.start_date_local.date() >= cal_week[0]) and (ride.start_date_local.date() <= cal_week[-1]))

    def best_month(self, month):
        all_years = set([chosen_activity.start_date_local.year for chosen_activity in self.chosen_activities])
        return max(
                [(year, month, self.by_month_year(month, year), self.activities.activity_counts.by_month_year(month, year)) for year in all_years],
                key=lambda y: y[2]
                )

    def _calculate_distance(self, comparator):
        to_ret = 0
        for chosen_activity in self.chosen_activities:
            if comparator(chosen_activity):
                to_ret += self.get_distance(chosen_activity.distance)
        return to_ret


class Activities(object):
    TYPE_TO_NAME = {
        'ride': 'Cycling',
        'run': 'Running'
    }

    ALL_ACTIVITY_TYPES = [
            'ride', 'run', 'swim', 'workout', 'hike', 'walk', 'nordicski',
            'alpineski', 'backcountryski', 'iceskate', 'inlineskate', 'kitesurf', 'rollerski',
            'windsurf', 'workout', 'snowboard', 'snowshoe'
    ]

    def __init__(self, activities, activity_type):
        self._chosen_activities = None

        self.activities = activities
        self.activity_type = activity_type

    @property
    def available_activity_types(self):
        return set(a.type for a in self.activities)

    @property
    def human_activity_type(self):
        return self.TYPE_TO_NAME.get(self.activity_type, self.activity_type.title())

    @property
    def chosen_activities(self):
        if not self._chosen_activities:
            self._chosen_activities = [a for a in self.activities
                                       if a.type.lower() == self.activity_type.lower()]

        return self._chosen_activities

    @property
    def rides(self):
        if not self._rides:
            self._rides = [a for a in self.activities if a.type == 'Ride']
        return self._rides

    @property
    def runs(self):
        if not self._runs:
            self._runs = [a for a in self.activities if a.type == 'Run']
        return self._runs

    @property
    def activity_counts(self):
        return ActivityCounter(self)

    @property
    def activity_distances(self):
        return DistanceCounter(self)


class Strava(object):
    def __init__(self):
        self.client_id = current_app.config['STRAVA_CLIENT_ID']
        self.client_secret = current_app.config['STRAVA_CLIENT_SECRET']
        self.redirect_uri = url_for('strava.confirm_auth', _external=True)

        self.client = StravaClient()

        self._activity_type = 'ride'  # rides or runs
        self._activities = None

    @property
    def activity_type(self):
        return self._activity_type

    @activity_type.setter
    def activity_type(self, value):
        self._activity_type = value
        self._activities = None

    @property
    def athlete(self):
        return self.client.get_athlete()

    @property
    def activities(self):
        if not self._activities:
            # current_year = datetime.datetime.now().year
            # after = datetime.datetime(current_year - 2, 12, 25)
            self._activities = Activities(self.client.get_activities(), self.activity_type)
        return self._activities

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

    @classmethod
    def by_token(cls, token):
        self = cls()
        self.client.access_token = token
        return self




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

    def activity_calendar(self):
        calendars = {}

        cal = calendar.Calendar()
        # Render weeks beginning on Sunday
        # cal.setfirstweekday(6)

        for year in [2016]:
            if year not in calendars:
                calendars[year] = {}
            for month in range(1, 13):

                calendars[year][month] = []

                for week in cal.monthdatescalendar(year, month):
                    week_list = []
                    for date in week:
                        date_info = {}
                        date_ride_distance = self.activities.activity_distances.by_day_month_year(date.day, date.month, date.year)
                        if date_ride_distance:
                            date_info["ride_distance"] = date_ride_distance

                        date_info["day_of_month"] = date.day
                        date_info["week_total_distance"] = self.activities.activity_distances.by_calendar_week(week)

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
        # cal.setfirstweekday(6)
        all_weeks = [item for sublist in [cal.monthdatescalendar(2016, month) for month in range(1,13)] for item in sublist]
        # Get the unique list of weeks
        return sorted([list(w) for w in set(tuple(w) for w in all_weeks)], key=lambda i: i[0])

    @property
    def graph_weekly_average(self):
        to_ret = []
        for week_num in self.range:
            to_ret.append(
                dict(
                    x=week_num,
                    y=sum([self.activities.activity_distances.by_calendar_week(self.weeks_in_year[w-1]) for w in range(1, week_num + 1)]) / week_num
                )
            )
            if datetime.date.today() in self.weeks_in_year[week_num]:
                latest_week = max([item['x'] for item in to_ret])
                for additional_week in range(latest_week, self.range[-1]):
                    to_ret.append(dict(x=additional_week, y=None))
                return json.dumps(to_ret)

    @property
    def weekly_average(self):
        to_ret = []
        for week_num in self.range:
            to_ret.append(
                (week_num, sum([self.activities.activity_distances.by_calendar_week(self.weeks_in_year[w-1]) for w in range(1, week_num + 1)]) / week_num)
            )

        first_half = int(math.ceil(len(to_ret) / 2.0))

        second_half = len(to_ret) - first_half
        return map(None, to_ret[:first_half], to_ret[second_half+1:])

    @property
    def range(self):
        return range(1, len(self.weeks_in_year) + 1)
