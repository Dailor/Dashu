import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import datetime

work_to_worker = sqlalchemy.Table(
    "work_to_worker", SqlAlchemyBase.metadata,
    sqlalchemy.Column('work_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('works.id')),
    sqlalchemy.Column('worker_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('workers.worker_id'))
)

work_list_to_worker = sqlalchemy.Table(
    "work_list_to_worker", SqlAlchemyBase.metadata,
    sqlalchemy.Column('work_list_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('works_list.id')),
    sqlalchemy.Column('worker', sqlalchemy.Integer, sqlalchemy.ForeignKey('workers.worker_id'))
)

work_list_to_work = sqlalchemy.Table(
    "work_list_to_work", SqlAlchemyBase.metadata,
    sqlalchemy.Column('work_list_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('works_list.id')),
    sqlalchemy.Column('work', sqlalchemy.Integer, sqlalchemy.ForeignKey('works.id'))
)


class Work(SqlAlchemyBase):
    __tablename__ = 'works'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    work = sqlalchemy.Column(sqlalchemy.String, unique=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    director_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('directors.director_id'))

    director = orm.relation("Director")
    # worker = orm.relation('Worker', secondary='work_to_worker', backref='worker_id')
    works_list = orm.relation('WorkList', secondary='work_list_to_work', backref='work')


class WorkList(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'works_list'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    work_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('works.id'), nullable=False)
    worker_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('workers.worker_id'), nullable=False)

    work_result_message = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    work_results_file = sqlalchemy.Column(sqlalchemy.BLOB, nullable=True)
    work_result_filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    status = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('work_status.id'), nullable=False, default=2)
    work_start = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now, nullable=True)
    work_end = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)

    director_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("directors.director_id"), nullable=False)

    work_url = orm.relation("Work")
    worker_url = orm.relation("Worker")
