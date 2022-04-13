from flask import Flask, render_template, redirect, request
from forms.search import SearchForm
from data import db_session
from data.products import Products
from data.shops import Shops
from data.category import Category
from data.colors import Colors
from data.requests import Requests
from data.product_api import blueprint


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.register_blueprint(blueprint)
db_session.global_init(f"db/penguins.db")
db_sess = db_session.create_session()


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
    return render_template('home.html', title='Главная страница', form=form)


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
                           params=params)


if __name__ == '__main__':
    main()