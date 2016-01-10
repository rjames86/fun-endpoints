from flask import (
    request,
    render_template,
    session,
    url_for,
    redirect,
    make_response,
    current_app,
    jsonify,
    g,
)
from . import strava, route, as_json
from flask.ext.login import login_user, logout_user, login_required, \
    current_user, redirect

import datetime

from ..models import Strava, CalendarInfo

@strava.before_app_request
def before_request():
    if request.endpoint == 'strava.authorize' or request.args.get('code'):
        return
    if not session.get('strava_token'):
        return redirect(url_for('strava.authorize'))


@route('/')
def index():
    activities = Strava.activities_by_token(session['strava_token'])
    calendar_info = CalendarInfo()
    import calendar

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

                    if date:
                        date_info["link"] = "some link"

                    date_info["day_of_month"] = date.day

                    if date.month == month:
                        date_info["style_class"] = "cur_month_date"
                    else:
                        date_info["style_class"] = "adjacent_month_date"

                    week_list.append(date_info)

                calendars[year][month].append(week_list)

    return render_template('strava/index.html',
                           activities=activities,
                           calendars=calendars,
                           month_names=calendar.month_name,
                           calendar_info=calendar_info)

@route('/auth/authorize')
def authorize():
    return redirect(Strava.authorization_url())

@route('/auth/confirm')
def confirm_auth():
    token = Strava().get_access_token(request.args.get('code'))
    print "setting session"
    session['strava_token'] = token
    print session
    return redirect(url_for('strava.index'))


@as_json("/athlete")
def athlete():
    print "STRAVA TOKEN", session.get('strava_token')
    return [Strava.athlete_by_token(session.get('strava_token'))]




