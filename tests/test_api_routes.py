from app import create_app
from models import db
from unittest import TestCase
from pprint import pprint


class TestCovidSearch(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_search_by_dates(self):
        """Test the search_by_dates endpoint returns proper GeoJSON"""
        with self.app.test_client() as client:
            # Make POST request with JSON data
            response = client.post(
                "/search/dates",
                json={"start_date": "2024-01-01", "end_date": "2024-02-01"},
            )

            # Check status code
            self.assertEqual(response.status_code, 200)

            # Get JSON data
            data = response.get_json()

            # Verify it's valid GeoJSON
            self.assertEqual(data["type"], "FeatureCollection")
            self.assertIn("features", data)

            # Check structure of features
            for feature in data["features"]:
                self.assertEqual(feature["type"], "Feature")
                self.assertIn("geometry", feature)
                self.assertIn("properties", feature)

                # Check specific properties
                props = feature["properties"]
                self.assertIn("risk", props)

    def test_failed_search_by_dates(self):
        """Test the search_by_dates endpoint returns proper GeoJSON"""
        with self.app.test_client() as client:
            # Make POST request with JSON data
            response = client.post(
                "/search/dates",
                json={"start_date": "2024-02-01", "end_date": "2024-01-01"},
            )

            # Check status code
            self.assertEqual(response.status_code, 404)

            # Get JSON data
            data = response.get_json()

            # Verify it's valid a failed search
            self.assertEqual(data, {"error": "No records found"})

    def test_search_by_dates_and_location(self):
        """Test the search_by_dates endpoint returns proper GeoJSON"""
        with self.app.test_client() as client:
            # Make POST request with JSON data
            response = client.post(
                "/search/location-dates",
                json={
                    "start_date": "2024-01-01",
                    "end_date": "2024-02-01",
                    "address": "California",
                },
            )

            # Check status code
            self.assertEqual(response.status_code, 200)

            # Get JSON data
            data = response.get_json()

            # Verify it's valid GeoJSON
            self.assertEqual(data["type"], "FeatureCollection")
            self.assertIn("features", data)

            # Check structure of features
            for feature in data["features"]:
                self.assertEqual(feature["type"], "Feature")
                self.assertIn("geometry", feature)
                self.assertIn("properties", feature)

                # Check specific properties
                props = feature["properties"]
                self.assertIn("NAME", props)

    def test_failed_search_by_dates_and_location(self):
        """Test the search_by_dates endpoint returns proper GeoJSON"""
        with self.app.test_client() as client:
            # Make POST request with JSON data
            response = client.post(
                "/search/dates",
                json={
                    "start_date": "2024-02-01",
                    "end_date": "2024-01-01",
                    "address": "Germany",
                },
            )

            # Check status code
            self.assertEqual(response.status_code, 404)

            # Get JSON data
            data = response.get_json()

            # Verify it's valid a failed search
            self.assertEqual(data, {"error": "No records found"})


class TestMapSearch(TestCase):
    def setUp(self):
        """Set up test database and client before each test"""
        self.app = create_app(database="wikmt_test_db", testing=True, csrf=False)
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_address_suggestions(self):
        with self.app.test_client() as client:
            # Make POST request with JSON data
            response = client.get(
                "/search/suggest",
                query_string={"address": "200 East 75 street"},
            )

            # Check status code
            self.assertEqual(response.status_code, 200)

            # Get JSON data
            data = response.get_json()

            # Verify it's correct
            self.assertEqual(
                len(data["data"]["suggestions"]), 10
            )  # We expect 10 results
            self.assertIn(
                {
                    "address": "200 East 75th Street",
                    "context": {
                        "address": {
                            "address_number": "200",
                            "id": "dXJuOm1ieGFkcjphNTRjZGI5Ni1iZjZiLTRjNDAtODFmZS0wZmFmZWI1MmE4Zjk",
                            "name": "200 East 75th Street",
                            "street_name": "East 75th Street",
                        },
                        "country": {
                            "country_code": "US",
                            "country_code_alpha_3": "USA",
                            "id": "dXJuOm1ieHBsYzpJdXc",
                            "name": "United States",
                        },
                        "district": {
                            "id": "dXJuOm1ieHBsYzpBUU5tN0E",
                            "name": "New York County",
                        },
                        "locality": {
                            "id": "dXJuOm1ieHBsYzpGREtLN0E",
                            "name": "Manhattan",
                        },
                        "neighborhood": {
                            "id": "dXJuOm1ieHBsYzpGV0JzN0E",
                            "name": "Lenox Hill",
                        },
                        "place": {"id": "dXJuOm1ieHBsYzpEZTVJN0E", "name": "New York"},
                        "postcode": {"id": "dXJuOm1ieHBsYzpBWG5PN0E", "name": "10021"},
                        "region": {
                            "id": "dXJuOm1ieHBsYzpBYVRz",
                            "name": "New York",
                            "region_code": "NY",
                            "region_code_full": "US-NY",
                        },
                        "street": {
                            "id": "dXJuOm1ieGFkcjphNTRjZGI5Ni1iZjZiLTRjNDAtODFmZS0wZmFmZWI1MmE4Zjk",
                            "name": "East 75th Street",
                        },
                    },
                    "feature_type": "address",
                    "full_address": "200 East 75th Street, New York, "
                    "New York 10021, United States",
                    "language": "en",
                    "maki": "marker",
                    "mapbox_id": "dXJuOm1ieGFkcjphNTRjZGI5Ni1iZjZiLTRjNDAtODFmZS0wZmFmZWI1MmE4Zjk",
                    "metadata": {},
                    "name": "200 East 75th Street",
                    "place_formatted": "New York, New York 10021, United States",
                },
                data["data"]["suggestions"],
            )

    def test_failed_address_suggestions(self):
        with self.app.test_client() as client:
            # Make POST request with JSON data
            response = client.get(
                "/search/suggest",
                query_string={"address": "fdfdsfat"},
            )

            # Check status code
            self.assertEqual(response.status_code, 200)

            # Get JSON data
            data = response.get_json()

            # Verify it's correct
            self.assertEqual(
                len(data["data"]["suggestions"]), 0
            )  # We expect 00 results

    def test_search_address_by_id(self):
        with self.app.test_client() as client:
            # Make POST request with JSON data
            response = client.post(
                "/search/find_address_by_id",
                json={
                    "mapboxId": "dXJuOm1ieGFkcjphNTRjZGI5Ni1iZjZiLTRjNDAtODFmZS0wZmFmZWI1MmE4Zjk"
                },
            )

            # Check status code
            self.assertEqual(response.status_code, 200)

            # Get JSON data
            data = response.get_json()

            self.assertEqual(
                data,
                {
                    "data": {
                        "attribution": "© 2025 Mapbox and its suppliers. All rights "
                        "reserved. Use of this data is subject to the Mapbox "
                        "Terms of Service. "
                        "(https://www.mapbox.com/about/maps/)",
                        "features": [
                            {
                                "geometry": {
                                    "coordinates": [-73.958996, 40.77146],
                                    "type": "Point",
                                },
                                "properties": {
                                    "address": "200 East 75th Street",
                                    "context": {
                                        "address": {
                                            "address_number": "200",
                                            "id": "dXJuOm1ieGFkcjphNTRjZGI5Ni1iZjZiLTRjNDAtODFmZS0wZmFmZWI1MmE4Zjk",
                                            "name": "200 East 75th Street",
                                            "street_name": "East 75th Street",
                                        },
                                        "country": {
                                            "country_code": "US",
                                            "country_code_alpha_3": "USA",
                                            "id": "dXJuOm1ieHBsYzpJdXc",
                                            "name": "United States",
                                        },
                                        "district": {
                                            "id": "dXJuOm1ieHBsYzpBUU5tN0E",
                                            "name": "New York County",
                                        },
                                        "locality": {
                                            "id": "dXJuOm1ieHBsYzpGREtLN0E",
                                            "name": "Manhattan",
                                        },
                                        "neighborhood": {
                                            "id": "dXJuOm1ieHBsYzpGV0JzN0E",
                                            "name": "Lenox Hill",
                                        },
                                        "place": {
                                            "id": "dXJuOm1ieHBsYzpEZTVJN0E",
                                            "name": "New York",
                                        },
                                        "postcode": {
                                            "id": "postcode.3167554343148898",
                                            "name": "10021",
                                        },
                                        "region": {
                                            "id": "dXJuOm1ieHBsYzpBYVRz",
                                            "name": "New York",
                                            "region_code": "NY",
                                            "region_code_full": "US-NY",
                                        },
                                        "street": {
                                            "id": "dXJuOm1ieGFkci1zdHI6YTU0Y2RiOTYtYmY2Yi00YzQwLTgxZmUtMGZhZmViNTJhOGY5",
                                            "name": "East 75th Street",
                                        },
                                    },
                                    "coordinates": {
                                        "accuracy": "rooftop",
                                        "latitude": 40.77146,
                                        "longitude": -73.958996,
                                        "routable_points": [
                                            {
                                                "latitude": 40.771589,
                                                "longitude": -73.958902,
                                                "name": "default",
                                            }
                                        ],
                                    },
                                    "feature_type": "address",
                                    "full_address": "200 East 75th Street, "
                                    "New York, New York "
                                    "10021, United States",
                                    "language": "en",
                                    "maki": "marker",
                                    "mapbox_id": "dXJuOm1ieGFkcjphNTRjZGI5Ni1iZjZiLTRjNDAtODFmZS0wZmFmZWI1MmE4Zjk",
                                    "metadata": {},
                                    "name": "200 East 75th Street",
                                    "name_preferred": "200 East 75th Street",
                                    "place_formatted": "New York, New York "
                                    "10021, United "
                                    "States",
                                },
                                "type": "Feature",
                            }
                        ],
                        "type": "FeatureCollection",
                    },
                    "success": True,
                },
            )

    def test_failed_search_address_by_id(self):
        with self.app.test_client() as client:
            # Make POST request with JSON data
            response = client.post(
                "/search/find_address_by_id",
                json={"mapboxId": "ffdf"},
            )

            # Check status code
            self.assertEqual(response.status_code, 200)

            # Get JSON data
            data = response.get_json()
            self.assertEqual(data["data"]["error"], "Bad id provided")
