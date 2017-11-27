from flask import current_app, render_template
from flask_mail import Message
from . import mail


def default_mail():
    msg = Message('This is an auto-generated email!', sender='onlinemusic97@gmail.com',
        recipients=['mukeshnithcse@gmail.com'])
    with app.app_context():
        msg.body = 'Hi there!'
        msg.html = '<b>How you doin?</b> It is great meeting you!'
        # mail.send(msg)


def send_email(app, arg):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + arg['subject'],
                sender=app.config['MAIL_SENDER'], recipients=[arg['to']])
    with app.app_context():
        msg.body = render_template('mail/' + arg['template'] + '.txt', name=arg['name'], token=arg['token'],
            msg=arg['msg'], time=arg['time'])
        msg.html = render_template('mail/' + arg['template'] + '.html', name=arg['name'],token=arg['token'],
            msg=arg['msg'], time=arg['time'])
        print ("Sending mail!!!!!")
        # mail.send(msg)