from flask import Flask, request, jsonify, render_template
from pony.orm import Database, Required, PrimaryKey, db_session, select, count
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # enabling CORS

# Connect to a SQLite database file
db = Database()
db.bind(provider='sqlite', filename='database.sqlite', create_db=True)

class Movie(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    director = Required(str)
    release_year = Required(int)
    genre = Required(str)
    synopsis = Required(str)

# Generate the database table if it doesn't exist
db.generate_mapping(create_tables=True)

@app.route('/movie', methods=['POST'])
@db_session
def add_movie():
    data = request.get_json()
    movie = Movie(
        title=data['title'],
        director=data['director'],
        release_year=data['release_year'],
        genre=data['genre'],
        synopsis=data['synopsis']
    )
    db.commit()  # commit the transaction
    return jsonify(success=True, id=movie.id)

@app.route('/movie/<int:movie_id>', methods=['GET'])
@db_session
def get_movie(movie_id):
    movie = Movie.get(id=movie_id)
    if movie is None:
        return {"error": "Movie not found"}, 404
    return jsonify(
        id=movie.id,
        title=movie.title,
        director=movie.director,
        release_year=movie.release_year,
        genre=movie.genre,
        synopsis=movie.synopsis
    )

@app.route('/movie/<int:movie_id>', methods=['PUT'])
@db_session
def update_movie(movie_id):
    movie = Movie.get(id=movie_id)
    if movie is None:
        return {"error": "Movie not found"}, 404
    data = request.get_json()
    movie.title = data.get('title', movie.title)
    movie.director = data.get('director', movie.director)
    movie.release_year = data.get('release_year', movie.release_year)
    movie.genre = data.get('genre', movie.genre)
    movie.synopsis = data.get('synopsis', movie.synopsis)
    return jsonify(success=True)

@app.route('/movie/<int:movie_id>', methods=['DELETE'])
@db_session
def delete_movie(movie_id):
    movie = Movie.get(id=movie_id)
    if movie is None:
        return {"error": "Movie not found"}, 404
    movie.delete()
    return jsonify(success=True)

@app.route('/movies', methods=['GET'])
@db_session
def get_movies():
    genre = request.args.get('genre')
    if genre:
        movies = select(m for m in Movie if m.genre == genre)[:]
    else:
        movies = select(m for m in Movie)[:]
    movies_list = [m.to_dict() for m in movies]
    return jsonify(movies_list)

@app.route('/genres', methods=['GET'])
@db_session
def get_genres():
    genres = select(m.genre for m in Movie).distinct()
    genres_list = [str(genre) for genre in genres]
    return jsonify(genres_list)


@app.route('/movies-per-genre', methods=['GET'])
@db_session
def get_movies_per_genre():
    movies_per_genre = {}
    genres = select(m.genre for m in Movie).distinct()
    for genre in genres:
        movie_count = count(m for m in Movie if m.genre == genre)
        movies_per_genre[genre] = movie_count
    return jsonify(movies_per_genre)


@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
