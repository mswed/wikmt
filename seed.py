from models import db
from app import create_app

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

test_app = create_app('wikmt_test_db')

with test_app.app_context():
    db.drop_all()
    db.create_all()
