# -*- coding:utf-8 -*-
from flask import flash, Blueprint, render_template, redirect, url_for, request, abort, send_from_directory
from flask_login import current_user, login_required, login_user, logout_user
from sjtuface.core.forms import LoginForm, PersonForm, PhotoForm
from sjtuface.core.models import db, User, Person, Photo
from sqlalchemy.exc import IntegrityError
import os
from utility import *
from sjtuface import create_facepp

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


# todo: login checks
@bp.route('/person', methods=['GET', 'POST'])
def person():
    form = PersonForm(request.form)
    errors = {}

    if not form.validate_on_submit():
        errors.update(form.errors)
    else:
        person_id = form.id.data
        name = form.name.data
        p = Person(person_id, name)

        try:
            # insert into db
            db.session.add(p)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            errors.setdefault("id", []).append("Duplicated id")

    people_list = Person.query.order_by(Person.id)
    return render_template('person.html', people=people_list, form=PersonForm(None), errors=errors)


@bp.route('/person/<string:person_id>', methods=['GET', 'POST'])
def person_detail(person_id):
    person_ = Person.query.filter_by(id=person_id).first()

    if not person_:
        abort(404)

    form = PhotoForm(request.form)
    errors = {}

    if not form.validate_on_submit():
        errors.update(form.errors)
    else:
        img = request.files[form.photo.name]
        if not is_image_file(img.filename, allowed_type=["jpg", "jpeg"]):
            errors.setdefault("photo", []).append("Only jpg/jpeg photo is accepted")
        else:

            # get file name
            filename = get_filename(img)

            # insert into db
            photo_ = Photo(filename, owner=person_)
            try:
                db.session.add(photo_)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errors.setdefault("photo", []).append("Picture already exists!")
            else:
                # save photo file
                img.save(os.path.join(UPLOAD_DIR, filename))

    photo_names = map(lambda photo: photo.filename, person_.photos)

    return render_template('person_detail.html',
                           person=person_, photo_names=photo_names, form=PhotoForm(None), errors=errors)


@bp.route('/uploads/<person_id>/<filename>')
def added_face(person_id, filename):
    return send_from_directory(os.path.join(UPLOAD_DIR, person_id), filename)



@bp.route('/train', methods = ['POST'])
def do_train():
    print 'training'
    facepp = create_facepp()
    facepp.initialize()
    return redirect(url_for('sjtuface.train'))

@bp.route('/train', methods = ['GET'])
def train():
    return render_template('train.html')

