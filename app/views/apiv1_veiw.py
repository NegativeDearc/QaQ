from app.models.model import db, qanda
from flask_restful import Resource
from flask import request


class MainContent(Resource):
    def get(self):
        if request.args.get("qid"):
            qid = request.args.get("qid")
        else:
            return {'error': 'query content failed'}
        return qanda.query_content(qid=qid)

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass


class QueryId(Resource):
    def get(self):
        if request.args.get("category"):
            category = request.args.get("category")
        else:
            category = 'all'
        return qanda.query_id(category=category)

    def post(self):
        if request.form.get("category"):
            category = request.form.get("category")
        else:
            category = 'all'
        return qanda.query_id(category=category)

    def put(self):
        pass

    def delete(self):
        pass