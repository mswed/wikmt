from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """
    Connect the database to the Flask app
    """

    db.app = app
    db.init_app(app)


from .user import User
from .address import Address
from .search import Search
from .historic_data import HistoricDataPoint
