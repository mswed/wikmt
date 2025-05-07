import os
import logging
from flask import (
    Flask,
    render_template,
    jsonify,
    redirect,
    url_for,
    flash,
    request,
    send_from_directory,
)
from flask_login import LoginManager, login_required, current_user
from models import connect_db, db, User
from services import (
    address_service,
    auth_service,
    home_service,
    search_service,
    user_service,
    risk_service,
    geo_service,
)
from api_calls.covid_api_calls import build_state_map, build_county_map
from api_calls.mapbox_api_calls import suggest_addresses, select_address
from forms import LoginForm, RegisterForm, SearchForm, LoginUpdateForm, PersonalInfoForm

# Configure logging at the top of your file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(database='wikmt_db', echo=False, redirects=True, testing=False, csrf=True):
    """
    Create a flask app
    :param database: str, database to connect to
    :param echo: bool, should SQLALchemy printout the code it's running? Default False
    :param redirects: bool, should flask follow redirects? Default True
    :param testing: bool, Are we runningn in testing mode? Default False
    :param csrf: bool, should we use csrf in WTF? Default True (set to false when testing)
    """

    logger.info('Starting application initialization')
    app = Flask(__name__)
    #
    # @app.before_request
    # def log_request_info():
    #     logger.info(f'Request received: {request.method} {request.path}')
    #     return None
    #
    # @app.after_request
    # def log_request_end(response):
    #     logger.info(
    #         f'Request completed: {request.method} {request.path} - Status: {response.status_code}'
    #     )
    #     return response
    #
    # # Log the database URL (with credential info hidden)
    # db_url = os.environ.get('DATABASE_URL', f'postgresql:///{database}')
    #
    # if 'postgresql://' in db_url:
    #     # Don't log the full URL with credentials
    #     logger.info(f'Database URL is configured: {db_url.split("@")[-1]}')
    # else:
    #     logger.info(f'Database URL: {db_url}')
    #
    # # Get DB_URI from environ variable (useful for production/testing) or,
    # # if not set there, use development local db.
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    #     'DATABASE_URL', f'postgresql:///{database}'
    # )
    #
    # logger.info('Configuring SQLAlchemy')
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_ECHO'] = echo
    # app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = redirects
    # app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
    # app.config['TESTING'] = testing
    # app.config['WTF_CSRF_ENABLED'] = csrf
    #
    # logger.info('Connecting to database')
    # try:
    #     connect_db(app)
    #     logger.info('Database connection successful')
    # except Exception as e:
    #     logger.info(f'Database connection failed {e}')
    #
    # # Set up flask-login
    # login_manager = LoginManager()
    # login_manager.init_app(app)
    #
    # # What to do when the user isn't logged it
    # login_manager.login_view = 'home'  # Redirect to home
    # login_manager.login_message = 'Login required!'
    # login_manager.login_message_category = 'danger'
    #
    # @login_manager.unauthorized_handler
    # def unauthorized():
    #     """Handle unauthorized access to protected routes"""
    #     if request.is_json or (
    #         request.accept_mimetypes.best == 'application/json' and not request.form
    #     ):
    #         return jsonify({'success': False, 'msg': 'Login required'}), 401
    #
    #     # Add the flash message before redirecting
    #     flash(login_manager.login_message, category=login_manager.login_message_category)
    #     return redirect(url_for('home'))
    #
    # @login_manager.user_loader
    # def load_user(user_id):
    #     """
    #     Flask-Login function to log the user in
    #     :param user_id: str, user ID. This is passed as a string and needs to be
    #     converted to int
    #     :returns: User
    #     """
    #     return db.session.query(User).get(int(user_id))

    ########################### NAVIGAGTION ##################################
    @app.route('/')
    def home():
        """
        Get the home page, which has both the login form and the search form
        """
        login_form = LoginForm()

        if current_user.is_authenticated:
            # We have a logged in user
            search_form = SearchForm()
            data = home_service.get_authenticated_home_data(current_user.id)
            return render_template(
                'map_logged_in.html',
                login_form=login_form,
                search_form=search_form,
                **data,
            )
        # The user is not logged in
        data = home_service.get_public_home_data()
        return render_template('map_logged_out.html', login_form=login_form, **data)

    @app.route('/login', methods=['POST'])
    def login():
        """
        Login to the site
        :returns: The home page, either as a render_template or as a redirect depending on the operation
        """

        # If user is already logged in, just redirect to home
        if current_user.is_authenticated:
            return redirect(url_for('home'))

        form = LoginForm()

        if not form.validate_on_submit():
            # Invalid login
            flash('User/Password can not be empty', 'danger')
            return redirect(url_for('home'))

        user = auth_service.authenticate_user(form.email.data, form.password.data)
        if not user:
            flash('Invalid username/password', 'danger')
            return redirect(url_for('home'))

        # Authentication was successful marked the user as logged in
        auth_service.login_user(user)
        return redirect(url_for('home'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """
        Register to the site
        """

        if current_user.is_authenticated:
            # The user is already logged in send them back to the home page
            flash('You are already logged in!', 'danger')
            return redirect(url_for('home'))

        # Set up the forms
        register_form = RegisterForm(prefix='register')
        login_form = LoginForm(prefix='login')

        if request.method == 'GET':
            # This is a get request show the fors
            return render_template('register.html', form=register_form, login_form=login_form)

        if not register_form.validate_on_submit():
            # Form validation failed warn the user
            flash('Failed to register because:', 'danger')
            for field, msg in register_form.errors.items():
                print(f'{field}: {msg[0]}')
                flash(f'{field}: {msg[0]}')
            return redirect(url_for('register'))

        # Try to register the user
        user, error = auth_service.register_user(
            email=register_form.email.data,
            password=register_form.password.data,
            birth_year=register_form.birth_year.data,
            sex=register_form.sex.data,
            race=register_form.race.data,
            ethnicity=register_form.ethnicity.data,
        )

        if error:
            # Registartion failed warn the user
            flash(error, 'danger')
            return redirect(url_for('register'))

        # Registertion was successful
        flash('Registered User! Please Log in...', 'success')
        return redirect(url_for('home'))

    @app.route('/account', methods=['GET'])
    @login_required
    def account():
        """
        Show account info
        :returns: Account page with user info
        """
        login_form = LoginForm(prefix='login')

        user, error = user_service.get_user_by_id(current_user.id)
        if error:
            flash(error, 'danger')
            return redirect(url_for('home'))

        login_update_form = LoginUpdateForm(obj=user, prefix='login-update')
        account_update_form = PersonalInfoForm(obj=user, prefix='account-update')

        # Handle get requests
        return render_template(
            'account.html',
            login_form=login_form,
            login_update_form=login_update_form,
            account_update_form=account_update_form,
            user=user,
        )

    @app.route('/account/update-login', methods=['POST'])
    @login_required
    def update_login():
        """
        Update the user's password
        """
        user, error = user_service.get_user_by_id(current_user.id)
        if error:
            flash(error, 'danger')
            return redirect(url_for('home'))

        login_update_form = LoginUpdateForm(prefix='login-update')

        if not login_update_form.validate_on_submit():
            flash('Failed to update login because:', 'danger')
            for field, msg in login_update_form.errors.items():
                print(f'{field}: {msg[0]}')
                flash(f'{field}: {msg[0]}')
            return redirect(url_for('account'))

        updated_user, error = user_service.update_user_password(
            user, login_update_form.password.data, login_update_form.new_password.data
        )
        if error:
            flash(error, 'danger')
            return redirect(url_for('account'))

        flash('Login details have been updated!', 'success')
        return redirect(url_for('account'))

    @app.route('/account/update', methods=['POST'])
    @login_required
    def update_details():
        """
        Update the user's details
        """
        user, error = user_service.get_user_by_id(current_user.id)
        if error:
            flash(error, 'danger')
            return redirect(url_for('home'))

        personal_info_form = PersonalInfoForm(prefix='account-update')

        if not personal_info_form.validate_on_submit():
            # Form validation failed warn the user
            flash('Failed to update user details because:', 'danger')
            for field, msg in personal_info_form.errors.items():
                print(f'{field}: {msg[0]}')
                flash(f'{field}: {msg[0]}')
            return redirect(url_for('account'))

        updated_user, error = user_service.update_user_details(
            user,
            personal_info_form.birth_year.data,
            personal_info_form.sex.data,
            personal_info_form.race.data,
            personal_info_form.ethnicity.data,
        )

        if error:
            print('Error is', error)
            flash(error, 'danger')
            return redirect(url_for('account'))

        flash('Successfully updated user details!', 'success')
        return redirect(url_for('account'))

    @app.route('/logout', methods=['POST'])
    @login_required
    def logout():
        """
        Log out of the site
        """
        auth_service.logout_user()
        flash('Logout Successful', 'success')
        return redirect(url_for('home'))

    @app.route('/about')
    def about():
        """
        Show the about page
        """
        login_form = LoginForm()
        return render_template('about.html', login_form=login_form)

    ############################ SEARCH COVID API ##################################

    @app.route('/search/dates', methods=['POST'])
    def search_by_dates():
        """
        End point to search the api and update the map. This is called by js on site load
        and when the user searches the database without providing an address. It returns
        state data
        :returns: json, state boundries and risk factors
        """
        start_date = request.json.get('start_date')
        end_date = request.json.get('end_date')
        return build_state_map(start_date, end_date)

    @app.route('/search/location-dates', methods=['POST'])
    def search_by_location_and_dates():
        """
        End point to search the api and update the map. This is called by js
        when the user searches the database with an address AND dates.
        The address field is actually the jurisdiction (State).
        :returns: json, state boundries and risk factors
        """
        start_date = request.json.get('start_date')
        end_date = request.json.get('end_date')
        address = request.json.get('address')

        return build_county_map(start_date, end_date, address)

    ############################ SEARCH MAPBOX API ##################################

    @app.route('/search/suggest')
    def suggest_address():
        address = request.args.get('address')
        return suggest_addresses(address)

    @app.route('/search/find_address_by_id', methods=['POST'])
    def find_address_by_id():
        address_id = request.json.get('mapboxId')

        # TODO: handle bad ids?
        return select_address(address_id)

    ############################ CALCULATE RISK OF DEATH ##################################

    @app.route('/death')
    @login_required
    def calculate_death_chance():
        try:
            # Get the query data from the user
            county_risk = request.args.get('risk_score', 0.00)
            user, error = user_service.get_user_by_id(current_user.id)

            if error:
                return jsonify({'success': False, 'msg': error}), 400

            death_risk = risk_service.calculate_death_risk(user, county_risk)
            return jsonify({'success': True, 'msg': death_risk}), 200
        except ValueError:
            return jsonify({'success': False, 'msg': 'Invalid risk score'}), 400

    ############################ SAVE OPERATIONS ##################################

    @app.route('/save/address', methods=['POST'])
    @login_required
    def save_address():
        # Get all required data from request
        search_address = request.json.get('address')
        mapbox_id = request.json.get('mapbox_id')

        address, error = address_service.create_address(current_user.id, search_address, mapbox_id)
        if error:
            return jsonify({'success': False, 'msg': error}), 400

        if not address:
            # Just in case we get None
            return jsonify({'success': False, 'msg': 'Failed to create address'}), 400

        return jsonify({'success': True, 'msg': 'Saved address', 'address_id': address.id})

    @app.route('/save/search', methods=['POST'])
    @login_required
    def save_search():
        # Get all required data from request
        start_date = request.json.get('start_date')
        end_date = request.json.get('end_date')
        address = request.json.get('address')
        mapbox_id = request.json.get('mapbox_id')

        search, error = search_service.create_search(
            current_user.id, start_date, end_date, address, mapbox_id
        )
        if error:
            return jsonify({'success': False, 'msg': error}), 400

        if not search:
            # Just in case we get None
            return jsonify({'success': False, 'msg': 'Failed to create search'}), 400

        return jsonify({'success': True, 'msg': 'Saved search', 'search_id': search.id})

    ############################ DELETE OPERATIONS ##################################

    @app.route('/delete/address', methods=['POST'])
    @login_required
    def delete_address():
        # Check if we have JSON data
        if not request.json:
            return jsonify({'success': False, 'msg': 'No JSON data received'}), 422

        # Get all required data from request
        address_id = request.json.get('addressId')

        success, message, status_code = address_service.delete_address(current_user.id, address_id)
        return jsonify({'success': success, 'msg': message}), status_code

    @app.route('/delete/search', methods=['POST'])
    @login_required
    def delete_search():
        if not request.json:
            return jsonify({'success': False, 'msg': 'No JSON data received'}), 422

        search_id = request.json.get('searchId')
        success, message, status_code = search_service.delete_search(current_user.id, search_id)

        return jsonify({'success': success, 'msg': message}), status_code

    ############################ LOAD OPERATIONS ##################################

    @app.route('/load/search', methods=['POST'])
    def load_search():
        """
        Loads a saved search into the UI. Called by app_control_lo.
        """
        if not request.json:
            return jsonify({'success': False, 'msg': 'No JSON data received'}), 422
        search_id = request.json.get('searchId')

        success, message, status_code = search_service.load_search(search_id)

        return jsonify({'success': success, 'msg': message}), status_code

    ############################ UTILS ##################################
    @app.route('/fips')
    def get_fips():
        """Get FIPS code for a state"""
        state = request.args.get('state')
        if not state:
            return jsonify({'success': False, 'msg': 'State parameter required'}), 400

        data, error, status_code = geo_service.get_state_fips(state)
        if error:
            return jsonify({'success': False, 'msg': error}), status_code

        return jsonify({'success': True, **data}), status_code

    @app.route('/counties')
    def build_counties():
        """Get counties geojson for a state"""
        fips = request.args.get('fips')
        if not fips:
            return jsonify({'success': False, 'msg': 'FIPS parameter required'}), 400

        data, error, status_code = geo_service.get_counties_by_fips(fips)
        if error:
            return jsonify({'success': False, 'msg': error}), status_code

        return jsonify(data), status_code

    @app.route('/static/data/counties.geojson')
    def get_all_counties():
        """
        Returns a geojson of all US counties
        """
        return send_from_directory('static/data', 'counties.geojson')

    @app.route('/health')
    def health_check():
        return 'OK', 200

    @app.route('/test-log')
    def test_log():
        logger.info('Test log route was accessed!')
        return 'This is a test log route'

    logger.info('Application initialized successfully')

    return app


app = create_app()
