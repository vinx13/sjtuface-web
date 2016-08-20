from flask_restful import Api, Resource, abort, reqparse, request
from flask import jsonify, redirect, url_for, flash, render_template
from ..models import db
from ..forms import PersonForm, PhotoForm
import sjtuface.core.models as models  # to avoid name conflict between resources and models
import sqlalchemy
import re, os, hashlib
from ..views import UPLOAD_DIR

api = Api(prefix="/api")


def get_or_abort(model, **filter_):
    try:
        x = model.query.filter_by(**filter_).first()
    except TypeError:
        raise
    else:
        if not x:
            abort(404)
        else:
            return x


class Person(Resource):
    def get(self, person_id):
        p = get_or_abort(person_id)
        return jsonify(id=p.id, name=p.name)

    def delete(self, person_id):
        p = get_or_abort(models.Person, id=person_id)
        db.session.delete(p)
        db.session.commit()
        return '', 204

    def put(self, person_id):
        pass
        # todo


class PersonList(Resource):
    def post(self):
        form = PersonForm(request.form)

        if not form.validate_on_submit():
            flash(form.errors)
            return redirect(url_for("sjtuface.person"))

        id = form.id.data
        name = form.name.data
        person = models.Person(id, name)
        try:
            db.session.add(person)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()
            flash("Duplicated id!")

        return redirect(url_for("sjtuface.person"))


class Photo(Resource):
    def delete(self, filename):
        p = get_or_abort(models.Photo, filename=filename)
        db.session.delete(p)
        db.session.commit()
        return '', 204


def is_image_file(filename):
    return re.match(r'^.+\.(jpg)$', filename)


def md5_file_name(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()


class Photos(Resource):
    def post(self):
        form = PhotoForm(request.form)
        errors = {}
        if not form.validate_on_submit():
            errors = form.errors
        else:
            img = request.files[form.photo.name]
            if not is_image_file(img.filename):
                errors.setdefault(form.photo.name, []).append("Only jpg photo is accepted")
            else:
                pid = form.person_id.data
                try:
                    os.mkdir(os.path.join(UPLOAD_DIR, pid))
                except OSError:
                    pass
                fname = md5_file_name(img.read()) + "." + img.filename.split(".", 1)[-1]
                img.seek(0)
                img.save(os.path.join(UPLOAD_DIR, pid, fname))
                # return redirect(url_for('sjtuface.added_face', person_id=pid, filename=fname))

        return render_template('add_face.html', form=PhotoForm(), errors=errors)
        # todo: api should not render


api.add_resource(PersonList, '/person')
api.add_resource(Person, '/person/<string:person_id>')
api.add_resource(Photos, '/photo')
api.add_resource(Photo, '/photo/<string:filename>')
