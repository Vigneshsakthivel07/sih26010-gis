import pandas as pd

from src.transform.projection import gps_to_local


def load_survey_csv(file_path):
    """
    Load modern survey coordinates.

    Supports two formats:

    1. GPS:
       point_id, latitude, longitude

    2. Projected/local:
       point_id, x, y
    """

    df = pd.read_csv(file_path)

    points = {}

    # ------------------------------------------
    # Format 1: GPS latitude / longitude
    # ------------------------------------------

    if "latitude" in df.columns and "longitude" in df.columns:

        for _, row in df.iterrows():

            x, y = gps_to_local(
                row["latitude"],
                row["longitude"]
            )

            points[row["point_id"]] = (x, y)

    # ------------------------------------------
    # Format 2: Already projected/local
    # ------------------------------------------

    elif "x" in df.columns and "y" in df.columns:

        for _, row in df.iterrows():

            points[row["point_id"]] = (
                float(row["x"]),
                float(row["y"])
            )

    else:

        raise ValueError(
            "Survey CSV must contain either "
            "latitude/longitude or x/y columns."
        )

    return points
