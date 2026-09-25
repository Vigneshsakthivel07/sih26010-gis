import pandas as pd
from src.digitization.pixel_to_local import pixel_to_local


def load_fmb_csv(file_path):
    df = pd.read_csv(file_path)

    points = {}

    for _, row in df.iterrows():
        points[row["point_id"]] = (
            float(row["x"]),
            float(row["y"])
        )

    return points


def load_digitized_fmb_csv(file_path):
    df = pd.read_csv(file_path)

    points = {}

    for _, row in df.iterrows():
        points[row["point_id"]] = (
            float(row["x"]),
            float(row["y"])
        )

    return pixel_to_local(points)
