from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields import PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.fields.html5 import SearchField
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
    name = StringField('Full Name', validators=[DataRequired(message='Please enter your full name.')], )
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


class SearchForm(FlaskForm):
    """Form for searching the database"""
    searchbox = SearchField('Book Title, Author or ISBN', validators=[DataRequired(message='Enter a search term')],
                            render_kw={"rows": 10})
    submit = SubmitField('Search')


class ReviewForm(FlaskForm):
    rating = SelectField('Rating (Stars)', choices=[n for n in range(1, 6)], validate_choice=True)
    review = TextAreaField('What did you think?', render_kw={"rows": 10})
    submit = SubmitField('Submit')
