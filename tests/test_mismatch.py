from src.geometry.fmb import load_fmb_csv
from src.geometry.survey import load_survey_csv

from src.transform.affine import (
    calculate_affine_transform,
    transform_point
)

from src.validation.distance import distance


# Load FMB
fmb_points = load_fmb_csv(
    "data/fmb/fmb_parcel_001.csv"
)


# Load mismatch survey
modern_points = load_survey_csv(
    "data/survey/modern_survey_mismatch.csv"
)


# Use A, B, C as stable control points
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


# Transform historical D
transformed_d = transform_point(
    fmb_points["D"],
    params
)


# Actual modern D
actual_d = modern_points["D"]


# Calculate deviation
deviation = distance(
    transformed_d,
    actual_d
)


print("Expected D position:")
print(transformed_d)

print("\nActual modern D position:")
print(actual_d)

print("\nD boundary deviation:")
print(round(deviation, 3), "metres")
