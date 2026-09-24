from shapely.geometry import Polygon, Point


def create_polygon(points):
    """
    Create a polygon from ordered (x, y) points.
    """

    return Polygon(points)


def create_point(x, y):
    return Point(x, y)
