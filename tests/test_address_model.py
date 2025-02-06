from app import create_app
from models import db, User, Address
from unittest import TestCase
from sqlalchemy.exc import IntegrityError


class TestAddressModel(TestCase):
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

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_address_creation(self):
        with self.app.app_context():
            address = Address(
                user_id=self.user_id,
                address="564 Broadway, Albany, NY 12005",
                mapbox_id="dfulaffda",
            )

            db.session.add(address)
            db.session.commit()

            found_address = db.session.get(Address, address.id)
            self.assertIsNotNone(found_address)
            self.assertEqual(found_address.address, "564 Broadway, Albany, NY 12005")

    def test_address_creation_without_address(self):
        with self.app.app_context():
            address = Address(
                user_id=self.user_id,
                address=None,
                mapbox_id="dfulaffda",
            )
            with self.assertRaises(IntegrityError):
                db.session.add(address)
                db.session.commit()

    def test_address_creation_without_non_existing_user(self):
        with self.app.app_context():
            address = Address(
                user_id=16,
                address="564 Broadway, Albany, NY 12005",
                mapbox_id="dfulaffda",
            )
            with self.assertRaises(IntegrityError):
                db.session.add(address)
                db.session.commit()

    def test_address_update(self):
        with self.app.app_context():
            address = Address(
                user_id=self.user_id, address="123 Test St", mapbox_id="abc123"
            )
            db.session.add(address)
            db.session.commit()

            # Update address
            address.address = "456 New St"
            db.session.commit()

            # Verify update
            updated_address = db.session.get(Address, address.id)
            self.assertEqual(updated_address.address, "456 New St")

    def test_address_deletion(self):
        with self.app.app_context():
            # Create an address
            address = Address(
                user_id=self.user_id,
                address="564 Broadway, Albany, NY 12005",
                mapbox_id="dfulaffda",
            )

            db.session.add(address)
            db.session.commit()
            # Save it's id for later
            address_id = address.id

            # Delete address
            db.session.delete(address)
            db.session.commit()

            # Check that it was deleted
            found_address = db.session.get(Address, address_id)
            self.assertIsNone(found_address)

    def test_muptiple_adresses_per_user(self):
        with self.app.app_context():
            # Create the addresses
            address01 = Address(
                user_id=self.user_id,
                address="564 Broadway, Albany, NY 12005",
                mapbox_id="dfulaffda",
            )

            address02 = Address(
                user_id=self.user_id,
                address="987 some place, AR, 19834",
                mapbox_id="glkapsdd",
            )

            db.session.add_all([address01, address02])
            db.session.commit()

            found_addresses = Address.query.filter_by(user_id=self.user_id).all()
            self.assertEqual(len(found_addresses), 2)
