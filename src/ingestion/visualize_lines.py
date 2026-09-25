from pathlib import Path

import cv2

from src.ingestion.map_lines import detect_lines


def create_line_overlay(image_path, output_path):

    image_path = Path(image_path)
    output_path = Path(output_path)

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    lines = detect_lines(image_path)

    for line in lines:

        x1 = line["x1"]
        y1 = line["y1"]
        x2 = line["x2"]
        y2 = line["y2"]

        cv2.line(
            image,
            (x1, y1),
            (x2, y2),
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

    return output_path


if __name__ == "__main__":

    input_path = (
        "data/fmb/processed/fmb_map.png"
    )

    output_path = (
        "data/fmb/processed/"
        "fmb_lines_overlay.png"
    )

    result = create_line_overlay(
        input_path,
        output_path
    )

    print("Overlay created:")
    print(result)
