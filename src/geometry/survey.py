import pandas as pd
from src.transform.projection import gps_to_local


def load_survey_csv(file_path):

    df = pd.read_csv(file_path)

    projected_points = []

    for _, row in df.iterrows():

        x, y = gps_to_local(
            row["latitude"],
            row["longitude"]
        )

        projected_points.append({
            "point_id": row["point_id"],
            "x": x,
            "y": y
        })

    return pd.DataFrame(projected_points)
