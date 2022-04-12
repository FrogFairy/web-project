import sqlalchemy
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


association_table = sqlalchemy.Table(
    'products_to_category',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('products', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('products.id')),
    sqlalchemy.Column('category', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('category.id'))
)


class Category(SqlAlchemyBase, UserMixin):
    __tablename__ = 'category'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)