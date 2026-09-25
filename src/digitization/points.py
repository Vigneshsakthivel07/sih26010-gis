import cv2
import math


def detect_lines(image_path):
    """
    Detect straight lines in the FMB image.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(
            f"Could not read image: {image_path}"
        )

    height, width = image.shape[:2]

    # Crop to the main parcel drawing area
    roi = image[235:1230, 70:950]

    gray = cv2.cvtColor(
        roi,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        50,
        150,
        apertureSize=3
    )

    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=math.pi / 180,
        threshold=60,
        minLineLength=60,
        maxLineGap=15
    )

    if lines is None:
        return []

    # Convert ROI coordinates back to original image coordinates
    adjusted_lines = []

    for line in lines:

        x1, y1, x2, y2 = line.reshape(-1)

        x1 += 70
        x2 += 70

        y1 += 235
        y2 += 235

        adjusted_lines.append(
            [[x1, y1, x2, y2]]
        )

    return adjusted_lines


def filter_long_lines(lines, minimum_length=80):
    """
    Remove very short lines caused by text and symbols.
    """

    filtered = []

    for line in lines:

        x1, y1, x2, y2 = line[0]

        length = math.sqrt(
            (x2 - x1) ** 2 +
            (y2 - y1) ** 2
        )

        if length >= minimum_length:
            filtered.append(line)

    return filtered
