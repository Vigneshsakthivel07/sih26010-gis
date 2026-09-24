import fitz
import cv2


def pdf_to_image(pdf_path, output_path, dpi=300):
    """
    Convert the first page of an FMB PDF into a PNG image.
    """

    document = fitz.open(pdf_path)

    page = document[0]

    zoom = dpi / 72

    matrix = fitz.Matrix(zoom, zoom)

    pixmap = page.get_pixmap(
        matrix=matrix,
        alpha=False
    )

    pixmap.save(output_path)

    document.close()

    return output_path


def preprocess_image(image_path, output_path):
    """
    Convert FMB image to grayscale and apply thresholding.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(
            f"Could not read image: {image_path}"
        )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    threshold = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    cv2.imwrite(
        output_path,
        threshold
    )

    return output_path
