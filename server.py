from flask import Flask, render_template, redirect
from forms.search import SearchForm


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# app.register_blueprint(jobs_api.blueprint)


def main():
    app.run(port=8080, host='127.0.0.1')


@app.route('/', methods=['GET', 'POST'])
def home():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect('/result')
    return render_template('home.html', title='Главная страница', form=form)


@app.route('/result')
def result():
    return render_template('result.html', title='Результаты поиска')


if __name__ == '__main__':
    main()