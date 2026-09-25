from pathlib import Path
import cv2
import pytesseract


def extract_header_text(image_path):
    image_path = Path(image_path)

    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Improve text visibility
    _, threshold = cv2.threshold(
        image,
        180,
        255,
        cv2.THRESH_BINARY
    )

    text = pytesseract.image_to_string(
        threshold,
        config="--psm 6"
    )

    return text


if __name__ == "__main__":

    image_path = "data/fmb/processed/fmb_header.png"

    text = extract_header_text(image_path)

    print("\n========== HEADER OCR ==========\n")
    print(text)
    print("\n================================")
