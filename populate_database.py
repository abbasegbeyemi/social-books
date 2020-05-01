import csv
import os

from sqlalchemy import create_engine, MetaData, select, Table, Column, Integer, String, text, func, tuple_
from sqlalchemy.testing import in_

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=False)
metadata = MetaData(bind=engine)
metadata.reflect()
conn = engine.connect()


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


def info_check(table: str, label: str, info: str) -> tuple:
    tb_info = metadata.tables[table]
    s = select(
        [
            tb_info.c.id
        ]).where(tb_info.c[label] == info)
    result = conn.execute(s).scalar()
    return bool(result), result


def user_info_get(labels: list, username: str) -> tuple:
    tb_info = metadata.tables['users']
    s = select(
        [
            tb_info.c[field] for field in labels
        ]).where(tb_info.c.username == username)
    result = conn.execute(s).fetchone()
    return result


def username_and_password_check(username: str, password: str) -> bool:
    table = metadata.tables['users']
    s = select(
        [
            func.count(table.c.id)
        ]).where(tuple_(table.c['username'], table.c['password'])
                 .in_([(username, password)]))
    result = conn.execute(s).scalar()
    return bool(result)


def insert_into_table(table: str, data):
    metadata.reflect(only=[table])
    tb_ins = metadata.tables[table]
    ins = tb_ins.insert()
    conn.execute(ins, data)


def add_new_users():
    # Add some random users
    new_users = [
        {'name': "Toyyibat Egbeyemi", 'email': "toyyibategbeyemi@gmail.com", 'username': "titiabike",
         'password': "khalid11"},
        {'name': "Khadijah Egbeyemi", 'email': "deejah27@gmail.com", 'username': "khadee", 'password': "maid232"},
        {'name': "Hafsa Egbeyemi", 'email': "hafsaadam@gmail.com", 'username': "danwake", 'password': "kano231"},
        {'name': "Muinat Egbeyemi", 'email': "muinatyusuf@gmail.com", 'username': "mimed21", 'password': "yusf222"}]
    insert_into_table('users', new_users)


def add_some_reviewers():
    # Add some random reviews
    new_reviews = [
        {'reviewer': 2, 'book': 999, 'rating': 4, 'review': "Loved this. A classic for sure!"},
        {'reviewer': 3, 'book': 543, 'rating': 1, 'review': 'Poor effort!'},
        {'reviewer': 4, 'book': 672, 'rating': 1, 'review': "Wow, I feel violated after reading this."},
        {'reviewer': 5, 'book': 625, 'rating': 5, 'review': "Loved it!."}
    ]
    insert_into_table('book_reviews', new_reviews)


if __name__ == '__main__':
    go = user_info_get(['name', 'email'], 'admin')
    print(go)
