#!/usr/bin/env python
# coding: utf-8
from flask_script import Manager
from sjtuface import create_app
from sjtuface.core.models import db, User, Person, Photo,AttendancePhoto
from werkzeug.security import generate_password_hash
from sjtuface.core.utility import create_dir_if_not_exist, delete_photo_file, UPLOAD_DIR

import os
import shutil

app = create_app()

manager = Manager(app)


@manager.command
def init():
    db.create_all()
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.mkdir(UPLOAD_DIR)
    create_db()
    create_default_group()
    seed()


@manager.command
def create_db():
    """Create database for """
    db.create_all()


@manager.option('-u', '--name', dest='username', default='admin')
@manager.option('-p', '--password', dest='password', default='123456')
def create_user(username, password):
    admin = User(username, generate_password_hash(password))
    db.session.add(admin)
    db.session.commit()


@manager.command
def seed():
    for p in Person.query.all():
        # delete every photo of this person
        for photo in p.photos:
            delete_photo_file(photo.filename)
            db.session.delete(photo)
        db.session.delete(p)

    db.session.commit()
    names = [u"傅园慧", u"宁泽涛", u"张继科", u"张梦雪", u"林武威",
             u"张杰", u"张杰(歌手)", u"刘强东"]
    person_list = [Person(unicode(i), unicode(n)) for i, n in zip(range(len(names)), names)]
    db.session.add_all(person_list)
    db.session.commit()


@manager.command
def _clean_photo():
    """
    Clean both photo file in db and in directory,
    create empty dir for every `Person`
    """
    for p in Photo.query.all():
        db.session.delete(p)
    for p in AttendancePhoto.query.all():
        db.session.delete(p)
    db.session.commit()


def create_default_group():
    pass


if __name__ == '__main__':
    manager.run()
