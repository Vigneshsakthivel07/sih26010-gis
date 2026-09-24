from src.geometry.fmb import load_fmb_csv
from src.geometry.survey import load_survey_csv
from shapely.validation import explain_validity

from src.transform.affine import (
    calculate_affine_transform
)

from src.transform.transform_points import (
    transform_points
)

from src.geometry.polygon import (
    polygon_from_point_dict
)

from src.validation.overlap import (
    calculate_overlap
)


# -----------------------------------------
# 1. Load FMB
# -----------------------------------------

fmb_points = load_fmb_csv(
    "data/fmb/fmb_parcel_001.csv"
)


# -----------------------------------------
# 2. Load modern survey
# -----------------------------------------

modern_points = load_survey_csv(
    "data/survey/modern_survey_mismatch.csv"
)


# -----------------------------------------
# 3. Control points
# -----------------------------------------

control_ids = ["A", "B", "C"]


source_points = [
    fmb_points[point_id]
    for point_id in control_ids
]


target_points = [
    modern_points[point_id]
    for point_id in control_ids
]


# -----------------------------------------
# 4. Calculate transformation
# -----------------------------------------

params = calculate_affine_transform(
    source_points,
    target_points
)


# -----------------------------------------
# 5. Transform FMB
# -----------------------------------------

transformed_fmb = transform_points(
    fmb_points,
    params
)


# -----------------------------------------
# 6. Create polygons
# -----------------------------------------

old_polygon = polygon_from_point_dict(
    transformed_fmb
)

new_polygon = polygon_from_point_dict(
    modern_points
)


# -----------------------------------------
# 7. Check polygon validity
# -----------------------------------------

print("Old polygon valid:", old_polygon.is_valid)
print("New polygon valid:", new_polygon.is_valid)

print("\nOld polygon reason:")
print(explain_validity(old_polygon))

print("\nNew polygon reason:")
print(explain_validity(new_polygon))

print("\nCalculating overlap...")

overlap = calculate_overlap(
    old_polygon,
    new_polygon
)

print(
    "Polygon overlap:",
    round(overlap, 2),
    "%"
)
