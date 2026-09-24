from src.geometry.fmb import load_fmb_csv
from src.geometry.survey import load_survey_csv

from src.transform.affine import (
    calculate_affine_transform,
    transform_point
)


# Load historical FMB points
fmb_points = load_fmb_csv(
    "data/fmb/fmb_parcel_001.csv"
)


# Load modern survey points
modern_points = load_survey_csv(
    "data/survey/modern_survey_001.csv"
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


print("Affine transformation parameters:")
print(params)


print("\nTransformed FMB points:")


for point_id, point in fmb_points.items():

    transformed = transform_point(
        point,
        params
    )

    print(
        point_id,
        "→",
        transformed
    )


print("\nActual modern points:")

for point_id, point in modern_points.items():

    print(
        point_id,
        "→",
        point
    )
