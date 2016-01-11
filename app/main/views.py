from flask import (
    request,
    render_template,
    session,
    url_for,
    redirect,
    current_app,
    jsonify,
)
from . import main, as_json
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from ..lib.mt_counties import mt_counties as counties
from .. import db
from app.models.models import Riders, RiderStatus, ValidRider
from ..email import send_email
from forms import CountyForm, AddRider


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
    send_email(
        current_app.config['FLASKY_ADMIN'],
        'New Rider Request',
        'main/email/pbp_rider_request',
        name=request.args.get('name'),
        email=request.args.get('email'),
        rider_name=request.args.get('rider_name')
    )
    return


@main.route("/pbp_rider_status")
def get_rider_status():
    return jsonify(RiderStatus.get_by_fram(request.args.get("fram"))._asdict())


@main.route("/pbp/add_rider", methods=["GET", "POST"])
@login_required
def add_pbp_rider():
    form = AddRider()
    if form.validate_on_submit():
        if ValidRider.query.filter_by(name=form.name.data).all():
            session['results'] = form.name.data + ' has already been added'
        else:
            new_rider = ValidRider(name=form.name.data.lower())
            session['results'] = form.name.data
            db.session.add(new_rider)
            db.session.commit()
    return render_template('main/pbp_add_rider.html', form=form, results=session.get('results'))


@main.route("/pbp/added_riders", methods=["GET"])
def show_added_pbp_riders():
    riders = ValidRider.query.all()
    return "<br>".join(sorted([rider.name for rider in riders]))


