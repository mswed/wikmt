from app import create_app
from models import db
from unittest import TestCase
from pprint import pprint


class TestUtilRoutes(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_fips(self):
        with self.app.test_client() as client:
            response = client.get(
                "/fips",
                query_string={"state": "New York"},
            )

            # Check status code
            self.assertEqual(response.status_code, 200)

            # Get JSON data
            data = response.get_json()
            self.assertEqual(data["fips"], "36")

            response = client.get(
                "/fips",
                query_string={"state": "Kansas"},
            )

            # Check status code
            self.assertEqual(response.status_code, 200)

            # Get JSON data
            data = response.get_json()
            self.assertEqual(data["fips"], "20")

    def test_counties(self):
        """Test the search_by_dates endpoint returns proper GeoJSON"""
        with self.app.test_client() as client:
            response = client.get(
                "/counties",
                query_string={"fips": "20"},
            )

            # Check status code
            self.assertEqual(response.status_code, 200)

            # Get JSON data
            data = response.get_json()
            self.assertIn(
                {
                    "type": "Feature",
                    "properties": {
                        "GEO_ID": "0500000US20029",
                        "STATE": "20",
                        "COUNTY": "029",
                        "NAME": "Cloud",
                        "LSAD": "County",
                        "CENSUSAREA": 715.342,
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-97.368574, 39.567018],
                                [-97.369839, 39.306011],
                                [-97.926096, 39.306517],
                                [-97.929097, 39.306397],
                                [-97.928462, 39.566915],
                                [-97.931844, 39.566921],
                                [-97.931482, 39.653767],
                                [-97.36867, 39.654043],
                                [-97.368653, 39.583833],
                                [-97.368374, 39.577145],
                                [-97.368635, 39.575926],
                                [-97.368574, 39.567018],
                            ]
                        ],
                    },
                    "id": "20029",
                },
                data["features"],
            )

    def test_all_counties(self):
        """Test the search_by_dates endpoint returns proper GeoJSON"""
        with self.app.test_client() as client:
            response = client.get(
                "/static/data/counties.geojson",
            )

            # Check status code
            self.assertEqual(response.status_code, 200)

            # Get JSON data
            data = response.get_json()
            self.assertIn(
                {
                    "type": "Feature",
                    "properties": {
                        "GEO_ID": "0500000US20029",
                        "STATE": "20",
                        "COUNTY": "029",
                        "NAME": "Cloud",
                        "LSAD": "County",
                        "CENSUSAREA": 715.342,
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [
                            [
                                [-97.368574, 39.567018],
                                [-97.369839, 39.306011],
                                [-97.926096, 39.306517],
                                [-97.929097, 39.306397],
                                [-97.928462, 39.566915],
                                [-97.931844, 39.566921],
                                [-97.931482, 39.653767],
                                [-97.36867, 39.654043],
                                [-97.368653, 39.583833],
                                [-97.368374, 39.577145],
                                [-97.368635, 39.575926],
                                [-97.368574, 39.567018],
                            ]
                        ],
                    },
                    "id": "20029",
                },
                data["features"],
            )
