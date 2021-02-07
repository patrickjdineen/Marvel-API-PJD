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
    print('checkpoint -1')
    form = UserLoginForm()
    print('checkpoint0')
    #try:
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User(email, password = password)
        print('checkpoint1')
        db.session.add(user)
        print('checkpoint2')
        db.session.commit()
        print('checkpoint3')
        return redirect(url_for('signin'))
    #except:
    #    print('checkpoint4')
    #    return Exception('Invalid Data in form. Please try again!')
    print('checkpoint b')
    return render_template('sign_up.html', form=form)

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        print('check 1')
        email = form.email.data
        password = form.password.data
        logged_user = User.query.filter(User.email_address == email).first()
        print(email)
        print(logged_user)
        print(password)
        print('check2')
        if logged_user and check_password_hash(logged_user.password,password):
            print('check3')
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