import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


association_table = sqlalchemy.Table(
    'products_to_colors',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('products', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('products.id')),
    sqlalchemy.Column('colors', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('colors.id'))
)


class Colors(SqlAlchemyBase, UserMixin):
    __tablename__ = 'colors'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)