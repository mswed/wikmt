from app import create_app
from models import db, User, Address, Search
from unittest import TestCase
from pprint import pprint


class TestAddressSaveOps(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        # Create tables and test user
        with self.app.app_context():
            db.create_all()
            test_user = User.register(email="test@testing.com", pwd="123456")
            db.session.add(test_user)
            db.session.commit()

            self.uid = test_user.id

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

    def test_can_save_address(self):
        with self.app.app_context():
            self.login_test_user(self.uid)

            response = self.client.post(
                "/save/address",
                json={
                    "address": "200 East 82nd Street NY NY 10028",
                    "mapbox_id": "somestring",
                },
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(data["msg"], "Saved address")
            saved_address = db.session.get(Address, data["address_id"])
            self.assertEqual(saved_address.address, "200 East 82nd Street NY NY 10028")

    def test_must_be_logged_in(self):
        with self.app.test_client() as client:
            response = client.post(
                "/save/address",
                json={
                    "address": "200 East 82nd Street NY NY 10028",
                    "mapbox_id": "somestring",
                },
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(data["msg"], "Login required")

    def test_must_provide_fields(self):
        with self.app.app_context():
            self.login_test_user(self.uid)

            response = self.client.post("/save/address", json={"address": "an address"})

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(
                data["msg"], "Missing required fields (address, mapbox_id)"
            )


class TestSearchSaveops(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        # Create tables and test user
        with self.app.app_context():
            db.create_all()
            test_user = User.register(email="test@testing.com", pwd="123456")
            db.session.add(test_user)
            db.session.commit()

            address = Address(
                user_id=test_user.id,
                address="564 Broadway, Albany, NY 12005",
                mapbox_id="dfulaffda",
            )

            db.session.add(address)
            db.session.commit()

            self.uid = test_user.id
            self.address_id = address.id

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

    def test_can_save_search(self):
        with self.app.app_context():
            self.login_test_user(self.uid)

            response = self.client.post(
                "/save/search",
                json={
                    "start_date": "2024-01-01",
                    "end_date": "2024-02-01",
                    "address": "564 Broadway, Albany, NY 12005",
                    "mapbox_id": "dfulaffda",
                },
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(data["msg"], "Saved search")
            saved_search = db.session.get(Search, data["search_id"])
            self.assertEqual(saved_search.address.id, 2)

    def test_can_save_search_for_new_address(self):
        with self.app.app_context():
            self.login_test_user(self.uid)

            response = self.client.post(
                "/save/search",
                json={
                    "start_date": "2024-01-01",
                    "end_date": "2024-02-01",
                    "address": "110 West 44 Street, NY NY 10022",
                    "mapbox_id": "bloopgoop",
                },
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(data["msg"], "Saved search")

            saved_search = db.session.get(Search, data["search_id"])
            saved_address = Address.query.filter_by(mapbox_id="bloopgoop").first()
            self.assertEqual(saved_search.address.id, saved_address.id)

    def test_must_be_logged_in(self):
        with self.app.test_client() as client:
            response = client.post(
                "/save/search",
                json={
                    "start_date": "2024-01-01",
                    "end_date": "2024-02-01",
                    "address": "564 Broadway, Albany, NY 12005",
                    "mapbox_id": "dfulaffda",
                },
            )

            data = response.get_json()

            # Check that we got the correct response
            self.assertEqual(data["msg"], "Login required")
