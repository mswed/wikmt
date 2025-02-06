from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Location:
    """
    A location class, used by the DataPoint class
    """

    state: str
    county: str


def risk_category(score):
    """
    Get a risk category based on a risk factor
    :param score: float, calculated risk score
    :returns: str, risk category
    """
    if score >= 80:
        risk_category = "Very High"
    elif score >= 60:
        risk_category = "High"
    elif score >= 40:
        risk_category = "Medium"
    elif score >= 20:
        risk_category = "Low"
    else:
        risk_category = "Very Low"

    return risk_category


class GeographicRegion:
    """
    A class representing a geographic region (state, county, etc.) containing
    waste water treatment facilities. Used to calculate aggregate risk metrics.
    """

    def __init__(self, facilities: List, name=None, county_names=None) -> None:
        """
        :param facilities: list, list of facility data
        :param name: str, optional name of county if available.
        """
        self.name = (
            facilities[0].state if name is None else name
        )  # We either get the name from the first record or get it from Flask
        self.facilities = facilities
        self._monitored_population = 0

        self.risk_categories = ["Very Low", "Low", "Medium", "High", "Very High"]

    def __repr__(self) -> str:
        return f"<GeographicRegion name: {self.name} facility_count: {self.facility_count}>"

    @property
    def facility_count(self):
        """
        How many facilities are in this region?
        :returns: int, number of facilities
        """
        return len(self.facilities)

    @property
    def monitored_population(self):
        """
        How many people are served by the facilities
        :returns: int, population served by facilities in region
        """
        if not self._monitored_population:
            self._monitored_population = sum(
                [f.population_served for f in self.facilities]
            )
        return self._monitored_population

    def risk_score(self):
        """
        Spread/Risk of COVID in the region weighted for the served population
        :returns: float, weighted risk scre
        """
        weighted_risk_score = 0
        for facility in self.facilities:
            population_weight = facility.population_served / self.monitored_population
            weighted_risk_score += facility.latest.risk_score * population_weight
        return weighted_risk_score

    def risk_category(self):
        """
        Get the region risk categry based on its risk score
        :returns: str, risk category
        """
        return risk_category(self.risk_score())

    def risk_id(self):
        """
        The map needs an id number instead of a string. This converts our risk category
        To a number based on the category list
        :returns: int, risk category ID (0-4)
        """
        if self.facility_count > 0:
            return self.risk_categories.index(self.risk_category())
        return 404

    def risk_trend(self):
        """
        Gets the trend in the facility. Is the spread getting worse, better, or is static?
        :returns: str, trend direction
        """
        if self.facility_count == 0:
            return "static"

        trend = sum([f.risk_trend() for f in self.facilities]) / self.facility_count
        if trend < 0:
            return "decreasing"
        elif trend > 0:
            return "increasing"
        return "static"


class WWTP:
    """
    A class containing a Waste Water Treatment plant info, for a specific range of dates
    """

    def __init__(self, site_data: List) -> None:
        """
        :param site_data: list, facility data from the API, usually provided by a search
        """
        self.site_id = site_data[0]["wwtp_id"]
        self.population_served = int(site_data[0]["population_served"])
        self.state = site_data[0]["wwtp_jurisdiction"]
        self.county = site_data[0]["county_names"]
        self.county_fips = site_data[0]["county_fips"]
        self._latest = None
        self._monitoring_period = 0

        self.site_data = sorted(site_data, key=lambda x: x["date_end"])
        self.sampling_dates = [dp["date_end"] for dp in self.site_data]
        self.unique_samples = len(set(self.sampling_dates))

        self.risk_over_time = [DataPoint(dp) for dp in self.site_data]

    def __repr__(self) -> str:
        return f"<WWTP site_id: {self.site_id} population_served: {self.population_served} state: {self.state} county: {self.county}>"

    @property
    def latest(self):
        """
        Get the last sample in the facility
        """
        if self._latest is None:
            self._latest = self.risk_over_time[-1]
        return self._latest

    @property
    def monitoring_period(self):
        """
        Get the facility's monitoring period (this may change based on our search)
        :returns: int, number of days monitored
        """
        if not self._monitoring_period:
            date_format = "%Y-%m-%d"
            first_date = datetime.strptime(self.sampling_dates[0], date_format)
            last_date = datetime.strptime(self.sampling_dates[-1], date_format)
            self._monitoring_period = (last_date - first_date).days

        return self._monitoring_period

    @property
    def all_readings(self):
        """
        All of the samples collected by the facility
        :returns: list, risk score for each datapoint collected
        """
        return [r.risk_score for r in self.risk_over_time]

    def monitoring_info(self):
        """
        Information about the monitored data: how many samples were taken, how many days
        were monitored and average days between the samples
        :returns: dict, {total_samples, days_monitored, avg_days_between_samples}
        """
        return {
            "total_samples": self.unique_samples,
            "days_monitored": self.monitoring_period,
            "avg_days_between_samples": self.monitoring_period
            / max(self.unique_samples - 1, 1),
        }

    def mean_risk(self):
        """
        Mean of found risk
        """
        return sum(self.all_readings) / len(self.risk_over_time)

    def risk_trend(self):
        """
        The facility's risk trend as a number
        :returns: int, -1 decreasing, 0 static, 1 increasing
        """
        if len(self.risk_over_time) > 1:
            if self.risk_over_time[-1].risk_score > self.risk_over_time[-2].risk_score:
                direction = 1
            elif (
                self.risk_over_time[-1].risk_score < self.risk_over_time[-2].risk_score
            ):
                direction = -1
            else:
                direction = 0
        else:
            direction = 0

        return direction

    def percentile_trend(self):
        """
        The risk trend percentile
        """
        return (
            self.risk_over_time[-1].precentile > self.risk_over_time[-2].precentile,
        )


class DataPoint:
    """
    A single data point for a single wwtp. Used to calculate the
    data point risk factor and category
    """

    def __init__(self, data_point: Dict) -> None:
        # Convert data
        self.precentile = float(data_point.get("percentile", 0) or 0)
        self.ptc_15d = float(data_point.get("ptc_15d", 0) or 0)
        self.detect_prop = float(data_point.get("detect_prop_15d", 0) or 0)
        self.population_served = (int(data_point.get("population_served", 0) or 0),)
        self.date_end = (data_point.get("date_end", ""),)
        self.location = Location(
            state=data_point.get("wwtp_jurisdiction", ""),
            county=data_point.get("county_names", ""),
        )
        self.validate()

    def __repr__(self) -> str:
        return f"<DataPoint: date_end: {self.date_end} precentile: {self.precentile} ptc_15d: {self.ptc_15d} score: {self.risk_score} category: {self.risk_category}>"

    @property
    def trend_score(self):
        return min(max((self.ptc_15d + 100) / 2, 0), 100)

    @property
    def risk_score(self):
        """
        The datapoint's risk score
        :returns: float, data point risk score
        """
        return (
            (self.precentile * 0.45)
            + (self.trend_score * 0.40)
            + (self.detect_prop * 0.15)
        )

    @property
    def risk_category(self):
        """
        The data point's risk category based on its score
        :returns: str, risk category
        """
        return risk_category(self.risk_score)

    def validate(self):
        """
        The API contains unreasonable values at time, this function tries to clean it up
        """
        # Precentiles need to be with in 0-100
        if self.precentile > 100 or self.precentile < 0:
            self.precentile = 0
        if self.detect_prop > 100 or self.detect_prop < 0:
            self.detect_prop = 0
        # A change of more than 1000% is unlikely
        if abs(self.ptc_15d) > 1000:
            self.ptc_15d = 0
