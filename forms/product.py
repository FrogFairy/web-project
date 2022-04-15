from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, IntegerField
from wtforms import SubmitField, FileField, SelectField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    category = SelectField('Категория', choices=['одежда', 'обувь', 'дом', 'аксессуары'], validators=[DataRequired()])
    color = SelectField('Цвет', choices=['голубой', 'оранжевый', 'желтый', 'красный',
                                         'коричневый', 'черный', 'белый', 'синий', 'фиолетовый', 'серый'],
                        validators=[DataRequired()])
    price = IntegerField('Цена (в рублях)', validators=[DataRequired()])
    about = TextAreaField('Описание', validators=[DataRequired()])
    image = FileField('Фотография')
    submit = SubmitField('Применить')