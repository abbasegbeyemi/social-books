from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields import PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class UserLoginForm(FlaskForm):
    """For the user to log in"""
    username = StringField('Username', validators=[DataRequired(message='Please fill in your username.')],
                           description={'placeholder': 'Username'})
    password = PasswordField('Password', validators=[DataRequired(message='Please enter your password.')],
                             description={'placeholder': 'Password'})
    remember = BooleanField('Remember me', default=False)
    submit = SubmitField('Sign in')


class UserRegistrationForm(FlaskForm):
    """For the user to register"""
    name = StringField('Full Name', validators=[DataRequired(message='Please enter your full name.')],)
    username = StringField('Username', validators=[DataRequired(message='Enter a username.')])
    email = StringField('Email', validators=[Email(message='Not a valid email address.'),
                                             DataRequired(message="Please enter an email address.")])
    password = PasswordField('Password',
                             validators=[Length(min=5, max=20,
                                                message='Your password should be between 5 and 20 characters.'),
                                         DataRequired(),
                                         EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Repeat Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password', message='Passwords must match.')])
    agree = BooleanField(validators=[DataRequired(message="Indicate that you agree with the terms and conditions")])
    submit = SubmitField('Register')
