import os

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import login_required, LoginManager, login_user, logout_user, current_user
from sqlalchemy import create_engine, MetaData

from forms import UserLoginForm, UserRegistrationForm, SearchForm, ReviewForm
from python_helpers.datbase_utils import user_info_get, info_check, add_user, username_and_password_check, \
    get_user_activity, get_goodreads_ratings, get_books_search, add_some_reviewers, get_book_reviews, api_book_data
from user import User

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
            # flash('Username or pasword is incorrect')
            return render_template('bootstrap-pages/signin-page.html',
                                   form=signin_form,
                                   alternative=alternative,
                                   title='Sign in')

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

    return render_template(
        # 'signin.html',
        'bootstrap-pages/signin-page.html',
        form=signin_form,
        alternative=alternative,
        title='Sign in')


@login_required
@app.route('/home', methods=['GET'])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('signin'))

    # Before we render the users data, we need to get all the books and pass to
    # the home page.
    user_activity = get_user_activity(current_user.get_id())

    isbn_list = [act['isbn'] for act in user_activity]

    # goodreads = get_goodreads_ratings(isbn_list) if isbn_list else []
    goodreads = [d for d in range(len(isbn_list))]

    searchform = SearchForm()

    return render_template('bootstrap-pages/home.html', activity=user_activity,
                           goodreads=goodreads,
                           searchform=searchform)


@app.route('/logout')
@login_required
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('signin'))
    # remove the username from the session if it is there
    logout_user()
    return redirect(url_for('signin'))


@app.route('/search', methods=['GET'])
def search():
    searchform = SearchForm()
    searchterm = request.args['searchbox']

    result = get_books_search(searchterm)
    return render_template('bootstrap-pages/search.html', result=result, searchform=searchform)


@login_required
@app.route('/detail/<isbn>')
def detail(isbn):
    searchform = SearchForm()
    # goodreads = get_goodreads_ratings([isbn])
    goodreads = [3]
    book = get_books_search(isbn)
    session['book'] = book[0]['id']
    session['isbn'] = book[0]['isbn']
    user_activity = get_user_activity(current_user.get_id())
    # Get the isbn of all the books the user has reviewed
    user_isbns = [book_isbn for book_isbn in [act['isbn'] for act in user_activity]]
    user_reviews = [book_review for book_review in [act['review'] for act in user_activity]]
    user_ratings = [book_review for book_review in [act['rating'] for act in user_activity]]

    list_check = {k: v for k, v in zip(user_isbns, zip(user_reviews, user_ratings))}

    try:
        book[0].update({'user_review': list_check[isbn]})
    except KeyError:
        pass

    other_reviews = get_book_reviews(isbn)

    # Filter the users review from the result
    filtered_reviews = [
        f for f in other_reviews if f['username'] != current_user.username
    ]

    book[0].update({'other_reviews': filtered_reviews})

    return render_template("bootstrap-pages/detail.html",
                           book=book[0],
                           goodreads=goodreads,
                           searchform=searchform)


@app.route('/review/<isbn>')
def review(isbn):
    book = get_books_search(isbn)
    reviewform = ReviewForm()
    searchform = SearchForm()
    return render_template("bootstrap-pages/review.html",
                           reviewform=reviewform,
                           searchform=searchform,
                           book=book[0])


@app.route('/submit_review', methods=['POST'])
def submit_review():
    # We need a dict as {reviewer, book, rating, review}
    # book:
    review_info = {
        'reviewer': current_user.get_id(),
        'book': int(session['book']),
        'rating': int(request.form['rating']),
        'review': request.form['review']
    }
    add_some_reviewers(review_info)
    return redirect(url_for('detail', isbn=session['isbn']))


@app.route('/api/<isbn>', methods=['GET'])
def book_data(isbn):
    response = api_book_data(isbn)
    response['average_review'] = str(round(response['average_review'], 2))
    return jsonify(response)
