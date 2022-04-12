from flask import Blueprint, render_template, abort, redirect, request
from jinja2 import TemplateNotFound
from . import db_session
from .category import Category
from forms.search import SearchForm
from .requests import Requests
from .products import Products
from .shops import Shops
from .colors import Colors


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