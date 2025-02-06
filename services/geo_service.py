import json
from states import us_states


class GeoService:
    def __init__(self):
        self.counties_file_path = "./static/data/counties.geojson"

    @staticmethod
    def get_state_fips(state):
        """
        Get FIPS code for a state
        :param state: str, state abbreviation
        :returns: tuple(data dict or None, error message or None, status code)
        """
        try:
            fips = us_states[state]["fips"]
            return {"fips": fips}, None, 200
        except KeyError:
            return None, f"State {state} not found", 404

    def get_counties_by_fips(self, fips):
        """
        Get counties for a state by FIPS code
        :param fips: str, state FIPS code
        :returns: tuple(geojson dict or None, error message or None, status code)
        """
        try:
            with open(self.counties_file_path) as input_file:
                data = json.load(input_file)
                counties = [
                    c for c in data["features"] if c["properties"]["STATE"] == fips
                ]

                if not counties:
                    return None, f"No counties found for FIPS code {fips}", 404

                return {"type": "FeatureCollection", "features": counties}, None, 200

        except FileNotFoundError:
            return None, "Counties data file not found", 404
        except json.JSONDecodeError:
            return None, "Invalid counties data file", 500
        except Exception as e:
            return None, str(e), 500
