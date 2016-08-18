# -*- coding:utf-8 -*-
from flask import flash, Blueprint, render_template, redirect, url_for, request, abort, send_from_directory
from flask_login import current_user, login_required, login_user, logout_user
from sjtuface.core.forms import LoginForm, PersonForm, FaceForm
from sjtuface.core.models import db, User, Person
import sqlalchemy
import os, re, time

bp = Blueprint('sjtuface', __name__)

# FIXME: where should I place this variable?
UPLOAD_DIR = os.path.abspath("sjtuface/static/uploads")


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


@bp.route('/person', methods=['GET', 'POST'])
def person():
    people_list = Person.query.order_by(Person.id)
    form = PersonForm(request.form)
    errors = {}
    if form.validate_on_submit():
        id = form.id.data
        name = form.name.data
        p = Person(id, name)
        try:
            db.session.add(p)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            errors.setdefault(form.id.name, []).append("Duplicated id")
    else:
        errors = form.errors
    return render_template('person.html', people=people_list, form=PersonForm(), errors=errors)


def is_image_file(filename):
    return re.match(r'^.+\.(jpg)$', filename)


def create_upload_sub_dir_if_not_exist(pid):
    if pid not in os.listdir(UPLOAD_DIR):
        os.mkdir(os.path.join(UPLOAD_DIR, pid))


# TODO:
# 1. better filename
# 2. more suffix for image
# 3. beatification
@bp.route('/upload', methods=['GET', 'POST'])
def add_face():
    form = FaceForm(request.form)
    errors = {}
    if form.validate_on_submit():
        img = request.files[form.photo.name]
        if not is_image_file(img.filename):
            errors.setdefault(form.photo.name, []).append("Only jpg photo is accepted")
        else:
            pid = form.person_id.data
            create_upload_sub_dir_if_not_exist(pid)
            fname = str(time.time()) + ".jpg"
            img.save(os.path.join(UPLOAD_DIR, pid, fname))
            return redirect(url_for('sjtuface.added_face', person_id=pid, filename=fname))
    else:
        errors = form.errors

    return render_template('add_face.html', form=FaceForm(), errors=errors)


@bp.route('/uploads/<person_id>/<filename>')
def added_face(person_id, filename):
    return send_from_directory(os.path.join(UPLOAD_DIR, person_id), filename)
