import csv


def load_points(csv_file):

    points = {}

    with open(csv_file, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            point_id = row["point_id"]

            x = float(row["x"])
            y = float(row["y"])

            points[point_id] = (x, y)

    return points


def pixel_to_local(
    points,
    scale_denominator=848,
    dpi=300
):
    """
    Convert FMB image pixels into approximate
    local ground coordinates in metres.

    The FMB scale is interpreted as:
        1 unit on paper = scale_denominator units on ground.

    The image was rendered at the specified DPI.

    This is a prototype scale conversion.
    Survey-grade georeferencing requires
    known ground control points.
    """

    if scale_denominator <= 0:
        raise ValueError(
            "Scale must be positive."
        )

    if dpi <= 0:
        raise ValueError(
            "DPI must be positive."
        )

    # Physical size of one image pixel on paper.
    paper_metres_per_pixel = (
        0.0254 / dpi
    )

    # Convert paper distance to ground distance.
    ground_metres_per_pixel = (
        paper_metres_per_pixel
        * scale_denominator
    )

    print(
        "Ground metres per pixel:",
        ground_metres_per_pixel
    )

    first_point = next(
        iter(points.values())
    )

    origin_x, origin_y = first_point

    local_points = {}

    for point_id, (x, y) in points.items():

        local_x = (
            (x - origin_x)
            * ground_metres_per_pixel
        )

        # Image Y increases downward.
        # Cartesian Y increases upward.
        local_y = (
            (origin_y - y)
            * ground_metres_per_pixel
        )

        local_points[point_id] = (
            local_x,
            local_y
        )

    return local_points
