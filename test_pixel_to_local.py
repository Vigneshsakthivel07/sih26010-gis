from src.digitization.pixel_to_local import (
    load_points,
    pixel_to_local
)


csv_file = (
    "data/fmb/fmb_selected_points.csv"
)


points = load_points(csv_file)

local_points = pixel_to_local(
    points,
    scale_denominator=848
)


print()
print("========== LOCAL FMB COORDINATES ==========")

for point_id, coordinates in local_points.items():

    x, y = coordinates

    print(
        f"{point_id}: "
        f"x={x:.3f} m, "
        f"y={y:.3f} m"
    )

print("===========================================")
