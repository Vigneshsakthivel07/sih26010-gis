from src.geometry.fmb import load_fmb_csv
from src.geometry.survey import load_survey_csv

from src.geometry.polygon import (
    polygon_from_point_dict
)


# Load FMB
fmb_points = load_fmb_csv(
    "data/fmb/fmb_parcel_001.csv"
)


# Create FMB polygon
fmb_polygon = polygon_from_point_dict(
    fmb_points
)


print("FMB polygon:")
print("Area:", fmb_polygon.area)
print("Perimeter:", fmb_polygon.length)
