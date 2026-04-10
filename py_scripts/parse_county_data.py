import csv
import json
import os

from helper_functions import AUG_DIR, state_fips_2


def parse_county_data(filepath, state_fips):
    state_fips = state_fips_2(state_fips)

    county_data = {}

    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            county_fips = row["FIPS"].strip().zfill(5)
            if county_fips[:2] != state_fips:
                continue

            population = int(row["population"])
            latitude = float(row["lat"])
            longitude = float(row["lon"])

            county_data[county_fips] = {
                "name": row["name"].strip(),
                "state": row["state"].strip(),
                "population": population,
                "lat": latitude,
                "lon": longitude,
            }

    os.makedirs(AUG_DIR, exist_ok=True)

    out_path = os.path.join(AUG_DIR, f"county_data_{state_fips}.json")

    with open(out_path, "w", encoding="utf-8") as out:
        json.dump(county_data, out, indent=2)

    return county_data


def load_county_data(state_fips):
    state_fips = state_fips_2(state_fips)

    path = os.path.join(AUG_DIR, f"county_data_{state_fips}.json")

    with open(path, encoding="utf-8") as f:
        return json.load(f)
