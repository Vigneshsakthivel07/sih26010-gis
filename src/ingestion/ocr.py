from pathlib import Path

import cv2
import pytesseract

from pytesseract import Output


def extract_text_with_boxes(image_path):
    """
    Extract OCR text together with its image coordinates
    and confidence score.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    data = pytesseract.image_to_data(
        image,
        config="--psm 6",
        output_type=Output.DICT
    )

    results = []

    for i in range(len(data["text"])):

        text = data["text"][i].strip()

        if not text:
            continue

        try:
            confidence = float(data["conf"][i])
        except ValueError:
            confidence = -1

        results.append({
            "text": text,
            "x": int(data["left"][i]),
            "y": int(data["top"][i]),
            "width": int(data["width"][i]),
            "height": int(data["height"][i]),
            "confidence": confidence
        })

    return results


if __name__ == "__main__":

    image_path = (
        "data/fmb/processed/FMB_page_1.png"
    )

    results = extract_text_with_boxes(image_path)

    print("\n========== OCR BOXES ==========\n")

    for item in results:
        print(
            f"{item['text']:20} "
            f"x={item['x']:4} "
            f"y={item['y']:4} "
            f"w={item['width']:3} "
            f"h={item['height']:3} "
            f"confidence={item['confidence']:.1f}"
        )

    print("\n================================")
