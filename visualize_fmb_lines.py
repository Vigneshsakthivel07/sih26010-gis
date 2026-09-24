import cv2

from src.digitization.points import (
    detect_lines,
    filter_long_lines
)

image_file = "data/fmb/raw/FMB_page.png"

output_file = (
    "data/fmb/raw/"
    "FMB_boundary_lines.png"
)

image = cv2.imread(image_file)

lines = detect_lines(image_file)

print("Detected lines:", len(lines))

filtered_lines = filter_long_lines(
    lines,
    minimum_length=80
)

print(
    "Long lines:",
    len(filtered_lines)
)

for line in filtered_lines:

    x1, y1, x2, y2 = line[0]

    cv2.line(
        image,
        (int(x1), int(y1)),
        (int(x2), int(y2)),
        (0, 0, 255),
        2
    )

cv2.imwrite(
    output_file,
    image
)

print(
    "Visualization saved to:",
    output_file
)
