import csv
import json
import os

_AUG_DIR = os.path.join(os.path.dirname(__file__), "..", "county_data", "augmented_data")


def parse_county_data(filepath, state_fips):
    # Normalize state FIPS to exactly 2 digits
    state_fips = str(state_fips).zfill(2)[:2]

    # Create an output dictionary keyed by 5-digit county FIPS code.
    county_data = {}

    # Open the demographics CSV and read rows by header names
    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        # Read each county row and keep only counties in the requested state
        for row in reader:
            county_fips = row["FIPS"].strip().zfill(5)
            if county_fips[:2] != state_fips:
                continue

            # Ensuring proper field types
            population = int(row["population"])
            latitude = float(row["lat"])
            longitude = float(row["lon"])

            # Store normalized county values in the output map
            county_data[county_fips] = {
                "name": row["name"].strip(),
                "state": row["state"].strip(),
                "population": population,
                "lat": latitude,
                "lon": longitude,
            }

    # Ensure the output folder exists before writing JSON
    os.makedirs(_AUG_DIR, exist_ok=True)

    # Build the output file path for this state
    out_path = os.path.join(_AUG_DIR, f"county_data_{state_fips}.json")

    # Write the parsed county data to a formatted JSON file
    with open(out_path, "w", encoding="utf-8") as out:
        json.dump(county_data, out, indent=2)

    # Return the parsed county data for direct reuse by callers
    return county_data


def load_county_data(state_fips):
    # Normalize state FIPS to exactly 2 digits
    state_fips = str(state_fips).zfill(2)[:2]

    # Build the JSON path for the requested state
    path = os.path.join(_AUG_DIR, f"county_data_{state_fips}.json")

    # Open and return the parsed county JSON content
    with open(path, encoding="utf-8") as f:
        return json.load(f)
