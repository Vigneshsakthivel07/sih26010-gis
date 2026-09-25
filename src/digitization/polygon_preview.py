import cv2
import csv


def create_polygon_preview(
    image_path,
    points_csv,
    output_path
):
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(
            f"Could not read image: {image_path}"
        )

    points = []

    with open(points_csv, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            x = int(row["x"])
            y = int(row["y"])

            points.append(
                (
                    x,
                    y
                )
            )

    if len(points) < 3:
        raise ValueError(
            "At least 3 points are required."
        )

    # Draw polygon edges
    for i in range(len(points)):

        p1 = points[i]

        p2 = points[
            (i + 1) % len(points)
        ]

        cv2.line(
            image,
            p1,
            p2,
            (0, 0, 255),
            4
        )

    # Draw points
    for i, point in enumerate(points):

        cv2.circle(
            image,
            point,
            8,
            (0, 255, 0),
            -1
        )

        cv2.putText(
            image,
            f"P{i + 1}",
            (
                point[0] + 10,
                point[1] - 10
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2
        )

    cv2.imwrite(
        output_path,
        image
    )

    return output_path
