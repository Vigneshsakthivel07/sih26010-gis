from src.geometry.fmb import load_fmb_csv
from src.geometry.survey import load_survey_csv

from src.transform.affine import (
    calculate_affine_transform
)

from src.transform.transform_points import (
    transform_points
)

from src.geometry.polygon import (
    polygon_from_point_dict
)


# Load data
fmb_points = load_fmb_csv(
    "data/fmb/fmb_parcel_001.csv"
)

modern_points = load_survey_csv(
    "data/survey/modern_survey_mismatch.csv"
)


# Control points
control_ids = ["A", "B", "C"]


source_points = [
    fmb_points[point_id]
    for point_id in control_ids
]


target_points = [
    modern_points[point_id]
    for point_id in control_ids
]


# Calculate transformation
params = calculate_affine_transform(
    source_points,
    target_points
)


# Transform entire FMB
transformed_points = transform_points(
    fmb_points,
    params
)


# Create polygons
historical_polygon = polygon_from_point_dict(
    transformed_points
)

modern_polygon = polygon_from_point_dict(
    modern_points
)


print("Transformed FMB polygon:")
print("Area:", round(historical_polygon.area, 3))
print(
    "Perimeter:",
    round(historical_polygon.length, 3)
)


print("\nModern survey polygon:")
print("Area:", round(modern_polygon.area, 3))
print(
    "Perimeter:",
    round(modern_polygon.length, 3)
)
