from flask import Blueprint, render_template, abort, redirect, request, make_response, url_for
import os
from . import db_session
from .category import Category
from forms.product import ProductForm
from .products import Products
from .shops import Shops
from .colors import Colors
from .users import Users
from data.email import generate_email
from flask_login import current_user, login_required
from datetime import date


user_api = Blueprint(
    'user_api',
    __name__,
    template_folder='templates'
)
db_session.global_init(f"db/penguins.db")
db_sess = db_session.create_session()


@user_api.route('/my', methods=['GET', 'POST'])
@login_required
def my():
    user = db_sess.query(Users).filter(Users.id == current_user.id).first()
    now = date.today()
    age = now - user.birthday
    if request.method == 'POST':
        if request.form['hidden'] == 'update':
            if current_user.check_password(request.form['password']):
                user.name = request.form['name']
                user.surname = request.form['surname']
                birthday = request.form['birthday'].split('-')
                user.birthday = date(year=int(birthday[0]), month=int(birthday[1]), day=int(birthday[2]))
                if user.email != request.form['email']:
                    if db_sess.query(Users).filter(Users.email == request.form['email']).first():
                        return render_template('my.html', title='Личный кабинет', user=current_user,
                                               message='Пользователь с такой почтой уже существует!', age=age)
                    generate_email(request.form['name'], request.form['email'], url_for('confirmed', _external=True))
                    user.email = request.form['email']
                db_sess.commit()
                return redirect('/my')
            return render_template('my.html', title='Личный кабинет', user=current_user,
                                   message='Неверный пароль!', age=age)
        shop = db_sess.query(Shops).filter(Shops.id == request.form['hidden']).first()
        user.shops.remove(shop)
        db_sess.delete(shop)
        db_sess.commit()
        return redirect('/my')
    return render_template('my.html', title='Личный кабинет', user=current_user, age=age)


@user_api.route('/add_shop', methods=['GET', 'POST'])
@login_required
def add_shop():
    if request.method == 'POST':
        if db_sess.query(Shops).filter(Shops.title == request.form['title']).first() or \
                db_sess.query(Shops).filter(Shops.email == request.form['email']).first():
            return render_template('add_shop.html', title='Создание магазина', user=current_user,
                                   message='Магазин с таким названием/почтой уже существует!')
        shop = Shops(title=request.form['title'],
                     email=request.form['email'],
                     user=current_user.id)
        db_sess.add(shop)
        db_sess.commit()
        user = db_sess.query(Users).filter(Users.id == current_user.id).first()
        user.shops.append(shop)
        db_sess.commit()
        return redirect('/my')
    return render_template('add_shop.html', title='Создание магазина', user=current_user)


@user_api.route('/shop/<int:id>', methods=['GET', 'POST'])
@login_required
def shop(id):
    shop = db_sess.query(Shops).filter(Shops.id == id).first()
    category = db_sess.query(Category)
    colors = db_sess.query(Colors)
    if request.method == 'POST':
        if request.form['hidden'].startswith('update'):
            return redirect(f'/add_product/{id}-{int(request.form["hidden"].split()[1])}')
        product = db_sess.query(Products).filter(Products.id == request.form['hidden']).first()
        shop.products.remove(product)
        db_sess.delete(product)
        db_sess.commit()
        return redirect(f'/shop/{id}')
    return render_template('shop.html', title=f'Магазин {shop.title}', current_user=current_user,
                           shop=shop, category=category, colors=colors, Category=Category, Colors=Colors)


@user_api.route('/add_product/<int:id>-<int:id_prod>', methods=['GET', 'POST'])
@user_api.route('/add_product/<int:id>', methods=['GET', 'POST'], defaults={'id_prod': -1})
@login_required
def add_product(id, id_prod):
    form = ProductForm()
    shop = db_sess.query(Shops).filter(Shops.id == id).first()
    category = db_sess.query(Category)
    colors = db_sess.query(Colors)
    if id_prod == -1:
        title = 'Добавление товара'
        product = Products()
        db_sess.commit()
    else:
        title = 'Редактирование товара'
        product = db_sess.query(Products).filter(Products.id == id_prod).first()
    if form.validate_on_submit():
        category = category.filter(Category.name == form.category.data).first()
        color = colors.filter(Colors.name == form.color.data).first()
        product.title = form.title.data.lower()
        product.category = category.id
        product.color = color.id
        product.shop = id
        product.price = form.price.data
        product.about = form.about.data
        product.rating, product.count = 0, 0
        if form.image.data.filename:
            f = form.image.data
            with open(os.path.abspath(os.path.join(os.path.dirname('static/img'), 'img', f.filename)), 'wb') as file:
                file.write(f.read())
            product.image = f'../static/img/{f.filename}'
        else:
            product.image = '../static/img/none.png'
        db_sess.add(product)
        db_sess.commit()
        shop.products.append(product)
        db_sess.commit()
        return redirect(f'/shop/{id}')
    return render_template('add_product.html', title=title,
                           form=form, current_user=current_user, product=product,
                           colors=colors, category=category,
                           Colors=Colors, Category=Category)