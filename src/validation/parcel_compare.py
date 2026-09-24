from src.validation.distance import distance
from src.transform.affine import transform_point


def compare_parcel(
    historical_points,
    modern_points,
    transform_params
):
    """
    Transform historical FMB points into the
    modern coordinate system and compare them
    with modern survey points.
    """

    deviations = {}

    for point_id in historical_points:

        old_point = historical_points[point_id]

        transformed_point = transform_point(
            old_point,
            transform_params
        )

        modern_point = modern_points[point_id]

        deviations[point_id] = distance(
            transformed_point,
            modern_point
        )

    return deviations
