import cv2

from src.digitization.corners import detect_corners


image_file = "data/fmb/raw/FMB_page.png"

output_file = (
    "data/fmb/raw/"
    "FMB_corners_detected.png"
)

image = cv2.imread(image_file)

corners = detect_corners(image_file)

print("Detected corners:", len(corners))

for corner in corners:

    x, y = corner.ravel()

    cv2.circle(
        image,
        (int(x), int(y)),
        8,
        (0, 0, 255),
        -1
    )

cv2.imwrite(
    output_file,
    image
)

print(
    "Corner visualization saved to:",
    output_file
)
