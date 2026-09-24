from src.geometry.fmb import load_fmb_csv
from src.geometry.survey import load_survey_csv
from src.geometry.polygon import polygon_from_point_dict, create_point
from src.transform.affine import calculate_affine_transform
from src.transform.transform_points import transform_points
from src.validation.parcel_compare import compare_parcel
from src.validation.point_check import check_points_inside
from src.validation.overlap import calculate_overlap
from src.validation.engine import validate_parcel


# --------------------------------------------------
# 1. Load historical FMB data
# --------------------------------------------------

fmb_points = load_fmb_csv(
    "data/fmb/fmb_parcel_001.csv"
)


# --------------------------------------------------
# 2. Load modern survey data
# --------------------------------------------------

modern_points = load_survey_csv(
    "data/survey/modern_survey_mismatch.csv"
)


# --------------------------------------------------
# 3. Select stable control points
# --------------------------------------------------

control_ids = ["A", "B", "C"]

source_control_points = [
    fmb_points[point_id]
    for point_id in control_ids
]

target_control_points = [
    modern_points[point_id]
    for point_id in control_ids
]


# --------------------------------------------------
# 4. Calculate coordinate transformation
# --------------------------------------------------

transform_params = calculate_affine_transform(
    source_control_points,
    target_control_points
)


# --------------------------------------------------
# 5. Transform historical FMB points
# --------------------------------------------------

transformed_fmb = transform_points(
    fmb_points,
    transform_params
)


# --------------------------------------------------
# 6. Calculate boundary deviations
# --------------------------------------------------

deviations = compare_parcel(
    fmb_points,
    modern_points,
    transform_params
)


# --------------------------------------------------
# 7. Create transformed FMB polygon
# --------------------------------------------------

fmb_polygon = polygon_from_point_dict(
    transformed_fmb
)


# --------------------------------------------------
# 8. Create modern survey polygon
# --------------------------------------------------

modern_polygon = polygon_from_point_dict(
    modern_points
)


# --------------------------------------------------
# 9. Check modern points inside FMB polygon
# --------------------------------------------------

modern_shapely_points = {}

for point_id, coordinates in modern_points.items():

    modern_shapely_points[point_id] = create_point(
        coordinates[0],
        coordinates[1]
    )


point_results = check_points_inside(
    fmb_polygon,
    modern_shapely_points
)


points_outside = sum(
    1
    for inside in point_results.values()
    if not inside
)


# --------------------------------------------------
# 10. Calculate polygon overlap
# --------------------------------------------------

overlap_percentage = calculate_overlap(
    fmb_polygon,
    modern_polygon
)


# --------------------------------------------------
# 11. Run final validation
# --------------------------------------------------

result = validate_parcel(
    deviations=deviations,
    overlap_percentage=overlap_percentage,
    points_outside=points_outside,
    tolerance=1.0,
    minimum_overlap=90.0
)


# --------------------------------------------------
# 12. Display results
# --------------------------------------------------

print()
print("===================================")
print("     SIH26010 PARCEL VALIDATION")
print("===================================")

print("\nBoundary Deviations:")

for point_id, value in deviations.items():

    print(
        f"{point_id} → {value:.3f} metres"
    )


print("\nPoint Location Check:")

for point_id, inside in point_results.items():

    print(
        f"{point_id} → "
        f"{'INSIDE' if inside else 'OUTSIDE'}"
    )


print("\nPolygon Overlap:")
print(
    f"{overlap_percentage:.2f}%"
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
