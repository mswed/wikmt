from . import db, bcrypt
from datetime import datetime
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """
    A user record
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False, unique=True)
    birth_year = db.Column(db.Integer)
    sex = db.Column(db.Text)
    race = db.Column(db.Text)
    ethnicity = db.Column(db.Text)

    addresses = db.relationship("Address", backref="users")

    @classmethod
    def authenticate(cls, email, password):
        """
        Authenticate the user
        :param email: str, email used to login
        :param password: str, user's plain text password
        :returns: User if hashed password matches the DB entry, else False
        """
        u = User.query.filter_by(email=email).first()
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False

    @classmethod
    def register(cls, email, pwd, birth_year=None, sex=None, race=None, ethnicity=None):
        """
        Register a user
        :param email: str, email used to login
        :param password: str, user's plain text password
        :param birth_year: int, user's year of birth. Used to calcualte age group
        :param sex: str, User's sex: Male, Female, Other
        :param race: str, User's race (CDC Categories): American Indian/Alaska Native, Asian, Black,
                                                        Pacific Islander, White, Other
        :param ethnicity: str, User's ethnicity (CDC Categories): Hispanic, Non-Hispanic
        :returns: User
        """
        hashed = bcrypt.generate_password_hash(pwd)

        # Convert byte string to standard string
        hashed_utf8 = hashed.decode("utf-8")

        return cls(
            email=email,
            password=hashed_utf8,
            birth_year=birth_year,
            sex=sex,
            race=race,
            ethnicity=ethnicity,
        )

    def update_password(self, pwd, new_pwd):
        """
        Update the user's password
        :param pwd: str, old password
        :param new_pwd: str, new password
        :returns: User if successful, else False
        """
        au = self.authenticate(self.email, pwd)
        if au:
            hashed = bcrypt.generate_password_hash(new_pwd)

            # Convert byte string to standard string
            hashed_utf8 = hashed.decode("utf-8")
            au.password = hashed_utf8

            return au
        else:
            return False

    def update_details(self, birth_year, sex, race, ethnicity):
        """
        Update user details
        :param birth_year: int, user's year of birth. Used to calcualte age group
        :param sex: str, User's sex: Male, Female, Other
        :param race: str, User's race (CDC Categories): American Indian/Alaska Native, Asian, Black,
                                                        Pacific Islander, White, Other
        :param ethnicity: str, User's ethnicity (CDC Categories): Hispanic, Non-Hispanic
        """
        self.birth_year = birth_year
        self.sex = sex
        self.race = race
        self.ethnicity = ethnicity

        return self

    def get_age_group(self):
        """
        To calculate the death risk we need to convert the user's age to their CDC age group
        :returns: str, user's age group or None if age is empty
        """
        if self.birth_year:
            age = datetime.now().year - self.birth_year
            if 0 <= age <= 17:
                age_group = "0 - 17 years"
            elif 18 <= age <= 49:
                age_group = "18 to 49 years"
            elif 50 <= age <= 64:
                age_group = "18 to 49 years"
            elif age >= 65:
                age_group = "65+ years"
            else:
                age_group = "unknown"

            return age_group
        else:
            return None
