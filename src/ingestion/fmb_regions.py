from pathlib import Path
import cv2


def crop_header(image_path, output_path):
    image_path = Path(image_path)
    output_path = Path(output_path)

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    height, width = image.shape[:2]

    header = image[150:560, 100:2150]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), header)

    return output_path


def crop_map(image_path, output_path):
    image_path = Path(image_path)
    output_path = Path(output_path)

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    height, width = image.shape[:2]

    print("Image width :", width)
    print("Image height:", height)

    # Remove the header and footer.
    map_region = image[560:3000, 100:2150]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), map_region)

    return output_path
