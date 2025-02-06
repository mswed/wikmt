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


class TestUserModel(TestCase):
    def setUp(self):
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create user first
            user01 = User.register(email="test01@testing.com", pwd="123456")
            user02 = User.register(
                email="test02@testing.com",
                pwd="123456",
                birth_year=1918,
                sex="male",
                race="white",
                ethnicity="Non-Hispanic",
            )

            db.session.add_all([user01, user02])
            db.session.commit()

            self.user01_id = user01.id

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_registration(self):
        with self.app.app_context():
            user = User.register(email="test03@testing.com", pwd="123456")
            db.session.add(user)
            db.session.commit()

            # Test user was created
            found_user = User.query.filter_by(email="test03@testing.com").first()
            self.assertIsNotNone(found_user)
            self.assertEqual(found_user.email, "test03@testing.com")

    def test_user_authentication(self):
        with self.app.app_context():
            # Test authentication
            auth_user = User.authenticate("test01@testing.com", "123456")
            self.assertIsNotNone(auth_user)

            # Test wrong password
            auth_user = User.authenticate("test01@testing.com", "wrong")
            self.assertFalse(auth_user)

    def test_update_password(self):
        with self.app.app_context():
            user = User.query.filter_by(email="test01@testing.com").first()
            updated_user = user.update_password("123456", "new_password")
            self.assertIsNotNone(updated_user)

            # Test authentication
            auth_user = User.authenticate("test01@testing.com", "new_password")
            self.assertIsNotNone(auth_user)

    def test_update_details(self):
        with self.app.app_context():
            user = User.query.filter_by(email="test01@testing.com").first()
            updated_user = user.update_details(
                birth_year=1973,
                sex="Female",
                race="Pacific Islander",
                ethnicity="Non-Hispanic",
            )
            self.assertIsNotNone(updated_user)

            # Test user was updated
            found_user = User.query.filter_by(email="test01@testing.com").first()
            self.assertIsNotNone(found_user)
            self.assertEqual(found_user.birth_year, 1973)

    def test_get_age_group(self):
        with self.app.app_context():
            user = User.query.filter_by(email="test02@testing.com").first()
            age_group = user.get_age_group()
            self.assertEqual(age_group, "65+ years")
            user = User.query.filter_by(email="test01@testing.com").first()
            age_group = user.get_age_group()
            self.assertIsNone(age_group)

    def test_get_user_addresses(self):
        with self.app.app_context():
            # Create the addresses
            address01 = Address(
                user_id=self.user01_id,
                address="564 Broadway, Albany, NY 12005",
                mapbox_id="dfulaffda",
            )

            address02 = Address(
                user_id=self.user01_id,
                address="987 some place, AR, 19834",
                mapbox_id="glkapsdd",
            )

            db.session.add_all([address01, address02])
            db.session.commit()

            # Grab the user
            user = db.session.get(User, self.user01_id)
            self.assertEqual(len(user.addresses), 2)
