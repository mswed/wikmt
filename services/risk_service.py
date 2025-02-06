from risk_models.mortality_model import MortalityCalculator


class RiskService:
    @staticmethod
    def calculate_death_risk(user, county_risk):
        """
        Calculate death risk based on user demographics and county risk
        :param user: User object with demographic data
        :param county_risk: float, risk score for the county
        :returns: str, Risk category
        """
        age_group = user.get_age_group()
        calculator = MortalityCalculator(
            age_group, user.sex, user.race, user.ethnicity, float(county_risk)
        )
        return calculator.risk_category
