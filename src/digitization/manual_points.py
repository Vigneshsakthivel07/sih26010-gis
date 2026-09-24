import cv2
import csv


points = []


def mouse_callback(event, x, y, flags, param):

    if event == cv2.EVENT_LBUTTONDOWN:

        point_id = len(points) + 1

        points.append(
            (point_id, x, y)
        )

        print(
            f"Point {point_id}: "
            f"x={x}, y={y}"
        )

        cv2.circle(
            param,
            (x, y),
            7,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            param,
            f"P{point_id}",
            (x + 10, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255),
            2
        )


def select_points(image_path, output_csv):

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(
            f"Could not read image: {image_path}"
        )

    display = image.copy()

    cv2.namedWindow("Select FMB Corners")

    cv2.setMouseCallback(
        "Select FMB Corners",
        mouse_callback,
        display
    )

    print()
    print("CLICK the actual parcel corners.")
    print("Press ENTER when finished.")
    print("Press R to reset points.")
    print()

    while True:

        cv2.imshow(
            "Select FMB Corners",
            display
        )

        key = cv2.waitKey(1) & 0xFF

        # ENTER → finish
        if key == 13:
            break

        # R → reset
        if key == ord("r"):

            points.clear()
            display = image.copy()

            print("Points reset.")

    cv2.destroyAllWindows()

    with open(
        output_csv,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            ["point_id", "x", "y"]
        )

        for point_id, x, y in points:

            writer.writerow(
                [f"P{point_id}", x, y]
            )

    print()
    print("Saved points to:")
    print(output_csv)
