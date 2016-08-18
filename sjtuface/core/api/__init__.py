from flask_restful import Api, Resource, abort, reqparse, request
from flask import jsonify, redirect, url_for, flash
from ..models import db
from ..forms import PersonForm
import sjtuface.core.models as models  # to avoid name conflict between resources and models
import sqlalchemy

api = Api(prefix="/api")


def get_or_abort(person_id):
    p = models.Person.query.filter_by(id=person_id).first()
    if not p:
        abort(404)
    else:
        return p


class Person(Resource):
    def get(self, person_id):
        p = get_or_abort(person_id)
        return jsonify(id=p.id, name=p.name)

    def delete(self, person_id):
        p = get_or_abort(person_id)
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


api.add_resource(PersonList, '/person')
api.add_resource(Person, '/person/<string:person_id>')
