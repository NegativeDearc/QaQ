from flask import Flask, request, session, abort
from app.config import config_dict
from app.models import db
from app.models.model import login
from flask_login import LoginManager
from flask_restful import Api
import os

lm = LoginManager()


def create_app(config=None):
    from app.views.main_view import main

    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    db.app = app

    lm.session_protection = 'strong'
    lm.login_view = "main.main_login"
    lm.refresh_view = "main.main_login"
    lm.needs_refresh_message = u"To protect your account, please re-authenticate to access this page."
    lm.needs_refresh_message_category = "info"

    # lm callback
    @lm.user_loader
    def load_user(uid):
        return login.get(uid)

    lm.init_app(app)

    app.register_blueprint(main)

    from app.views.apiv1_veiw import MainContent, QueryId
    api = Api(app)
    api.add_resource(MainContent, '/apiv1.0/querycontent', endpoint='content')
    api.add_resource(QueryId, '/apiv1.0/queryid', endpoint='queryid')


    return app


def csrf_protect():
    if request.method == 'POST':
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_crsf_token'):
            abort(403)


def generate_csrf_token():
    if '_crsf_token' not in session:
        session['_crsf_token'] = os.urandom(30).encode('hex')
    return session['_crsf_token']


app = create_app(config=config_dict["dev"])
app.jinja_env.globals['crsf_token'] = generate_csrf_token