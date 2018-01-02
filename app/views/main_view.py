from flask import Blueprint, render_template, request, redirect, url_for, g, flash, make_response
from app.models.model import db, qanda, login
from flask_login import login_required, login_user, logout_user, current_user, login_fresh, login_url
from sqlalchemy.sql import or_
from app.config import config_dict
import os
import time


main = Blueprint('main', __name__)


@main.before_request
def before_request():
    g.user = current_user


@main.route("/")
def main_root():
    categories = qanda.categories()
    return render_template('index.html', categories=categories)


@main.route('/login', methods=["GET", "POST"])
def main_login():
    if request.method == 'POST':
        user = login.query.filter(or_(login.user == request.form.get("usr"),
                                      login.nickname == request.form.get('usr'))
                                  ).first()
        if user is not None and user.verify_password(request.form.get('pwd', None)):
            login_user(user, remember=True, force=True, fresh=True)  # it will return True if success
            if not request.args.get("next"):  # if get None , redirect to main.main_edit
                return redirect(url_for("main.main_backend"))
            return redirect(request.args.get("next"))
        else:
            flash('Wrong user name or password.')
        print request.form
        print request.args.get("next")
        print current_user
    return render_template("login.html")


@main.route('/upload/image', methods=['POST'])
def main_upload_image():
    f = request.files['file']
    postfix = f.filename.split('.')[-1]
    filename = time.strftime("%Y%m%d%H%M%S", time.localtime()) + '.%s' % postfix
    url = os.path.join(config_dict['pro'].IMAGE_UPLOAD_PATH, filename)
    print url
    f.save(url)
    response = make_response('static/img/%s' % filename)
    return response


@main.route('/backend', methods=["GET", "POST"])
@login_required
def main_backend():
    database = {}
    archive = qanda.archive()
    print archive

    if request.args.get("edit") == 'true':
        uuid = request.args.get('uid')
        database = qanda.query_uid(uuid)

    if request.method == 'POST':
        # insert new recorder
        if 'sub_new' in request.form.keys():
            print request.form
            try:
                db.session.add(qanda(request.form))
                db.session.commit()
            except Exception:
                db.session.rollback()
            return redirect(url_for("main.main_backend"))
        # update an exist recorder
        if 'update_' in request.form.keys():
            print request.form
            try:
                 db.session.query(qanda).filter(qanda.uuid == uuid).update({
                     "title": request.form.get("title"),
                     "category": request.form.get("category"),
                     "content": request.form.get("content"),
                     "answer": request.form.get("answer"),
                 })
                 db.session.commit()
            except Exception:
                db.session.rollback()
            return redirect(url_for("main.main_backend"))

    if request.args.get("logout") == "True":
        # Logs a user out. (You do not need to pass the actual user.)
        # This will also clean up the remember me
        # bug:AttributeError: 'AnonymousUserMixin' object has no attribute 'user'
        # By default, when a user is not actually logged in,
        # current_user is set to an AnonymousUserMixin object.
        logout_user()
        return redirect(url_for("main.main_login"))
    return render_template("backend.html", database = database, archive=archive)