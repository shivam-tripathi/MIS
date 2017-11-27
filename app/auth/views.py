from flask import render_template, request, session, redirect, url_for, current_app as app, flash
from flask_login import login_required, login_user, logout_user, current_user
from .. import login_manager
from ..models import User, Role, db
from .forms import SigninForm, SignupForm
from . import auth


@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    fields = {'email':'Email', 'pwd':'Password'}
    form = SigninForm()
    email = session.get('email', '')

    if request.method == 'GET':
        email = email if email else ''
        return render_template('auth/signin.html', form=form, email=email)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash('User not found!')
                return redirect(url_for('.signin'))

            if user.verify_password(form.pwd.data):
                session['name'] = user.name
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
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


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

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

        return render_template('auth/signup.html', form=form, name=name, username=username, email=email)

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
                    password=form.pwd.data,
                    role=role)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user, True)
        session['name'] = form.name.data
        return redirect(url_for('main.index'))
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


@auth.route('/logout')
@login_required
def signout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@login_manager.unauthorized_handler
def unauthorized_callback():
    flash('You need to be signed in to view this page')
    return redirect(url_for('auth.signin'))