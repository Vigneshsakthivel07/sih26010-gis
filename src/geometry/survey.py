import pandas as pd

from src.transform.projection import gps_to_local


def load_survey_csv(file_path):
    """
    Load modern survey GPS coordinates
    and convert them into projected coordinates.
    """

    df = pd.read_csv(file_path)

    points = {}

    for _, row in df.iterrows():

        x, y = gps_to_local(
            row["latitude"],
            row["longitude"]
        )

        points[row["point_id"]] = (
            x,
            y
        )

    return points
