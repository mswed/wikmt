from . import db


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
