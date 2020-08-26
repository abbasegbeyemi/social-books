import csv
import os
import time

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, MetaData, select, Table, Column, Integer, String, text, func, tuple_, bindparam
from sqlalchemy.sql import or_

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData(bind=engine)
metadata.reflect()
conn = engine.connect()

# Goodreads key
KEY = 'pLPMOz2T2i1YBu2QgsHw'


def create_books_table():
    books_table = Table('books', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('isbn', String, nullable=False),
                        Column('title', String, nullable=False),
                        Column('author', String, nullable=False),
                        Column('year', Integer, nullable=False),
                        )
    metadata.create_all(engine)

    with open('books.csv') as f:
        filereader = csv.DictReader(f)
        for row in filereader:
            # Dont do this ever again
            ins = books_table.insert().values(isbn=row['isbn'],
                                              title=row['title'],
                                              author=row['author'],
                                              year=int(row['year']))
            conn.execute(ins)


def get_books_table_data():
    metadata.reflect(only=['books'])
    books = metadata.tables['books']
    s = select([books])
    result = conn.execute(s)
    return result


def create_reviews_table():
    query = text(
        "CREATE TABLE book_reviews("
        "id SERIAL PRIMARY KEY,"
        "reviewer INTEGER REFERENCES users,"
        "book INTEGER REFERENCES books,"
        "rating INTEGER,"
        "review VARCHAR)"
    )
    conn.execute(query)


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


def add_new_users():
    # Add some random users
    new_users = [
        {'name': "Toyyibat Egbeyemi", 'email': "toyyibategbeyemi@gmail.com", 'username': "titiabike",
         'password': "khalid11"},
        {'name': "Khadijah Egbeyemi", 'email': "deejah27@gmail.com", 'username': "khadee", 'password': "maid232"},
        {'name': "Hafsa Egbeyemi", 'email': "hafsaadam@gmail.com", 'username': "danwake", 'password': "kano231"},
        {'name': "Muinat Egbeyemi", 'email': "muinatyusuf@gmail.com", 'username': "mimed21", 'password': "yusf222"}]
    insert_into_table('users', new_users)


def add_some_reviewers(new_review: dict):
    # Add some random reviews
    # new_reviews = [
    #     {'reviewer': 2, 'book': 999, 'rating': 4, 'review': "Loved this. A classic for sure!"},
    #     {'reviewer': 3, 'book': 543, 'rating': 1, 'review': 'Poor effort!'},
    #     {'reviewer': 4, 'book': 672, 'rating': 1, 'review': "Wow, I feel violated after reading this."},
    #     {'reviewer': 5, 'book': 625, 'rating': 5, 'review': "Loved it!."}
    # ]
    insert_into_table('book_reviews', new_review)


def get_user_activity(userid: int) -> list:
    """
    Returs a list of dictionaries which contain details of books a particular user has
    reviewed.
    :param userid: id of the user {int}
    :return:
    """
    usertable = metadata.tables['users']
    bookstable = metadata.tables['books']
    reviewstable = metadata.tables['book_reviews']

    fields = ('isbn', 'title', 'author', 'year', 'image_url', 'rating', 'review')

    query = select([
        bookstable.c.isbn,
        bookstable.c.title,
        bookstable.c.author,
        bookstable.c.year,
        bookstable.c.image_url,
        reviewstable.c.rating,
        reviewstable.c.review
    ]).select_from(
        reviewstable.join(
            usertable).join(
            bookstable)).where(
        usertable.c.id == userid
    )
    return [{k: v for k, v in zip(fields, res)} for res in conn.execute(query).fetchall()]


def get_goodreads_ratings(isbns: list) -> list:
    isb_keys = ','.join(isbns)
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": KEY, "isbns": isb_keys})
    books = res.json()['books']
    ratings = [c['average_rating'] for c in books]
    return ratings


def get_book_info(isbn):
    params = {"key": KEY, "q": str(isbn)}
    res = requests.get("https://www.goodreads.com/search/index.xml",
                       params=params)
    # soup = BeautifulSoup(res.text, 'xml')
    # image_url.text Gives the url to full size image
    # small_image_url Gives link to small image
    # average_rating gives the average rating

    return res


# Populate the books table with the right image URLS
def populate_book_images():
    bookstable = metadata.tables['books']
    query = select([bookstable.c.id, bookstable.c.isbn]).where(bookstable.c.small_image_url.is_(None))
    isbns = conn.execute(query).fetchall()

    upd_data = []

    for idx, isbn in isbns:
        res = get_book_info(isbn)
        soup = BeautifulSoup(res.text, 'xml')

        if soup.title is None:
            print(f"{isbn} got no match from goodreads")
            continue

        image_url = soup.image_url.text or ""
        small_image_url = soup.small_image_url.text or ""
        data = {'b_id': idx, 'image_url': image_url, 'small_image_url': small_image_url}

        upd_data.append(data)
        time.sleep(0.7)

        # Table update clause

        upd = bookstable.update().where(
            bookstable.c.id == bindparam(
                'b_id'
            )).values(
            {
                'small_image_url': bindparam('small_image_url'),
                'image_url': bindparam('image_url')
            }
        )
        conn.execute(upd, data)
        print(f"Inserted {data['b_id']} into table")

    return upd_data


def get_books_search(searchterm: str) -> list:
    if not searchterm:
        return []

    searchterm = f"%{searchterm}%"
    fields = ['id', 'isbn', 'title', 'author', 'year', 'image_url']
    bookstable = metadata.tables['books']
    query = select(
        [
            bookstable.c.id,
            bookstable.c.isbn,
            bookstable.c.title,
            bookstable.c.author,
            bookstable.c.year,
            bookstable.c.image_url,
        ]
    ).where(
        or_(
            bookstable.c.isbn.ilike(searchterm),
            bookstable.c.author.ilike(searchterm),
            bookstable.c.title.ilike(searchterm)
        )
    )

    result = conn.execute(query).fetchall()
    return [{k: v for k, v in zip(fields, res)} for res in result]


def get_book_reviews(isbn: str):
    usertable = metadata.tables['users']
    bookstable = metadata.tables['books']
    reviewstable = metadata.tables['book_reviews']

    fields = ['username', 'rating', 'review']

    query = select([
        usertable.c.username,
        reviewstable.c.rating,
        reviewstable.c.review
    ]).select_from(
        reviewstable.join(
            usertable).join(
            bookstable)
    ).where(
        bookstable.c.isbn == isbn
    )
    return [
        {k: v for k, v in zip(fields, res)}
        for res in conn.execute(query).fetchall()
    ]


def api_book_data(isbn):
    bookstable = metadata.tables['books']
    reviewstable = metadata.tables['book_reviews']

    fields = ['title', 'author', 'year', 'isbn', 'review_count', 'average_review']

    query = select([
        bookstable.c.title,
        bookstable.c.author,
        bookstable.c.year,
        bookstable.c.isbn,
        func.count(reviewstable.c.rating),
        func.avg(reviewstable.c.rating),
    ]).select_from(
        reviewstable.join(
            bookstable)
    ).where(
        bookstable.c.isbn == isbn
    ).group_by(
        bookstable.c.title,
        bookstable.c.author,
        bookstable.c.year,
        bookstable.c.isbn,
    )

    res = conn.execute(query).fetchone()
    return {k: v for k, v in zip(fields, res)}


if __name__ == '__main__':
    go = api_book_data("0692572031")
    print(go['average_review'])
    # for c in go:
    #     print(c)
    # print(go)
