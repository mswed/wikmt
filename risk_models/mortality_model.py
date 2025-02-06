import json
import os
from pprint import pprint
from flask import current_app


class MortalityCalculator:
    """
    Calculate chances of death based on user demograpics and current county Covid spread
    """

    def __init__(
        self, age, sex=None, race=None, ethnicity=None, county_risk_score=50.00
    ):
        self.age = age
        self.sex = sex
        self.race = race
        self.ethnicity = ethnicity
        self.county_risk_score = county_risk_score

        self.intersectional_multipliers = self.load_intersectional_multipliers()
        self.base_multipliers = self.load_base_multipliers()

    @property
    def risk_category(self):
        return self.calc_risk_category(self.calculate_personalized_risk()[0])

    def load_intersectional_multipliers(self):
        """
        Load the intersectional multipliers list from disk
        """
        # We need to use the current flask app to get the file path
        file_path = os.path.join(
            current_app.root_path, "risk_models", "intersectional_multipliers.json"
        )
        with open(file_path) as multipliers:
            return json.load(multipliers)

    def load_base_multipliers(self):
        """
        Load the base multipliers list from disk
        """
        # We need to use the current flask app to get the file path
        file_path = os.path.join(
            current_app.root_path, "risk_models", "mortality_multipliers.json"
        )
        with open(file_path) as multipliers:
            return json.load(multipliers)

    def calc_risk_category(self, score):
        """
        Return a category based on the risk level
        :returns: str, categry
        """
        # Determine the risk category
        if score >= 80:
            risk_category = "Absolutly it will"
        elif score >= 60:
            risk_category = "Probably"
        elif score >= 40:
            risk_category = "Maybe?"
        elif score >= 20:
            risk_category = "Probably not"
        else:
            risk_category = "I don't think so"

        return risk_category

    def apply_multiplier(self, risk_score, multiplier_data):
        """
        Apply a risk multiplier while keeping score in 0-100 range
        :param risk_score: float, base wastewater risk (0-100)
        :param multiplier_data: dict, multiplier and confidence ranges
        returns: Adjusted risk score (0-100)
        """
        # Apply multiplier and dampen once at the end
        risk = risk_score * multiplier_data["multiplier"]

        # Apply dampening to final result
        dampened_risk = risk_score + (risk - risk_score) * 0.2

        # Cap between 0-100
        return min(max(dampened_risk, 0), 100)

    def calculate_personalized_risk(self):
        """
        Calculate the personal risk based on the user's demograpics
        :returns: list(risk, confidence)
        """
        # Calculate combined multiplier
        combined_multiplier = 1.0
        total_sample_size = 0

        for factor, value in [
            ("age_groups", self.age),
            ("sex", self.sex),
            ("race", self.race),
            ("ethnicity", self.ethnicity),
        ]:
            if value and value in self.base_multipliers[factor]:
                current_multiplier = self.base_multipliers[factor][value]["multiplier"]
                combined_multiplier *= current_multiplier
                total_sample_size += self.base_multipliers[factor][value]["sample_size"]

        # Calculate final risk with single dampening
        raw_risk = self.county_risk_score * combined_multiplier

        dampened_risk = (
            self.county_risk_score + (raw_risk - self.county_risk_score) * 0.2
        )

        final_risk = min(max(dampened_risk, 0), 100)

        # Calculate confidence intervals
        confidence = {
            "low": self.county_risk_score
            + (
                self.county_risk_score * combined_multiplier * 0.8
                - self.county_risk_score
            )
            * 0.2,
            "high": self.county_risk_score
            + (
                self.county_risk_score * combined_multiplier * 1.2
                - self.county_risk_score
            )
            * 0.2,
            "sample_size": total_sample_size,
        }

        confidence["low"] = min(max(confidence["low"], 0), 100)
        confidence["high"] = min(max(confidence["high"], 0), 100)

        return final_risk, confidence
