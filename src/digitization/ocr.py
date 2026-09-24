import pytesseract
import cv2


def extract_text(image_path):
    """
    Extract text from an FMB image using Tesseract OCR.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(
            f"Could not read image: {image_path}"
        )

    text = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    return text
