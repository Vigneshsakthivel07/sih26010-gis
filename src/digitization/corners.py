import cv2


def detect_corners(image_path):
    """
    Detect candidate corners in an FMB image
    using the Shi-Tomasi corner detector.
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

    # Detect strong corner points
    corners = cv2.goodFeaturesToTrack(
        gray,
        maxCorners=100,
        qualityLevel=0.01,
        minDistance=20
    )

    if corners is None:
        return []

    corners = corners.astype(int)

    return corners
