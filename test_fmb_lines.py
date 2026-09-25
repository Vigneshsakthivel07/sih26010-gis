import cv2

from src.digitization.points import (
    detect_lines,
    filter_border_lines
)


image_file = "data/fmb/raw/FMB_page.png"

image = cv2.imread(image_file)

height, width = image.shape[:2]

lines = detect_lines(image_file)

print("Original lines:", len(lines))


filtered_lines = filter_border_lines(
    lines,
    width,
    height
)

print("After border filtering:", len(filtered_lines))


for i, line in enumerate(filtered_lines[:20]):

    x1, y1, x2, y2 = line.reshape(-1)

    print(
        f"Line {i + 1}: "
        f"({x1}, {y1}) -> ({x2}, {y2})"
    )
