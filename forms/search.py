from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    request = StringField("Я ищу...", validators=[DataRequired()])
    submit = SubmitField("Поиск", validators=[DataRequired()])