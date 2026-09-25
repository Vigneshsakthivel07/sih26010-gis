from src.digitization.fmb_polygon import (
    create_fmb_polygon
)

from shapely.validation import explain_validity


points_file = (
    "data/fmb/fmb_selected_points.csv"
)

polygon = create_fmb_polygon(points_file)

print()
print("========== FMB POLYGON ==========")

print("Valid:", polygon.is_valid)

print(
    "Reason:",
    explain_validity(polygon)
)

print(
    "Number of vertices:",
    len(polygon.exterior.coords) - 1
)

print("=================================")
