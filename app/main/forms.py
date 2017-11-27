from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, Regexp, Email


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[InputRequired()])
    submit = SubmitField('Submit')


# class SignupForm(FlaskForm):
#     name = StringField('Name', validators=[InputRequired(), Length(min=3, max=25), Regexp('^[\w+\s\w+]+$')])
#     username = StringField('Username', validators=[InputRequired(), Length(min=3, max=10), Regexp('^[\S]+$')])
#     pwd = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=25)])
#     cnfpwd = PasswordField('Confirm Password', validators=[InputRequired(), Length(min=5, max=25)])
#     email = StringField('Email', validators=[InputRequired(), Email()])
#     submit = SubmitField('Submit')


# class SigninForm(FlaskForm):
#     email = StringField('Email', validators=[InputRequired(), Email()])
#     pwd = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=25)])
#     submit = SubmitField('Submit')


class ResetForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Submit')


class TokenForm(FlaskForm):
    token = StringField('Token', validators=[InputRequired()])
    submit = SubmitField('Submit')
