import os
from models import db, HistoricDataPoint
from app import create_app
from tqdm import tqdm
import csv

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    path = "./static/data/NWSS_Public_SARS-CoV-2_Wastewater_Metric_Data.csv"
    if os.path.isfile(path):
        # Populate historic data, right now we have date up to 07/2024
        with open(
            "./static/data/NWSS_Public_SARS-CoV-2_Wastewater_Metric_Data.csv"
        ) as f:
            csv_reader = csv.DictReader(f)  # Uses first row as headers

            for record in tqdm(csv_reader):
                dp = HistoricDataPoint(
                    wwtp_jurisdiction=record.get("wwtp_jurisdiction"),
                    wwtp_id=record.get("wwtp_id"),
                    reporting_jurisdiction=record.get("reporting_jurisdiction"),
                    sample_location=record.get("sample_location"),
                    sample_location_specify=record.get("sample_location_specify"),
                    key_plot_id=record.get("key_plot_id"),
                    county_names=record.get("county_names"),
                    county_fips=record.get("county_fips"),
                    population_served=record.get("population_served"),
                    date_start=record.get("date_start"),
                    date_end=record.get("date_end"),
                    ptc_15d=record.get("ptc_15d"),
                    detect_prop_15d=record.get("detect_prop_15d"),
                    percentile=record.get("percentile"),
                    sampling_prior=record.get("sampling_prior"),
                    first_sample_date=record.get("first_sample_date"),
                )
                db.session.add(dp)
                db.session.commit()
            print("Finished!")


test_app = create_app("wikmt_test_db")

with test_app.app_context():
    db.drop_all()
    db.create_all()
