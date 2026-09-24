from src.geometry.fmb import load_fmb_csv
from src.geometry.survey import load_survey_csv

from src.transform.affine import (
    calculate_affine_transform
)

from src.validation.parcel_compare import (
    compare_parcel
)


# ------------------------------------------------
# 1. Load historical FMB
# ------------------------------------------------

fmb_points = load_fmb_csv(
    "data/fmb/fmb_parcel_001.csv"
)


# ------------------------------------------------
# 2. Load modern survey
# ------------------------------------------------

modern_points = load_survey_csv(
    "data/survey/modern_survey_mismatch.csv"
)


# ------------------------------------------------
# 3. Select stable control points
# ------------------------------------------------

control_ids = ["A", "B", "C"]


source_points = [
    fmb_points[point_id]
    for point_id in control_ids
]


target_points = [
    modern_points[point_id]
    for point_id in control_ids
]


# ------------------------------------------------
# 4. Calculate affine transformation
# ------------------------------------------------

transform_params = calculate_affine_transform(
    source_points,
    target_points
)


# ------------------------------------------------
# 5. Compare transformed FMB with modern survey
# ------------------------------------------------

deviations = compare_parcel(
    fmb_points,
    modern_points,
    transform_params
)


# ------------------------------------------------
# 6. Print results
# ------------------------------------------------

print("Point deviations:")

for point_id, value in deviations.items():

    print(
        point_id,
        "→",
        round(value, 3),
        "metres"
    )
