from flask import (
    render_template,
    flash,
    redirect,
    url_for
)
from . import admin
from ..models import User
from .. import db
from forms import TokenForm
from flask.ext.login import login_required


@admin.route('/')
def index():
    return "Hello admins."


@admin.route('/add_token', methods=['GET', 'POST'])
@login_required
def add_token():
    form = TokenForm()
    users = User.query.all()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is not None:
            user.reset_token(form.token.data)
            flash("Token updated for %s" % form.name.data)
            return redirect(url_for('admin.add_token'))
        else:
            user = User(
                username=form.name.data,
                token=form.token.data
                )
            db.session.add(user)
            db.session.commit()
            flash('Token generated for %s.' % form.name.data)
    return render_template('admin/token.html', form=form, users=users)
