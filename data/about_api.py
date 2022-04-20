from flask import Blueprint, render_template, abort, redirect, request, make_response, url_for
from jinja2 import TemplateNotFound
import os
from . import db_session
from forms.question import QuestionForm
from .email import generate_email
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


about_api = Blueprint(
    'about_api',
    __name__,
    template_folder='templates'
)
db_session.global_init(f"db/penguins.db")
db_sess = db_session.create_session()


@about_api.route('/contacts')
def contacts():
    return render_template('contacts.html', current_user=current_user, title='Контакты')


@about_api.route('/developers')
def developers():
    return render_template('developers.html', current_user=current_user, title='Разработчики')


@about_api.route('/help')
def help():
    return render_template('help.html', current_user=current_user, title='Помощь')


@about_api.route('/question', methods=['GET', 'POST'])
def question():
    form = QuestionForm()
    if form.validate_on_submit():
        generate_email('', 'dashanov535@mail.ru', text=form.text.data + f'\nОтправлено пользователем {form.email.data}')
        return render_template('question.html', title='Задать вопрос', current_user=current_user, form=form,
                               message='Вопрос отправлен')
    return render_template('question.html', title='Задать вопрос', current_user=current_user, form=form)