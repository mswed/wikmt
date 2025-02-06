from . import db


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
