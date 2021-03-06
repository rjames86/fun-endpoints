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
    Response
)
from . import strava, route, as_json
from app.lib.decorators import cached
from flask.ext.login import login_user, logout_user, login_required, \
    current_user, redirect

import datetime

from app.models.strava import Strava, CalendarInfo, AverageMileageChart

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


@strava.before_app_request
def before_request():
    if request.endpoint == 'strava.authorize' or request.args.get('code'):
        return
    if not session.get('strava_token'):
        return redirect(url_for('strava.authorize'))


# http://flask.pocoo.org/docs/0.10/patterns/streaming/
def stream_template(template_name, **context):
    current_app.update_template_context(context)
    t = current_app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv


@route('/')
def index():
    return redirect(url_for('strava.activity', activity_type='ride'))


@route('/by_token/<token>')
def by_token(token):
    session['strava_token'] = token
    return redirect(url_for('strava.activity', activity_type='ride'))


@route('/reset_token')
def reset_token():
    del session['strava_token']
    return redirect(url_for('strava.index'))


@timer
@route('/<activity_type>')
def activity(activity_type):
    if activity_type == 'runs':
        activity_type = 'run'
    strava = Strava.by_token(session['strava_token'])
    strava.activity_type = activity_type
    calendar_info = CalendarInfo.by_activities(strava.activities)
    mileage_chart = AverageMileageChart.by_activities(strava.activities)

    return Response(stream_template('strava/index.html',
                                    strava=strava,
                                    activities=strava.activities,
                                    calendar_info=calendar_info,
                                    mileage_chart=mileage_chart))

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
