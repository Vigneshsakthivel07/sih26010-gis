from src.transform.affine import transform_point


def transform_points(points, transform_params):
    """
    Transform all points using the calculated
    affine transformation.
    """

    transformed = {}

    for point_id, point in points.items():

        transformed[point_id] = transform_point(
            point,
            transform_params
        )

    return transformed
