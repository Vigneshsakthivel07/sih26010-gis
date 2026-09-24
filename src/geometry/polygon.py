from shapely.geometry import Polygon, Point


def create_polygon(points):
    """
    Create a polygon from ordered coordinate points.
    """

    return Polygon(points)


def create_point(x, y):
    """
    Create a Shapely Point.
    """

    return Point(x, y)


def polygon_from_point_dict(points):
    """
    Create a polygon from a dictionary:

    {
        "A": (x, y),
        "B": (x, y),
        "C": (x, y),
        "D": (x, y)
    }

    The dictionary must contain points
    in boundary order.
    """

    coordinates = list(points.values())

    return Polygon(coordinates)
