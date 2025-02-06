"""
General utilities to collect and analyze CDC data
"""

import json
import requests
import pandas as pd
from collections import defaultdict
import math
from tqdm import tqdm
from math import sqrt
from pprint import pprint


def calculate_wilson_score_interval(deaths, cases, confidence=0.95):
    """
    Calculate Wilson score interval for a proportion
    :param deaths: int, number of deaths
    :param cases: int, number of cases
    :param confidence: float, confidence level (default 95%)
    :returns: tuple (low, center, high) confidence bounds
    """
    if cases == 0:
        return 0, 0, 0

    # Calculate proportion
    p = deaths / cases

    # z value for 95% confidence is 1.96
    z = 1.96

    # Wilson score interval formula
    denominator = 1 + z**2 / cases
    center = (p + z**2 / (2 * cases)) / denominator
    spread = z * sqrt((p * (1 - p) + z**2 / (4 * cases)) / cases) / denominator

    return center - spread, center, center + spread


def calculate_base_rates(mortality_data):
    """
    Calculate overall death rates for each category
    """
    base_rates = {}
    for category, data in mortality_data.items():
        total_deaths = sum(
            group["deaths"]
            for group in data.values()
            if group.get("deaths") is not None
        )
        total_cases = sum(
            group["cases"] for group in data.values() if group.get("cases") is not None
        )
        base_rates[category] = total_deaths / total_cases if total_cases > 0 else 0
    return base_rates


def create_multipliers(mortality_data):
    """
    Create multipliers dictionary from mortality data
    """
    # Get base rates
    base_rates = calculate_base_rates(mortality_data)

    # Calculate single category multipliers
    multipliers = {}

    # Process each category
    for category, data in mortality_data.items():
        multipliers[category] = {}

        for group, counts in data.items():
            # Skip non-meaningful categories
            if group in ["NaN", "Unknown", "Missing"]:
                continue

            if counts["cases"] > 0:
                death_rate = counts["deaths"] / counts["cases"]
                low, center, high = calculate_wilson_score_interval(
                    counts["deaths"], counts["cases"]
                )

                multipliers[category][group] = {
                    "multiplier": death_rate / base_rates[category],
                    "confidence_range": {
                        "low": low / base_rates[category],
                        "high": high / base_rates[category],
                    },
                    "sample_size": counts["cases"],
                    "death_rate": death_rate,
                }

    return multipliers


def calculate_intersectional_stats(stats_file):
    """
    Single-pass calculation of intersectional statistics
    Args:
        stats_file: Path to CSV with case/death data
    Returns:
        dict with multipliers and confidence ranges
    """
    print(f"Starting analysis of {stats_file}")

    # Store raw counts for all intersections
    stats = {
        # Double intersections
        "age_race": defaultdict(lambda: {"deaths": 0, "cases": 0}),
        "age_sex": defaultdict(lambda: {"deaths": 0, "cases": 0}),
        "age_ethnicity": defaultdict(lambda: {"deaths": 0, "cases": 0}),
        "race_sex": defaultdict(lambda: {"deaths": 0, "cases": 0}),
        "race_ethnicity": defaultdict(lambda: {"deaths": 0, "cases": 0}),
        "sex_ethnicity": defaultdict(lambda: {"deaths": 0, "cases": 0}),
        # Triple intersections
        "age_race_sex": defaultdict(lambda: {"deaths": 0, "cases": 0}),
        "age_race_ethnicity": defaultdict(lambda: {"deaths": 0, "cases": 0}),
        "age_sex_ethnicity": defaultdict(lambda: {"deaths": 0, "cases": 0}),
        "race_sex_ethnicity": defaultdict(lambda: {"deaths": 0, "cases": 0}),
        # All factors
        "age_race_sex_ethnicity": defaultdict(lambda: {"deaths": 0, "cases": 0}),
    }

    # Process in chunks
    chunksize = 50000  # Smaller chunks to manage memory
    processed_records = 0
    valid_records = 0

    print("Processing data for intersectional statistics...")

    chunks = pd.read_csv(stats_file, chunksize=chunksize, low_memory=False)
    for chunk_num, chunk in enumerate(chunks):
        chunk_valid = 0

        for _, record in chunk.iterrows():
            processed_records += 1

            # Skip records with missing values
            if (
                pd.isna(record["age_group"])
                or pd.isna(record["race"])
                or pd.isna(record["sex"])
                or pd.isna(record["ethnicity"])
            ):
                continue

            valid_records += 1
            chunk_valid += 1

            # Create intersection keys
            # Double intersections
            age_race = f"{record['age_group']}_{record['race']}"
            age_sex = f"{record['age_group']}_{record['sex']}"
            age_ethnicity = f"{record['age_group']}_{record['ethnicity']}"
            race_sex = f"{record['race']}_{record['sex']}"
            race_ethnicity = f"{record['race']}_{record['ethnicity']}"
            sex_ethnicity = f"{record['sex']}_{record['ethnicity']}"

            # Triple intersections
            age_race_sex = f"{record['age_group']}_{record['race']}_{record['sex']}"
            age_race_ethnicity = (
                f"{record['age_group']}_{record['race']}_{record['ethnicity']}"
            )
            age_sex_ethnicity = (
                f"{record['age_group']}_{record['sex']}_{record['ethnicity']}"
            )
            race_sex_ethnicity = (
                f"{record['race']}_{record['sex']}_{record['ethnicity']}"
            )

            # All factors
            all_factors = f"{record['age_group']}_{record['race']}_{record['sex']}_{record['ethnicity']}"

            is_death = record.get("death_yn", "No") == "Yes"

            # Update counts for double intersections
            stats["age_race"][age_race]["cases"] += 1
            stats["age_sex"][age_sex]["cases"] += 1
            stats["age_ethnicity"][age_ethnicity]["cases"] += 1
            stats["race_sex"][race_sex]["cases"] += 1
            stats["race_ethnicity"][race_ethnicity]["cases"] += 1
            stats["sex_ethnicity"][sex_ethnicity]["cases"] += 1

            # Update counts for triple intersections
            stats["age_race_sex"][age_race_sex]["cases"] += 1
            stats["age_race_ethnicity"][age_race_ethnicity]["cases"] += 1
            stats["age_sex_ethnicity"][age_sex_ethnicity]["cases"] += 1
            stats["race_sex_ethnicity"][race_sex_ethnicity]["cases"] += 1

            # Update counts for all factors
            stats["age_race_sex_ethnicity"][all_factors]["cases"] += 1

            if is_death:
                # Update death counts for double intersections
                stats["age_race"][age_race]["deaths"] += 1
                stats["age_sex"][age_sex]["deaths"] += 1
                stats["age_ethnicity"][age_ethnicity]["deaths"] += 1
                stats["race_sex"][race_sex]["deaths"] += 1
                stats["race_ethnicity"][race_ethnicity]["deaths"] += 1
                stats["sex_ethnicity"][sex_ethnicity]["deaths"] += 1

                # Update death counts for triple intersections
                stats["age_race_sex"][age_race_sex]["deaths"] += 1
                stats["age_race_ethnicity"][age_race_ethnicity]["deaths"] += 1
                stats["age_sex_ethnicity"][age_sex_ethnicity]["deaths"] += 1
                stats["race_sex_ethnicity"][race_sex_ethnicity]["deaths"] += 1

                # Update death counts for all factors
                stats["age_race_sex_ethnicity"][all_factors]["deaths"] += 1

        # Save checkpoint and print progress
        if chunk_num % 10 == 0 and chunk_num > 0:
            print(f"Saving intermediate results at {processed_records:,} records...")
            with open(
                f"intersectional_stats_checkpoint_{processed_records}.json", "w"
            ) as f:
                json.dump(stats, f)

        print(
            f"Chunk {chunk_num + 1}: {chunk_valid:,} valid out of {chunksize:,} records."
        )
        print(
            f"Running totals: {valid_records:,} valid out of {processed_records:,} ({(valid_records / processed_records * 100):.1f}%)"
        )

    print(f"\nData processing complete!")
    print(
        f"Final totals: {valid_records:,} valid records out of {processed_records:,} ({(valid_records / processed_records * 100):.1f}%)"
    )
    print("\nCalculating multipliers and confidence intervals...")

    # Calculate multipliers and confidence intervals
    results = {}
    for category, data in stats.items():
        print(f"\nProcessing {category}")
        results[category] = {}

        # Calculate baseline death rate
        total_deaths = sum(group["deaths"] for group in data.values())
        total_cases = sum(group["cases"] for group in data.values())
        baseline_rate = total_deaths / total_cases if total_cases > 0 else 0
        print(f"Baseline death rate: {baseline_rate:.4%}")

        for group, counts in data.items():
            if counts["cases"] >= 1000:  # Minimum sample size
                death_rate = counts["deaths"] / counts["cases"]
                multiplier = death_rate / baseline_rate

                # Calculate confidence interval
                z = 1.96  # 95% confidence level
                n = counts["cases"]
                p = death_rate

                # Wilson score interval
                denominator = 1 + z**2 / n
                center = (p + z**2 / (2 * n)) / denominator
                spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator

                results[category][group] = {
                    "multiplier": multiplier,
                    "confidence_range": {
                        "low": max(0, center - spread),
                        "high": min(1, center + spread),
                    },
                    "sample_size": counts["cases"],
                    "death_rate": death_rate,
                }
                print(
                    f"{group}: {multiplier:.2f}x ({counts['cases']:,} cases, {death_rate:.4%} death rate)"
                )

    print("\nSaving final results to intersectional_multipliers.json")
    # Save results
    with open("intersectional_multipliers.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Analysis complete!")
    return results


def calculate_multipliers(stats):
    with open(stats, "r") as input_file:
        data = json.load(input_file)
        multipliers = {}

        for category, data in data.items():
            multipliers[category] = {}
            # Calculate overall death rate for this category
            total_deaths = sum(group["deaths"] for group in data.values())
            total_cases = sum(group["cases"] for group in data.values())
            baseline_rate = total_deaths / total_cases if total_cases > 0 else 0

            # Calculate multiplier for each group
            for group, counts in data.items():
                if group not in ["NaN", "Unknown", "Missing"] and counts["cases"] > 0:
                    group_rate = counts["deaths"] / counts["cases"]
                    multipliers[category][group] = group_rate / baseline_rate

        return multipliers


# Calcualte intersectional multipliers from CDC source data
# stats = "/home/mswed/Downloads/COVID-19_Case_Surveillance_Public_Use_Data_with_Geography.csv"
# calculate_intersectional_stats(stats)

with open("./mortality_stats.json") as mstats:
    data = json.load(mstats)
    multipliers = create_multipliers(data)
    pprint(multipliers)
    # Save to JSON file
    with open("mortality_multipliers.json", "w") as f:
        json.dump(multipliers, f, indent=2)
