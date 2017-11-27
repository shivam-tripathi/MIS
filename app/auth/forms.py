from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Regexp, Email


class SigninForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    pwd = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=25)])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Submit')


class SignupForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=25), Regexp('^[\w+\s\w+]+$')])
    username = StringField('Username', validators=[InputRequired(), Length(min=3, max=10), Regexp('^[\S]+$')])
    pwd = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=25)])
    cnfpwd = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=5, max=25)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Submit')