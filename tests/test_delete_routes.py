from app import create_app
from models import db, User, Address, Search
from unittest import TestCase
from pprint import pprint


class TestAddressDeleteOps(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        # Create tables and test user
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            test_user01 = User.register(email="test@testing.com", pwd="123456")
            test_user02 = User.register(email="test2@testing.com", pwd="123456")

            db.session.add_all([test_user01, test_user02])
            db.session.commit()

            address01 = Address(
                user_id=test_user01.id,
                address="200 East 82nd Street NY NY 10028",
                mapbox_id="something_else",
            )

            address02 = Address(
                user_id=test_user02.id,
                address="567 Albany NY 12405",
                mapbox_id="also_somethine_else",
            )

            db.session.add_all([address01, address02])
            db.session.commit()

            self.uid01 = test_user01.id
            self.uid02 = test_user02.id
            self.address_id_01 = address01.id
            self.address_id_02 = address02.id

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login_test_user(self, uid):
        """
        Helper to log in a test user

        :param user: User object to log in
        :returns: Response from login request
        """
        with self.app.app_context():
            user = db.session.query(User).get(uid)

            test = self.client.post(
                "/login",
                data={
                    "email": user.email,
                    "password": "123456",
                },
                follow_redirects=True,
            )

            return test

    def test_can_delete_address(self):
        """
        Logged in users can delete their addresses
        """
        # We need to wrap the test inside the app context for database
        # operations to work
        with self.app.app_context():
            self.login_test_user(self.uid01)

            response = self.client.post(
                "/delete/address",
                json={"addressId": self.address_id_01},
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["msg"], "Deleted address")

            # Check that the address was removed from the db
            saved_address = db.session.get(Address, self.address_id_01)
            self.assertIsNone(saved_address)

    def test_must_be_logged_in(self):
        with self.app.test_client() as client:
            response = client.post(
                "/delete/address",
                json={"addressId": self.address_id_01},
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(response.status_code, 401)
            self.assertEqual(data["msg"], "Login required")

    def test_must_provide_json(self):
        with self.app.app_context():
            self.login_test_user(self.uid01)

            response = self.client.post(
                "/delete/address",
                json={},
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(data["msg"], "No JSON data received")

    def test_can_not_delete_other_user_address(self):
        with self.app.app_context():
            self.login_test_user(self.uid01)

            response = self.client.post(
                "/delete/address",
                json={"addressId": self.address_id_02},
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                data["msg"], "You are not authorized to delete this address"
            )

            # Check that the address was not removed from the db
            saved_address = db.session.get(Address, self.address_id_02)
            self.assertEqual(saved_address.address, "567 Albany NY 12405")

    def test_can_not_delete_address_if_in_search(self):
        with self.app.app_context():
            # Create address and search
            address03 = Address(
                user_id=self.uid01,
                address="654 Dingo Drive Alabama 230495",
                mapbox_id="last_id",
            )
            db.session.add(address03)
            db.session.commit()

            search = Search(
                user_id=self.uid01,
                address_id=address03.id,
                start_date="2024-01-01",
                end_date="2024-02-01",
            )
            db.session.add(search)
            db.session.commit()

            # Login
            self.login_test_user(self.uid01)
            response = self.client.post(
                "/delete/address",
                json={"addressId": address03.id},
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(response.status_code, 409)
            self.assertEqual(
                data["msg"],
                "This address is attached to a search. Please delete the search first.",
            )

            # Check that the address was not removed from the db
            saved_address = db.session.get(Address, address03.id)
            self.assertEqual(saved_address.address, "654 Dingo Drive Alabama 230495")


class TestSearchDeleteOps(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        # Create tables and test user
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            test_user01 = User.register(email="test@testing.com", pwd="123456")
            test_user02 = User.register(email="test2@testing.com", pwd="123456")

            db.session.add_all([test_user01, test_user02])
            db.session.commit()

            address01 = Address(
                user_id=test_user01.id,
                address="200 East 82nd Street NY NY 10028",
                mapbox_id="something_else",
            )

            address02 = Address(
                user_id=test_user02.id,
                address="567 Albany NY 12405",
                mapbox_id="also_somethine_else",
            )

            db.session.add_all([address01, address02])
            db.session.commit()

            search01 = Search(
                user_id=test_user01.id,
                address_id=address01.id,
                start_date="2024-01-01",
                end_date="2024-02-01",
            )
            db.session.add(search01)
            db.session.commit()

            search02 = Search(
                user_id=test_user02.id,
                address_id=address02.id,
                start_date="2024-01-01",
                end_date="2024-02-01",
            )
            db.session.add(search02)
            db.session.commit()

            self.uid01 = test_user01.id
            self.uid02 = test_user02.id
            self.address_id_01 = address01.id
            self.address_id_02 = address02.id
            self.search_id_01 = search01.id
            self.search_id_02 = search02.id

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login_test_user(self, uid):
        """
        Helper to log in a test user

        :param user: User object to log in
        :returns: Response from login request
        """
        with self.app.app_context():
            user = db.session.query(User).get(uid)

            test = self.client.post(
                "/login",
                data={
                    "email": user.email,
                    "password": "123456",
                },
                follow_redirects=True,
            )

            return test

    def test_can_delete_search(self):
        with self.app.app_context():
            self.login_test_user(self.uid01)

            response = self.client.post(
                "/delete/search",
                json={"searchId": self.search_id_01},
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["msg"], "Deleted search")

            # Check that the address was removed from the db
            saved_search = db.session.get(Search, self.search_id_01)
            self.assertIsNone(saved_search)

    def test_must_be_logged_in(self):
        with self.app.test_client() as client:
            response = client.post(
                "/delete/search",
                json={"searchId": self.search_id_01},
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(response.status_code, 401)
            self.assertEqual(data["msg"], "Login required")

    def test_must_provide_json(self):
        with self.app.app_context():
            self.login_test_user(self.uid01)

            response = self.client.post(
                "/delete/search",
                json={},
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(data["msg"], "No JSON data received")

    def test_can_not_delete_other_user_search(self):
        with self.app.app_context():
            self.login_test_user(self.uid01)

            response = self.client.post(
                "/delete/search",
                json={"searchId": self.search_id_02},
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(response.status_code, 403)
            self.assertEqual(
                data["msg"], "You are not authorized to delete this search"
            )

            # Check that the search was not removed from the db
            saved_address = db.session.get(Search, self.search_id_02)
            self.assertIsNotNone(saved_address)
