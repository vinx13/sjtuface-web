import os

SRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = "mysql://root:123456@localhost/flaskblog"

#: cache settings
# find options on http://pythonhosted.org/Flask-Cache/
CACHE_TYPE = 'simple'

SQLALCHEMY_TRACK_MODIFICATIONS = True

DEFAULT_GROUP_NAME = "default"

API_KEY = 'do_not_tell_you'
API_SECRET = 'do_not_tell_you'