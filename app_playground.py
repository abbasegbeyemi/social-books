import os

import requests
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, TextAreaField, SubmitField
from flask_session import Session
from sqlalchemy import create_engine
from wtforms.validators import DataRequired

from forms import UserLoginForm
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
app.secret_key = 'gkdfgfsdkfgskfgdfgsdfsdfdhsghkfdfks'
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


class ContactForm(FlaskForm):
    name = StringField("Name of Student", validators=[DataRequired(message="Please enter your name!")])
    gender = RadioField('Gender', choices=[('M', 'Male'), ('F', 'Female')])
    address = TextAreaField("Address", validators=[DataRequired(message="Please enter your address!")])
    submit = SubmitField("Send")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            return render_template('contact.html', form=form)
        else:
            return render_template('hello.html', name=form.name, address=form.address)
    elif request.method == 'GET':
        return render_template('contact.html', form=form)

# app.config['SESSION-PERMANENT'] = False
# app.config['SESSION-TYPE'] = "filesystem"
# app.config['SECRET-KEY'] = "kjgkagsdkajsdg"


# Configure session to use filesystem


# # Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))


# db = scoped_session(sessionmaker(bind=engine))  s

# with engine.connect() as connection:
#     books = connection.execute("SELECT * FROM books")
#     for row in books:
#         print(f"title: {row.title}")

# KEY = "pLPMOz2T2i1YBu2QgsHw"
# res = requests.get("https://www.goodreads.com/book/review_counts.json",
#                    params={
#                        "key": KEY,
#                        "isbns": "0984358161"
#                    }
#                    )

# @app.route("/", methods=['GET', 'POST'])
# def index():
# form = UserLoginForm()
# if form.validate_on_submit():
#     return redirect(url_for('hello'))
# return render_template("signup.html")


# @app.route("/more")
# def more():
#     form = UserLoginForm()
#     if form.validate_on_submit():
#         return redirect(url_for('hello'))
#     return render_template("more.html")
#
#
# @app.route("/hello", methods=["POST"])
# def hello():
#     useremail = request.form.get("useremail")
#     userpassword = request.form.get("userpassword")
#     return render_template("hello.html", useremail=useremail, userpassword=userpassword)

# @app.route('/')
# def student():
#     return render_template('signup.html')
#
#
# @app.route('/result', methods=['POST', 'GET'])
# def result():
#     if request.method == 'POST':
#         result = request.form
#         return render_template("hello.html", result=result)
# @app.route('/')
# def index():
#     if 'username' in session:
#         username = session['username']
#         return 'Logged in as ' + username + '<br>' + \
#                "<b><a href = '/logout'>click here to log out</a></b>"
#     return "You are not logged in <br><a href = '/login'></b>" + \
#            "click here to log in</b></a>"
#
#
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         session['username'] = request.form['username']
#         return redirect(url_for('index'))
#     return '''
#
#    <form action = "" method = "post">
#       <p><input type = text name = 'username'/></p>
#       <p><input type = submit value = Login/></p>
#    </form>
#
#    '''
#
#
# @app.route('/logout')
# def logout():
#     # remove the username from the session if it is there
#     session.pop('username', None)
#     return redirect(url_for('index'))
#

# if __name__ == '__main__':
#     app.run(debug=True)
