from . import app
from models import *
from flask import request, session, redirect, url_for, \
    abort, render_template, flash

@app.route('/')
def index():
    posts = get_global_recent_posts()
    return render_template('index.html', posts=posts)

@app.route('/register', methods=['GET','POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 1:
            error = 'Your username must be at least one character.'
        elif len(password) < 5:
            error = 'Your password must be at least 5 characters.'
        elif not User(username).set_password(password).register():
            error = 'A user with that username already exists.'
        else:
            flash('Successfully registered. Please login.')
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username)

        if not user.find():
            error = 'A user with that username does not exist.'
        elif not user.verify_password(password):
            error = 'That password is incorrect.'
        else:
            session['logged_in'] = True
            session['username'] = user.username
            flash('Logged in.')
            return redirect(url_for('profile', username=username))

    return render_template('login.html', error=error)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/like_post/<post_id>', methods=['GET'])
def like_post(post_id):
    user = User(session['username'])
    user.like_post(post_id)
    flash('Liked post.')
    return redirect(request.referrer)

@app.route('/profile/<username>', methods=['GET'])
def profile(username):
    posts = get_users_recent_posts(username)

    similar = []
    common = []

    if session['logged_in']:
        if session['username'] == username:
            similar = get_similar_users(session['username'])
        else:
            common = get_common_bw_two_users(username, session['username'])

    return render_template(
        'profile.html',
        username=username,
        posts=posts,
        similar=similar,
        common=common
    )

@app.route('/profile/<username>/add_post', methods=['POST'])
def add_post(username):
    user = User(session['username'])
    title = request.form['title']
    text = request.form['text']
    tags = request.form['tags']

    if title == '':
        abort(400, 'You must give your post a title.')
    if tags == '':
        abort(400, 'You must give your post at least one tag.')
    if text == '':
        abort(400, 'You must give your post a texy body.')

    user.add_post(title, tags, text)
    return redirect(url_for('profile', username=username))