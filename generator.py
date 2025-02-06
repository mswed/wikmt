import json
import random
from datetime import datetime, timedelta
from pprint import pprint
import math
from states import stateFipsToName


def create_counties_list(path):
    county_list = []
    with open(path) as county_data:
        counties = json.load(county_data)
        for c in counties["features"]:
            county = {
                "fips": c.get("id"),
                "state": stateFipsToName.get(c["properties"]["STATE"]),
                "name": c["properties"]["NAME"],
            }
            county_list.append(county)
    pprint(county_list)

    return county_list


class RiskPattern:
    """Generate consistent risk patterns for geographic regions"""

    def __init__(self, base_risk, volatility):
        self.base_risk = base_risk  # Base risk level (0-100)
        self.volatility = volatility  # How much the risk varies over time
        self.trend = random.uniform(-0.5, 0.5)  # Overall trend direction

    def get_risk_values(self, date, base_offset=0):
        """Generate risk values for a specific date"""
        days_since_start = (date - datetime(2023, 1, 1)).days

        # Create a seasonal pattern with yearly cycle
        seasonal = math.sin(2 * math.pi * days_since_start / 365) * 10

        # Add trend component
        trend = self.trend * days_since_start / 30

        # Add random noise
        noise = random.gauss(0, self.volatility)

        # Combine components and ensure within bounds
        base = max(0, min(100, self.base_risk + seasonal + trend + noise + base_offset))

        # Generate consistent values for each metric
        percentile = min(100.0, max(0.0, base + random.uniform(-5, 5)))
        ptc_15d = int((base - 50) * 10)  # Convert to integer percent change
        detect_prop = int(min(100, max(60, base + random.uniform(-10, 10))))

        return {
            "percentile": percentile,
            "ptc_15d": ptc_15d,
            "detect_prop": detect_prop,
        }


def generate_wwtp_timeseries(wwtp, start_date, end_date, risk_pattern):
    """Generate time series data for a single WWTP"""
    time_series_data = []
    current_date = start_date

    # Create facility-specific offset
    facility_offset = random.uniform(-10, 10)

    while current_date <= end_date:
        # Random sampling interval between 7-14 days
        sampling_interval = random.randint(7, 14)
        sample_end_date = current_date + timedelta(days=14)

        # Get risk values for this date
        risk_values = risk_pattern.get_risk_values(current_date, facility_offset)

        record = {
            **wwtp,
            "date_start": current_date.strftime("%Y-%m-%d"),
            "date_end": sample_end_date.strftime("%Y-%m-%d"),
            "ptc_15d": risk_values["ptc_15d"],  # Already integer
            "detect_prop_15d": risk_values["detect_prop"],  # Already integer
            "percentile": risk_values["percentile"],  # Already float
            "sampling_prior": "no",
            "first_sample_date": current_date.strftime("%Y-%m-%d"),
        }

        time_series_data.append(record)
        current_date += timedelta(days=sampling_interval)

    return time_series_data


def generate_county_wwtps(county, base_id, county_risk_pattern):
    """Generate WWTPs for a single county"""
    wwtps = []
    num_wwtps = random.randint(1, 5)

    for i in range(num_wwtps):
        wwtp_id = base_id + i  # Integer ID
        population_served = random.randint(5000, 500000)  # Integer population
        location_specify = str(random.randint(100, 999))

        wwtps.append(
            {
                "wwtp_jurisdiction": county["state"],
                "wwtp_id": wwtp_id,  # Integer
                "reporting_jurisdiction": county["state"],
                "sample_location": "Before treatment plant",
                "sample_location_specify": location_specify,
                "key_plot_id": f"NWSS_{county['state'].lower()[:2]}_{wwtp_id}_Before treatment plant_{location_specify}_raw wastewater",
                "county_names": county["name"],
                "county_fips": county["fips"],
                "population_served": population_served,  # Integer
            }
        )

    return wwtps


def generate_state_risk_patterns(counties):
    """Generate base risk patterns for each state"""
    state_patterns = {}
    for county in counties:
        if county["state"] not in state_patterns:
            state_patterns[county["state"]] = RiskPattern(
                base_risk=random.uniform(30, 70), volatility=random.uniform(3, 8)
            )
    return state_patterns


def generate_county_risk_patterns(counties, state_patterns):
    """Generate risk patterns for each county based on state patterns"""
    county_patterns = {}
    for county in counties:
        state_pattern = state_patterns[county["state"]]
        county_patterns[county["fips"]] = RiskPattern(
            base_risk=state_pattern.base_risk + random.uniform(-10, 10),
            volatility=state_pattern.volatility * random.uniform(0.8, 1.2),
        )
    return county_patterns


def generate_wwtp_data(
    counties, start_date_str="2023-01-01", end_date_str="2025-01-31"
):
    """Main function to generate all WWTP data"""
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Generate risk patterns
    state_patterns = generate_state_risk_patterns(counties)
    county_patterns = generate_county_risk_patterns(counties, state_patterns)

    all_data = []
    base_id = 1000

    for county in counties:
        county_wwtps = generate_county_wwtps(
            county, base_id, county_patterns[county["fips"]]
        )
        base_id += len(county_wwtps)

        for wwtp in county_wwtps:
            time_series_data = generate_wwtp_timeseries(
                wwtp, start_date, end_date, county_patterns[county["fips"]]
            )
            all_data.extend(time_series_data)

    return all_data


def save_to_json(data, output_file):
    """Save generated data to a JSON file"""
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)


# Example usage:
if __name__ == "__main__":
    sample_counties = create_counties_list(
        "/home/mswed/Documents/coding/springboard/capstone/wikmt/static/data/counties.geojson"
    )

    wwtp_data = generate_wwtp_data(
        counties=sample_counties, start_date_str="2023-01-01", end_date_str="2025-01-31"
    )

    save_to_json(
        wwtp_data,
        "/home/mswed/Documents/coding/springboard/capstone/wikmt/static/data/wwtp_data.json",
    )
    print(f"Generated {len(wwtp_data)} records for {len(sample_counties)} counties")
