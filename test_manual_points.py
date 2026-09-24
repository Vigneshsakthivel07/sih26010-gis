from src.digitization.manual_points import (
    select_points
)


image_file = (
    "data/fmb/raw/FMB_page.png"
)

output_file = (
    "data/fmb/fmb_selected_points.csv"
)


select_points(
    image_file,
    output_file
)
