from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, autoincrement=True)
    username = db.Column(db.Unicode(64), primary_key=True)
    password = db.Column(db.Unicode(128))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    # These methods are required by Flask-Login

    def get_id(self):
        return self.username

    def __unicode__(self):
        return self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False


class Person(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.Unicode(64), primary_key=True)
    name = db.Column(db.Unicode(64))

    def __init__(self, id, name):
        self.id = id
        self.name = name


class Photo(db.Model):
    __tablename__ = 'photo'

    filename = db.Column(db.Unicode(64), primary_key=True)
    owner_id = db.Column(db.Unicode(64), db.ForeignKey('person.id'))
    owner = db.relationship(Person, backref=db.backref('photos'))

    def __init__(self, filename, owner):
        self.filename = filename
        self.owner = owner


class AttendancePhoto(db.Model):
    __tablename__ = 'attendance_photo'

    filename = db.Column(db.Unicode(64), primary_key=True)
    owner_name = db.Column(db.Unicode(64), db.ForeignKey('user.username'))
    owner = db.relationship(User, backref=db.backref('photos'))

    def __init__(self, filename, owner):
        self.filename = filename
        self.owner = owner
