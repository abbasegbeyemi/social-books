import os

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_login import login_required, LoginManager, login_user, logout_user, current_user

from forms import UserLoginForm, UserRegistrationForm
from user import User
from sqlalchemy import create_engine, MetaData, select, func, tuple_

# region App Initialization
app = Flask(__name__)
app.secret_key = os.urandom(16)
login_manager = LoginManager()
login_manager.init_app(app)

# endregion

# region Database Initialization
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData(bind=engine)
metadata.reflect()
conn = engine.connect()


# endregion

# region Database Utils
def insert_into_table(table: str, data):
    # metadata.reflect(only=[table])
    tb_ins = metadata.tables[table]
    ins = tb_ins.insert()
    conn.execute(ins, data)


def add_user(user: dict):
    """
    Add user to database
    :param user: The user details. user = { 'name': str, 'email': str, 'username': str, 'password': str }
    :return: None
    """
    new_user = [user]
    insert_into_table('users', new_user)


def info_check(table: str, label: str, info: str) -> tuple:
    """
    This just serves to check a table for info, and return true or false, and ID
    of the data if present.
    :param table: str [ table name ]
    :param label: str [ label for the info you're interested in ]
    :param info: str [ info you are interested in ]
    :return: bool [ True or false if info is present ]
    """
    tb_info = metadata.tables[table]
    s = select(
        [
            tb_info.c.id
        ]).where(tb_info.c[label] == info)
    result = conn.execute(s).scalar()
    return bool(result), result


def username_and_password_check(username: str, password: str) -> bool:
    """
    Checks the entered username and password against the database
    :param username: str
    :param password: str
    :return: bool [ True or false if account is registered ]
    """
    table = metadata.tables['users']
    s = select(
        [
            func.count(table.c.id)
        ]).where(tuple_(table.c['username'], table.c['password'])
                 .in_([(username, password)]))
    result = conn.execute(s).scalar()
    return bool(result)


def user_info_get(labels: list, idx: str) -> tuple:
    tb_info = metadata.tables['users']
    idx = int(idx)
    s = select(
        [
            tb_info.c[field] for field in labels
        ]).where(tb_info.c.id == idx)
    result = conn.execute(s).fetchone()
    return result


# endregion


# region User Authentication
@login_manager.user_loader
def load_user(user_id):
    name, email, username = user_info_get(
        ['name', 'email', 'username'],
        user_id
    )
    if username:
        return User(user_id, name, email, username)
    else:
        return None


# endregion


@app.route('/register', methods=['GET', 'POST'])
def register():
    signup_form = UserRegistrationForm()
    alternative = {'label': 'Sign in', 'endpoint': 'signin'}
    if not signup_form.validate_on_submit():
        return render_template('bootstrap-pages/signup-page.html',
                               form=signup_form,
                               alternative=alternative,
                               title='Register')

    # When you get here, you're good. Now let's see if you already have an account
    user_details = request.form
    # Check the database for user presence
    exists, _ = info_check('users', 'email', user_details['email'])
    if exists:
        return redirect(url_for('signin'))

    user = {
        'name': user_details['name'],
        'email': user_details['email'],
        'username': user_details['username'],
        'password': user_details['password']
    }
    add_user(user)
    return redirect(url_for('signin'))


@app.route('/', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    signin_form = UserLoginForm()
    alternative = {'label': 'Register', 'endpoint': 'register'}
    if signin_form.validate_on_submit():
        # Check if account exists
        user_details = request.form
        exists = username_and_password_check(
            user_details['username'],
            user_details['password'])
        if not exists:
            flash('Username or pasword is incorrect')
            return render_template('signin.html',
                                   form=signin_form,
                                   alternative=alternative)

        _, user_id = info_check('users',
                                'username',
                                user_details['username'])
        user_id, name, email, username = user_info_get(
            ['id', 'name', 'email', 'username'],
            user_id
        )
        if user_id:
            remember = user_details.get('remember') is not None
            user = User(user_id, name, email, username)
            login_user(user, remember=remember)

            return redirect(url_for('home'))

    return render_template('bootstrap-pages/signin-page.html',
                           form=signin_form,
                           alternative=alternative,
                           title='Sign in')


@login_required
@app.route('/home', methods=['GET'])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('signin'))

    return render_template('bootstrap-pages/home.html')


@app.route('/logout')
@login_required
def logout():
    # remove the username from the session if it is there
    logout_user()
    return redirect(url_for('signin'))


@app.route('/search')
def search():
    return render_template('bootstrap-pages/search.html')
