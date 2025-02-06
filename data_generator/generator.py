import json
from pprint import pprint
from ..states import stateFipsToName


def create_counties_list(path):
    county_list = []
    with open(path) as county_data:
        counties = json.load(county_data)
        for c in counties:
            county = {
                "fips": c.get("id"),
                "state": stateFipsToName.get(c["properties"]["STATE"]),
                "name": c["properties"]["NAME"],
            }
            county_list.append(county)
    pprint(county_list)

    return county_list
