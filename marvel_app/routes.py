from marvel_app import app
from marvel_app.form import UserLoginForm

from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required

import os


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods = ["GET","POST"])
def sign_up():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        return redirect(url_for('signin'))
    return render_template('sign_up.html', form=form)

@app.route('/signin')
def sign_in():
    form = UserLoginForm()
    return render_template('sign_in.html', form=form)