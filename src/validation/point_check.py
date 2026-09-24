from shapely.geometry import Point


def check_points_inside(polygon, points, tolerance=0.01):
    """
    Check whether each survey point is inside
    or sufficiently close to the parcel boundary.

    tolerance is measured in metres.
    """

    result = {}

    for point_id, point in points.items():

        shapely_point = Point(point)

        # Normal case: point is inside or on boundary
        if polygon.covers(shapely_point):
            result[point_id] = True
            continue

        # Allow a small measurement/numerical tolerance
        if polygon.distance(shapely_point) <= tolerance:
            result[point_id] = True
        else:
            result[point_id] = False

    return result
