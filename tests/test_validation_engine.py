from src.validation.engine import validate_parcel


deviations = {
    "A": 0.0,
    "B": 0.0,
    "C": 0.0,
    "D": 114.774
}


result = validate_parcel(
    deviations=deviations,
    overlap_percentage=100.0,
    points_outside=1,
    tolerance=1.0,
    minimum_overlap=90.0
)


print("Parcel Validation Result")
print("------------------------")

for key, value in result.items():

    if isinstance(value, float):
        print(
            key,
            ":",
            round(value, 3)
        )

    else:
        print(
            key,
            ":",
            value
        )
