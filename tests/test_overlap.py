from shapely.geometry import Polygon

from src.validation.overlap import calculate_overlap


# Historical FMB parcel
old_polygon = Polygon([
    (0, 0),
    (100, 0),
    (100, 80),
    (0, 80)
])


# Modern survey parcel
new_polygon = Polygon([
    (2, 1),
    (98, 1),
    (98, 79),
    (2, 79)
])


overlap = calculate_overlap(
    old_polygon,
    new_polygon
)


print(
    "Polygon overlap:",
    round(overlap, 2),
    "%"
)
