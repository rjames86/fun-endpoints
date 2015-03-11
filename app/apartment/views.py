from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import apartment
from .. import db
from ..models import User, Permission, Role, ApartmentUnits
from ..decorators import admin_required, permission_required
from forms import EditProfileForm, EditProfileAdminForm
from ..lib.parse_transaction import TransactionParser


@apartment.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('apartment/user.html', user=user)


@apartment.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    return render_template('apartment/edit_profile.html', form=form)


@apartment.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.apartment_unit = ApartmentUnits.query.get(form.apartment_unit.data)
        user.name = form.name.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.name.data = user.name
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.apartment_unit.data = user.apartmentunit_id
    return render_template('apartment/edit_profile.html', form=form, user=user)


@apartment.route('/rental', methods=['GET'])
@login_required
def rental():
    if not current_user.apartment_unit:
        return render_template('main/rental.html')
    transactions = TransactionParser.parse(
        'apartment/transactionreport_unit{}.txt'.format(current_user.apartment_unit.unit_number))
    return render_template(
        'main/rental.html',
        data=transactions)


@apartment.route('/rental/<int:apartment>', methods=['GET'])
@login_required
@admin_required
def rental_admin(apartment):
    apartment_unit = ApartmentUnits.query.filter_by(unit_number=apartment).first()
    transactions = TransactionParser.parse(
        'apartment/transactionreport_unit{}.txt'.format(apartment_unit.unit_number))
    return render_template(
        'main/rental.html',
        data=transactions)


@apartment.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"


@apartment.route('/view')
@login_required
@permission_required(Permission.VIEW)
def for_moderators_only():
    return "For comment moderators!"
