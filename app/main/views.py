from flask import render_template, request, session, redirect, url_for, current_app as app, flash
import os
from .. import db
from ..models import User
from ..email import send_email
from . import main
from .forms import NameForm, SigninForm, SignupForm, ResetForm, TokenForm
from passlib.hash import sha256_crypt
from threading import Thread


@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html', form=form, name=session.get('name'))


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    fields = {'name':'Name', 'username':'Username', 'pwd':'Password', 'cnfpwd':'Confirm Password', 'email':'Email'}
    errors = {'name':'Name can contain only alphanumeric values and underscores allowed 3-25 characters long',
                'username': 'Username has to be unique with no spaces',
                'pwd': 'Password should lie between 5-25 characters',
                'cnfpwd': 'Passwords don\'t match',
                'email': 'Invalid email'}

    if request.method == 'GET':
        name = username = email = ''
        if session.get('values'):
            name = session['values'].get('name', '')
            username = session['values'].get('username', '')
            email = session['values'].get('email', '')
            session['values'] = {}

        return render_template('signup.html', form=form, name=name, username=username, email=email)

    if form.validate_on_submit():
        form.username.data = form.username.data.lower()
        form.email.data = form.email.data.lower()
        session['values'] = {'name':form.name.data, 'username':form.username.data, 'email':form.email.data}

        find_username = User.query.filter_by(username=form.username.data).first()
        find_email = User.query.filter_by(email=form.email.data).first()
        if find_username is not None or find_email is not None:
            if find_username is not None:
                flash('Username already in use. Try a different one!')
                session['values']['username'] = ''

            if find_email is not None:
                flash('Email already in use. Try a different one!')
                session['values']['email'] = ''

            return redirect(url_for('.signup'))

        session['values'] = {}
        role =  Role.query.filter_by(name='User').first()
        new_user = User(name=form.name.data,
                    username=form.username.data,
                    email=form.email.data,
                    password=sha256_crypt.hash(form.pwd.data),
                    role=role)

        db.session.add(new_user)
        db.session.commit()

        session['name'] = form.name.data
        return redirect(url_for('.index'))
    else:
        flag = True
        session['values'] = {'name':form.name.data, 'username':form.username.data, 'email':form.email.data}
        error_msg = ''
        for field in fields:
            if field in form.errors:
                if flag:
                    flash(errors[field])
                session['values'][field] = ''
        return redirect(url_for('.signup'))


@main.route('/signin', methods=['GET', 'POST'])
def signin():
    fields = {'email':'Email', 'pwd':'Password'}
    form = SigninForm()
    email = session.get('email', '')

    if request.method == 'GET':
        email = email if email else ''
        return render_template('signin.html', form=form, email=email)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash('User not found!')
                return redirect(url_for('.signin'))

            if user.verify_password(form.pwd.data):
                session['name'] = user.name
                return redirect(url_for('.index'))
            else:
                flash('Incorrect password!')
                session['email'] = form.email.data
                return redirect(url_for('.signin'))
        else:
            if 'email' in form.errors:
                flash('Invalid email')
                form.email.data = ''
            if 'pwd' in form.errors:
                flash('Invalid password')
            session['email'] = form.email.data
            return redirect(url_for('.signin'))


@main.route('/reset', methods=['GET', 'POST'])
def reset():
    form = ResetForm()
    if request.method == 'GET':
        return render_template('reset.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash('User not found!')
                return redirect(url_for('.reset'))

            if app.config['MAIL_USERNAME']:
                arg = {'to': user.email, 'subject': 'Password Reset', 'template': 'mail_reset',
                    'name': user.name, 'token':'21089512', 'msg': 'reset passwork token', 'time': '5'}
                print (app)
                print (arg)
                thr = Thread(target=send_email, args=[app, arg])
                thr.start()

            session['name'] = user.name
            flash('A reset token has been sent to your email-id.')
            return redirect(url_for('.token', msg='Password Reset'))
        else:
            flash('Invalid email')
            return redirect(url_for('.reset'))


@main.route('/token/<msg>', methods=['GET', 'POST'])
def token(msg):
    form = TokenForm()
    if request.method == 'GET':
        return render_template('token.html', form=form, msg=msg)
    elif request.method == 'POST':
        if form.validate_on_submit():
            return redirect(url_for('.index'))
        else:
            flash('Incorrect token')
            return redirect(url_for('.reset'))
