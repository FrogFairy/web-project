from flask import Flask, render_template
from forms.search import SearchForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'very_secret_key'
# app.register_blueprint(jobs_api.blueprint)


def main():
    app.run(port=8080, host='127.0.0.1')


@app.route('/')
def home():
    form = SearchForm()
    if form.validate_on_submit():
        return render_template('result.html', title='Результаты поиска', form=form)
    return render_template('home.html', title='Главная страница', form=form)


if __name__ == '__main__':
    main()