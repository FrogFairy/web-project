from flask import Flask, render_template, redirect, request
from forms.search import SearchForm
from forms.login import LoginForm
from forms.register import RegisterForm
from data import db_session
from data.products import Products
from data.shops import Shops
from data.category import Category
from data.colors import Colors
from data.requests import Requests
from data.users import Users
from data.baskets import Baskets
from data.product_api import blueprint
from data.user_api import user_api
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from data.email import generate_email


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.register_blueprint(blueprint)
app.register_blueprint(user_api)
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init(f"db/penguins.db")
db_sess = db_session.create_session()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


def main():
    app.run(port=8080, host='127.0.0.1')


@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm()
    if form.validate_on_submit():
        req = Requests(title=form.request.data, color='', category='', sort='По умолчанию')
        db_sess.add(req)
        db_sess.commit()
        return redirect(f'/result/{req.id}')
    return render_template('home.html', title='Главная страница', form=form, current_user=current_user)


@app.route('/result/<int:req>', methods=['GET', 'POST'])
def result(req):
    req = db_sess.query(Requests).filter(Requests.id == req).first()
    form = SearchForm(request=req.title)
    products = db_sess.query(Products).filter(Products.title.like(f"%{req.title.lower()}%"))
    colors = db_sess.query(Colors)
    categories = db_sess.query(Category)
    shops = db_sess.query(Shops)
    if request.method == "POST":
        color = ', '.join(i for i in request.form.getlist('color'))
        category = ', '.join(i for i in request.form.getlist('category'))
        sort = request.form["sort"]
        req = Requests(title=form.request.data, color=color, category=category, sort=sort)
        db_sess.add(req)
        db_sess.commit()
        if form.validate_on_submit():
            return redirect(f'/result/{req.id}')
    if req.category:
        products = products.filter(Products.category.in_([categories.filter(Category.name == i).first().id for i in req.category.split(', ')]))
    if req.color:
        products = products.filter(Products.color.in_([colors.filter(Colors.name == i).first().id for i in req.color.split(', ')]))
    if products:
        if req.sort == "По популярности":
            products = products.order_by(Products.count)
        elif req.sort == "По рейтингу":
            products = products.order_by(Products.rating)[::-1]
        elif req.sort == "По увеличению цены":
            products = products.order_by(Products.price)
        elif req.sort == "По уменьшению цены":
            products = products.order_by(Products.price)[::-1]
    params = {'color': req.color.split(', '), 'category': req.category.split(', '), 'sort': req.sort}
    return render_template('result.html', title='Результаты поиска', form=form,
                           products=products, request=req, colors=colors,
                           categories=categories, shops=shops, Category=Category, Colors=Colors, Shops=Shops,
                           params=params, current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают", current_user=current_user)
        if db_sess.query(Users).filter(Users.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть", current_user=current_user)
        basket = Baskets()
        db_sess.add(basket)
        db_sess.commit()
        user = Users(
            name=form.name.data,
            surname=form.surname.data,
            birthday=form.birthday.data,
            email=form.email.data,
            basket_id=basket.id
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        generate_email(user.name, user.email)
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(Users).filter(Users.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form, current_user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/confirmed')
def confirmed():
    if current_user.is_authenticated:
        user = db_sess.query(Users).filter(Users.id == current_user.id).first()
        user.confirmed = True
        db_sess.commit()
        return redirect('/')
    return redirect('/login')


if __name__ == '__main__':
    main()