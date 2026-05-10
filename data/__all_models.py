import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Excuse(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'excuses'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    likes= sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    dislikes= sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    is_prime = sqlalchemy.Column(sqlalchemy.Boolean,nullable=False, default=False)

