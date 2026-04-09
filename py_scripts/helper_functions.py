import math
import matplotlib.pyplot as plt


STATE_FIPS_TO_NAME = {
    "01": "Alabama",
    "02": "Alaska",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "15": "Hawaii",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
}


def _haversine_miles(lat1, lon1, lat2, lon2):
    # Radius of Earth in miles
    R = 3958.7613

    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def plot_centers(state_shp, cdata, centers, title_suffix):
    # Plot the state map and mark selected center counties.
    center_fips = sorted(set(centers) & set(cdata))
    centroids = state_shp[state_shp["GEOID"].isin(center_fips)].copy()
    centroids["pt"] = centroids.geometry.centroid
    fig, ax = plt.subplots(figsize=(12, 10))
    state_shp.plot(ax=ax, color="lightgray", edgecolor="black", linewidth=0.5)

    # Plot the centroids of the selected center counties
    for _, row in centroids.iterrows():
        fips = row["GEOID"]
        pt = row["pt"]
        ax.scatter(pt.x, pt.y, s=45, c="red", edgecolors="black", linewidths=0.5)
        
        # Annotate county name above the point, in bold font
        ax.annotate(
            cdata[fips]["name"],
            (pt.x, pt.y),
            fontsize=7,
            ha="center",
            va="bottom",
            fontweight="bold"
        )

    state_name = next(iter(cdata.values()))["state"]
    ax.set_title(f"Vaccine centers - {state_name} ({title_suffix})")
    ax.axis("off")
    plt.show()
