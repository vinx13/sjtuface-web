# -*- coding: utf-8 -*-
from flask import flash, Blueprint, render_template, redirect, url_for, request, abort
from forms import LoginForm
from flask.ext.login import current_user, login_required, login_user, logout_user
from sqlalchemy import desc
from models import db, User

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
    return True # TODO


@bp.route('/person')
def manage_person():
    fake_people_list = ["奥巴马", "张杰", "谢娜", "傅园慧", "林武威"]
    return render_template('person.html', people=[{"name": n} for n in fake_people_list])


@bp.route('/add_face')
def add_face():
    return render_template('add_face.html')

