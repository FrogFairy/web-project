import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin


class Products(SqlAlchemyBase, UserMixin):
    __tablename__ = 'products'

    id = sqlalchemy.Column(sqlalchemy.Integer, 
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    category = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("category.id"))
    color = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("colors.id"), nullable=True)
    shop = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("shops.id"), nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    rating = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    count = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    image = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    shops = orm.relation('Shops', back_populates='products')
    categories = orm.relation("Category",
                              secondary="products_to_category",
                              backref="products")
    colors = orm.relation("Colors",
                          secondary="products_to_colors",
                          backref="products")
    comments = orm.relation('Comments', back_populates='products')