from flask_restful import Api, Resource, abort, reqparse, request
from flask import jsonify, redirect, url_for, flash, render_template
from ..models import db
import sjtuface.core.models as models  # to avoid name conflict between resources and models

from ..utility import delete_photo_file

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
        for photo in p.photos:
            delete_photo_file(photo.filename)
            db.session.delete(photo)
        db.session.delete(p)
        db.session.commit()
        return '', 204

    def put(self, person_id):
        pass
        # todo


class Photo(Resource):
    def delete(self, filename):
        p = get_or_abort(models.Photo, filename=filename)
        delete_photo_file(filename)
        db.session.delete(p)
        db.session.commit()
        return '', 204


api.add_resource(Person, '/person/<string:person_id>')
api.add_resource(Photo, '/photo/<string:filename>')
