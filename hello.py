from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *

app = Flask(__name__)
app.config['SECRET_KEY'] = '3ad05b627be2e0258a6a67ebccf54db633847c76'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

class SignupForm(FlaskForm):
    name = StringField('Username', validators=[Required(), Length(min=1, max=10), Regexp("^[\w]{3,16}$")])
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


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                           current_time=datetime.utcnow())


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'GET':
        return render_template('signup.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            return redirect(url_for('index'))
        else:
            return '<h1> Invalid submission </h1> %s' % (form.errors)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = SigninForm()
    if request.method == 'GET':
        print ('GET method')
        return render_template('signin.html', form = form)
    elif request.method == 'POST':
        print ('POST method')
        if form.validate_on_submit():
            return redirect(url_for('index'))
        else:
            return '<h1> Invalid submission %s </h1>' % (form.errors)

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
    manager.run()
