from src.validation.engine import validate_parcel


result = validate_parcel(
    max_deviation=0.894,
    overlap_percentage=93.6,
    points_outside=0,
    tolerance=1.0,
    minimum_overlap=90.0
)


print("Validation result:")
print(result)
