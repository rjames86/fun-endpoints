from flask import (
    request,
    render_template,
    session,
    url_for,
    redirect,
    current_app,
    jsonify,
)
from . import strava, route, as_json
from flask.ext.login import login_user, logout_user, login_required, \
    current_user, redirect

from ..models import Strava

@strava.before_app_request
def before_request():
    endpoint = request.endpoint or ''
    print "ENDPOINT", endpoint
    if not session.get('strava_token'):
        if 'auth' not in endpoint:
            return redirect(url_for('strava.authorize'))

@route('/')
def index():
    return render_template('strava/index.html')

@route('/auth/authorize')
def authorize():
    return redirect(Strava.authorization_url())

@route('/auth/confirm')
def confirm_auth():
    print "IN THE CONFIRM ENDPOINT"
    if not request.args.get('code'):
        return redirect(url_for('strava.authorize'))
    else:
        print "GONNA SET CODE TO", request.args.get('code')
        Strava.set_token_by_code(request.args.get('code'))
    return redirect(url_for('strava.index'))

@as_json("/athlete")
def athlete():
    return Strava.athlete_by_token(session.get('strava_token'))




