from src.validation.api import validate_land_parcel


result = validate_land_parcel(
    fmb_file="data/fmb/fmb_parcel_001.csv",
    survey_file="data/survey/modern_survey_mismatch.csv"
)

print("Status:", result["status"])
print("Maximum deviation:", result["maximum_deviation"])
print("Average deviation:", result["average_deviation"])
print("Overlap:", result["overlap_percentage"])
print("Points outside:", result["points_outside"])