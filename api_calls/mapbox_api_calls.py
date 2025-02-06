import requests
from uuid import uuid4
from flask import session

MAPBOX_TOKEN = "pk.eyJ1Ijoid2lsc29ucHVkZG5oZWFkIiwiYSI6ImNsd2UwY2Y3ZDA3N2Uyam10dmFtMmZmMTkifQ.dGeq-h9UrNpca716xUCzKA"
MAPBOX_API_BASE_URL = "https://api.mapbox.com/search/searchbox/v1/"


def create_query(address):
    """
    Query mapbox api
    :returns: json, found records in the db
    """
    params = {"access_token": MAPBOX_TOKEN}
    params["q"] = address
    data = requests.get(
        MAPBOX_API_BASE_URL + "forward",
        params=params,
    ).json()

    if "message" in data:
        return {"success": False, "error": data["message"]}, 500

    if not data:
        print("returning", data)
        return {"success": False, "data": data}, 404

    print("results", data)
    return {"success": True, "data": data}, 200


def suggest_addresses(address):
    """
    Get address suggestions from the API. Oce the user provides 3 characters of an address
    a list of locations is returned
    :param address: str, address to search for
    :returns: json, up to 10 suggested addresses
    """
    # Suggesting addresses requires a token
    if "mapbox_session_token" not in session:
        session["mapbox_session_token"] = str(uuid4())

    params = {
        "access_token": MAPBOX_TOKEN,
        "q": address,
        "limit": "10",
        "session_token": session["mapbox_session_token"],
        "types": "region, postcode, district, city, street, address",
        "country": "US",
    }
    data = requests.get(
        MAPBOX_API_BASE_URL + "suggest",
        params=params,
    ).json()

    if "message" in data:
        return {"success": False, "error": data["message"]}, 500

    return {"success": True, "data": data}, 200


def select_address(mapbox_id):
    """
    Select an address from the address suggestions based on its mapbox_id
    :param mapbox_id: str, selected address mapbox_id
    :returns: json, address details
    """
    # Getting an addresses requires a token
    if "mapbox_session_token" not in session:
        session["mapbox_session_token"] = str(uuid4())

    params = {
        "access_token": MAPBOX_TOKEN,
        "session_token": session["mapbox_session_token"],
    }
    data = requests.get(
        MAPBOX_API_BASE_URL + f"retrieve/{mapbox_id}",
        params=params,
    ).json()

    if "message" in data:
        return {"success": False, "error": data["message"]}, 500

    return {"success": True, "data": data}, 200
