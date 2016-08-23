from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, FileField
from wtforms.validators import DataRequired


class LoginForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    # remember_me = BooleanField('remember_me', default=False)


class PersonForm(Form):
    id = StringField('id', validators=[DataRequired()])
    name = StringField('name', validators=[DataRequired()])


class PhotoForm(Form):
    person_id = StringField('id', validators=[DataRequired()])
    photo = FileField('photo')


class AttendancePhotoForm(Form):
    photo = FileField('photo')


class IdentifyForm(Form):
    photo = FileField('photo') # photo to be recognized

