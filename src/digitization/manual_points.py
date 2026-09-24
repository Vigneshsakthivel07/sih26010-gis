import cv2
import csv


points = []

zoom = 0.5
offset_x = 0
offset_y = 0

dragging = False
last_x = 0
last_y = 0


def redraw(image):
    """
    Create the zoomed and panned view.
    """

    height, width = image.shape[:2]

    new_width = int(width * zoom)
    new_height = int(height * zoom)

    resized = cv2.resize(
        image,
        (new_width, new_height)
    )

    # Create screen-sized canvas
    canvas_width = 1200
    canvas_height = 800

    canvas = 255 * \
        __import__("numpy").ones(
            (canvas_height, canvas_width, 3),
            dtype="uint8"
        )

    # Calculate visible region
    x1 = max(0, offset_x)
    y1 = max(0, offset_y)

    x2 = min(
        new_width,
        offset_x + canvas_width
    )

    y2 = min(
        new_height,
        offset_y + canvas_height
    )

    visible = resized[
        y1:y2,
        x1:x2
    ]

    canvas[
        0:visible.shape[0],
        0:visible.shape[1]
    ] = visible

    return canvas


def mouse_callback(event, x, y, flags, param):

    global zoom
    global offset_x
    global offset_y
    global dragging
    global last_x
    global last_y

    image = param

    # LEFT CLICK → select point
    if event == cv2.EVENT_LBUTTONDOWN:

        original_x = int(
            (x + offset_x) / zoom
        )

        original_y = int(
            (y + offset_y) / zoom
        )

        point_id = len(points) + 1

        points.append(
            (
                point_id,
                original_x,
                original_y
            )
        )

        print(
            f"P{point_id}: "
            f"x={original_x}, "
            f"y={original_y}"
        )

    # MOUSE WHEEL → zoom
    elif event == cv2.EVENT_MOUSEWHEEL:

        if flags > 0:
            zoom *= 1.2
        else:
            zoom /= 1.2

        zoom = max(
            0.2,
            min(zoom, 5.0)
        )

        print(
            f"Zoom: {zoom:.2f}"
        )

    # RIGHT BUTTON → start pan
    elif event == cv2.EVENT_RBUTTONDOWN:

        dragging = True

        last_x = x
        last_y = y

    elif event == cv2.EVENT_MOUSEMOVE:

        if dragging:

            dx = last_x - x
            dy = last_y - y

            offset_x += dx
            offset_y += dy

            last_x = x
            last_y = y

    elif event == cv2.EVENT_RBUTTONUP:

        dragging = False


def select_points(
    image_path,
    output_csv
):

    global points

    points = []

    image = cv2.imread(
        image_path
    )

    if image is None:
        raise FileNotFoundError(
            f"Could not read image: {image_path}"
        )

    print()
    print("===================================")
    print(" FMB POINT SELECTION TOOL")
    print("===================================")
    print()
    print("LEFT CLICK  → Select corner")
    print("MOUSE WHEEL → Zoom in/out")
    print("RIGHT DRAG  → Move / Pan")
    print("R           → Reset points")
    print("ENTER       → Finish")
    print()
    
    cv2.namedWindow(
        "FMB Point Selector",
        cv2.WINDOW_NORMAL
    )

    cv2.resizeWindow(
        "FMB Point Selector",
        1200,
        800
    )

    cv2.setMouseCallback(
        "FMB Point Selector",
        mouse_callback,
        image
    )

    while True:

        display = redraw(image)

        # Draw selected points
        for point_id, px, py in points:

            screen_x = int(
                px * zoom - offset_x
            )

            screen_y = int(
                py * zoom - offset_y
            )

            if (
                0 <= screen_x < 1200
                and 0 <= screen_y < 800
            ):

                cv2.circle(
                    display,
                    (screen_x, screen_y),
                    7,
                    (0, 0, 255),
                    -1
                )

                cv2.putText(
                    display,
                    f"P{point_id}",
                    (
                        screen_x + 10,
                        screen_y - 10
                    ),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )

        cv2.imshow(
            "FMB Point Selector",
            display
        )

        key = cv2.waitKey(20) & 0xFF

        if key == 13:
            break

        if key == ord("r"):

            points = []

            print(
                "Points reset."
            )

    cv2.destroyAllWindows()

    with open(
        output_csv,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "point_id",
                "x",
                "y"
            ]
        )

        for point_id, x, y in points:

            writer.writerow(
                [
                    f"P{point_id}",
                    x,
                    y
                ]
            )

    print()
    print("Saved:")
    print(output_csv)
