from flask import Blueprint, render_template, abort, redirect, request, make_response
from jinja2 import TemplateNotFound
from . import db_session
from .category import Category
from forms.search import SearchForm
from .requests import Requests
from .products import Products
from .shops import Shops
from .colors import Colors
from .comments import Comments
from .users import Users
from .baskets import Baskets
from flask_login import LoginManager, current_user


blueprint = Blueprint(
    'category_api',
    __name__,
    template_folder='templates'
)
db_session.global_init(f"db/penguins.db")
db_sess = db_session.create_session()
translate = {'clothes': 'одежда', 'shoes': 'обувь', 'house': 'дом', 'accessories': 'аксессуары'}


@blueprint.route('/<title>', defaults={'req': ''}, methods=['GET', 'POST'])
@blueprint.route('/<title>/<int:req>', methods=['GET', 'POST'])
def page(title, req):
    try:
        if req:
            req = db_sess.query(Requests).filter(Requests.id == req).first()
            form = SearchForm(request=req.title)
            products = db_sess.query(Products).filter(Products.title.like(f"%{req.title.lower()}%"))
        else:
            products = db_sess.query(Products)
            form = SearchForm()
        colors = db_sess.query(Colors)
        category = db_sess.query(Category).filter(Category.name == translate[title]).first()
        shops = db_sess.query(Shops)
        if request.method == "POST":
            color = ', '.join(i for i in request.form.getlist('color'))
            sort = request.form["sort"]
            req = Requests(title=form.request.data, color=color, category=translate[title], sort=sort)
            db_sess.add(req)
            db_sess.commit()
            if form.validate_on_submit():
                return redirect(f'/{title}/{req.id}')
        products = products.filter(Products.category == category.id)
        if req:
            if req.color:
                products = products.filter(
                    Products.color.in_([colors.filter(Colors.name == i).first().id for i in req.color.split(', ')]))
            if products:
                if req.sort == "По популярности":
                    products = products.order_by(Products.count)
                elif req.sort == "По рейтингу":
                    products = products.order_by(Products.rating)[::-1]
                elif req.sort == "По увеличению цены":
                    products = products.order_by(Products.price)
                elif req.sort == "По уменьшению цены":
                    products = products.order_by(Products.price)[::-1]
            params = {'color': req.color.split(', '), 'sort': req.sort}
        else:
            params = {'color': '', 'sort': 'По умолчанию'}
        return render_template('category.html', title=translate[title].capitalize(),
                               category=category.name, form=form, params=params,
                               colors=colors, products=products,
                               shops=shops, Colors=Colors, Shops=Shops)
    except TemplateNotFound:
        abort(404)


@blueprint.route('/product/<int:id>', methods=["GET", "POST"])
def product(id):
    visits_count = int(request.cookies.get("visits_count", 0))
    res = make_response()
    res.set_cookie("visits_count", str(visits_count + 1),
                   max_age=60 * 60 * 24 * 365 * 2)
    colors = db_sess.query(Colors)
    categories = db_sess.query(Category)
    shops = db_sess.query(Shops)
    product = db_sess.query(Products).filter(Products.id == id).first()
    comments = db_sess.query(Comments).filter(Comments.product_id == id).all()
    users = db_sess.query(Users)
    product.count += 1
    db_sess.commit()
    if request.method == "POST":
        # код для отправки товара в корзину
        pass
    return render_template('product.html', title=product.title.capitalize(),
                           product=product, categories=categories, shops=shops,
                           colors=colors, Category=Category, Shops=Shops, Colors=Colors,
                           comments=comments, Comments=Comments, users=users, Users=Users)


@blueprint.route('/basket', methods=['GET', 'POST'])
def basket():
    basket = db_sess.query(Baskets).filter(Baskets.id == 1).first()
    if request.method == 'POST':
        prod = basket.products.split(', ')
        prod.remove(str(request.form['hidden']))
        basket.products = ', '.join(prod)
        db_sess.commit()
    basket = db_sess.query(Baskets).filter(Baskets.id == 1).first()
    products = db_sess.query(Products).filter(Products.id.in_(basket.products.split(', '))).all()
    colors = db_sess.query(Colors)
    shops = db_sess.query(Shops)
    category = db_sess.query(Category)
    return render_template('basket.html', title='Корзина', products=products,
                           colors=colors, Colors=Colors,
                           shops=shops, Shops=Shops, category=category, Category=Category)