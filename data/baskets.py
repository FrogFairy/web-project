import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin


class Baskets(SqlAlchemyBase, UserMixin):
    __tablename__ = 'baskets'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    products = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    ordered = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    users = orm.relation('Users', back_populates='baskets')