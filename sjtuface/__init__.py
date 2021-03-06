from flask import Flask, session, request, abort, redirect, url_for
from .core.models import db
from .core.recognition import FaceRecognitionSys
from flask_login import LoginManager

import config
import sys

reload(sys)
sys.setdefaultencoding("utf-8")


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    register_database(app)
    register_blueprint(app)
    register_api(app)
    init_login(app)
    # create_admin(app, db)
    # init_csrf_protection(app)
    return app


def register_log():
    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)


def register_database(app):
    db.init_app(app)
    db.app = app
    # cache.init_app(app)


def register_blueprint(app):
    from .core.views import bp
    app.register_blueprint(bp)
    # from .core.api import api
    # api.init_app(app)
    # moved to `register api`


def register_api(app):
    from .core.api import api
    api.init_app(app)


# Initialize flask-login
def init_login(app):
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        from .core.models import User
        return db.session.query(User).get(user_id)

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for("sjtuface.login"))


def init_csrf_protection(app):
    app.jinja_env.globals['csrf_token'] = generate_csrf_token

    @app.before_request
    def csrf_protect():
        if request.method == "POST":
            token = session.pop('_csrf_token', None)
            if not token or token != request.form.get('_csrf_token'):
                abort(403)


def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = 'some_random_string()'  # FIXME
    return session['_csrf_token']


def create_facepp():
    return FaceRecognitionSys(config.DEFAULT_GROUP_NAME)