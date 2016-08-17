# -*- coding: utf-8 -*-
from flask import flash, Blueprint, render_template, redirect, url_for, request, abort
from .forms import LoginForm, PersonForm
from flask_login import current_user, login_required, login_user, logout_user
from .models import db, User, Person
import sqlalchemy

bp = Blueprint('sjtuface', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).get(form.username.data)
        login_user(user)

        flash('Logged in successfully.')

        next = request.args.get('next')
        # next_is_valid should check if the user has valid
        # permission to access the `next` url
        if not next_is_valid(next):
            return abort(400)

        return redirect(next or url_for('sjtuface.manage_person'))
    return render_template('login.html', form=form)


def next_is_valid(next):
    return True  # TODO


@bp.route('/person', methods=['GET'])
def manage_person():
    people_list = Person.query.order_by(Person.id)
    return render_template('person.html', people=people_list, form=PersonForm())


@bp.route('/person/add', methods=['POST'])
def add_person():
    form = PersonForm(request.form)

    if form.validate_on_submit():
        id = form.id.data
        name = form.name.data
        person = Person(id, name)
        try:
            db.session.add(person)
            db.session.commit()
        except sqlalchemy.orm.exc.FlushError:
            # fixme: when duplication really happens, this cannot catch the error
            flash("duplicate id")

        return redirect(url_for('sjtuface.manage_person'))
    else:
        abort(406)


@bp.route('/person/delete', methods=['POST'])
def delete_person():
    # todo
    did = request.data
    p = Person.query.filter_by(id=did).first()
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('sjtuface.manage_person'))


@bp.route('/add_face')
def add_face():
    return render_template('add_face.html')
