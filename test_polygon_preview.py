from src.digitization.polygon_preview import (
    create_polygon_preview
)


image_file = (
    "data/fmb/raw/FMB_page.png"
)

points_file = (
    "data/fmb/fmb_selected_points.csv"
)

output_file = (
    "data/fmb/raw/FMB_selected_polygon.png"
)


create_polygon_preview(
    image_file,
    points_file,
    output_file
)

print(
    "Polygon preview saved to:"
)

print(output_file)
