from flask import flash
from flask_login import login_user, logout_user
from sqlalchemy.exc import IntegrityError
from models.user import db, User


class AuthService:
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate user with provided credentials
        :param email: str, user's email
        :param password: str, user's password
        :returns: User, if authenticated, else False
        """
        return User.authenticate(email, password)

    @staticmethod
    def login_user(user):
        """
        Log in user using flask-login and set flash message
        :param user: Object, user model object
        """

        # Set the flask-login user
        login_user(user)
        flash("Logged in!", "success")

    @staticmethod
    def register_user(
        email, password, birth_year=None, sex=None, race=None, ethnicity=None
    ):
        """
        Register a new user
        :params email: str, user's email
        :param password: str, user's password
        :param birth_year: int, user's birth year (optional)
        :param sex: str, user's sex (optional)
        :param race: str, user's race (optional)
        :param ethnicity: str, user's ethnicity (optional)
        :returns: tuple: (User, str), (User object if successful, error message if any)
        """
        try:
            new_user = User.register(
                email=email,
                pwd=password,
                birth_year=birth_year,
                sex=sex,
                race=race,
                ethnicity=ethnicity,
            )
            db.session.add(new_user)
            db.session.commit()
            return new_user, None

        except IntegrityError:
            # The user already exists. Rollback the transaction and alert the user
            db.session.rollback()
            return None, f"User {email} already exists!"

    @staticmethod
    def logout_user():
        """
        Logout the currrent user user flask-login
        """
        logout_user()
