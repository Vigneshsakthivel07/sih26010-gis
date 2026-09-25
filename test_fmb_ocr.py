from src.digitization.ocr import extract_text


image_file = "data/fmb/raw/FMB_processed.png"

text = extract_text(image_file)

print("\n========== OCR RESULT ==========\n")
print(text)
print("\n================================")
