from flask import render_template, request, session, redirect, url_for, current_app as app, flash
import os
from .. import db
from ..models import User
from ..email import send_email
from . import main
from .forms import NameForm, ResetForm, TokenForm
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
