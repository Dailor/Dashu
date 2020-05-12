import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    account_type = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('accounts_type.id'))

    user_name = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    birthday = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False)

    photo = sqlalchemy.Column(sqlalchemy.BLOB)

    email = sqlalchemy.Column(sqlalchemy.String, unique=True)

    about_me = sqlalchemy.Column(sqlalchemy.String, nullable=True)



    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_full_name(self):
        return f"{self.surname} {self.name}"


class Worker(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'workers'

    worker_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), primary_key=True)
    director_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('directors.director_id'), nullable=True)

    payment = sqlalchemy.Column(sqlalchemy.Integer)
    status = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('worker_status.id'))

    user = orm.relation('User')
    works = orm.relation('Work', secondary='work_to_worker', backref='work_id')
    works_list = orm.relation('WorkList', secondary='work_list_to_worker', backref='worker')
    director = orm.relation('Director')


class Director(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'directors'

    director_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), primary_key=True)

    companies = orm.relation('Work', back_populates='director')
    workers = orm.relation('Worker', back_populates='director')

    user = orm.relation('User')
