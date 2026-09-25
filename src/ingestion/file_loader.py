from pathlib import Path

from src.ingestion.pdf_loader import pdf_to_images
from src.ingestion.image_loader import load_image
from src.ingestion.csv_loader import load_csv


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".tif",
    ".tiff",
    ".csv",
}


def detect_file_type(file_path):

    file_path = Path(file_path)

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    if extension == ".pdf":
        return "pdf"

    if extension == ".csv":
        return "csv"

    return "image"


def load_fmb(file_path, output_dir):
    """
    Normalize an FMB input into a common representation.
    """

    file_path = Path(file_path)

    file_type = detect_file_type(file_path)

    if file_type == "pdf":

        images = pdf_to_images(
            file_path,
            output_dir
        )

        return {
            "file_type": "pdf",
            "source": file_path,
            "images": images,
        }

    if file_type == "image":

        image = load_image(file_path)

        return {
            "file_type": "image",
            "source": file_path,
            "images": [file_path],
            "image_data": [image],
        }

    if file_type == "csv":

        dataframe = load_csv(file_path)

        return {
            "file_type": "csv",
            "source": file_path,
            "dataframe": dataframe,
        }
