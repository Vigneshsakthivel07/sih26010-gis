import csv
from shapely.geometry import Polygon


def load_selected_points(csv_file):
    """
    Load manually selected FMB points.
    """

    points = []

    with open(csv_file, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            x = float(row["x"])
            y = float(row["y"])

            points.append((x, y))

    return points


def create_fmb_polygon(csv_file):
    """
    Create a Shapely polygon from
    manually selected FMB vertices.
    """

    points = load_selected_points(csv_file)

    if len(points) < 3:
        raise ValueError(
            "At least 3 points are required."
        )

    polygon = Polygon(points)

    return polygon
