from datetime import datetime
from flask import Flask, render_template
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask_moment import Moment

app = Flask(__name__)

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def index():
    return render_template('index.html',
                           current_time=datetime.utcnow())


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

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
