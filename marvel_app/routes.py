from marvel_app import app, db
from flask import render_template, request, redirect, url_for, session, jsonify, flash
from marvel_app.form import UserLoginForm
from marvel_app.models import User, check_password_hash, Hero, hero_schema, heroes_schema
from flask_login import login_user, logout_user, current_user, login_required

import os


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods = ['GET','POST'])
def sign_up():
    print('checkpoint -1')
    form = UserLoginForm()
    print('checkpoint0')
    try:
        if request.method == 'POST' and form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = User(email, password = password)
            print('checkpoint1')
            db.session.add(user)
            print('checkpoint2')
            db.session.commit()
            print('checkpoint3')

            #return redirect(url_for('signin'))
    except:
        print('checkpoint4')
        return Exception('Invalid Data in form. Please try again!')
    print('checkpoint b')
    return render_template('sign_up.html', form=form)

@app.route('/signin')
def sign_in():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        return redirect(url_for('home'))
    return render_template('sign_in.html', form=form)


