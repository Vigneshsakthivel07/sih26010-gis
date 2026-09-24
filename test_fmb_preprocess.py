from src.digitization.preprocess import (
    pdf_to_image,
    preprocess_image
)


pdf_file = "data/fmb/raw/FMB.pdf"

raw_image = "data/fmb/raw/FMB_page.png"

processed_image = "data/fmb/raw/FMB_processed.png"


pdf_to_image(
    pdf_file,
    raw_image
)

print("PDF converted to image:")
print(raw_image)


preprocess_image(
    raw_image,
    processed_image
)

print("Image preprocessing completed:")
print(processed_image)
