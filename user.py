from flask_login import UserMixin
from flask_session.sessions import text_type


class User(UserMixin):
    """User class for login manager and session manager"""

    def __init__(self, user_id, name, email, username):
        """Constructor for User"""
        super().__init__()
        self._username = username
        self._email = email
        self._name = name
        self._id = str(user_id)

    def get_id(self):
        try:
            return text_type(self._id)
        except AttributeError:
            raise NotImplementedError('No `id` attribute available.')

    @property
    def name(self):
        return self._name

    @property
    def email(self):
        return self._email

    @property
    def username(self):
        return self._username
