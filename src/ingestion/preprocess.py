from pathlib import Path
import cv2


def preprocess_fmb(image_path, output_dir):
    """
    Preprocess an FMB image for later
    boundary and OCR extraction.
    """

    image_path = Path(image_path)
    output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Read original image
    image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    # 2. Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    gray_path = output_dir / "fmb_grayscale.png"
    cv2.imwrite(str(gray_path), gray)

    # 3. Reduce small image noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 4. Improve local contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(blurred)

    enhanced_path = output_dir / "fmb_enhanced.png"
    cv2.imwrite(str(enhanced_path), enhanced)

    # 5. Adaptive threshold
    threshold = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        10
    )

    threshold_path = output_dir / "fmb_threshold.png"
    cv2.imwrite(str(threshold_path), threshold)

    return {
        "original": image_path,
        "grayscale": gray_path,
        "enhanced": enhanced_path,
        "threshold": threshold_path
    }
