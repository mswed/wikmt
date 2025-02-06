import json
from pprint import pprint
import requests
from collections import defaultdict
from typing import DefaultDict
import logging
from sqlalchemy import or_

from risk_models.ww_risk_model import GeographicRegion, WWTP
from states import us_states
from models import HistoricDataPoint
from requests.exceptions import JSONDecodeError

CDC_APP_TOKEN = "cKqpxnVxCfF4ZuZmymC16v7OU"
COVID_API_URL = "https://data.cdc.gov/resource/nT8mc-b4w4.json"
COVID_WASTEWATERP_API_URL = "https://data.cdc.gov/resource/2ew6-ywp6.json"

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
logger.setLevel("DEBUG")


def query_cdc(statements):
    """
    Query the WWTP covid CDC api.
    :param statements: dict, SQL like statements for the search
    :returns: json, found records in the db
    """
    logger.debug("Accessing CDC dataset 2ew6-ywp6.json")
    params = {"$$app_token": CDC_APP_TOKEN}
    params = params | statements
    res = requests.get(
        COVID_WASTEWATERP_API_URL,
        params=params,
    )

    if res.status_code != 200:
        logger.debug(f"CDC query failed with status {res.status_code}")
        # Figure our where the error is stored
        try:
            # Try to get JSON error message
            error_detail = res.json()
        except JSONDecodeError:
            # If not JSON, get text content
            error_detail = res.text

        if res.status_code == 404:
            # The CDC website is still down
            return {"success": False, "msg": "CDC website could not be reached"}, 404
        else:
            return {"success": False, "msg": f"Unexpected error: {error_detail}"}, 500

    data = res.json()
    logger.debug(f"CDC query was successful and returned {res}")
    return {"success": True, "data": data}, 200


def query_historic_data(start_date, end_date, jurisdiction=None, override=None):
    """
    Query the historic WWTP covid data
    :param start_date: str, start date of sampling
    :param end_date: str, end date of sampling
    :returns: json, found records in the db
    """

    if jurisdiction is None:
        # State level search
        logger.debug("State level search")
        logger.debug(f"date_start <= {end_date} AND date_end >= {start_date}")
        results = HistoricDataPoint.query.filter(
            HistoricDataPoint.date_start <= end_date,
            HistoricDataPoint.date_end >= start_date,
        ).all()
        logger.debug(f"Results are: {results}")
    else:
        # County level search
        logger.debug("County level search")
        if override is None:
            # Normal County search
            logger.debug(
                f"date_start <= {end_date} AND date_end >= {start_date} AND wwtp_jurisdiction == {jurisdiction}"
            )
            results = HistoricDataPoint.query.filter(
                HistoricDataPoint.wwtp_jurisdiction == jurisdiction,
                HistoricDataPoint.date_start <= end_date,
                HistoricDataPoint.date_end >= start_date,
            ).all()
            logger.debug(f"Results are: {results}")

        else:
            # Special county search (like NYC)
            results = HistoricDataPoint.query.filter(
                or_(
                    HistoricDataPoint.wwtp_jurisdiction == jurisdiction,
                    HistoricDataPoint.wwtp_jurisdiction == override,
                ),
                HistoricDataPoint.date_start <= end_date,
                HistoricDataPoint.date_end >= start_date,
            ).all()

    if results:
        data = [item.to_dict() for item in results]
        return {"success": True, "data": data}, 200
    else:
        return {"success": False, "error": "No records found"}, 404


def calculate_counties_risk_factor(records):
    """
    Calcualte risk factor for database records
    :param records: dict, records from database to process
    :returns: list(GeographicRegion), states and their risk factor
    """
    # Create a default dictionary to avoid key errors
    facilities: DefaultDict[str, list] = defaultdict(list)

    # We first collect the organize each facility data so we have
    # one record for each facility containing all of its data
    for record in records:
        wwtp_id = record["wwtp_id"]
        facilities[wwtp_id].append(record)

    county_data = defaultdict(list)

    # Then we convert the facility into a class and add them to the county
    for facility_data in facilities.values():
        # Grab the first sample record so we can collect some general data
        first_record = facility_data[0]
        # Some facilities belong to more than one county
        facility_counties_fips = first_record["county_fips"].split(",")
        for fc in facility_counties_fips:
            county_data[fc].append(WWTP(facility_data))

    # Finally we create the county class and calculate the risk score
    counties = []
    for fips, plants in county_data.items():
        counties.append(GeographicRegion(plants, fips))

    for county in counties:
        logger.debug(county)
    return counties


def calculate_states_risk_factor(records):
    """
    Calcualte risk factor for database records
    :param records: dict, records from database to process
    :returns: list(GeographicRegion), states and their risk factor
    """
    # Create a default dictionary to avoid key errors
    facilities: DefaultDict[str, list] = defaultdict(list)

    # We first collect the facilities data
    for record in records:
        wwtp_id = record["wwtp_id"]
        facilities[wwtp_id].append(record)

    state_data = defaultdict(list)

    # Then we convert them to a class and add them to the state
    for facility_data in facilities.values():
        wwtp = WWTP(facility_data)
        state_data[wwtp.state].append(WWTP(facility_data))

    # Finally we create the state class and calculate the risk score
    states = []
    for state, plants in state_data.items():
        states.append(GeographicRegion(plants))

    return states


def build_states_json(states):
    """
    Takes a list of states and their risk factors and attaches them to the
    states boundry json
    :param states: list(GeographicRegion), list of states and their risk factors
    :returns: json, states boundries and risk factor
    """
    with open("./static/data/statesRisk.geojson", "r") as f:
        template = json.load(f)
        for s in states:
            # Find risk data
            state = s.name
            risk = s.risk_id()

            try:
                # Search the template for the state
                target = [
                    t for t in template["features"] if state == t["properties"]["name"]
                ][0]
                # Set the state's risk level
                target["properties"]["risk"] = risk
            except IndexError:
                target = None

        return template


def build_counties_json(counties, state):
    """
    Takes a list of states and their risk factors and attaches them to the
    states boundry json
    :param counties: list(GeographicRegion), list of counties and their risk factors
    :param state: str, name of states the counties are in
    :returns: json, county boundries and risk factor
    """
    fips = us_states[state]["fips"]
    with open("./static/data/counties.geojson") as input_file:
        # Build a map of only the counties in the selected state
        data = json.load(input_file)
        selected_state_counties = [
            c for c in data["features"] if c["properties"]["STATE"] == fips
        ]

        if selected_state_counties:
            for c in counties:
                # Go through our list of counties and their risk factor
                county_fips = c.name

                try:
                    # Search the template for the county
                    target = [
                        county
                        for county in selected_state_counties
                        if county_fips == county["id"]
                    ][0]
                    props = target["properties"]
                    # Set the state's risk level
                    props["risk_id"] = c.risk_id()
                    props["risk_score"] = c.risk_score()
                    props["risk_category"] = c.risk_category()
                    props["risk_trend"] = c.risk_trend()
                    props["monitored_population"] = c.monitored_population
                    props["facility_count"] = c.facility_count

                except IndexError as e:
                    target = None

        map = {"type": "FeatureCollection", "features": selected_state_counties}
        return map


def build_state_map(start_date, end_date):
    """
    Search the WWTP database for a range of dates, calculate the state risk factor for these dates
    :param start_date: str, sampling start date
    :param end_date: str, sampling end date
    :returns: json, state boundries and risk factors
    """
    # We first query the CDC, hopefully it's back online
    res, status_code = query_cdc(
        {"$where": f"date_start <= '{end_date}' AND date_end >= '{start_date}'"}
    )
    if status_code != 200:
        # The CDC website is still down, try getting historic data instead
        res, status_code = query_historic_data(start_date, end_date)
        if status_code == 404:
            return {"error": "No historic records found"}

    if not res["data"]:
        logger.debug(
            f"No results for: date_start <= '{end_date}' AND date_end >= '{start_date}'"
        )
        return {"error": "No records found"}, 404

    states = calculate_states_risk_factor(res["data"])
    states_risk_json = build_states_json(states)

    return (states_risk_json, 200)


def build_county_map(start_date, end_date, jurisdiction):
    """
    Search the WWTP database for a range of dates in a specific state, calculate the state risk factor for these dates
    :param start_date: str, sampling start date
    :param end_date: str, sampling end date
    :returns: json, state boundries and risk factors
    """
    # Some jurisdictions have multiple areas for example NYC is its own juristictions with in NY State
    overrides = {"New York": "New York City"}

    # We first query the CDC database, hoping that it's still around
    query = f"date_start <= '{end_date}' AND date_end >= '{start_date}' AND wwtp_jurisdiction = '{jurisdiction}'"
    if jurisdiction in overrides.keys():
        query = f"date_start <= '{end_date}' AND date_end >= '{start_date}' AND (wwtp_jurisdiction = '{jurisdiction}' OR wwtp_jurisdiction = '{overrides[jurisdiction]}')"
    res, status_code = query_cdc({"$where": query})

    if status_code != 200:
        # The CDC website is still down, try getting historic data instead
        res, status_code = query_historic_data(
            start_date, end_date, jurisdiction, override=overrides.get("jurisdiction")
        )
        if status_code == 404:
            return {"error": "No historic records found"}, 404

    if not res["data"]:
        return {"error": "No records found"}, 404

    counties = calculate_counties_risk_factor(res["data"])
    counties_risk_json = build_counties_json(counties, jurisdiction)

    return counties_risk_json
