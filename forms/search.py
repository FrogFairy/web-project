<<<<<<< HEAD
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    request = StringField("Я ищу...", validators=[DataRequired()])
=======
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    request = StringField("Я ищу...", validators=[DataRequired()])
>>>>>>> 4ebbabcdd4f3a43add42109c89773780f5bbf83a
    submit = SubmitField("Поиск")