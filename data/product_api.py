from flask import Blueprint, render_template, abort, redirect, request, make_response, url_for
from jinja2 import TemplateNotFound
import os
from . import db_session
from .category import Category
from forms.search import SearchForm
from forms.comment import CommentForm
from .requests import Requests
from .products import Products
from .shops import Shops
from .colors import Colors
from .comments import Comments
from .users import Users
from .baskets import Baskets
from flask_login import current_user, login_required


blueprint = Blueprint(
    'product_api',
    __name__,
    template_folder='templates'
)
db_session.global_init(f"db/penguins.db")
db_sess = db_session.create_session()
translate = {'clothes': 'одежда', 'shoes': 'обувь', 'house': 'дом', 'accessories': 'аксессуары',}


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
                               shops=shops, Colors=Colors, Shops=Shops,
                               current_user=current_user)
    except TemplateNotFound:
        abort(404)


@blueprint.route('/product/<int:id>', methods=["GET", "POST"])
def product(id):
    colors = db_sess.query(Colors)
    categories = db_sess.query(Category)
    shops = db_sess.query(Shops)
    product = db_sess.query(Products).filter(Products.id == id).first()
    comments = db_sess.query(Comments).filter(Comments.product_id == id).all()
    users = db_sess.query(Users)
    db_sess.commit()
    if current_user.is_authenticated:
        flag = current_user.id in list(map(lambda x: users.filter(Users.id == x.author).first().id, comments))
    else:
        flag = True
    if request.method == "POST":
        if current_user.is_authenticated:
            product.count += 1
            basket = db_sess.query(Baskets).filter(Baskets.id == current_user.basket_id).first()
            prod = basket.products.split(', ') if basket.products else []
            prod.append(request.form['hidden'])
            basket.products = ', '.join(prod)
            db_sess.commit()
    return render_template('product.html', title=product.title.capitalize(),
                           product=product, categories=categories, shops=shops,
                           colors=colors, Category=Category, Shops=Shops, Colors=Colors,
                           comments=comments, Comments=Comments, users=users, Users=Users,
                           current_user=current_user, flag=flag)


@blueprint.route('/basket', methods=['GET', 'POST'])
@login_required
def basket():
    basket = db_sess.query(Baskets).filter(Baskets.id == current_user.basket_id).first()
    if request.method == 'POST':
        prod = basket.products.split(', ')
        prod.remove(str(request.form['hidden']))
        basket.products = ', '.join(prod)
        db_sess.commit()
        return redirect('/basket')
    basket = db_sess.query(Baskets).filter(Baskets.id == current_user.basket_id).first()
    products = []
    if basket.products:
        for i in basket.products.split(', '):
            products.append(db_sess.query(Products).filter(Products.id == int(i)).first())
    colors = db_sess.query(Colors)
    shops = db_sess.query(Shops)
    category = db_sess.query(Category)
    return render_template('basket.html', title='Корзина', products=products, Products=Products,
                           colors=colors, Colors=Colors, basket=basket,
                           shops=shops, Shops=Shops, category=category, Category=Category,
                           current_user=current_user)


@blueprint.route('/comment/<int:id>',  methods=['GET', 'POST'])
@login_required
def add_comment(id):
    form = CommentForm()
    product = db_sess.query(Products).filter(Products.id == id).first()
    if form.validate_on_submit():
        comment = Comments()
        comment.rating = form.rating.data
        comment.text = form.text.data
        comment.author = current_user.id
        comment.product_id = id
        f = request.files['image']
        if f:
            with open(os.path.abspath(os.path.join(os.path.dirname('static/img'), 'img', f.filename)), 'wb') as file:
                file.write(f.read())
            comment.image = f'../static/img/{f.filename}'
        db_sess.add(comment)
        db_sess.commit()
        comments = db_sess.query(Comments).filter(Comments.product_id == id).all()
        product.rating = round((product.rating + int(form.rating.data)) / len(comments), 1)
        product.comments.append(comment)
        db_sess.commit()
        return redirect(f'/product/{id}')
    return render_template('comment.html', title='Добавление комментария',
                           form=form, current_user=current_user, product=product)


@blueprint.route('/chemistry/<int:id>')
@blueprint.route('/cat/<int:id>')
def premium(id):
    return redirect(f'/product/{id}')


@blueprint.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    basket = db_sess.query(Baskets).filter(Baskets.id == current_user.basket_id).first()
    if not basket.products:
        return redirect('/basket')
    products = db_sess.query(Products).filter(Products.id.in_(list(map(int, basket.products.split(', '))))).all()
    summ = sum(map(lambda x: x.price, products))
    if request.method == 'POST':
        basket.products = ''
        db_sess.commit()
        return render_template('buy.html', title='Оплата', current_user=current_user,
                               message='Покупка оплачена. Ждите доставку в ближайшие 10-20 лет')
    return render_template('buy.html', title='Оплата', current_user=current_user, sum=summ)