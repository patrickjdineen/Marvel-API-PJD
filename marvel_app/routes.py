from marvel_app import app, db, oauth
from flask import render_template, request, redirect, url_for, session, jsonify, flash
from marvel_app.form import UserLoginForm
from marvel_app.models import User, check_password_hash, Hero, hero_schema, heroes_schema
from flask_login import login_user, logout_user, current_user, login_required
from marvel_app.helpers import get_jwt, token_required, verify_owner

import os


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods = ['GET','POST'])
def signup():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User(email, password = password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('signin'))
    return render_template('sign_up.html', form=form)

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        logged_user = User.query.filter(User.email_address == email).first()
        print(email)
        print(logged_user)
        print(password)
        if logged_user and check_password_hash(logged_user.password,password):
            login_user(logged_user)
            return redirect(url_for('home'))
    return render_template('sign_in.html', form=form)

@app.route('/heroes')
@login_required
def heroes():
    jwt = get_jwt(current_user)
    return render_template('heroes.html', jwt = jwt)

@app.route('/logout')
def logout():
    logout_user()
    if session:
        for key in list(session.keys()):
            session.pop(key)
    return redirect(url_for('home'))

#API Routes
#create
@app.route('/hero', methods = ['POST'])
@token_required
def _hero(current_user_token):
    hero_name = request.json['hero_name']
    description = request.json['description']
    comics_appeared = request.json['comics_appeared']
    super_power = request.json['super_power']
    user_id = current_user_token.token
    hero = Hero(hero_name, description,comics_appeared,super_power, user_id = user_id)
    db.session.add(hero)
    db.session.commit()
    print(hero)
    response = hero_schema.dump(hero)
    return jsonify(response)


#get all
@app.route('/hero', methods = ['GET'])
@token_required
def get_heroes(current_user_token):
    owner, current_user_token = verify_owner(current_user_token)
    heroes = Hero.query.filter_by(user_id = owner.user_id).all()
    response = heroes_schema.dump(heroes)
    return jsonify(response)

#get 1
@app.route('/hero/<id>', methods = ['GET'])
@token_required
def get_hero(current_user_token,id):
    owner, current_user_token = verify_owner(current_user_token)
    hero = Hero.query.get(id)
    response = hero_schema.dump(hero)
    return jsonify(response)

#update 1
@app.route('/hero/<id>', methods = ['POST','PUT'])
@token_required
def update_hero(current_user_token,id):
    hero_name = request.json['hero_name']
    description = request.json['description']
    comics_appeared = request.json['comics_appeared']
    super_power = request.json['super_power']
    user_id = current_user_token.token
    
    hero = Hero(hero_name, description,comics_appeared,super_power, user_id = user_id)
    db.session.commit()
    response = hero_schema.dump(hero)
    return jsonify(response)

# delete
#get 1
@app.route('/hero/<id>', methods = ['DELETE'])
@token_required
def del_hero(current_user_token, id):
    owner, current_user_token = verify_owner(current_user_token)
    hero = Hero.query.get(id)
    db.session.delete(hero)
    db.session.commit()
    response = hero_schema.dump(hero)
    return jsonify(response)


#GOOGLE AUTH ROUTES
google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),

    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/google-auth')
def google_auth():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize',_external = True)
    return google.authorize_redirect(redirect_uri)    

@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    response = google.get('userinfo')
    user_info = response.json()
    user = oauth.google.userinfo()
    session['profile'] = user_info

    user = User.query.filter_by(email_address = user_info['email']).first()
    if user:
        user.first_name = user_info['given_name']
        user.last_name = user_info['family_name']
        user.email_address = user_info['email']
        user.g_auth_verify = user_info['verified_email']
        db.session.add(user)
        db.session.commit()
        login_user(user)
        session.permenant = True
        return redirect(url_for('home'))
    else:
        g_first_name = user_info['given_name']
        g_last_name = user_info['family_name']
        g_email = user_info['email']
        g_verified = user_info['verified_email']

        user = User(
            first_name = g_first_name,
            last_name = g_last_name,
            email_address = g_email,
            g_auth_verify = g_verified
        )

        db.session.add(user)
        db.session.commit()
        login_user(user)
        session.permanent = True
        return redirect(url_for('home'))
    return redirect(url_for('home'))