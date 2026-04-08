import csv
import json
import os

_AUG_DIR = os.path.join(os.path.dirname(__file__), "..", "county_data", "augmented_data")


def parse_county_data(filepath, state_fips):
    """
    Read demographics CSV with columns: FIPS, name, state, population, lat, lon.
    FIPS are zero-padded to 5 digits.
    """
    state_fips = str(state_fips).zfill(2)[:2]
    rows = {}
    with open(filepath, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = {h.lower().strip(): h for h in reader.fieldnames or []}

        def col(*names):
            for n in names:
                if n in fields:
                    return fields[n]
            return None

        fcol = col("fips", "geoid", "countyfips")
        ncol = col("name", "ctyname", "county_name")
        scol = col("state", "stname", "state_name")
        pcol = col("population", "popestimate2025", "pop")
        lat_col = col("lat", "intptlat", "latitude")
        lon_col = col("lon", "intptlong", "longitude")
        if not all([fcol, ncol, scol, pcol, lat_col, lon_col]):
            raise ValueError(
                "CSV must include FIPS, name, state, population, lat, lon (flexible column names)."
            )

        for row in reader:
            fp = str(row[fcol]).strip().replace('"', "")
            if len(fp) < 5:
                fp = fp.zfill(5)
            if not fp.startswith(state_fips):
                continue
            name = row[ncol].strip()
            st = row[scol].strip()
            try:
                pop = int(float(row[pcol]))
            except (TypeError, ValueError):
                continue
            try:
                lat = float(row[lat_col])
                lon = float(row[lon_col])
            except (TypeError, ValueError):
                continue
            entry = {
                "name": name,
                "state": st,
                "population": pop,
                "lat": lat,
                "lon": lon,
            }
            rows[fp] = entry

    os.makedirs(_AUG_DIR, exist_ok=True)
    out_path = os.path.join(_AUG_DIR, f"county_data_{state_fips}.json")
    with open(out_path, "w", encoding="utf-8") as out:
        json.dump(rows, out, indent=2)
    return rows


def load_county_data(state_fips):
    state_fips = str(state_fips).zfill(2)[:2]
    path = os.path.join(_AUG_DIR, f"county_data_{state_fips}.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)
