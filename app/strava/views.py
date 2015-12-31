from flask import (
    request,
    render_template,
    session,
    url_for,
    redirect,
    current_app,
    jsonify,
)
from . import route, as_json
from flask.ext.login import login_user, logout_user, login_required, \
    current_user, redirect

from ..model import Strava

@auth.before_app_request
def before_request():
    if not session.get('strava_token'):
        return redirect(url_for('strava.authorize'))

@route('/')
def index():
    return render_template('strava/index.html')

@route('/auth/authorize')
def authorize():
    return redirect(Strava.authorization_url())

@route('/auth/confirm')
def confirm_auth():
    if not request.get('code'):
        return redirect(url_for('strava.authorize'))
    else:
        Strava.set_token_by_code(request.get('code'))
        return

@as_json("/athlete")
def athlete():
    return Strava.athlete_by_token(session.get('strava_token'))




