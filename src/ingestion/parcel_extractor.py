from pathlib import Path
import csv
import math
import re

import cv2
import numpy as np
import pytesseract
from pytesseract import Output

from src.ingestion.map_lines import detect_lines
from src.ingestion.measurement_ocr import extract_measurements


TARGET_LABEL = "10A"


def _ocr_target_label(image, target=TARGET_LABEL):
    """Find the target survey/parcel label using OCR."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(
        gray,
        config="--psm 11",
        output_type=Output.DICT,
    )

    candidates = []

    for i, raw in enumerate(data["text"]):
        text = raw.strip().upper().replace(" ", "")
        if text != target.upper().replace(" ", ""):
            continue

        try:
            conf = float(data["conf"][i])
        except (ValueError, TypeError):
            conf = -1

        x = int(data["left"][i])
        y = int(data["top"][i])
        w = int(data["width"][i])
        h = int(data["height"][i])

        candidates.append(
            {
                "text": raw.strip(),
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "confidence": conf,
            }
        )

    if not candidates:
        return None

    return max(candidates, key=lambda item: item["confidence"])


def _line_length(line):
    return math.hypot(
        line["x2"] - line["x1"],
        line["y2"] - line["y1"],
    )


def _line_angle(line):
    return math.degrees(
        math.atan2(
            line["y2"] - line["y1"],
            line["x2"] - line["x1"],
        )
    ) % 180


def _point_segment_distance(px, py, line):
    x1, y1 = line["x1"], line["y1"]
    x2, y2 = line["x2"], line["y2"]

    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)

    t = (
        (px - x1) * dx + (py - y1) * dy
    ) / (dx * dx + dy * dy)

    t = max(0.0, min(1.0, t))

    qx = x1 + t * dx
    qy = y1 + t * dy

    return math.hypot(px - qx, py - qy)


def _line_intersection(a, b):
    """Return intersection of two infinite lines, or None."""
    x1, y1, x2, y2 = a["x1"], a["y1"], a["x2"], a["y2"]
    x3, y3, x4, y4 = b["x1"], b["y1"], b["x2"], b["y2"]

    denominator = (
        (x1 - x2) * (y3 - y4)
        - (y1 - y2) * (x3 - x4)
    )

    if abs(denominator) < 1e-9:
        return None

    px = (
        (x1 * y2 - y1 * x2) * (x3 - x4)
        - (x1 - x2) * (x3 * y4 - y3 * x4)
    ) / denominator

    py = (
        (x1 * y2 - y1 * x2) * (y3 - y4)
        - (y1 - y2) * (x3 * y4 - y3 * x4)
    ) / denominator

    return px, py


def _angle_difference(a, b):
    diff = abs(a - b) % 180
    return min(diff, 180 - diff)


def _cluster_points(points, radius=18):
    """
    Merge nearby intersection candidates.
    Returns representative points with supporting counts.
    """
    clusters = []

    for point in points:
        assigned = False

        for cluster in clusters:
            cx = cluster["x"] / cluster["count"]
            cy = cluster["y"] / cluster["count"]

            if math.hypot(point[0] - cx, point[1] - cy) <= radius:
                cluster["x"] += point[0]
                cluster["y"] += point[1]
                cluster["count"] += 1
                assigned = True
                break

        if not assigned:
            clusters.append(
                {
                    "x": point[0],
                    "y": point[1],
                    "count": 1,
                }
            )

    result = []

    for cluster in clusters:
        result.append(
            {
                "x": round(cluster["x"] / cluster["count"], 2),
                "y": round(cluster["y"] / cluster["count"], 2),
                "supporting_intersections": cluster["count"],
            }
        )

    return result


def _filter_lines_for_target(
    lines,
    target,
    image_shape,
    max_distance=950,
):
    """
    Keep substantial candidate lines in the neighborhood of the target
    parcel. This is intentionally a candidate filter, not a final boundary
    classifier.
    """
    height, width = image_shape[:2]

    cx = target["x"] + target["width"] / 2
    cy = target["y"] + target["height"] / 2

    selected = []

    for line in lines:
        length = _line_length(line)
        if length < 80:
            continue

        mx = (line["x1"] + line["x2"]) / 2
        my = (line["y1"] + line["y2"]) / 2

        distance = math.hypot(mx - cx, my - cy)

        if distance > max_distance:
            continue

        # Avoid tiny text-like segments.
        angle = _line_angle(line)

        selected.append(
            {
                **line,
                "length": round(length, 2),
                "angle": round(angle, 2),
                "midpoint_distance_to_target": round(distance, 2),
            }
        )

    return selected


def _find_intersection_candidates(
    lines,
    min_angle=12,
    max_angle=168,
    max_extension=35,
):
    """
    Generate corner candidates from pairs of non-parallel line segments.
    We allow a small extension beyond the detected segments because Hough
    lines often stop just before a visible corner.
    """
    points = []

    for i in range(len(lines)):
        a = lines[i]

        for j in range(i + 1, len(lines)):
            b = lines[j]

            angle_diff = _angle_difference(
                a["angle"],
                b["angle"],
            )

            if angle_diff < min_angle:
                continue

            point = _line_intersection(a, b)

            if point is None:
                continue

            px, py = point

            da = _point_segment_distance(px, py, a)
            db = _point_segment_distance(px, py, b)

            if da > max_extension or db > max_extension:
                continue

            points.append((px, py))

    return _cluster_points(points, radius=18)


def _measurement_candidates_near_target(
    measurements,
    target,
    max_distance=1100,
):
    """
    Keep measurement candidates in the target parcel neighborhood.
    """
    cx = target["x"] + target["width"] / 2
    cy = target["y"] + target["height"] / 2

    selected = []

    for item in measurements:
        mx = item["x"] + item["width"] / 2
        my = item["y"] + item["height"] / 2

        distance = math.hypot(
            mx - cx,
            my - cy,
        )

        if distance <= max_distance:
            selected.append(
                {
                    **item,
                    "target_distance_px": round(
                        distance,
                        2,
                    ),
                }
            )

    return selected


def _create_overlay(
    image,
    target,
    lines,
    points,
    measurements,
    output_path,
):
    overlay = image.copy()

    # Target OCR box: green.
    cv2.rectangle(
        overlay,
        (
            target["x"],
            target["y"],
        ),
        (
            target["x"] + target["width"],
            target["y"] + target["height"],
        ),
        (0, 255, 0),
        3,
    )

    # Candidate boundary lines: red.
    for line in lines:
        cv2.line(
            overlay,
            (
                line["x1"],
                line["y1"],
            ),
            (
                line["x2"],
                line["y2"],
            ),
            (0, 0, 255),
            2,
        )

    # Candidate corner points: yellow.
    for index, point in enumerate(points, start=1):
        x = int(round(point["x"]))
        y = int(round(point["y"]))

        cv2.circle(
            overlay,
            (x, y),
            8,
            (0, 255, 255),
            -1,
        )

        cv2.putText(
            overlay,
            f"P{index}",
            (x + 10, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 128, 255),
            2,
            cv2.LINE_AA,
        )

    # Measurement candidates: blue text marker.
    for item in measurements:
        x = int(item["x"])
        y = int(item["y"])

        cv2.rectangle(
            overlay,
            (x, y),
            (
                x + int(item["width"]),
                y + int(item["height"]),
            ),
            (255, 0, 0),
            2,
        )

        cv2.putText(
            overlay,
            f"{item['value']:.1f}",
            (x, max(20, y - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cv2.imwrite(
        str(output_path),
        overlay,
    )


def _write_points_csv(points, output_path):
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "point_id",
                "x",
                "y",
                "source",
                "confidence",
                "supporting_intersections",
                "status",
            ],
        )

        writer.writeheader()

        for index, point in enumerate(
            points,
            start=1,
        ):
            writer.writerow(
                {
                    "point_id": f"P{index}",
                    "x": point["x"],
                    "y": point["y"],
                    "source": "fmb_image_intersection",
                    "confidence": "",
                    "supporting_intersections": point[
                        "supporting_intersections"
                    ],
                    "status": "CANDIDATE",
                }
            )


def _write_measurements_csv(
    measurements,
    output_path,
):
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "measurement_id",
                "value",
                "unit",
                "x",
                "y",
                "ocr_confidence",
                "color",
                "orientation",
                "boundary_distance_px",
                "status",
            ],
        )

        writer.writeheader()

        for index, item in enumerate(
            measurements,
            start=1,
        ):
            writer.writerow(
                {
                    "measurement_id": f"M{index}",
                    "value": item["value"],
                    "unit": "m",
                    "x": item["x"],
                    "y": item["y"],
                    "ocr_confidence": item[
                        "confidence"
                    ],
                    "color": item["color"],
                    "orientation": item[
                        "orientation"
                    ],
                    "boundary_distance_px": item[
                        "boundary_distance_px"
                    ],
                    "status": "CANDIDATE",
                }
            )


def extract_parcel_candidates(
    image_path,
    output_dir,
    target=TARGET_LABEL,
):
    """
    First parcel-extraction milestone.

    It does NOT declare a legal/final boundary. It produces candidate
    boundary lines, corner points, and measurement candidates for
    confirmation.
    """
    image_path = Path(image_path)
    output_dir = Path(output_dir)

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    target_box = _ocr_target_label(
        image,
        target=target,
    )

    if target_box is None:
        raise ValueError(
            f"Could not find target parcel label "
            f"'{target}' using OCR."
        )

    all_lines = detect_lines(
        image_path,
        remove_noise=True,
    )

    target_lines = _filter_lines_for_target(
        all_lines,
        target_box,
        image.shape,
    )

    points = _find_intersection_candidates(
        target_lines
    )

    all_measurements = extract_measurements(
        image_path,
        lines=all_lines,
    )

    target_measurements = (
        _measurement_candidates_near_target(
            all_measurements,
            target_box,
        )
    )

    overlay_path = (
        output_dir /
        "parcel_10A_candidates.png"
    )

    _create_overlay(
        image,
        target_box,
        target_lines,
        points,
        target_measurements,
        overlay_path,
    )

    points_csv = (
        output_dir /
        "points_candidates.csv"
    )

    measurements_csv = (
        output_dir /
        "measurements_candidates.csv"
    )

    _write_points_csv(
        points,
        points_csv,
    )

    _write_measurements_csv(
        target_measurements,
        measurements_csv,
    )

    return {
        "target": target_box,
        "candidate_lines": target_lines,
        "candidate_points": points,
        "candidate_measurements": target_measurements,
        "overlay": overlay_path,
        "points_csv": points_csv,
        "measurements_csv": measurements_csv,
    }


if __name__ == "__main__":
    image_path = (
        "data/fmb/processed/fmb_map.png"
    )

    output_dir = (
        Path("data/fmb/processed")
    )

    result = extract_parcel_candidates(
        image_path=image_path,
        output_dir=output_dir,
        target="10A",
    )

    print("\n========== PARCEL EXTRACTION ==========\n")

    print(
        "Target:",
        result["target"]
    )

    print(
        "Candidate lines:",
        len(result["candidate_lines"])
    )

    print(
        "Candidate points:",
        len(result["candidate_points"])
    )

    print(
        "Candidate measurements:",
        len(result["candidate_measurements"])
    )

    print(
        "\nOverlay:",
        result["overlay"]
    )

    print(
        "Points CSV:",
        result["points_csv"]
    )

    print(
        "Measurements CSV:",
        result["measurements_csv"]
    )

    print(
        "\nIMPORTANT: All points and measurements "
        "are CANDIDATES and require confirmation."
    )
