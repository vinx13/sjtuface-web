# -*- coding:utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, request, abort, send_from_directory, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash

from sjtuface import create_facepp
from sjtuface.core.forms import LoginForm, PersonForm, PhotoForm, AttendancePhotoForm, IdentifyForm
from sjtuface.core.models import db, User, Person, Photo, AttendancePhoto
from utility import *

bp = Blueprint('sjtuface', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    form = LoginForm()
    errors = {}
    if not form.validate_on_submit():
        errors.update(form.errors)
    else:
        user = db.session.query(User).get(form.username.data)
        if not user:
            errors.setdefault("username", []).append("该用户名不存在!")
        elif not check_password_hash(user.password, form.password.data):
            errors.setdefault("password", []).append("密码错误!")
        else:
            login_user(user)
            next = request.args.get('next')
            # next_is_valid should check if the user has valid
            # permission to access the `next` url
            if next_is_valid(next):
                return redirect(next or url_for('sjtuface.home'))
            else:
                return abort(400)

    return render_template('login.html', form=form, errors=errors)


def next_is_valid(next):
    return True  # TODO


@bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for("sjtuface.login"))


@bp.route('/', methods=['GET'])
@bp.route('/home', methods=['GET'])
@login_required
def home():
    return render_template("home.html")


@bp.route('/person', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
def added_face(person_id, filename):
    return send_from_directory(os.path.join(UPLOAD_DIR, person_id), filename)


@bp.route('/api/train', methods=['POST'])
def train():
    facepp = create_facepp()
    facepp.initialize()
    return '', 200


@bp.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    errors = {}
    if request.method == "POST":
        form = AttendancePhotoForm()
        img = form.photo.data

        if not is_image_file(img.filename, allowed_type=["jpg", "jpeg"]):
            errors.setdefault("photo", []).append("Only jpg/jpeg photo is accepted")
        else:
            # get file name
            filename = get_filename(img)

            # insert into db
            photo_ = AttendancePhoto(filename, owner=current_user)
            try:
                db.session.add(photo_)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errors.setdefault("photo", []).append("Picture already exists!")
            else:
                # save photo file
                img.save(os.path.join(ATTENDANCE_UPLOAD_DIR, filename))

    photo_names = map(lambda photo: photo.filename, current_user.photos)
    person_list = Person.query.all()

    return render_template("attendence.html",
                           person_list=person_list, photo_names=photo_names,
                           form=AttendancePhotoForm(None), errors=errors)


@bp.route('/api/identify', methods=['POST'])
def identify():
    print('in')
    facepp = create_facepp()
    results = {}
    for photo_ in AttendancePhoto.query.filter_by(owner_name=current_user.username):
        path = os.path.join(ATTENDANCE_UPLOAD_DIR, photo_.filename)
        ret = facepp.identify_new_face(path)
        print(ret)
        most_possible_one = find_outstanding_one(ret)
        results[photo_.filename] = most_possible_one[u'person_name'] or u'uncertain'
    print(results)
    return jsonify(results), 200


def find_outstanding_one(lst, key=None, min_threshold=None, diff_threshold=None):
    tmp = map(key, lst) if key else lst

    m = max(tmp)
    if min_threshold and m < min_threshold:
        return None

    ind = tmp.index(m)
    second_m = max(x for i, x in enumerate(tmp) if i != ind)

    if diff_threshold and m - second_m < diff_threshold:
        return None

    return lst[ind]
