from app import create_app
from models import db, User, Address, Search
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from datetime import datetime


class TestSearchModel(TestCase):
    def setUp(self):
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create user first
            user = User.register(email="test01@testing.com", pwd="123456")

            db.session.add(user)
            db.session.commit()

            self.user_id = user.id

            # Then an address
            address = Address(
                user_id=self.user_id,
                address="564 Broadway, Albany, NY 12005",
                mapbox_id="dfulaffda",
            )

            db.session.add(address)
            db.session.commit()

            self.address_id = address.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_search_creation(self):
        with self.app.app_context():
            search = Search(
                user_id=self.user_id,
                address_id=self.address_id,
                start_date="2024-12-01",
                end_date="2024-12-15",
            )

            db.session.add(search)
            db.session.commit()

            found_search = db.session.get(Search, search.id)
            self.assertIsNotNone(found_search)
            self.assertEqual(
                found_search.start_date,
                datetime.strptime("2024-12-01", "%Y-%m-%d").date(),
            )

    def test_search_creation_with_nonexistent_address_id(self):
        with self.app.app_context():
            search = Search(
                user_id=self.user_id,
                address_id=999,
                start_date="2024-12-01",
                end_date="2024-12-15",
            )
            with self.assertRaises(IntegrityError):
                db.session.add(search)
                db.session.commit()

    def test_search_creation_with_nonexistent_user_id(self):
        with self.app.app_context():
            search = Search(
                user_id=999,
                address_id=self.address_id,
                start_date="2024-12-01",
                end_date="2024-12-15",
            )
            with self.assertRaises(IntegrityError):
                db.session.add(search)
                db.session.commit()

    def test_search_update(self):
        with self.app.app_context():
            search = Search(
                user_id=self.user_id,
                address_id=self.address_id,
                start_date="2024-12-01",
                end_date="2024-12-15",
            )
            db.session.add(search)
            db.session.commit()

            # Update address
            search.start_date = "2024-12-07"
            db.session.commit()

            # Verify update
            updated_search = db.session.get(Search, search.id)
            self.assertEqual(
                updated_search.start_date,
                datetime.strptime("2024-12-07", "%Y-%m-%d").date(),
            )

    def test_search_deletion(self):
        with self.app.app_context():
            # Create an address
            search = Search(
                user_id=self.user_id,
                address_id=self.address_id,
                start_date="2024-12-01",
                end_date="2024-12-15",
            )
            db.session.add(search)
            db.session.commit()

            # Save it's id for later
            search_id = search.id

            # Delete address
            db.session.delete(search)
            db.session.commit()

            # Check that it was deleted
            found_search = db.session.get(Search, search_id)
            self.assertIsNone(found_search)

    def test_multiple_searches_per_user(self):
        with self.app.app_context():
            # Create the addresses
            search01 = Search(
                user_id=self.user_id,
                address_id=self.address_id,
                start_date="2024-12-01",
                end_date="2024-12-15",
            )

            search02 = Search(
                user_id=self.user_id,
                address_id=self.address_id,
                start_date="2023-12-01",
                end_date="2023-12-15",
            )

            db.session.add_all([search01, search02])
            db.session.commit()

            found_searches = Search.query.filter_by(user_id=self.user_id).all()
            self.assertEqual(len(found_searches), 2)
