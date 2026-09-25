from pathlib import Path
import cv2


def crop_header(image_path, output_path):
    """
    Crop the FMB header containing metadata such as
    Survey Number, Taluk, Area, Village and Scale.
    """

    image_path = Path(image_path)
    output_path = Path(output_path)

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    height, width = image.shape[:2]

    print("Image width :", width)
    print("Image height:", height)

    # Header region of the current FMB layout.
    #
    # We deliberately keep this as a separate region
    # instead of OCR-ing the entire cadastral drawing.

    header = image[150:560, 100:2150]

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cv2.imwrite(
        str(output_path),
        header
    )

    return output_path
