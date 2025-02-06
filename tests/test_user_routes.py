from app import create_app
from models import db, User
from unittest import TestCase
from pprint import pprint


class TestHomePage(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        # Create tables and test user
        with self.app.app_context():
            db.create_all()
            self.test_user = User.register(email="test@testing.com", pwd="123456")
            db.session.add(self.test_user)
            db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_not_logged_in(self):
        with self.app.test_client() as client:
            res = client.get("/")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

            # Check that each column has something in it
            self.assertIn("<h4>Recently Saved Searches</h4>", html)
            self.assertIn('<h5 class="card-title">Date Range</h5>', html)
            self.assertIn("<span>Very Low Risk</span>", html)

    def test_user_logged_in(self):
        with self.app.test_client() as client:
            # Login
            res = client.post(
                "/login",
                data={"email": "test@testing.com", "password": "123456"},
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            self.assertIn(
                '<span class="badge fs-5 text-center rounded-pill my-2 text-bg-success">Logged in!</span>',
                html,
            )

            res = client.get("/")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

            # Check that each column has something in it
            self.assertIn('id="search-button"', html)
            self.assertIn('<div class="card-header">Saved Addresses</div>', html)

    def test_failed_login(self):
        with self.app.test_client() as client:
            # Login
            res = client.post(
                "/login",
                data={"email": "testno@testing.com", "password": "123456"},
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(
                '<span class="badge fs-5 text-center rounded-pill my-2 text-bg-danger">Invalid username/password</span>',
                html,
            )

    def test_can_logout(self):
        with self.app.test_client() as client:
            # Login
            res = client.post(
                "/login",
                data={"email": "test@testing.com", "password": "123456"},
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            self.assertIn(
                '<span class="badge fs-5 text-center rounded-pill my-2 text-bg-success">Logged in!</span>',
                html,
            )

            res = client.post("/logout", follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Logout Successful", html)

            # Check that each column has something in it
            self.assertIn("<h4>Recently Saved Searches</h4>", html)
            self.assertIn('<h5 class="card-title">Date Range</h5>', html)
            self.assertIn("<span>Very Low Risk</span>", html)


class TestRegister(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        # Create tables and test user
        with self.app.app_context():
            db.create_all()
            self.test_user = User.register(email="test@testing.com", pwd="123456")
            db.session.add(self.test_user)
            db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_not_logged_in(self):
        with self.app.test_client() as client:
            res = client.get("/register")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

            # Check that we got the form
            self.assertIn(
                "<h6>Optional Data - Filling these fields will allow you to get statistic that are more specific to you</h6>",
                html,
            )

    def test_user_is_logged_in(self):
        """
        If the user is logged in we should redirect to the home page and display
        a warning
        """
        with self.app.test_client() as client:
            # Login
            res = client.post(
                "/login",
                data={"email": "test@testing.com", "password": "123456"},
                follow_redirects=True,
            )

            # Try to register
            res = client.get("/register", follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

            # Check that we got a warning
            self.assertIn(
                "You are already logged in!",
                html,
            )
            # Check that we were redirected to the home page (logged in version)
            self.assertIn('<div class="card-header">Saved Addresses</div>', html)

    def test_can_register(self):
        with self.app.test_client() as client:
            res = client.post(
                "/register",
                data={
                    "register-email": "dingo@bingo.com",
                    "register-password": "fun_stuff",
                    "register-birth_year": "1990",
                    "register-sex": "Female",
                    "register-race": "Asian",
                    "register-ethnicity": "Non-Hispanic",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

            # Check that we got the flash
            self.assertIn(
                "Registered User",
                html,
            )
            # Check that we were redirected to the home page (logged out version)
            self.assertIn("<h4>Recently Saved Searches</h4>", html)

    def test_birth_year_must_be_valid_year(self):
        with self.app.test_client() as client:
            res = client.post(
                "/register",
                data={
                    "register-email": "dingo@bingo.com",
                    "register-password": "fun_stuff",
                    "register-birth_year": "2040",
                    "register-sex": "Female",
                    "register-race": "Asian",
                    "register-ethnicity": "Non-Hispanic",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

            # Check that we got the flash
            self.assertIn(
                "Failed to register because",
                html,
            )
            self.assertIn(
                "birth_year: Number must be between 1900 and 2025.",
                html,
            )
            # Check that we were redirected to the home page (logged out version)
            self.assertIn(
                "<h6>Optional Data - Filling these fields will allow you to get statistic that are more specific to you</h6>",
                html,
            )

    def test_birth_year_can_be_empty(self):
        with self.app.test_client() as client:
            res = client.post(
                "/register",
                data={
                    "register-email": "dingo@bingo.com",
                    "register-password": "fun_stuff",
                    "register-birth_year": "1990",
                    "register-sex": "Female",
                    "register-race": "Asian",
                    "register-ethnicity": "Non-Hispanic",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

            # Check that we got the flash
            self.assertIn(
                "Registered User",
                html,
            )
            # Check that we were redirected to the home page (logged out version)
            self.assertIn("<h4>Recently Saved Searches</h4>", html)

    def test_must_have_unique_email(self):
        with self.app.test_client() as client:
            res = client.post(
                "/register",
                data={
                    "register-email": "test@testing.com",
                    "register-password": "fun_stuff",
                    "register-birth_year": "1990",
                    "register-sex": "Female",
                    "register-race": "Asian",
                    "register-ethnicity": "Non-Hispanic",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)

            # Check that we got the flash
            self.assertIn("User test@testing.com already exists!", html)
            # Check that we are still in the register page
            self.assertIn(
                "<h6>Optional Data - Filling these fields will allow you to get statistic that are more specific to you</h6>",
                html,
            )

    def test_password_must_be_8_chars(self):
        with self.app.test_client() as client:
            res = client.post(
                "/register",
                data={
                    "register-email": "dingo@bingo.com",
                    "register-password": "123456",
                    "register-birth_year": "2040",
                    "register-sex": "Female",
                    "register-race": "Asian",
                    "register-ethnicity": "Non-Hispanic",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

            # Check that we got the flash
            self.assertIn(
                "Failed to register because",
                html,
            )
            self.assertIn(
                "password: Password must be at least 8 characters long",
                html,
            )
            # Check that we were redirected to the home page (logged out version)
            self.assertIn(
                "<h6>Optional Data - Filling these fields will allow you to get statistic that are more specific to you</h6>",
                html,
            )

    def test_must_provide_email_and_password(self):
        with self.app.test_client() as client:
            res = client.post(
                "/register",
                data={
                    "register-email": "",
                    "register-password": "",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            # Check that we got the flash
            self.assertIn("Failed to register because", html)
            self.assertIn("email: This field is required", html)
            self.assertIn("password: This field is required", html)
            # Check that we are still in the register page
            self.assertIn(
                "<h6>Optional Data - Filling these fields will allow you to get statistic that are more specific to you</h6>",
                html,
            )


class TestAccount(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

        # Create tables and test user
        with self.app.app_context():
            db.create_all()
            self.test_user = User.register(
                email="test@testing.com",
                pwd="123456",
                birth_year="1990",
                sex="Female",
                race="Asian",
                ethnicity="Non-Hispanic",
            )

            db.session.add(self.test_user)
            db.session.commit()

            self.user_id = self.test_user.id

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
        """
        If the user is logged in we should redirect to the home page and display
        a warning
        """
        with self.app.test_client() as client:
            res = client.get("/account", follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

            # Check that we got the form
            self.assertIn(
                "Login required",
                html,
            )

    def test_user_is_logged_in(self):
        with self.app.test_client() as client:
            # Login
            res = client.post(
                "/login",
                data={"email": "test@testing.com", "password": "123456"},
                follow_redirects=True,
            )

            # Try to show account info
            res = client.get("/account")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)

            # Check that we got the account page
            self.assertIn(
                "<h2>Account Details</h2>",
                html,
            )
            self.assertIn(
                "Update Password",
                html,
            )
            self.assertIn(
                "Update Personal Info",
                html,
            )

    def test_can_update_login(self):
        with self.app.app_context():
            self.login_test_user(self.user_id)

            user = db.session.get(User, self.user_id)
            old_password = user.password

            res = self.client.post(
                "/account/update-login",
                data={
                    "login-update-email": "test@testing.com",
                    "login-update-password": "123456",
                    "login-update-new_password": "ding dong",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            self.assertIn("Login details have been updated!", html)

            updated_user = db.session.get(User, self.user_id)
            self.assertNotEqual(updated_user.password, old_password)

    def test_password_must_be_8_chars(self):
        with self.app.app_context():
            self.login_test_user(self.user_id)

            user = db.session.get(User, self.user_id)
            old_password = user.password

            res = self.client.post(
                "/account/update-login",
                data={
                    "login-update-email": "test@testing.com",
                    "login-update-password": "123456",
                    "login-update-new_password": "123",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            # Check that we got the flash
            self.assertIn(
                "Failed to update login because:",
                html,
            )
            self.assertIn(
                "password: Password must be at least 8 characters long",
                html,
            )

            updated_user = db.session.get(User, self.user_id)
            self.assertEqual(updated_user.password, old_password)

    def test_login_only_updates_if_correct_pass(self):
        with self.app.app_context():
            self.login_test_user(self.user_id)

            user = db.session.get(User, self.user_id)
            old_password = user.password

            res = self.client.post(
                "/account/update-login",
                data={
                    "login-update-email": "test@testing.com",
                    "login-update-password": "blah",
                    "login-update-new_password": "ding dong",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            self.assertIn("Wrong password", html)

            updated_user = db.session.get(User, self.user_id)
            self.assertEqual(updated_user.password, old_password)

    def test_login_only_updates_if_not_empty(self):
        """
        The user must provide the old password and the old one to update the login
        """
        with self.app.app_context():
            self.login_test_user(self.user_id)

            user = db.session.get(User, self.user_id)
            old_password = user.password

            res = self.client.post(
                "/account/update-login",
                data={
                    "login-update-email": "test@testing.com",
                    "login-update-password": "blah",
                    "login-update-new_password": "",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            self.assertIn("new_password: This field is required.", html)

            updated_user = db.session.get(User, self.user_id)
            self.assertEqual(updated_user.password, old_password)

    def test_can_update_profile(self):
        with self.app.app_context():
            self.login_test_user(self.user_id)
            res = self.client.post(
                "/account/update",
                data={
                    "account-update-birth_year": "1978",
                    "account-update-sex": "Male",
                    "account-update-race": "Black",
                    "account-update-ethnicity": "Hispanic",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            self.assertIn("Successfully updated user details!", html)

            updated_user = db.session.get(User, self.user_id)
            self.assertEqual(updated_user.birth_year, 1978)
            self.assertEqual(updated_user.sex, "Male")
            self.assertEqual(updated_user.race, "Black")
            self.assertEqual(updated_user.ethnicity, "Hispanic")

    def test_updated_birth_year_must_be_valid(self):
        with self.app.app_context():
            self.login_test_user(self.user_id)
            res = self.client.post(
                "/account/update",
                data={
                    "account-update-birth_year": "2040",
                    "account-update-sex": "Male",
                    "account-update-race": "Black",
                    "account-update-ethnicity": "Hispanic",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            # Check that we got the flash
            self.assertIn("Failed to update user details because", html)
            self.assertIn(
                "birth_year: Number must be between 1900 and 2025.",
                html,
            )

    def test_can_update_profile_only_when_logged_in(self):
        with self.app.test_client() as client:
            res = client.post(
                "/account/update",
                data={
                    "account-update-birth_year": "1978",
                    "account-update-sex": "Male",
                    "account-update-race": "Black",
                    "account-update-ethnicity": "Hispanic",
                },
                follow_redirects=True,
            )
            html = res.get_data(as_text=True)
            # Get a warning and redirect to homepage
            self.assertIn("<h4>Recently Saved Searches</h4>", html)

            with self.app.app_context():
                # User info has not changed
                updated_user = db.session.get(User, self.user_id)
                self.assertEqual(updated_user.birth_year, 1990)
                self.assertEqual(updated_user.sex, "Female")
                self.assertEqual(updated_user.race, "Asian")
                self.assertEqual(updated_user.ethnicity, "Non-Hispanic")
