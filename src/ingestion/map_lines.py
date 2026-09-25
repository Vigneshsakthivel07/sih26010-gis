from pathlib import Path
import math
import cv2
import pytesseract
from pytesseract import Output


def _line_length(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def _line_angle(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180


def _near_edge_line(x1, y1, x2, y2, width, height, margin):
    """
    Remove the outer FMB/page frame.
    """
    if x1 < margin and x2 < margin:
        return True

    if x1 > width - margin and x2 > width - margin:
        return True

    if y1 < margin and y2 < margin:
        return True

    if y1 > height - margin and y2 > height - margin:
        return True

    return False


def _find_north_arrow_mask(image):
    """
    Find the 'N' of the north arrow and return
    a rectangle around the north-arrow symbol.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    data = pytesseract.image_to_data(
        gray,
        config="--psm 11",
        output_type=Output.DICT
    )

    height, width = gray.shape

    candidates = []

    for i, raw in enumerate(data["text"]):

        text = raw.strip().upper()

        if text != "N":
            continue

        x = int(data["left"][i])
        y = int(data["top"][i])
        box_width = int(data["width"][i])
        box_height = int(data["height"][i])

        center_x = x + box_width / 2
        center_y = y + box_height / 2

        # North arrow is usually in the upper-right area.
        if center_x > 0.60 * width and center_y < 0.35 * height:
            candidates.append(
                (x, y, box_width, box_height)
            )

    if not candidates:
        return None

    # Select the candidate closest to upper-right corner.
    x, y, box_width, box_height = min(
        candidates,
        key=lambda box:
        (width - (box[0] + box[2])) + box[1]
    )

    return (
        x - 80,
        y - 80,
        x + box_width + 100,
        y + box_height + 220
    )


def detect_lines(image_path, remove_noise=True):

    image_path = Path(image_path)

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        50,
        150,
        apertureSize=3
    )

    height, width = gray.shape

    edge_margin = int(
        0.05 * min(width, height)
    )

    # ------------------------------------------
    # Remove north arrow
    # ------------------------------------------

    if remove_noise:

        north_mask = _find_north_arrow_mask(image)

        if north_mask:

            x1, y1, x2, y2 = north_mask

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(width, x2)
            y2 = min(height, y2)

            edges[y1:y2, x1:x2] = 0

    # ------------------------------------------
    # Hough line detection
    # ------------------------------------------

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=math.pi / 180,
        threshold=80,
        minLineLength=80,
        maxLineGap=20
    )

    results = []

    if lines is None:
        return results

    for line in lines:

        # IMPORTANT:
        # HoughLinesP returns:
        # [x1, y1, x2, y2]
        #
        # NOT:
        # [[x1, y1, x2, y2]]
        #
        # Therefore do NOT use line[0].

        x1, y1, x2, y2 = map(
            int,
            line
        )

        length = _line_length(
            x1, y1, x2, y2
        )

        angle = _line_angle(
            x1, y1, x2, y2
        )

        if remove_noise:

            # ----------------------------------
            # Remove page/document border
            # ----------------------------------

            if _near_edge_line(
                x1,
                y1,
                x2,
                y2,
                width,
                height,
                edge_margin
            ):
                continue

            # ----------------------------------
            # Remove extremely long frame lines
            # ----------------------------------

            if length > 0.90 * max(
                width,
                height
            ):
                continue

        results.append(
            {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "length": round(length, 2),
                "angle": round(angle, 2)
            }
        )

    return results


def create_line_overlay(
    image_path,
    output_path
):

    image_path = Path(image_path)
    output_path = Path(output_path)

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    lines = detect_lines(
        image_path,
        remove_noise=True
    )

    for line in lines:

        cv2.line(
            image,
            (
                line["x1"],
                line["y1"]
            ),
            (
                line["x2"],
                line["y2"]
            ),
            (0, 0, 255),
            2
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cv2.imwrite(
        str(output_path),
        image
    )

    return output_path, len(lines)


if __name__ == "__main__":

    input_path = (
        "data/fmb/processed/fmb_map.png"
    )

    output_path = (
        "data/fmb/processed/"
        "fmb_lines_overlay.png"
    )

    result, count = create_line_overlay(
        input_path,
        output_path
    )

    print("Overlay:", result)
    print(
        "Filtered candidate lines:",
        count
    )
