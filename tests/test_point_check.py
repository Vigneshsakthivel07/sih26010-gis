from shapely.geometry import Polygon, Point

from src.validation.point_check import check_points_inside


# Historical FMB parcel
polygon = Polygon([
    (0, 0),
    (100, 0),
    (100, 80),
    (0, 80)
])


# Modern survey points
modern_points = {
    "A": Point(10, 10),
    "B": Point(90, 10),
    "C": Point(90, 70),
    "D": Point(10, 70)
}


# Check points
results = check_points_inside(
    polygon,
    modern_points
)


print("Point-in-polygon results:")

for point_id, inside in results.items():

    print(
        point_id,
        "→",
        "INSIDE" if inside else "OUTSIDE"
    )
