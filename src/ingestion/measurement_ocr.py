from pathlib import Path
import math
import re
import cv2
import pytesseract
from pytesseract import Output

# Accept common OCR forms such as 20.6, 25, 89.4.
NUMBER_RE = re.compile(r"^\d{1,3}(?:[.,]\d{1,2})?$")


def _parse_number(text):
    text = text.strip().replace(",", ".")
    # Small OCR cleanup for common trailing-letter mistakes.
    text = re.sub(r"(?<=\d)[lI]$", "", text)
    if not NUMBER_RE.match(text):
        return None
    try:
        value = float(text)
    except ValueError:
        return None
    if value <= 0 or value > 500:
        return None
    return value


def _rotate(image, direction):
    if direction == "original":
        return image
    if direction == "cw":
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    if direction == "ccw":
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    raise ValueError(direction)


def _box_to_original(
    x,
    y,
    w,
    h,
    original_shape,
    direction
):
    """
    Convert an OCR bounding box from a rotated
    image back to original image coordinates.
    """

    H, W = original_shape[:2]

    if direction == "original":
        return x, y, w, h

    if direction == "cw":

        # Rotated clockwise:
        #
        # x' = H - 1 - y
        # y' = x

        original_x = H - (y + h)
        original_y = x

        return (
            original_x,
            original_y,
            h,
            w
        )

    if direction == "ccw":

        # Rotated counter-clockwise:
        #
        # x' = y
        # y' = W - 1 - x

        original_x = y
        original_y = W - (x + w)

        return (
            original_x,
            original_y,
            h,
            w
        )

    raise ValueError(direction)

def _blue_mask(image):
    """Keep blue cadastral annotations/dimensions while removing black/red text."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(
        hsv,
        (90, 50, 40),
        (140, 255, 255),
    )
    return cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),
    )


def _gray_variants(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(blurred, 180, 255, cv2.THRESH_BINARY)
    return [gray, binary]


def _distance_point_to_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    qx = x1 + t * dx
    qy = y1 + t * dy
    return math.hypot(px - qx, py - qy)


def _nearest_line(candidate, lines):
    cx = candidate["x"] + candidate["width"] / 2
    cy = candidate["y"] + candidate["height"] / 2
    best = float("inf")
    best_line = None
    for line in lines or []:
        distance = _distance_point_to_segment(
            cx, cy,
            line["x1"], line["y1"],
            line["x2"], line["y2"],
        )
        if distance < best:
            best = distance
            best_line = line
    return best, best_line


def _deduplicate(candidates):
    """Merge the same measurement found by multiple OCR passes."""
    kept = []
    for item in sorted(
        candidates,
        key=lambda x: (
            x["color"] == "blue",
            x["confidence"],
        ),
        reverse=True,
    ):
        duplicate = False
        for existing in kept:
            same_value = abs(item["value"] - existing["value"]) < 0.01
            close = (
                abs(item["x"] - existing["x"]) < 40
                and abs(item["y"] - existing["y"]) < 40
            )
            if same_value and close:
                duplicate = True
                break
        if not duplicate:
            kept.append(item)
    return kept


def _run_ocr(image, color, direction, original_shape, min_confidence):
    rotated = _rotate(image, direction)
    data = pytesseract.image_to_data(
        rotated,
        config="--psm 11",
        output_type=Output.DICT,
    )
    results = []

    for i, raw in enumerate(data["text"]):
        raw_text = raw.strip()
        value = _parse_number(raw_text)
        if value is None:
            continue

        try:
            confidence = float(data["conf"][i])
        except (ValueError, TypeError):
            confidence = -1

        if confidence < min_confidence:
            continue

        x = int(data["left"][i])
        y = int(data["top"][i])
        w = int(data["width"][i])
        h = int(data["height"][i])

        # Tiny OCR boxes are usually fragments of dashed lines/symbols.
        if w < 10 or h < 12:
            continue

        # On this FMB, black/red integers are mostly parcel/point labels.
        # Keep grayscale candidates when they contain a decimal point;
        # blue candidates are retained because the dimension layer is blue.
        if color == "gray" and "." not in raw_text and "," not in raw_text:
            continue
        x, y, w, h = _box_to_original(
            x, y, w, h, original_shape, direction
        )

        results.append({
            "value": value,
            "x": int(x),
            "y": int(y),
            "width": int(w),
            "height": int(h),
            "confidence": round(confidence, 1),
            "color": color,
            "orientation": direction,
        })

    return results


def extract_measurements(
    image_path,
    lines=None,
    min_confidence=45,
    boundary_distance=90,
):
    """
    Extract measurement candidates from an FMB map.

    Strategy:
    1. OCR the blue annotation layer because FMB dimensions are commonly blue.
    2. OCR grayscale in three orientations to recover rotated/black text.
    3. Convert rotated OCR boxes back to original coordinates.
    4. Attach distance to the nearest detected boundary line.
    5. Deduplicate repeated detections.

    Output is a candidate list, not a legally authoritative interpretation.
    """
    image_path = Path(image_path)
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    candidates = []

    # Blue dimensions/annotations are the strongest signal on this FMB.
    blue = _blue_mask(image)
    for direction in ("original", "cw", "ccw"):
        candidates.extend(
            _run_ocr(
                blue,
                "blue",
                direction,
                image.shape,
                min_confidence,
            )
        )

    # Grayscale catches non-blue dimensions and acts as a fallback.
    for gray_variant in _gray_variants(image):
        for direction in ("original", "cw", "ccw"):
            candidates.extend(
                _run_ocr(
                    gray_variant,
                    "gray",
                    direction,
                    image.shape,
                    min_confidence,
                )
            )

    candidates = _deduplicate(candidates)

    for candidate in candidates:
        distance, nearest = _nearest_line(candidate, lines)
        candidate["boundary_distance_px"] = round(distance, 1)
        candidate["near_boundary"] = distance <= boundary_distance
        if nearest is not None:
            candidate["nearest_line"] = {
                "x1": nearest["x1"],
                "y1": nearest["y1"],
                "x2": nearest["x2"],
                "y2": nearest["y2"],
            }

    candidates.sort(key=lambda x: (x["y"], x["x"]))
    return candidates

if __name__ == "__main__":

    from src.ingestion.map_lines import detect_lines

    image_path = (
        "data/fmb/processed/fmb_map.png"
    )

    lines = detect_lines(image_path)

    results = extract_measurements(
        image_path,
        lines=lines
    )

    print(
        "\n========== "
        "IMPROVED MEASUREMENTS "
        "==========\n"
    )

    for item in results:

        print(
            f"value={item['value']:6.2f} "
            f"x={item['x']:4} "
            f"y={item['y']:4} "
            f"conf={item['confidence']:5.1f} "
            f"color={item['color']:5} "
            f"orientation={item['orientation']:8} "
            f"near_boundary={item['near_boundary']} "
            f"distance={item['boundary_distance_px']}"
        )

    print(
        f"\nTotal candidates: "
        f"{len(results)}"
    )
