from pyproj import Transformer


def gps_to_local(latitude, longitude):
    """
    Convert latitude/longitude to a projected
    coordinate system measured in metres.

    EPSG:4326 = WGS84 latitude/longitude.
    EPSG:32643 = UTM Zone 43N.
    """

    transformer = Transformer.from_crs(
        "EPSG:4326",
        "EPSG:32643",
        always_xy=True
    )

    x, y = transformer.transform(longitude, latitude)

    return x, y
