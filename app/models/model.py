# coding=utf-8

from app.models import db
from datetime import datetime
from uuid import uuid1
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql.expression import text, desc
from itertools import chain
from random import shuffle
from bs4 import BeautifulSoup


def _get_uid():
    return uuid1().__str__()


def _get_now():
    return datetime.now()


def sanitize_html(value):
    soup = BeautifulSoup(value, "html.parser")
    for tag in soup.findAll(True):
        tag.hidden = True
    soup = unicode(soup)
    return soup


# if you want use db.create_all()
# import all db models after import db from app
class qanda(db.Model):
    __tablename__ = "qanda"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    category = db.Column(db.String(50))
    uuid = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    answer = db.Column(db.String(200), nullable=False)
    add_time = db.Column(db.DATETIME)

    def __init__(self, form):
        self.category = form.get("category", None)
        self.uuid = _get_uid()
        self.title = form.get("title", None)
        self.content = form.get("content", None)
        self.answer = form.get("answer", None)
        self.add_time = _get_now()

    @classmethod
    def categories(cls):
        sql = text('''
        SELECT category FROM (SELECT * FROM qanda GROUP BY category);
        ''')

        rv = db.session.execute(sql).fetchall()
        return rv

    @classmethod
    def query_uid(cls, uid):
        """
        query database by uuid
        """
        sql = text("""
        SELECT title, content, answer FROM qanda WHERE uuid = :c;
        """)

        rv = db.session.execute(sql, params={"c": uid}).fetchone()
        rv_json = {
            'title': rv[0], 'content': rv[1], 'answer': rv[2]
        }

        return rv_json

    @classmethod
    def query_id(cls, category):
        """
        generate database id filter by categorys
        """
        if category == 'all':
            sql = text("""
            SELECT id FROM qanda;
            """)

            rv = db.session.execute(sql).fetchall()
            id_list = list(chain(*rv))
            # shuffle the list like random sampling
            shuffle(id_list)

            rv_json = {"query_id": id_list}
            return rv_json
        else:
            sql = text("""
            SELECT id FROM qanda WHERE category = :a;
            """)

            rv = db.session.execute(sql, params={"a": category}).fetchall()
            id_list = list(chain(*rv))
            # shuffle the list like random sampling
            shuffle(id_list)

            rv_json = {"query_id": id_list}
            return rv_json

    @classmethod
    def query_content(cls, qid):
        """
        query question & answer from database by query id(qid)
        """
        sql = text("""
        SELECT id, category, uuid, title, content, answer FROM qanda WHERE id = :b;
        """)

        rv = db.session.execute(sql, params={"b": qid}).fetchone()

        rv_json = {
            "content": {
                "id": rv[0], "category": rv[1], 'uuid': rv[2], 'title': rv[3], 'content': rv[4], 'answer': rv[5]
            }
        }
        return rv_json

    @classmethod
    def archive(cls):
        rv = {}

        for _categories in cls.categories():
            # print _categories[0]
            a = cls.query.filter(cls.category == _categories[0]).order_by(desc(cls.add_time)).all()
            b = []

            for _a in a:
                # print _a.title
                b.append(tuple((sanitize_html(_a.title), _a.uuid)))

            rv.update({_categories[0]: b})
        return rv


class login(db.Model, UserMixin):
    __tablename__ = "login"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    user = db.Column(db.String(50), nullable=False)
    nickname = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    def __init__(self, user=None, nickname=None, pwd=None):
        self.user = user
        self.nickname = nickname
        self.password_hash = generate_password_hash(pwd, method="pbkdf2:sha1", salt_length=16)

    @property
    def password(self):
        raise AttributeError("You Can't Read the Original Password!")

    @password.setter
    def password(self, pwd=None):
        self.password_hash = generate_password_hash(pwd, method="pbkdf2:sha1", salt_length=16)

    def verify_password(self, pwd=None):
        if pwd is None:
            return False
        return check_password_hash(self.password_hash, pwd)

    def is_authenticated(self):
        return False

    def is_active(self):
        # flask_login.login_user(user, remember=False, force=False, fresh=True)[source]
        # Logs a user in. You should pass the actual user object to this.
        # If the user’s is_active property is False, they will not be logged in unless force is True.
        return False

    def is_anonymous(self):
        return False

    def get_id(self):
        """
        get user id from profile file, if not exist, it will
        generate a uuid for the user.
        :return:unicode
        """
        if self.user is not None:
            return unicode(self.id)
        return unicode(uuid1())

    @staticmethod
    def get(user_id):
        """
        try to return user_id corresponding User object.
        This method is used by load_user callback function
        :param user_id:
        :return:Login class
        """
        if not user_id:
            return None
        else:
            lg = login.query.filter(login.id == user_id).one()
            return lg
