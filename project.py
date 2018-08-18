#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Genre, Movie
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Movie Catalog App"


# Connect to Database and create database session
engine = create_engine('sqlite:///moviecatalog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# GConnect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        # response = make_response(
        # json.dumps('Successfully disconnected.'), 200)
        # response.headers['Content-Type'] = 'application/json'
        response = redirect(url_for('showGenres'))
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON Endpoints
@app.route('/genres/JSON')
def genresJSON():
    genres = session.query(Genre).all()
    return jsonify(Genres=[g.serialize for g in genres])


@app.route('/genres/<int:genre_id>/movies/JSON')
def moviesJSON(genre_id):
    genre = session.query(Genre).filter_by(id=genre_id).one()
    movies = session.query(Movie).filter_by(genre_id=genre_id).all()
    return jsonify(Movies=[m.serialize for m in movies])


@app.route('/genres/<int:genre_id>/movies/<int:movie_id>/JSON')
def movieJSON(genre_id, movie_id):
    movie = session.query(Movie).filter_by(id=movie_id).one()
    return jsonify(Movie=movie.serialize)


# Show all genres
@app.route('/')
@app.route('/genres/')
def showGenres():
    genres = session.query(Genre).all()
    movies = session.query(Movie).all()
    return render_template('genres.html', genres=genres, movies=movies)


# Create a new genre
@app.route('/genres/new/', methods=['GET', 'POST'])
def newGenre():
    if 'username' not in login_session:
        return redirect('/login')
    genres = session.query(Genre).all()
    if request.method == 'POST':
        newGenre = Genre(name=request.form['name'],
                         user_id=login_session['user_id'])
        session.add(newGenre)
        session.commit()
        return redirect(url_for('showGenres'))
    else:
        return render_template('newGenre.html', genres=genres)


# Edit a genre
@app.route('/genres/<int:genre_id>/edit/', methods=['GET', 'POST'])
def editGenre(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genres = session.query(Genre).all()
    editedGenre = session.query(Genre).filter_by(id=genre_id).one()
    if editedGenre.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        if request.form['name']:
            editedGenre.name = request.form['name']
            return redirect(url_for('showGenres'))
    else:
        return render_template('editGenre.html', genres=genres,
                               genre=editedGenre)


# Delete a genre
@app.route('/genres/<int:genre_id>/delete/', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genres = session.query(Genre).all()
    genreToDelete = session.query(Genre).filter_by(id=genre_id).one()
    moviesInGenre = session.query(Movie).filter_by(genre_id=genre_id).all()
    if genreToDelete.user_id != login_session['user_id']:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        for movie in moviesInGenre:
            session.delete(movie)
        session.delete(genreToDelete)
        session.commit()
        return redirect(url_for('showGenres'))
    else:
        return render_template('deleteGenre.html', genres=genres,
                               genre=genreToDelete)


# Show movies
@app.route('/genres/<int:genre_id>/')
@app.route('/genres/<int:genre_id>/movies/')
def showMovies(genre_id):
    genres = session.query(Genre).all()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    movies = session.query(Movie).filter_by(genre_id=genre_id).all()
    return render_template('movies.html', genre=genre, genres=genres,
                           movies=movies)


# Display Movie Info
@app.route('/genres/<int:genre_id>/movies/<int:movie_id>/')
def movieInfo(genre_id, movie_id):
    genres = session.query(Genre).all()
    movie = session.query(Movie).filter_by(id=movie_id).one()
    return render_template('movieInfo.html', genres=genres, movie=movie)


# Add a new movie
@app.route('/genres/<int:genre_id>/movies/new/', methods=['GET', 'POST'])
def newMovie(genre_id):
    if 'username' not in login_session:
        return redirect('/login')
    genres = session.query(Genre).all()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if login_session['user_id'] != genre.user_id:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        newMovie = Movie(name=request.form['name'],
                         poster=request.form['poster'],
                         director=request.form['director'],
                         description=request.form['description'],
                         genre_id=genre_id, user_id=genre.user_id)
        session.add(newMovie)
        session.commit()
        return redirect(url_for('showMovies', genre_id=genre_id))
    else:
        return render_template('newMovie.html', genres=genres,
                               genre_id=genre_id)


# Edit a movie
@app.route('/genres/<int:genre_id>/movies/<int:movie_id>/edit/',
           methods=['GET', 'POST'])
def editMovie(genre_id, movie_id):
    if 'username' not in login_session:
        return redirect('/login')
    genres = session.query(Genre).all()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    editedMovie = session.query(Movie).filter_by(id=movie_id).one()
    if login_session['user_id'] != genre.user_id:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        if request.form['name']:
            editedMovie.name = request.form['name']
        if request.form['poster']:
            editedMovie.poster = request.form['poster']
        if request.form['director']:
            editedMovie.director = request.form['director']
        if request.form['description']:
            editedMovie.description = request.form['description']
        session.add(editedMovie)
        session.commit()
        return redirect(url_for('showMovies', genre_id=genre_id))
    else:
        return render_template('editMovie.html', genres=genres,
                               genre_id=genre_id, movie_id=movie_id,
                               movie=editedMovie)


# Delete a movie
@app.route('/genres/<int:genre_id>/movies/<int:movie_id>/delete/',
           methods=['GET', 'POST'])
def deleteMovie(genre_id, movie_id):
    if 'username' not in login_session:
        return redirect('/login')
    genres = session.query(Genre).all()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    movieToDelete = session.query(Movie).filter_by(id=movie_id).one()
    if login_session['user_id'] != genre.user_id:
        return "<script>{alert('Unauthorized');}</script>"
    if request.method == 'POST':
        session.delete(movieToDelete)
        session.commit()
        return redirect(url_for('showMovies', genre_id=genre_id))
    else:
        return render_template('deleteMovie.html', genres=genres,
                               movie=movieToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
