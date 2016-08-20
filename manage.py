#!/usr/bin/env python
# coding: utf-8
from flask.ext.script import Manager
from sjtuface import create_app
from sjtuface.core.models import db, User, Person, Photo
from werkzeug.security import generate_password_hash
from sjtuface.core.utility import create_dir_if_not_exist, delete_photo_dir, UPLOAD_DIR

app = create_app()

manager = Manager(app)


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
        delete_photo_dir(p.id,silent=True)
        db.session.delete(p)
    db.session.commit()
    names = ["傅园慧", "宁泽涛", "张继科", "张梦雪", "林武威",
             "Obama", "Hitler", "Hillary", "Jobs"]
    person_list = [Person(i, n) for i, n in zip(range(len(names)), names)]
    db.session.add_all(person_list)
    db.session.commit()
    for n in range(len(names)):
        create_dir_if_not_exist(str(n), UPLOAD_DIR)


@manager.command
def _clean_photo():
    """
    Clean both photo file in db and in directory,
    create empty dir for every `Person`
    """
    for p in Photo.query.all():
        db.session.delete(p)
    db.session.commit()
    for p in Person.query.all():
        delete_photo_dir(p.id, silent=True)
        create_dir_if_not_exist(p.id, UPLOAD_DIR)

if __name__ == '__main__':
    manager.run()
