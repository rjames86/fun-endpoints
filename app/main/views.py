from flask import (
    request,
    render_template,
    session,
    url_for,
    redirect,
    current_app,
)
from . import main, as_json
from ..lib.mt_counties import mt_counties as counties
from ..models import Riders
from ..email import send_email
from forms import CountyForm


@main.route('/')
def index():
    return render_template('index.html')


@main.route("/ip", methods=["GET"])
def get_my_ip():
    return str(request.remote_addr), 200


@main.route("/mt_counties", methods=["GET", "POST"])
def mt_counties():
    form = CountyForm()
    to_ret = None
    if form.validate_on_submit():
        to_ret = counties[str(form.county_number.data)]
        session['results'] = to_ret
        return redirect(url_for('main.mt_counties'))
    return render_template('main/counties.html', form=form, results=session.get('results'))


@main.route("/pbp")
def pbp():
    return render_template('main/pbp.html')


@as_json("/pbp_riders")
def local_pbp_riders():
    return Riders.get_local_riders()


@as_json("/pbp_riders/all")
def all_pbp_riders():
    return Riders.get_all_riders()


@main.route("/pbp_rider_request", methods=["POST"])
def pbp_rider_request():
    print request
    print request.args
    print request.args.get('name')
    print request.args.get('email')
    print request.args.get('rider_name')
    send_email(
        current_app.config['FLASKY_ADMIN'],
        'New Rider Request',
        'main/email/pbp_rider_request',
        name=request.args.get('name'),
        email=request.args.get('email'),
        rider_name=request.args.get('rider_name')
    )
    return
