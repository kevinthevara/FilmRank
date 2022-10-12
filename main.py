from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc, desc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)



api_key= 'API_KEY'

app.config['SECRET_KEY'] = 'SECRET_KEY'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'

url = 'https://api.themoviedb.org/3/movie'

db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String, unique=True, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String, nullable=True)
    img_url = db.Column(db.String, unique=True, nullable=False)

db.create_all()


class EditForm(FlaskForm):
    rating = FloatField('Your rating out of 10: ', validators=[DataRequired()])
    review = StringField('Your review: ', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddForm(FlaskForm):
    title = StringField('Movie title: ', validators=[DataRequired()])
    submit = SubmitField('Add Movie')

db.create_all()
session = db.session
Bootstrap(app)


@app.route("/")
def home():
    movies = Movie.query.order_by(Movie.rating).all()
    leng = len(movies)
    for item in movies:
        item.ranking = leng
        leng -= 1

    return render_template("index.html",  movies=movies)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    id = request.args['id']
    movie_to_update = Movie.query.get(id)
    form = EditForm()

    if form.validate_on_submit():
        movie_to_update.rating = form.rating.data
        movie_to_update.review = form.review.data
        session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie_to_update=movie_to_update, form=form)

@app.route('/delete', methods=['GET', 'POST'])
def delete():
    id = request.args['id']
    movie_to_update = Movie.query.get(id)
    session.delete(movie_to_update)
    session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        params = {
            'page': 1,
            'language': 'en-US',
            'api_key': f'{api_key}',
            'query': form.title.data
        }
        movie_db = requests.get(url="https://api.themoviedb.org/3/search/movie", params=params)
        list_of_movies = movie_db.json()
        print(list_of_movies)
        return render_template('select.html', list_of_movies=list_of_movies)
    return render_template('add.html', form=form)

@app.route('/select', methods=['GET', 'POST'])
def select():
    id = request.args['id']

    params = {
        'api_key': api_key,
        'language': 'en-US'
    }

    new_url = f"{url}/{id}"
    movie = requests.get(url=new_url, params=params)
    movie_info = movie.json()

    print(movie_info)

    title = movie_info['original_title']

    img_url = f"https://www.themoviedb.org/t/p/w300{movie_info['poster_path']}"

    year = movie_info['release_date'].split('-')[0]

    description = movie_info['overview']

    movie_to_update = Movie(title=title, year=year, description=description, rating=None, ranking=None, review=None, img_url=img_url)
    db.session.add(movie_to_update)
    db.session.commit()

    return redirect(url_for('edit', id=movie_to_update.id))

if __name__ == '__main__':
    app.run(debug=True)
