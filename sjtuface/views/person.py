# -*- coding:utf-8 -*-
from flask import flash, Blueprint, render_template, redirect, url_for, request, abort
from sjtuface.core.forms import PersonForm
from sjtuface.core.models import db, Person
import sqlalchemy

bp_person = Blueprint('person', __name__, url_prefix="/person")


@bp_person.route('/', methods=['GET'])
def index():
    people_list = Person.query.order_by(Person.id)
    return render_template('person.html', people=people_list, form=PersonForm())


@bp_person.route('/add', methods=['POST'])
def add():
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

        return redirect(url_for('person.index'))
    else:
        abort(406)


@bp_person.route('/delete', methods=['POST'])
def delete():
    did = request.form['did']
    p = Person.query.filter_by(id=did).first()
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('person.index'))


@bp_person.route('/add_face')
def add_face():
    return render_template('add_face.html')
