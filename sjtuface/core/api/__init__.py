from flask_restful import Api, Resource, abort, reqparse, request
from flask import jsonify, redirect, url_for, flash, render_template
from ..models import db
import sjtuface.core.models as models  # to avoid name conflict between resources and models
from ..views import UPLOAD_DIR
import os
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

#
# class PersonList(Resource):
#     def post(self):
#         form = PersonForm(request.form)
#
#         if not form.validate_on_submit():
#             flash(form.errors)
#             return redirect(url_for("sjtuface.person"))
#
#         id = form.id.data
#         name = form.name.data
#         person = models.Person(id, name)
#         try:
#             db.session.add(person)
#             db.session.commit()
#         except sqlalchemy.exc.IntegrityError:
#             db.session.rollback()
#             flash("Duplicated id!")
#
#         return redirect(url_for("sjtuface.person"))


class Photo(Resource):
    def delete(self, filename):
        p = get_or_abort(models.Photo, filename=filename)
        path = os.path.join(UPLOAD_DIR, p.owner.id, filename)
        print(path)
        db.session.delete(p)
        db.session.commit()
        return '', 204


# api.add_resource(PersonList, '/person')
api.add_resource(Person, '/person/<string:person_id>')
api.add_resource(Photo, '/photo/<string:filename>')
