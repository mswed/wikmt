from app import create_app
from models import db, User, Address
from unittest import TestCase


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
