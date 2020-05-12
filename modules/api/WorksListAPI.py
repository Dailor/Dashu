from flask_restful import Resource
from flask import jsonify
from data.work import WorkList
from data.users import User
from data import db_session


class WorkListAPI(Resource):
    def get(self):
        session = db_session.create_session()
        works_list = session.query(WorkList).all()
        return jsonify({'works_list': [item.to_dict(
            only=("id",
                  "work_id",
                  "worker_id",
                  "work_result_message",
                  "status",
                  "work_start",
                  "work_end",
                  "director_id")) for item in works_list]})
