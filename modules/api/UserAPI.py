from flask_restful import Resource
from flask import jsonify
from data.work import WorkList
from data.users import User
from data import db_session


class UsersList(Resource):
    def get(self):
        session = db_session.create_session()
        users_list = session.query(User).all()
        return jsonify({'works_list': [item.to_dict(
            only=("id",
                  "account_type",
                  "user_name",
                  "surname",
                  "name",
                  "birthday",
                  "email",
                  "about_me")) for item in users_list]})
