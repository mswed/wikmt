from app import create_app
from models import db, User
from unittest import TestCase
from flask_login import login_user
from pprint import pprint


class TestDeathRoute(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        # Create tables and test user
        with self.app.app_context():
            db.create_all()

            self.very_low_risk_user = User.register(
                email="test@testing.com",
                pwd="123456",
                birth_year="1995",
                sex="Female",
                race="Asian",
                ethnicity="Non-Hispanic",
            )

            self.low_risk_user = User.register(
                email="test2@testing.com",
                pwd="123456",
                birth_year="1990",
                sex="Male",
                race="White",
                ethnicity="Hispanic",
            )

            self.medium_risk_user = User.register(
                email="test3@testing.com",
                pwd="123456",
                birth_year="1975",
                sex="Male",
                race="Black",
                ethnicity="Hispanic",
            )

            self.high_risk_user = User.register(
                email="test4@testing.com",
                pwd="123456",
                birth_year="1965",
                sex="Female",
                race="Black",
                ethnicity="Non-Hispanic",
            )

            self.very_high_risk_user = User.register(
                email="test5@testing.com",
                pwd="123456",
                birth_year="1940",
                sex="Male",
                race="American Indian/Alaska Native",
                ethnicity="Non-Hispanic",
            )
            db.session.add_all(
                [
                    self.very_low_risk_user,
                    self.low_risk_user,
                    self.medium_risk_user,
                    self.high_risk_user,
                    self.very_high_risk_user,
                ]
            )
            db.session.commit()

            self.very_low_risk_user_uid = self.very_low_risk_user.id
            self.low_risk_user_uid = self.low_risk_user.id
            self.medium_risk_user_uid = self.medium_risk_user.id
            self.high_risk_user_uid = self.high_risk_user.id
            self.very_high_risk_user_uid = self.very_high_risk_user.id

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

    def test_user_not_logged_in(self):
        """Test death risk calculation without login"""
        response = self.client.get(
            "/death",
            query_string={"risk_score": "20.00"},
            headers={"Accept": "application/json"},
        )

        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data["msg"], "Login required")

    def test_user_is_very_low_risk(self):
        """Test death risk calculation for very low risk user"""
        with self.client as client:
            self.login_test_user(self.very_low_risk_user_uid)

            response = self.client.get("/death", query_string={"risk_score": "15.00"})
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertEqual(data["success"], True)
            self.assertEqual(data["msg"], "I don't think so")

    def test_user_is_low_risk(self):
        """Test death risk calculation for low risk user"""
        with self.client as client:
            self.login_test_user(self.low_risk_user_uid)

            response = self.client.get("/death", query_string={"risk_score": "40.00"})
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertEqual(data["success"], True)
            self.assertEqual(data["msg"], "Probably not")

    def test_user_is_medium_risk(self):
        """Test death risk calculation for medium risk user"""
        with self.client as client:
            self.login_test_user(self.medium_risk_user_uid)

            response = self.client.get("/death", query_string={"risk_score": "60.00"})
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertEqual(data["success"], True)
            self.assertEqual(data["msg"], "Maybe?")

    def test_user_is_high_risk(self):
        """Test death risk calculation for high risk user"""
        with self.client as client:
            self.login_test_user(self.high_risk_user_uid)

            response = self.client.get("/death", query_string={"risk_score": "80.00"})
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertEqual(data["success"], True)
            self.assertEqual(data["msg"], "Probably")

    def test_user_is_very_high_risk(self):
        """Test death risk calculation for very high risk user"""
        with self.client as client:
            self.login_test_user(self.very_high_risk_user_uid)

            response = self.client.get("/death", query_string={"risk_score": "100.00"})
            self.assertEqual(response.status_code, 200)

            data = response.get_json()
            self.assertEqual(data["success"], True)
            self.assertEqual(data["msg"], "Absolutly it will")

    def test_invalid_risk_score(self):
        """Test with invalid risk score"""
        with self.client as client:
            self.login_test_user(self.very_high_risk_user_uid)

            response = self.client.get("/death", query_string={"risk_score": "Invalid"})
            self.assertEqual(response.status_code, 400)

            data = response.get_json()
            self.assertEqual(data["success"], False)
            self.assertEqual(data["msg"], "Invalid risk score")
