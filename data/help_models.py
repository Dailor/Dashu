from .db_session import SqlAlchemyBase
import sqlalchemy
from sqlalchemy import orm
import datetime


class AccountType(SqlAlchemyBase):
    __tablename__ = 'accounts_type'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)


class WorkStatus(SqlAlchemyBase):
    __tablename__ = 'work_status'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)


class WorkerStatus(SqlAlchemyBase):
    __tablename__ = 'worker_status'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)


class InviteStatus(SqlAlchemyBase):
    __tablename__ = 'invite_status'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)


class DirectorInvite(SqlAlchemyBase):
    __tablename__ = 'director_invite'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    director_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('directors.director_id'))
    worker_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('workers.worker_id'))

    status_invite = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('invite_status.id'), default=1)

    director = orm.relation('Director')


class ChatHistory(SqlAlchemyBase):
    __tablename__ = 'chat_history'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    msg = sqlalchemy.String(sqlalchemy.String)
    date_msg = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)


class Chats(SqlAlchemyBase):
    __tablename__ = "chats"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    first_member_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    second_member_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))

    chat_history_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('chat_history.id'))

    chat_history = orm.relation('ChatHistory')
