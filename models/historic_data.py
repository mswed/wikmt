from . import db


class HistoricDataPoint(db.Model):
    """
    Historic Data from the CDC
    """

    __tablename__ = "historic"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wwtp_jurisdiction = db.Column(db.Text)
    wwtp_id = db.Column(db.Text)
    reporting_jurisdiction = db.Column(db.Text)
    sample_location = db.Column(db.Text)
    sample_location_specify = db.Column(db.Text)
    key_plot_id = db.Column(db.Text)
    county_names = db.Column(db.Text)
    county_fips = db.Column(db.Text)
    population_served = db.Column(db.Text)
    date_start = db.Column(db.Date)
    date_end = db.Column(db.Date)
    ptc_15d = db.Column(db.Text)
    detect_prop_15d = db.Column(db.Text)
    percentile = db.Column(db.Text)
    sampling_prior = db.Column(db.Text)
    first_sample_date = db.Column(db.Date)

    def to_dict(self):
        return {
            "wwtp_jurisdiction": self.wwtp_jurisdiction,
            "wwtp_id": self.wwtp_id,
            "reporting_jurisdiction": self.reporting_jurisdiction,
        }
