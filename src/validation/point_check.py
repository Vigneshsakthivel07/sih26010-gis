def check_points_inside(polygon, points):

    result = {}

    for point_id, point in points.items():

        result[point_id] = polygon.contains(point)

    return result
