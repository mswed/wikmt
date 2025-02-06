from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """
    Connect the database to the Flask app
    """

    db.app = app
    db.init_app(app)


class Address(db.Model):
    """
    An address record
    Fields: user_id, address, mapbox_id, latitude, longitude
    """

    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    address = db.Column(db.Text, nullable=False)
    mapbox_id = db.Column(db.Text)


class User(db.Model):
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


class Search(db.Model):
    """
    A search record
    Fields: user_id, address_id, start_date, end_date
    """

    __tablename__ = "searches"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    address_id = db.Column(db.Integer, db.ForeignKey("addresses.id"))
    condition = db.Column(db.Text, nullable=False, default="Covid19")
    name = db.Column(db.Text)
    age = db.Column(db.Integer)
    sex = db.Column(db.Text)
    race = db.Column(db.Text)
    ethnicity = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    process = db.Column(db.Text)
    exposure = db.Column(db.Boolean)
    current_status = db.Column(db.Text)
    symptomatic = db.Column(db.Text)
    hospitalized = db.Column(db.Text)
    icu = db.Column(db.Text)
    death = db.Column(db.Text)
    preexisting_conditions = db.Column(db.Text)

    user = db.relationship("User", backref="searches")
    address = db.relationship("Address", backref="searches")


class HistoricDataPoint(db.Model):
    """
    Historic Data from the CDC
    """

    __tablename__ = "historic"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wwtp_jurisdiction = db.Column(db.Text)
    wwtp_id = db.Column(db.Text)
    reporting_jurisdiction = db.Column(db.Text)
    sample_location = db.Column(db.Text)
    sample_location_specify = db.Column(db.Text)
    key_plot_id = db.Column(db.Text)
    county_names = db.Column(db.Text)
    county_fips = db.Column(db.Text)
    population_served = db.Column(db.Text)
    date_start = db.Column(db.Date)
    date_end = db.Column(db.Date)
    ptc_15d = db.Column(db.Text)
    detect_prop_15d = db.Column(db.Text)
    percentile = db.Column(db.Text)
    sampling_prior = db.Column(db.Text)
    first_sample_date = db.Column(db.Date)

    def to_dict(self):
        return {
            "wwtp_jurisdiction": self.wwtp_jurisdiction,
            "wwtp_id": self.wwtp_id,
            "reporting_jurisdiction": self.reporting_jurisdiction,
        }
