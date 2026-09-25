from pathlib import Path
import fitz


def pdf_to_images(pdf_path, output_dir, dpi=300):
    """
    Convert every PDF page into a high-resolution PNG image.

    Returns:
        list[Path]: generated image paths
    """

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    document = fitz.open(pdf_path)

    image_paths = []

    scale = dpi / 72
    matrix = fitz.Matrix(scale, scale)

    for page_number, page in enumerate(document, start=1):

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        output_path = (
            output_dir /
            f"{pdf_path.stem}_page_{page_number}.png"
        )

        pixmap.save(str(output_path))

        image_paths.append(output_path)

    document.close()

    return image_paths
