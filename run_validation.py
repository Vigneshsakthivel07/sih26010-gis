from src.validation.validator import validate_parcel_from_files
from src.validation.plot import plot_parcel_comparison
from src.validation.result import save_validation_result

result = validate_parcel_from_files(
    fmb_file="data/fmb/fmb_parcel_001.csv",
    survey_file="data/survey/modern_survey_001.csv",
    control_ids=["A", "C", "G"],
    tolerance=1.0,
    minimum_overlap=90.0
)

json_file = save_validation_result(result)

print()
print("JSON result:")
print(json_file)

plot_file = plot_parcel_comparison(
    transformed_fmb=result["transformed_fmb"],
    modern_points=result["modern_points"],
    deviations=result["deviations"]
)

print()
print("GIS comparison map:")
print(plot_file)

print()
print("===================================")
print("     SIH26010 PARCEL VALIDATION")
print("===================================")

print("\nBoundary Deviations:")

for point_id, value in result["deviations"].items():

    print(
        f"{point_id} → {value:.3f} metres"
    )


print("\nPoint Location Check:")

for point_id, inside in result["point_results"].items():

    print(
        f"{point_id} → "
        f"{'INSIDE' if inside else 'OUTSIDE'}"
    )


print("\nPolygon Overlap:")

print(
    f"{result['overlap_percentage']:.2f}%"
)


print("\nFinal Validation:")

print(
    f"Status → {result['status']}"
)

print(
    f"Maximum deviation → "
    f"{result['maximum_deviation']:.3f} m"
)

print(
    f"Average deviation → "
    f"{result['average_deviation']:.3f} m"
)

print(
    f"Points outside → "
    f"{result['points_outside']}"
)

print(
    f"Deviation check → "
    f"{result['deviation_ok']}"
)

print(
    f"Overlap check → "
    f"{result['overlap_ok']}"
)

print(
    f"Point check → "
    f"{result['points_ok']}"
)

print("===================================")
