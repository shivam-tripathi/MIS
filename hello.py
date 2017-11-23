from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from threading import Thread

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = '3ad05b627be2e0258a6a67ebccf54db633847c76'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    ('mysql://root:root@localhost/test')

app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_SENDER'] = 'Shivam Tripathi <onlinemusic97@gmailcom>'
app.config['MAIL_SUBJECT_PREFIX'] = '[onlinemusic97] wrote: '

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager = Manager(app)
manager.add_command('shell', Shell(make_context=make_shell_context))
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)
mail = Mail(app)


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
    name = db.Column(db.String(64))
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(128), unique=True, index=True)
    password = db.Column(db.String(128), unique=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class SignupForm(FlaskForm):
    name = StringField('Name', validators=[Required(), Length(min=3, max=25), Regexp('^[\w+\s\w+]+$')])
    username = StringField('Username', validators=[Required(), Length(min=3, max=10), Regexp('^[\S]+$')])
    pwd = PasswordField('Password', validators=[Required(), Length(min=5, max=25)])
    cnfpwd = PasswordField('Confirm Password', validators=[Required(), Length(min=5, max=25)])
    email = StringField('Email', validators=[Required(), Email()])
    submit = SubmitField('Submit')


class SigninForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Email()])
    pwd = PasswordField('Password', validators=[Required(), Length(min=5, max=25)])
    submit = SubmitField('Submit')


class ResetForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Email()])
    submit = SubmitField('Submit')

class TokenForm(FlaskForm):
    token = StringField('Token', validators=[Required()])
    submit = SubmitField('Submit')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
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

            return redirect(url_for('signup'))

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
        return redirect(url_for('index'))
    else:
        flag = True
        session['values'] = {'name':form.name.data, 'username':form.username.data, 'email':form.email.data}
        error_msg = ''
        for field in fields:
            if field in form.errors:
                if flag:
                    flash(errors[field])
                session['values'][field] = ''
        return redirect(url_for('signup'))


@app.route('/signin', methods=['GET', 'POST'])
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
                return redirect(url_for('signin'))

            if sha256_crypt.verify(form.pwd.data, user.password):
                session['name'] = user.name
                return redirect(url_for('index'))
            else:
                flash('Incorrect password!')
                session['email'] = form.email.data
                return redirect(url_for('signin'))
        else:
            if 'email' in form.errors:
                flash('Invalid email')
                form.email.data = ''
            if 'pwd' in form.errors:
                flash('Invalid password')
            session['email'] = form.email.data
            return redirect(url_for('signin'))


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = ResetForm()
    if request.method == 'GET':
        return render_template('reset.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash('User not found!')
                return redirect(url_for('reset'))

            if app.config['MAIL_USERNAME']:
                arg = {'to': user.email, 'subject': 'Password Reset', 'template': 'mail_reset',
                    'name': user.name, 'token':'21089512', 'msg': 'reset passwork token', 'time': '5'}
                print (app)
                print (arg)
                thr = Thread(target=send_email, args=[app, arg])
                thr.start()

            session['name'] = user.name
            flash('A reset token has been sent to your emailid.')
            return redirect(url_for('token', msg='Password reset'))
        else:
            flash('Invalid email')
            return redirect(url_for('reset'))


@app.route('/token/<msg>', methods=['GET', 'POST'])
def token(msg):
    form = TokenForm()
    if request.method == 'GET':
        return render_template('token.html', form=form, msg=msg)
    if request.method == 'POST':
        if form.validate_on_submit():
            redirect(url_for('index'))
        else:
            flash('Incorrect token')
            redirect(url_for('reset'))


def send_email(app, arg):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + arg['subject'],
                sender=app.config['MAIL_SENDER'], recipients=[arg['to']])

    with app.app_context():
        msg.body = render_template(arg['template'] + '.txt', name=arg['name'], token=arg['token'],
            msg=arg['msg'], time=arg['time'])
        msg.html = render_template(arg['template'] + '.html', name=arg['name'],token=arg['token'],
            msg=arg['msg'], time=arg['time'])
        print ("Sending mail!!!!!")
        # mail.send(msg)


if __name__ == '__main__':
    db.create_all()
    manager.run()
