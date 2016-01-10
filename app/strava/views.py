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
from ..lib.decorators import cached
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
@cached()
def index():
    activities = Strava.activities_by_token(session['strava_token'])
    calendar_info = CalendarInfo.by_activities(activities)

    return render_template('strava/index.html',
                           activities=activities,
                           calendar_info=calendar_info)


@route('/auth/authorize')
def authorize():
    return redirect(Strava.authorization_url())


@route('/auth/confirm')
def confirm_auth():
    token = Strava().get_access_token(request.args.get('code'))
    session['strava_token'] = token
    return redirect(url_for('strava.index'))


@as_json("/athlete")
def athlete():
    return [Strava.athlete_by_token(session.get('strava_token'))]
