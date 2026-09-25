from src.validation.api import validate_land_parcel


result = validate_land_parcel(
    fmb_file="data/fmb/fmb_demo_local.csv",
    survey_file="data/survey/modern_survey_mismatch_demo.csv",
    control_ids=["P1", "P3", "P7"],
    tolerance=1.0,
    minimum_overlap=90.0
)


print("\n========== VALIDATION RESULT ==========")

print("Status:", result["status"])

print(
    "Maximum deviation:",
    result["maximum_deviation"],
    "m"
)

print(
    "Average deviation:",
    result["average_deviation"],
    "m"
)

print(
    "Overlap:",
    result["overlap_percentage"],
    "%"
)

print(
    "Points outside:",
    result["points_outside"]
)

print("\nDeviations:")

for point_id, deviation in result["deviations"].items():
    print(
        point_id,
        "→",
        round(deviation, 3),
        "m"
    )
