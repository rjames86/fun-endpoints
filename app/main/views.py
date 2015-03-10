from flask import (
    request,
    render_template,
    session,
    url_for,
    redirect,
    jsonify
)
from . import main
from ..lib.mt_counties import mt_counties as counties
from forms import CountyForm


@main.route('/')
def index():
    return "Hello World."


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
