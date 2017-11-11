from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '3ad05b627be2e0258a6a67ebccf54db633847c76'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class SignupForm(FlaskForm):
    name = StringField('Username', validators=[Required(), Length(min=3, max=25), Regexp("\w+\s\w+")])
    pwd = PasswordField('Password', validators=[Required(), Length(min=5, max=25)])
    cnfpwd = PasswordField('Confirm Password', validators=[Required(), Length(min=5, max=25)])
    email = StringField('Email', validators=[Required(), Email()])
    submit = SubmitField('Submit')

class SigninForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Email()])
    pwd = PasswordField('Password', validators=[Required(), Length(min=5, max=25)])
    submit = SubmitField('Submit')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    fields = {'name':'Name', 'pwd':'Password', 'cnfpwd':'Confirm Password', 'email':'Email'}
    errors = {'name':'Name can contain only alphanumeric values and underscores allowed 3-25 characters long',
                'pwd': "Password should lie between 5-25 characters",
                'cnf': "Passwords don't match",
                'email': "Invalid email"}

    if request.method == 'GET':
        name = session['values']['name'] if session['values'].get('name') else ""
        email = session['values']['email'] if session['values'].get('email') else ""
        session['values'] = {}
        return render_template('signup.html', form=form, name=name, email=email)

    if form.validate_on_submit():
        return redirect(url_for('index'))
    else:
        for field in fields:
            if field in form.errors:
                flash(errors[field])
                break
        session['values'] = {'name':form.name.data, 'email':form.email.data}
        return redirect(url_for('signup'))


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    fields = {'email':'Email', 'pwd':'Password'}
    form = SigninForm()

    if request.method == 'GET':
        email = session['email'] if session.get('email') else ""
        session['email'] = None
        return render_template('signin.html', form = form, email=email)
    elif request.method == 'POST':
        if form.validate_on_submit():
            return redirect(url_for('index'))
        else:
            for field in fields:
                if field in form.errors:
                    flash("Invalid %s " % fields[field])
                    break
            session['email'] = form.email.data
            return redirect(url_for('signin'))


class Check:
    def __init__(self, one, two, three):
        self.one = one
        self.two = two
        self.three = three

    def get_alpha(self):
        return self.one

@app.route('/check')
def check():
    obj = Check(1, "Two", [i for i in range(10)])
    print (obj.three, obj.two)
    return render_template('check.html', obj=obj, lis=obj.three, str=obj.two, user=obj.two)

if __name__ == '__main__':
    db.create_all()
    manager.run()
