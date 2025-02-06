from app import create_app
from models import db, User, Address, Search
from unittest import TestCase
from pprint import pprint


class TestSearchLoadOps(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        # Create tables and test user
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            test_user01 = User.register(email="test@testing.com", pwd="123456")

            db.session.add(test_user01)
            db.session.commit()

            address01 = Address(
                user_id=test_user01.id,
                address="200 East 82nd Street NY NY 10028",
                mapbox_id="something_else",
            )

            db.session.add(address01)
            db.session.commit()

            search01 = Search(
                user_id=test_user01.id,
                address_id=address01.id,
                start_date="2024-01-01",
                end_date="2024-02-01",
            )
            db.session.add(search01)
            db.session.commit()

            self.uid01 = test_user01.id
            self.address_id_01 = address01.id
            self.search_id_01 = search01.id

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

    def test_can_load_search(self):
        response = self.client.post(
            "/load/search",
            json={"searchId": self.search_id_01},
        )

        data = response.get_json()

        # Check that we got the correct response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            data["success"],
            {
                "address": "200 East 82nd Street NY NY 10028",
                "mapboxId": "something_else",
                "startDate": "2024-01-01",
                "endDate": "2024-02-01",
            },
        )
