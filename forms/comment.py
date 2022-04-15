from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import SubmitField, FileField, SelectField
from wtforms.validators import DataRequired


class CommentForm(FlaskForm):
    rating = SelectField('Оценка', choices=[5, 4, 3, 2, 1], validators=[DataRequired()])
    text = TextAreaField("Комментарий")
    image = FileField("Фотографии")
    submit = SubmitField('Применить')