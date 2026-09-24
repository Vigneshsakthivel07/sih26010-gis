def calculate_overlap(old_polygon, new_polygon):

    intersection = old_polygon.intersection(
        new_polygon
    )

    union = old_polygon.union(
        new_polygon
    )

    if union.area == 0:
        return 0

    overlap = (
        intersection.area /
        union.area
    ) * 100

    return overlap
