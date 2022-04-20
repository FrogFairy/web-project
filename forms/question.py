from flask_wtf import FlaskForm
from wtforms import SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired


class QuestionForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    text = TextAreaField("Вопрос", validators=[DataRequired()])
    submit = SubmitField('Отправить')