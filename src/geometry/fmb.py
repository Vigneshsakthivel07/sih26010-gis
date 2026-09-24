import pandas as pd


def load_fmb_csv(file_path):
    """
    Load historical FMB coordinates
    from a CSV file.
    """

    df = pd.read_csv(file_path)

    points = {}

    for _, row in df.iterrows():
        points[row["point_id"]] = (
            float(row["x"]),
            float(row["y"])
        )

    return points
